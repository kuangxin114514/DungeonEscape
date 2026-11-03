$ErrorActionPreference="Continue"
Add-Type -AssemblyName System.Drawing,System.Windows.Forms
$drawing=[System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs=Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UC.cs"
try{Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs}catch{}
[UC]::InitDpi()
$docs="C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
$pyExe="C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"

function SaveCrop($bmp,$name,$x,$y,$w,$h){
  $x=[Math]::Max(0,$x); $y=[Math]::Max(0,$y)
  $w=[Math]::Min($w,$bmp.Width-$x); $h=[Math]::Min($h,$bmp.Height-$y)
  if($w -lt 8 -or $h -lt 8){return}
  $r=New-Object System.Drawing.Rectangle($x,$y,$w,$h)
  $crop=$bmp.Clone($r,$bmp.PixelFormat)
  $crop.Save((Join-Path $docs $name),[System.Drawing.Imaging.ImageFormat]::Png)
  $crop.Dispose(); Write-Host "CROP $name"
}

function FindAddGreen([System.Drawing.Bitmap]$bmp){
  # Prefer leftmost green blob in top-left Components chrome (x<220, y 90-200)
  $sx=0;$sy=0;$n=0;$minX=9999;$maxX=0;$minY=9999;$maxY=0
  for($y=90;$y -lt 200;$y++){
    for($x=5;$x -lt 220;$x++){
      $c=$bmp.GetPixel($x,$y)
      if($c.G -gt 145 -and $c.G -gt ($c.R+45) -and $c.R -lt 110 -and $c.B -lt 110){
        $sx+=$x; $sy+=$y; $n++
        if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}
        if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y}
      }
    }
  }
  if($n -lt 40){
    # expand search y
    for($y=200;$y -lt 320;$y++){
      for($x=5;$x -lt 220;$x++){
        $c=$bmp.GetPixel($x,$y)
        if($c.G -gt 145 -and $c.G -gt ($c.R+45) -and $c.R -lt 110 -and $c.B -lt 110){
          $sx+=$x; $sy+=$y; $n++
          if($x -lt $minX){$minX=$x}; if($x -gt $maxX){$maxX=$x}
          if($y -lt $minY){$minY=$y}; if($y -gt $maxY){$maxY=$y}
        }
      }
    }
  }
  if($n -lt 40){ return @{ok=$false} }
  return @{ok=$true; cx=[int]($sx/$n); cy=[int]($sy/$n); n=$n; minX=$minX; maxX=$maxX; minY=$minY; maxY=$maxY}
}

function RealMenu($bmp,$gMaxY){
  $dark=0; $rows=0
  $yy=$gMaxY+90
  if($yy -ge $bmp.Height){return $false}
  for($x=40;$x -lt 300;$x+=8){
    $c=$bmp.GetPixel($x,$yy); $a=($c.R+$c.G+$c.B)/3.0
    if($a -gt 35 -and $a -lt 100){$dark++}
  }
  for($y=$gMaxY+50; $y -lt [Math]::Min($bmp.Height-10,$gMaxY+400); $y+=22){
    $hits=0
    for($x=90;$x -lt 320;$x+=4){
      $c=$bmp.GetPixel($x,$y)
      if($c.R -gt 180 -and $c.G -gt 150 -and $c.B -lt 160){continue}
      $s=$c.R+$c.G+$c.B
      if($s -gt 420 -and $s -lt 720){$hits++}
    }
    if($hits -gt 10){$rows++}
  }
  Write-Host "RealMenu dark=$dark rows=$rows"
  return ($dark -ge 10 -and $rows -ge 4)
}

