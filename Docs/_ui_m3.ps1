$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UC.cs"
try { Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs } catch {}
[UC]::InitDpi()
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
function SaveHalf($bmp,$name){ $bw=[int]($bmp.Width*0.4); $bh=[int]($bmp.Height*0.4); $b2=New-Object System.Drawing.Bitmap $bw,$bh; $g=[System.Drawing.Graphics]::FromImage($b2); $g.DrawImage($bmp,0,0,$bw,$bh); $b2.Save((Join-Path $docs $name),[System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $b2.Dispose(); Write-Host "SAVE $name" }
function SaveCrop($bmp,$name,$x,$y,$w,$h){ if($x -lt 0){$x=0}; if($y -lt 0){$y=0}; $mw=$bmp.Width-$x; $mh=$bmp.Height-$y; if($w -gt $mw){$w=$mw}; if($h -gt $mh){$h=$mh}; $rect=New-Object System.Drawing.Rectangle($x,$y,$w,$h); $crop=$bmp.Clone($rect,$bmp.PixelFormat); $crop.Save((Join-Path $docs $name),[System.Drawing.Imaging.ImageFormat]::Png); $crop.Dispose(); Write-Host "CROP $name" }

& $py "$docs\_run_sync_sword2.py" | Out-Host
Start-Sleep -Milliseconds 2500
$proc = Get-Process UE4Editor | Select-Object -First 1
[UC]::Force($proc.MainWindowHandle)
$rect = New-Object UC+RECT
[UC]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
$bmp = [UC]::Cap($proc.MainWindowHandle)
$gc = [UC]::GreenBtn($bmp)
Write-Host "Green cx=$($gc[0]) cy=$($gc[1]) n=$($gc[2]) maxX=$($gc[3]) minX=$($gc[4]) maxY=$($gc[5]) minY=$($gc[6])"
SaveCrop $bmp "ue_m3_before.png" 0 70 500 650
$bmp.Dispose()
if ($gc[0] -lt 0) { Write-Host "no green"; exit 1 }

# Select mesh row ~260
[UC]::ClickAt(($rect.Left+130), ($rect.Top+260))
Start-Sleep -Milliseconds 350

# Click green button LEFT part (text), not chevron
$gx = $rect.Left + [int](($gc[4] + $gc[0]) / 2)
$gy = $rect.Top + $gc[1]
Write-Host "Click green text $gx,$gy"
[UC]::Force($proc.MainWindowHandle)
[UC]::ClickAt($gx, $gy)
Start-Sleep -Milliseconds 1100
$bmp = [UC]::Cap($proc.MainWindowHandle)
SaveCrop $bmp "ue_m3_menu.png" 0 70 520 700
SaveHalf $bmp "ue_m3_menu_full.png"
# Detect popup: look for search field or list items - bright search box near green
$searchBright=0
for($y=155; $y -lt 220; $y++){ for($x=30; $x -lt 280; $x++){ if($x -ge $bmp.Width -or $y -ge $bmp.Height){continue}; $c=$bmp.GetPixel($x,$y); if($c.R -gt 40 -and $c.R -lt 90 -and $c.G -gt 40 -and $c.B -gt 40){ $searchBright++ } } }
Write-Host "darkPanelPixels=$searchBright"
$bmp.Dispose()

# Type Static Mesh slowly
[UC]::Force($proc.MainWindowHandle)
Start-Sleep -Milliseconds 200
foreach($ch in @('S','T','A','T','I','C',' ','M','E','S','H')) {
  if ($ch -eq ' ') { [UC]::Tap(0x20) } else { [UC]::Tap([byte][char]$ch) }
  Start-Sleep -Milliseconds 60
}
Start-Sleep -Milliseconds 900
$bmp = [UC]::Cap($proc.MainWindowHandle)
SaveCrop $bmp "ue_m3_filter.png" 0 70 520 700
$bmp.Dispose()

# Down arrow a few times and Enter - Static Mesh Component usually near top when filtered
[UC]::Tap(0x28); Start-Sleep -Milliseconds 100
[UC]::Tap(0x28); Start-Sleep -Milliseconds 100
[UC]::Tap(0x0D)
Start-Sleep -Milliseconds 1500
$bmp = [UC]::Cap($proc.MainWindowHandle)
SaveCrop $bmp "ue_m3_after.png" 0 70 520 700
SaveHalf $bmp "ue_m3_after_full.png"
$bmp.Dispose()
Write-Host "DONE_M3"