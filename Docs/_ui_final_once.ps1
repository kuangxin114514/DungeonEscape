$ErrorActionPreference="Continue"
Add-Type -AssemblyName System.Drawing,System.Windows.Forms
$drawing=[System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs=Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UC.cs"
try{ Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs }catch{}
[UC]::InitDpi()
$docs="C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
$py="C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"

function SaveCrop($bmp,$name,$x,$y,$w,$h){
  if($x -lt 0){$x=0}; if($y -lt 0){$y=0}
  $mw=$bmp.Width-$x; $mh=$bmp.Height-$y
  if($w -gt $mw){$w=$mw}; if($h -gt $mh){$h=$mh}
  if($w -lt 8 -or $h -lt 8){return}
  $crop=$bmp.Clone((New-Object System.Drawing.Rectangle $x,$y,$w,$h),$bmp.PixelFormat)
  $crop.Save((Join-Path $docs $name),[System.Drawing.Imaging.ImageFormat]::Png)
  $crop.Dispose(); Write-Host "CROP $name"
}

function IsRealMenu([System.Drawing.Bitmap]$bmp, [int]$greenMaxY){
  # Real Add menu: dark panel (~50-70 gray) spanning x~20-340 below green, with many light-text rows
  $darkCols=0; $textRows=0
  for($x=40;$x -lt 300;$x+=10){
    $c=$bmp.GetPixel($x, ($greenMaxY+80))
    $avg=($c.R+$c.G+$c.B)/3
    if($avg -gt 35 -and $avg -lt 95){ $darkCols++ }
  }
  for($y=$greenMaxY+40; $y -lt [Math]::Min($bmp.Height,$greenMaxY+380); $y+=20){
    $hits=0
    for($x=90;$x -lt 320;$x+=4){
      $c=$bmp.GetPixel($x,$y)
      # reject tan selection 201,174,140
      if($c.R -gt 180 -and $c.G -gt 150 -and $c.B -lt 160){ continue }
      if(($c.R+$c.G+$c.B) -gt 420 -and ($c.R+$c.G+$c.B) -lt 720){ $hits++ }
    }
    if($hits -gt 12){ $textRows++ }
  }
  Write-Host "MenuProbe darkCols=$darkCols textRows=$textRows"
  return ($darkCols -ge 12 -and $textRows -ge 5)
}

function SelectMesh($rect){
  # Click several Y candidates under Capsule for CharacterMesh0; verify orange selection near that row
  $proc=Get-Process UE4Editor|Select-Object -First 1
  foreach($my in @(255,270,245,285,300)){
    [UC]::Force($proc.MainWindowHandle)
    [UC]::ClickAt(($rect.Left+130), ($rect.Top+$my))
    Start-Sleep -Milliseconds 350
    $bmp=[UC]::Cap($proc.MainWindowHandle)
    # orange/tan selection around click y
    $hits=0
    for($yy=$my-8; $yy -le $my+8; $yy++){
      for($xx=40;$xx -lt 280;$xx+=3){
        $c=$bmp.GetPixel($xx,$yy)
        if($c.R -gt 170 -and $c.G -gt 120 -and $c.G -lt 200 -and $c.B -lt 160 -and $c.R -gt $c.B+40){ $hits++ }
      }
    }
    Write-Host "MeshTry y=$my selHits=$hits"
    SaveCrop $bmp "ue_final_mesh_$my.png" 0 150 420 220
    $bmp.Dispose()
    if($hits -gt 80){ Write-Host "Mesh selected at $my"; return $true }
  }
  return $false
}

function AddWeapon($label, $filterText){
  Write-Host "==== ADD $label filter=$filterText ===="
  & $py "$docs\_run_one.py" "$docs\_sync_$($label)_now.py" | Out-Host
  Start-Sleep -Milliseconds 1800
  $proc=Get-Process UE4Editor|Select-Object -First 1
  [UC]::Force($proc.MainWindowHandle)
  $rect=New-Object UC+RECT
  [UC]::GetWindowRect($proc.MainWindowHandle,[ref]$rect)|Out-Null
  Write-Host "WIN $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top)"
  $bmp=[UC]::Cap($proc.MainWindowHandle)
  $gc=[UC]::GreenBtn($bmp)
  Write-Host "Green cx=$($gc[0]) cy=$($gc[1]) minX=$($gc[4]) maxX=$($gc[3]) minY=$($gc[6]) maxY=$($gc[5]) n=$($gc[2])"
  SaveCrop $bmp "ue_final_$($label)_0.png" 0 50 500 520
  $bmp.Dispose()
  if($gc[0] -lt 0){ Write-Host "NO GREEN"; return $false }

  [void](SelectMesh $rect)

  # Open menu - click left-center of green (not arrow)
  $gx=$rect.Left + [int](($gc[4]+$gc[0])/2)
  $gy=$rect.Top + $gc[1]
  [UC]::Force($proc.MainWindowHandle)
  [UC]::ClickAt($gx,$gy)
  Start-Sleep -Milliseconds 1100
  $bmp=[UC]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_final_$($label)_menu.png" 0 60 520 750
  $open=IsRealMenu $bmp $gc[5]
  Write-Host "RealMenu=$open"
  if(-not $open){
    # second try: click green center
    $bmp.Dispose()
    [UC]::ClickAt(($rect.Left+$gc[0]), ($rect.Top+$gc[1]))
    Start-Sleep -Milliseconds 1100
    $bmp=[UC]::Cap($proc.MainWindowHandle)
    SaveCrop $bmp "ue_final_$($label)_menu2.png" 0 60 520 750
    $open=IsRealMenu $bmp $gc[5]
    Write-Host "RealMenu2=$open"
  }
  if(-not $open){ $bmp.Dispose(); return $false }

  # Menu search: click near top of dropdown (search field inside menu ~ greenMaxY+25)
  $searchY = $rect.Top + $gc[5] + 28
  $searchX = $rect.Left + 160
  [UC]::ClickAt($searchX, $searchY)
  Start-Sleep -Milliseconds 250
  [System.Windows.Forms.Clipboard]::SetText($filterText)
  Start-Sleep -Milliseconds 80
  # Ctrl+A then Ctrl+V
  [UC]::keybd_event(0x11,0,0,[UIntPtr]::Zero)
  [UC]::Tap(0x41)
  [UC]::keybd_event(0x11,0,2,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 60
  [UC]::keybd_event(0x11,0,0,[UIntPtr]::Zero)
  [UC]::Tap(0x56)
  [UC]::keybd_event(0x11,0,2,[UIntPtr]::Zero)
  Start-Sleep -Milliseconds 700
  $bmp.Dispose()
  $bmp=[UC]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_final_$($label)_filtered.png" 0 60 520 500

  # Click first filtered result: typically ~70-90px below greenMaxY after filter
  $pickY = $rect.Top + $gc[5] + 78
  Write-Host "Click filtered result at y offset $($gc[5]+78)"
  [UC]::ClickAt(($rect.Left+170), $pickY)
  Start-Sleep -Milliseconds 1200
  $bmp.Dispose()
  $bmp=[UC]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_final_$($label)_after.png" 0 50 500 500
  $still=IsRealMenu $bmp $gc[5]
  Write-Host "AfterPick menuStill=$still"
  $bmp.Dispose()
  return (-not $still)
}

$okS = AddWeapon "sword" "SM_KayKitSword"
Write-Host "sword_result=$okS"
$okH = AddWeapon "shield" "SM_KayKitShield"
Write-Host "shield_result=$okH"

$proc=Get-Process UE4Editor|Select-Object -First 1
[UC]::Force($proc.MainWindowHandle)
[UC]::Tap(0x76) # F7
Start-Sleep -Milliseconds 1500
[UC]::keybd_event(0x11,0,0,[UIntPtr]::Zero)
[UC]::Tap(0x53)
[UC]::keybd_event(0x11,0,2,[UIntPtr]::Zero)
Start-Sleep -Milliseconds 900
$bmp=[UC]::Cap($proc.MainWindowHandle)
SaveCrop $bmp "ue_final_done.png" 0 50 520 520
$bmp.Dispose()

& $py "$docs\_run_one.py" "$docs\_verify_scs.py" | Out-Host
Write-Host "FINAL sword=$okS shield=$okH"