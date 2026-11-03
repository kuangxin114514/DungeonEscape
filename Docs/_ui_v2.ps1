$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UB.cs"
Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function SaveBmp($name,$bmp){ $bmp.Save((Join-Path $docs $name), [System.Drawing.Imaging.ImageFormat]::Png); Write-Host "SAVE $name" }
function SaveCrop($name,$bmp,$x,$y,$w,$h){ $w=[Math]::Min($w,$bmp.Width-$x); $h=[Math]::Min($h,$bmp.Height-$y); $crop=$bmp.Clone((New-Object System.Drawing.Rectangle $x,$y,$w,$h), $bmp.PixelFormat); SaveBmp $name $crop; $crop.Dispose() }
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_sync_sword2.py" | Out-Host
Start-Sleep -Milliseconds 1500
$proc = Get-Process UE4Editor | Select-Object -First 1
[UB]::Force($proc.MainWindowHandle)
$rect = New-Object UB+RECT
[UB]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
Write-Host "RECT $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top)"
$bmp = [UB]::Cap($proc.MainWindowHandle)
$gc = [UB]::Green($bmp)
SaveCrop "ue_v2_before.png" $bmp 0 80 380 420
$bmp.Dispose()
Write-Host "Green cx=$($gc[0]) cy=$($gc[1]) n=$($gc[2]) maxX=$($gc[3]) minX=$($gc[4])"
if ($gc[0] -lt 0) { Write-Host "FAIL no green"; exit 1 }

# Select CharacterMesh0 - approximate row under Arrow
$meshX = $rect.Left + 120
$meshY = $rect.Top + 235
Write-Host "Click mesh $meshX,$meshY"
[UB]::Click($meshX, $meshY)
Start-Sleep -Milliseconds 400

# Click CENTER of green Add Component (not chevron)
$gx = $rect.Left + [int](($gc[4]+$gc[3])/2)
$gy = $rect.Top + $gc[1]
Write-Host "Click green center $gx,$gy"
[UB]::Force($proc.MainWindowHandle)
[UB]::Click($gx, $gy)
Start-Sleep -Milliseconds 900
$bmp = [UB]::Cap($proc.MainWindowHandle)
$wc = [UB]::WhiteCount($bmp, 20, 150, 320, 520)
Write-Host "WhiteCount after click=$wc"
SaveCrop "ue_v2_menu.png" $bmp 0 80 400 500
SaveBmp "ue_v2_full.png" $bmp
$bmp.Dispose()

if ($wc -lt 800) {
  Write-Host "Menu weak - try chevron hold"
  [UB]::Force($proc.MainWindowHandle)
  $cx = $rect.Left + $gc[3] - 6
  $cy = $rect.Top + $gc[1]
  [UB]::Move($cx,$cy); Start-Sleep -Milliseconds 50
  [UB]::Down(); Start-Sleep -Milliseconds 400; [UB]::Up()
  Start-Sleep -Milliseconds 900
  $bmp = [UB]::Cap($proc.MainWindowHandle)
  $wc = [UB]::WhiteCount($bmp, 20, 150, 320, 520)
  Write-Host "WhiteCount after hold=$wc"
  SaveCrop "ue_v2_menu2.png" $bmp 0 80 400 500
  $bmp.Dispose()
}

[UB]::Force($proc.MainWindowHandle)
Start-Sleep -Milliseconds 200
# Type "static mesh" via keybd
[UB]::TypeAscii("static mesh")
Start-Sleep -Milliseconds 700
$bmp = [UB]::Cap($proc.MainWindowHandle)
SaveCrop "ue_v2_filter.png" $bmp 0 80 400 500
$bmp.Dispose()
[UB]::Tap(0x28) # down
Start-Sleep -Milliseconds 150
[UB]::Tap(0x0D) # enter
Start-Sleep -Milliseconds 1200
$bmp = [UB]::Cap($proc.MainWindowHandle)
SaveCrop "ue_v2_after.png" $bmp 0 80 400 500
# shrink full
$bw=[int]($bmp.Width*0.5); $bh=[int]($bmp.Height*0.5)
$b2=New-Object System.Drawing.Bitmap $bw,$bh
$g=[System.Drawing.Graphics]::FromImage($b2)
$g.DrawImage($bmp,0,0,$bw,$bh)
SaveBmp "ue_v2_after_full.png" $b2
$g.Dispose(); $bmp.Dispose(); $b2.Dispose()
Write-Host "DONE wc_last_known"
