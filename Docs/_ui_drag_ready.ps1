$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UC.cs"
try { Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs } catch {}
[UC]::InitDpi()
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"

function SaveCrop($bmp,$name,$x,$y,$w,$h){
  if($x -lt 0){$x=0}; if($y -lt 0){$y=0}
  $mw=$bmp.Width-$x; $mh=$bmp.Height-$y
  if($w -gt $mw){$w=$mw}; if($h -gt $mh){$h=$mh}
  if($w -lt 10 -or $h -lt 10){ return }
  $crop=$bmp.Clone((New-Object System.Drawing.Rectangle $x,$y,$w,$h), $bmp.PixelFormat)
  $crop.Save((Join-Path $docs $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $crop.Dispose()
  Write-Host "CROP $name"
}

function AddStaticMeshFromCB([string]$assetName, [string]$label) {
  Write-Host "==== ADD $label ($assetName) ===="
  Set-Clipboard $assetName
  Start-Sleep -Milliseconds 300

  $proc = Get-Process UE4Editor | Select-Object -First 1
  [UC]::Force($proc.MainWindowHandle)
  $rect = New-Object UC+RECT
  [UC]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
  Write-Host "RECT L=$($rect.Left) T=$($rect.Top) W=$($rect.Right-$rect.Left) H=$($rect.Bottom-$rect.Top)"

  $bmp = [UC]::Cap($proc.MainWindowHandle)
  $gc = [UC]::GreenBtn($bmp)
  Write-Host "Green cx=$($gc[0]) cy=$($gc[1]) minX=$($gc[4]) maxX=$($gc[3])"
  SaveCrop $bmp "ue_dr_$($label)_before.png" 0 60 500 420
  if ($gc[0] -lt 0) { $bmp.Dispose(); throw "no green Add button" }

  # 1) Click Mesh / CharacterMesh0 in components tree (below Capsule/Arrow)
  # From prior layouts ~ y 230-300; try CharacterMesh0 which is usually 4th row
  $meshX = $rect.Left + 130
  $meshY = $rect.Top + 250
  [UC]::ClickAt($meshX, $meshY)
  Start-Sleep -Milliseconds 350
  # Also try slightly lower if needed - click again at 275
  [UC]::ClickAt($meshX, ($rect.Top + 275))
  Start-Sleep -Milliseconds 300

  # 2) Click green +添加组件 (left-center of green region)
  $gx = $rect.Left + [Math]::Max(40, [int](($gc[4] + $gc[0]) / 2))
  $gy = $rect.Top + $gc[1]
  [UC]::Force($proc.MainWindowHandle)
  [UC]::ClickAt($gx, $gy)
  Start-Sleep -Milliseconds 900
  $bmp.Dispose()
  $bmp = [UC]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_dr_$($label)_menu.png" 0 70 520 700

  # 3) Click search box (just under green button) then paste asset name
  $searchX = $rect.Left + 160
  $searchY = $rect.Top + ($gc[5] + 28)  # just below green maxY
  if ($searchY -lt ($rect.Top + 150)) { $searchY = $rect.Top + 165 }
  [UC]::ClickAt($searchX, $searchY)
  Start-Sleep -Milliseconds 250
  # Ctrl+A then Ctrl+V
  [UC]::Tap(0x11) | Out-Null # noop safety
  # keybd: Ctrl down, A, Ctrl up; Ctrl down, V, Ctrl up
  Add-Type -Namespace W -Name K -MemberDefinition @"
    [System.Runtime.InteropServices.DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, System.UIntPtr dwExtraInfo);
"@ -ErrorAction SilentlyContinue
  function Chord([byte]$vk) {
    [UC]::keybd_event(0x11, 0, 0, [UIntPtr]::Zero) # ctrl down
    Start-Sleep -Milliseconds 20
    [UC]::Tap($vk)
    Start-Sleep -Milliseconds 20
    [UC]::keybd_event(0x11, 0, 2, [UIntPtr]::Zero) # ctrl up
    Start-Sleep -Milliseconds 40
  }
  Chord 0x41  # Ctrl+A
  Start-Sleep -Milliseconds 80
  Chord 0x56  # Ctrl+V
  Start-Sleep -Milliseconds 700

  $bmp.Dispose()
  $bmp = [UC]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_dr_$($label)_filtered.png" 0 70 520 500

  # 4) Find first filtered result row - bright text below search, typically ~220-280
  # Prefer clicking ~55px below search bar (first result)
  $resultY = $searchY - $rect.Top + 55
  # Scan for bright text rows in menu
  $bestY = -1; $bestBright = 0
  for ($y = ($gc[5] + 40); $y -lt 420 -and $y -lt $bmp.Height; $y++) {
    $sum = 0; $n = 0
    for ($x = 80; $x -lt 360 -and $x -lt $bmp.Width; $x += 3) {
      $c = $bmp.GetPixel($x, $y)
      $sum += ($c.R + $c.G + $c.B); $n++
    }
    $avg = $sum / [Math]::Max(1,$n)
    if ($avg -gt 420 -and $avg -gt $bestBright) {
      # require some continuity (text row)
      $bestBright = $avg; $bestY = $y
    }
  }
  # Cluster: take first strong row after search
  $firstRow = -1
  for ($y = ($gc[5] + 45); $y -lt 380 -and $y -lt $bmp.Height; $y++) {
    $hits = 0
    for ($x = 90; $x -lt 300; $x += 2) {
      $c = $bmp.GetPixel($x, $y)
      if (($c.R + $c.G + $c.B) -gt 450) { $hits++ }
    }
    if ($hits -gt 25) { $firstRow = $y; break }
  }
  if ($firstRow -lt 0) { $firstRow = $resultY }
  Write-Host "firstRowY=$firstRow bestY=$bestY searchRel=$($searchY-$rect.Top)"
  $bmp.Dispose()

  [UC]::Force($proc.MainWindowHandle)
  [UC]::ClickAt(($rect.Left + 180), ($rect.Top + $firstRow))
  Start-Sleep -Milliseconds 1200

  $bmp = [UC]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp "ue_dr_$($label)_after.png" 0 60 520 450
  $bmp.Dispose()
  Write-Host "DONE_ADD $label"
}

# Sync sword, add sword
& $py "$docs\_run_one.py" "$docs\_sync_sword_now.py" | Out-Host
Start-Sleep -Milliseconds 1800
AddStaticMeshFromCB "SM_KayKitSword" "sword"

# Sync shield, add shield
& $py "$docs\_run_one.py" "$docs\_sync_shield_now.py" | Out-Host
Start-Sleep -Milliseconds 1200
AddStaticMeshFromCB "SM_KayKitShield" "shield"

# Compile: click toolbar Compile (usually top, near left of BP editor - orange/question if dirty)
$proc = Get-Process UE4Editor | Select-Object -First 1
[UC]::Force($proc.MainWindowHandle)
$rect = New-Object UC+RECT
[UC]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
# Compile button often around x=420-520 relative in BP editor chrome; try F7 hotkey instead
[UC]::Tap(0x76)  # F7 compile in UE
Start-Sleep -Milliseconds 1500
# Ctrl+S save
[UC]::keybd_event(0x11, 0, 0, [UIntPtr]::Zero)
[UC]::Tap(0x53)
[UC]::keybd_event(0x11, 0, 2, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 1000

$bmp = [UC]::Cap($proc.MainWindowHandle)
SaveCrop $bmp "ue_dr_final_components.png" 0 60 520 500
# wider viewport crop
SaveCrop $bmp "ue_dr_final_viewport.png" 500 80 900 700
$bmp.Dispose()

# Verify via python
& $py "$docs\_run_one.py" "$docs\_verify_scs.py" | Out-Host
Write-Host "ALL_UI_DONE"