function DoAdd($label,$filter){
  Write-Host "==== $label ===="
  & $pyExe "$docs\_run_one.py" "$docs\_sync_$($label)_now.py" | Out-Host
  Start-Sleep -Milliseconds 2000
  $proc=Get-Process UE4Editor|Select-Object -First 1
  # Maximize hard
  [UC]::ShowWindow($proc.MainWindowHandle,3)
  [UC]::Force($proc.MainWindowHandle)
  Start-Sleep -Milliseconds 500
  $rect=New-Object UC+RECT
  [UC]::GetWindowRect($proc.MainWindowHandle,[ref]$rect)|Out-Null
  Write-Host "WIN $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top)"

  $bmp=[UC]::Cap($proc.MainWindowHandle)
  $g=FindAddGreen $bmp
  Write-Host "Green ok=$($g.ok) cx=$($g.cx) cy=$($g.cy) bounds $($g.minX),$($g.minY)-$($g.maxX),$($g.maxY) n=$($g.n)"
  SaveCrop $bmp "ue_last_$($label)_0.png" 0 40 520 560
  if(-not $g.ok){ $bmp.Dispose(); return $false }

  # Click Mesh: from typical hierarchy Self~175 Capsule~200 Arrow~225 Mesh~248
  foreach($my in @(248,262,238,275)){
    [UC]::ClickAt(($rect.Left+135),($rect.Top+$my))
    Start-Sleep -Milliseconds 280
  }
  $bmp.Dispose()

  # Open Add menu
  $gx=$rect.Left + [int](($g.minX + $g.cx)/2)
  $gy=$rect.Top + $g.cy
  [UC]::Force($proc.MainWindowHandle)
  Write-Host "ClickAdd $gx,$gy"
  [UC]::ClickAt($gx,$gy)
  Start-Sleep -Milliseconds 1200
  $bmp=[UC]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_last_$($label)_menu.png" 0 50 540 780
  $open=RealMenu $bmp $g.maxY
  Write-Host "open=$open"
  if(-not $open){
    $bmp.Dispose()
    [UC]::ClickAt(($rect.Left+$g.cx),($rect.Top+$g.cy))
    Start-Sleep -Milliseconds 1200
    $bmp=[UC]::Cap($proc.MainWindowHandle)
    SaveCrop $bmp "ue_last_$($label)_menu2.png" 0 50 540 780
    $open=RealMenu $bmp $g.maxY
    Write-Host "open2=$open"
  }
  if(-not $open){ $bmp.Dispose(); return $false }

  # Click menu search field (inside dropdown, just under green)
  $sx=$rect.Left+150; $sy=$rect.Top+$g.maxY+30
  [UC]::ClickAt($sx,$sy)
  Start-Sleep -Milliseconds 200
  [System.Windows.Forms.Clipboard]::SetText($filter)
  [UC]::keybd_event(0x11,0,0,[UIntPtr]::Zero); [UC]::Tap(0x41); [UC]::keybd_event(0x11,0,2,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 50
  [UC]::keybd_event(0x11,0,0,[UIntPtr]::Zero); [UC]::Tap(0x56); [UC]::keybd_event(0x11,0,2,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 800
  $bmp.Dispose()
  $bmp=[UC]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_last_$($label)_filt.png" 0 50 540 480

  # First result row ~ maxY+75
  $ry=$rect.Top+$g.maxY+75
  Write-Host "PickResult $(($rect.Left+170)),$ry"
  [UC]::ClickAt(($rect.Left+170),$ry)
  Start-Sleep -Milliseconds 1300
  $bmp.Dispose()
  $bmp=[UC]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_last_$($label)_after.png" 0 50 520 520
  $still=RealMenu $bmp $g.maxY
  Write-Host "stillOpen=$still"
  $bmp.Dispose()
  return (-not $still)
}

$r1=DoAdd "sword" "SM_KayKitSword"
Write-Host "sword=$r1"
$r2=DoAdd "shield" "SM_KayKitShield"
Write-Host "shield=$r2"

$proc=Get-Process UE4Editor|Select-Object -First 1
[UC]::Force($proc.MainWindowHandle)
[UC]::Tap(0x76)
Start-Sleep -Milliseconds 1500
[UC]::keybd_event(0x11,0,0,[UIntPtr]::Zero); [UC]::Tap(0x53); [UC]::keybd_event(0x11,0,2,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 800
$bmp=[UC]::Cap($proc.MainWindowHandle)
SaveCrop $bmp "ue_last_final.png" 0 50 520 520
$bmp.Dispose()
& $pyExe "$docs\_run_one.py" "$docs\_verify_scs.py" | Out-Host
Write-Host "DONE sword=$r1 shield=$r2"