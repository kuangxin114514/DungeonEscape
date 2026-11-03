$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UC.cs"
Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs
[UC]::InitDpi()
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_sync_sword2.py" | Out-Host
Start-Sleep -Milliseconds 2500
$proc = Get-Process UE4Editor | Select-Object -First 1
[UC]::Force($proc.MainWindowHandle)
$rect = New-Object UC+RECT
[UC]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
Write-Host "RECT $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top) dpiAware metrics SM=$([UC]::GetSystemMetrics(0))x$([UC]::GetSystemMetrics(1))"
$bmp = [UC]::Cap($proc.MainWindowHandle)
$gc = [UC]::GreenBtn($bmp)
Write-Host "Green cx=$($gc[0]) cy=$($gc[1]) n=$($gc[2]) maxX=$($gc[3]) minX=$($gc[4]) maxY=$($gc[5]) minY=$($gc[6])"
$or = [UC]::FindOrangeBottom($bmp)
Write-Host "Orange cx=$($or[0]) cy=$($or[1]) n=$($or[2])"
# save half layout
$bw=[int]($bmp.Width*0.5); $bh=[int]($bmp.Height*0.5)
$b2=New-Object System.Drawing.Bitmap $bw,$bh
$g=[System.Drawing.Graphics]::FromImage($b2)
$g.DrawImage($bmp,0,0,$bw,$bh)
$b2.Save("$docs\ue_dpi_layout.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $b2.Dispose()
if ($gc[0] -lt 0) { Write-Host "FAIL no green"; $bmp.Dispose(); exit 1 }

# Color under planned click points
function Sample($bmp,$x,$y,$label){ $c=$bmp.GetPixel($x,$y); Write-Host "Sample $label $x,$y = $($c.R),$($c.G),$($c.B)" }
Sample $bmp $gc[0] $gc[1] "greenCenter"
Sample $bmp 120 235 "meshGuess"
$bmp.Dispose()

# 1) Select CharacterMesh0
$meshAbsX = $rect.Left + 120
$meshAbsY = $rect.Top + 235
[UC]::ClickAt($meshAbsX, $meshAbsY)
Start-Sleep -Milliseconds 400

# 2) Click green Add Component center
$gx = $rect.Left + $gc[0]
$gy = $rect.Top + $gc[1]
[UC]::Force($proc.MainWindowHandle)
[UC]::ClickAt($gx, $gy)
Start-Sleep -Milliseconds 1000
$bmp = [UC]::Cap($proc.MainWindowHandle)
$crop=$bmp.Clone((New-Object System.Drawing.Rectangle 0,80,[Math]::Min(420,$bmp.Width),[Math]::Min(520,$bmp.Height-80)), $bmp.PixelFormat)
$crop.Save("$docs\ue_dpi_menu.png", [System.Drawing.Imaging.ImageFormat]::Png)
$crop.Dispose()
# count bright-ish menu rows (dark theme menus still have lighter hover)
$bright=0
for($y=150;$y -lt 480 -and $y -lt $bmp.Height;$y++){ for($x=20;$x -lt 300 -and $x -lt $bmp.Width;$x++){ $c=$bmp.GetPixel($x,$y); if(($c.R+$c.G+$c.B) -gt 420){ $bright++ } } }
Write-Host "BrightPixelsInMenuArea=$bright"
$bmp.Dispose()

# Type filter
[UC]::Force($proc.MainWindowHandle)
Start-Sleep -Milliseconds 150
[UC]::TypeAscii("static mesh")
Start-Sleep -Milliseconds 800
$bmp = [UC]::Cap($proc.MainWindowHandle)
$crop=$bmp.Clone((New-Object System.Drawing.Rectangle 0,80,[Math]::Min(420,$bmp.Width),[Math]::Min(520,$bmp.Height-80)), $bmp.PixelFormat)
$crop.Save("$docs\ue_dpi_filter.png", [System.Drawing.Imaging.ImageFormat]::Png)
$crop.Dispose(); $bmp.Dispose()
[UC]::Tap(0x28)
Start-Sleep -Milliseconds 120
[UC]::Tap(0x0D)
Start-Sleep -Milliseconds 1400
$bmp = [UC]::Cap($proc.MainWindowHandle)
$crop=$bmp.Clone((New-Object System.Drawing.Rectangle 0,80,[Math]::Min(420,$bmp.Width),[Math]::Min(520,$bmp.Height-80)), $bmp.PixelFormat)
$crop.Save("$docs\ue_dpi_after.png", [System.Drawing.Imaging.ImageFormat]::Png)
$crop.Dispose()
$bw=[int]($bmp.Width*0.5); $bh=[int]($bmp.Height*0.5)
$b2=New-Object System.Drawing.Bitmap $bw,$bh
$g=[System.Drawing.Graphics]::FromImage($b2)
$g.DrawImage($bmp,0,0,$bw,$bh)
$b2.Save("$docs\ue_dpi_after_full.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $b2.Dispose(); $bmp.Dispose()
Write-Host "DONE"
