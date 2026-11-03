$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UC.cs"
try { Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs } catch { }
[UC]::InitDpi()
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
function SaveHalf($bmp, $name) {
  $bw = [int]($bmp.Width * 0.42); $bh = [int]($bmp.Height * 0.42)
  $b2 = New-Object System.Drawing.Bitmap $bw, $bh
  $g = [System.Drawing.Graphics]::FromImage($b2)
  $g.DrawImage($bmp, 0, 0, $bw, $bh)
  $b2.Save((Join-Path $docs $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $b2.Dispose()
  Write-Host "SAVE $name"
}
function SaveCrop($bmp, $name, $x, $y, $w, $h) {
  if ($x -lt 0) { $x = 0 }; if ($y -lt 0) { $y = 0 }
  $mw = $bmp.Width - $x; $mh = $bmp.Height - $y
  if ($w -gt $mw) { $w = $mw }; if ($h -gt $mh) { $h = $mh }
  $rect = New-Object System.Drawing.Rectangle($x, $y, $w, $h)
  $crop = $bmp.Clone($rect, $bmp.PixelFormat)
  $crop.Save((Join-Path $docs $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $crop.Dispose()
  Write-Host "CROP $name"
}

& $py "$docs\_run_sync_sword2.py" | Out-Host
Start-Sleep -Milliseconds 2500
$proc = Get-Process UE4Editor | Select-Object -First 1
[UC]::Force($proc.MainWindowHandle)
$rect = New-Object UC+RECT
[UC]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
Write-Host "RECT $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top)"
$bmp = [UC]::Cap($proc.MainWindowHandle)
$gc = [UC]::GreenBtn($bmp)
$or = [UC]::FindOrangeBottom($bmp)
Write-Host "Green cx=$($gc[0]) cy=$($gc[1]) n=$($gc[2]) maxX=$($gc[3]) minX=$($gc[4])"
Write-Host "Orange cx=$($or[0]) cy=$($or[1]) n=$($or[2])"
SaveHalf $bmp "ue_drag_before.png"
SaveCrop $bmp "ue_drag_comp.png" 0 80 450 550

# Select CharacterMesh0 - scale: green~138, mesh row ~ green+ (235-134)*scale
# In physical bitmap component rows are denser; estimate from known structure
# Self ~168, Capsule~200, Arrow~230, Mesh~260, Boom~290
$meshX = 130; $meshY = 260
$c = $bmp.GetPixel($meshX, $meshY)
Write-Host "MeshGuess pixel $($c.R),$($c.G),$($c.B) at $meshX,$meshY"
$bmp.Dispose()

[UC]::ClickAt(($rect.Left + $meshX), ($rect.Top + $meshY))
Start-Sleep -Milliseconds 450
$bmp = [UC]::Cap($proc.MainWindowHandle)
SaveCrop $bmp "ue_drag_mesh_sel.png" 0 80 450 550
$bmp.Dispose()

if ($or[0] -lt 0 -or $gc[0] -lt 0) { Write-Host "FAIL missing targets"; exit 1 }

# Drag from orange (SM selected in CB) to green Add Component
$x0 = $rect.Left + $or[0]
$y0 = $rect.Top + $or[1]
$x1 = $rect.Left + $gc[0]
$y1 = $rect.Top + $gc[1]
Write-Host "DRAG from $x0,$y0 to $x1,$y1"
[UC]::Force($proc.MainWindowHandle)
[UC]::Drag($x0, $y0, $x1, $y1)
Start-Sleep -Milliseconds 1500

$bmp = [UC]::Cap($proc.MainWindowHandle)
SaveCrop $bmp "ue_drag_after.png" 0 80 450 600
SaveHalf $bmp "ue_drag_after_full.png"
$bmp.Dispose()
Write-Host "DONE_DRAG"