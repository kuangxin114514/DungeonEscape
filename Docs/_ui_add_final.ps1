$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UA.cs"
Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function SaveCrop($name, $h, $x, $y, $w, $hh) {
  $bmp = [UA]::Cap($h)
  $w = [Math]::Min($w, $bmp.Width-$x); $hh=[Math]::Min($hh,$bmp.Height-$y)
  $rect = New-Object System.Drawing.Rectangle $x,$y,$w,$hh
  $crop = $bmp.Clone($rect, $bmp.PixelFormat)
  $crop.Save((Join-Path $docs $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $crop.Dispose(); $bmp.Dispose()
  Write-Host "CROP $name"
}
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_sync_sword2.py" | Out-Host
Start-Sleep -Milliseconds 1200
$proc = Get-Process UE4Editor | Select-Object -First 1
[UA]::Force($proc.MainWindowHandle)
$rect = New-Object UA+RECT
[UA]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
Write-Host "RECT $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top)"
$bmp = [UA]::Cap($proc.MainWindowHandle)
$gc = [UA]::Green($bmp)
$bmp.Dispose()
Write-Host "Green cx=$($gc[0]) cy=$($gc[1]) n=$($gc[2]) maxX=$($gc[3]) minX=$($gc[4])"
if ($gc[0] -lt 0) { Write-Host "FAIL no green"; exit 1 }
[UA]::Click(($rect.Left + 110), ($rect.Top + 290))
Start-Sleep -Milliseconds 350
$rx = $rect.Left + $gc[3] - 8
$ry = $rect.Top + $gc[1]
Write-Host "Hold chevron $rx,$ry"
[UA]::Hold($rx, $ry, 320)
Start-Sleep -Milliseconds 1000
SaveCrop "ue_menu_crop.png" $proc.MainWindowHandle 0 80 360 450
[System.Windows.Forms.SendKeys]::SendWait("static mesh")
Start-Sleep -Milliseconds 800
SaveCrop "ue_filter_crop.png" $proc.MainWindowHandle 0 80 360 450
[System.Windows.Forms.SendKeys]::SendWait("{DOWN}")
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1200
SaveCrop "ue_added_crop.png" $proc.MainWindowHandle 0 80 360 450
$bmp = [UA]::Cap($proc.MainWindowHandle)
$bw=[int]($bmp.Width*0.45); $bh=[int]($bmp.Height*0.45)
$b2=New-Object System.Drawing.Bitmap $bw,$bh
$g=[System.Drawing.Graphics]::FromImage($b2)
$g.DrawImage($bmp,0,0,$bw,$bh)
$b2.Save((Join-Path $docs "ue_added_full.png"), [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$bmp.Dispose();$b2.Dispose()
Write-Host "DONE"
