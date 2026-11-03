$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UC2.cs"
try { Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs } catch { Write-Host $_ }
[UC2]::InitDpi()
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"

function SaveCrop($bmp,$name,$x,$y,$w,$h){
  if($x -lt 0){$x=0}; if($y -lt 0){$y=0}
  $mw=$bmp.Width-$x; $mh=$bmp.Height-$y
  if($w -gt $mw){$w=$mw}; if($h -gt $mh){$h=$mh}
  if($w -lt 8 -or $h -lt 8){return}
  $crop=$bmp.Clone((New-Object System.Drawing.Rectangle $x,$y,$w,$h),$bmp.PixelFormat)
  $crop.Save((Join-Path $docs $name),[System.Drawing.Imaging.ImageFormat]::Png)
  $crop.Dispose(); Write-Host "CROP $name"
}

function SyncAsset($pyfile) {
  & $py "$docs\_run_one.py" $pyfile | Out-Host
  Start-Sleep -Milliseconds 1500
}

function AddOne($label) {
  Write-Host "==== $label ===="
  $proc = Get-Process UE4Editor | Select-Object -First 1
  [UC2]::Force($proc.MainWindowHandle)
  Start-Sleep -Milliseconds 200
  $rect = New-Object UC2+RECT
  [UC2]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
  Write-Host "WIN $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top)"

  $bmp = [UC2]::Cap($proc.MainWindowHandle)
  $gc = [UC2]::GreenBtn($bmp)
  Write-Host "Green cx=$($gc[0]) cy=$($gc[1]) minX=$($gc[4]) maxX=$($gc[3]) minY=$($gc[6]) maxY=$($gc[5]) n=$($gc[2])"
  SaveCrop $bmp "ue_v2_$($label)_0.png" 0 50 480 520
  if ($gc[0] -lt 0) { $bmp.Dispose(); throw "no green" }

  # Select 网格体 (CharacterMesh0) - from screenshots it's under Capsule, typically y~230-260 client
  # In capture coords relative to window client area of bitmap:
  # Hierarchy: Self~175, Capsule~200, Arrow~220, Mesh~240, CameraBoom~260
  $meshRelY = 248
  [UC2]::ClickAt(($rect.Left + 140), ($rect.Top + $meshRelY))
  Start-Sleep -Milliseconds 400
  $bmp.Dispose()
  $bmp = [UC2]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_v2_$($label)_mesh.png" 0 50 480 400

  # Click green Add - use center of green blob
  $gx = $rect.Left + $gc[0]
  $gy = $rect.Top + $gc[1]
  Write-Host "Click green at abs $gx,$gy"
  [UC2]::Force($proc.MainWindowHandle)
  [UC2]::ClickAt($gx, $gy)
  Start-Sleep -Milliseconds 1100
  $bmp.Dispose()
  $bmp = [UC2]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_v2_$($label)_menu.png" 0 60 520 720
  $open = [UC2]::MenuOpen($bmp, $gc[5])
  Write-Host "MenuOpen=$open"

  if (-not $open) {
    # retry click green slightly left (on the + text not arrow)
    $gx2 = $rect.Left + [Math]::Max($gc[4]+20, 55)
    $gy2 = $rect.Top + $gc[1]
    Write-Host "Retry green $gx2,$gy2"
    [UC2]::ClickAt($gx2, $gy2)
    Start-Sleep -Milliseconds 1100
    $bmp.Dispose()
    $bmp = [UC2]::Cap($proc.MainWindowHandle)
    SaveCrop $bmp "ue_v2_$($label)_menu2.png" 0 60 520 720
    $open = [UC2]::MenuOpen($bmp, $gc[5])
    Write-Host "MenuOpen2=$open"
  }

  if (-not $open) {
    Write-Host "FAIL menu did not open for $label"
    $bmp.Dispose()
    return $false
  }

  # Find SM_KayKit* row: in Common, look for row with gray mesh icon + long bright text
  # From prior success, item sits roughly y 300-380 in window coords when menu open
  # Scan for rows with high text brightness in x=70-400
  $candidates = @()
  for ($y = ($gc[5] + 50); $y -lt 520 -and $y -lt $bmp.Height; $y++) {
    $hits = 0
    for ($x = 90; $x -lt 380 -and $x -lt $bmp.Width; $x += 2) {
      $c = $bmp.GetPixel($x, $y)
      if (($c.R + $c.G + $c.B) -gt 470) { $hits++ }
    }
    if ($hits -gt 30) { $candidates += $y }
  }
  # Cluster into row centers
  $rows = @(); $start = -1; $prev = -99
  foreach ($y in $candidates) {
    if ($y -gt $prev + 3) {
      if ($start -ge 0) { $rows += [int](($start + $prev) / 2) }
      $start = $y
    }
    $prev = $y
  }
  if ($start -ge 0) { $rows += [int](($start + $prev) / 2) }
  Write-Host "textRows=$($rows -join ',')"

  # Score rows: prefer those with gray cube icon at x~35-50 and in Common band (after ~2 scripting rows)
  $bestY = -1; $bestScore = -999
  foreach ($ry in $rows) {
    $score = 0
    if ($ry -ge 280 -and $ry -le 430) { $score += 10 }
    for ($dx = 28; $dx -le 58; $dx++) {
      $c = $bmp.GetPixel($dx, $ry)
      $avg = ($c.R + $c.G + $c.B) / 3.0
      if ($avg -gt 60 -and $avg -lt 170) { $score += 1 }
    }
    # longer label (SM_KayKitSword) => more bright pixels across width
    $wide = 0
    for ($x = 100; $x -lt 420 -and $x -lt $bmp.Width; $x += 3) {
      $c = $bmp.GetPixel($x, $ry)
      if (($c.R + $c.G + $c.B) -gt 450) { $wide++ }
    }
    $score += [Math]::Min(15, $wide)
    Write-Host "row $ry score=$score wide=$wide"
    if ($score -gt $bestScore) { $bestScore = $score; $bestY = $ry }
  }
  if ($bestY -lt 0) {
    # fallback known positions from earlier successful menu open
    $bestY = 330
  }
  Write-Host "Click menu item y=$bestY score=$bestScore"
  $bmp.Dispose()

  [UC2]::Force($proc.MainWindowHandle)
  [UC2]::ClickAt(($rect.Left + 170), ($rect.Top + $bestY))
  Start-Sleep -Milliseconds 1400

  $bmp = [UC2]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_v2_$($label)_after.png" 0 50 480 480
  $stillOpen = [UC2]::MenuOpen($bmp, $gc[5])
  Write-Host "AfterClick menuStillOpen=$stillOpen (want false)"
  $bmp.Dispose()
  return (-not $stillOpen)
}

# Ensure BP open + sword in CB
SyncAsset "$docs\_sync_sword_now.py"
$ok1 = AddOne "sword"
Write-Host "sword_ok=$ok1"

SyncAsset "$docs\_sync_shield_now.py"
$ok2 = AddOne "shield"
Write-Host "shield_ok=$ok2"

# Compile F7 + Ctrl+S
$proc = Get-Process UE4Editor | Select-Object -First 1
[UC2]::Force($proc.MainWindowHandle)
[UC2]::Tap(0x76)
Start-Sleep -Milliseconds 1200
[UC2]::keybd_event(0x11, 0, 0, [UIntPtr]::Zero)
[UC2]::Tap(0x53)
[UC2]::keybd_event(0x11, 0, 2, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 800

$bmp = [UC2]::Cap($proc.MainWindowHandle)
SaveCrop $bmp "ue_v2_final.png" 0 50 520 520
$bmp.Dispose()

& $py "$docs\_run_one.py" "$docs\_verify_scs.py" | Out-Host
Write-Host "FINISHED sword=$ok1 shield=$ok2"