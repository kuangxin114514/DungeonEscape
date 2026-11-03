$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
Add-Type -ReferencedAssemblies $drawing -TypeDefinition (Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UA.cs")
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function Shot($n) {
  $proc = Get-Process UE4Editor | Select-Object -First 1
  $bmp = [UA]::Cap($proc.MainWindowHandle)
  $bw=[int]($bmp.Width*0.5); $bh=[int]($bmp.Height*0.5)
  $b2=New-Object System.Drawing.Bitmap $bw,$bh
  $g=[System.Drawing.Graphics]::FromImage($b2)
  $g.DrawImage($bmp,0,0,$bw,$bh)
  $b2.Save((Join-Path $docs $n), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose(); $b2.Dispose()
  Write-Host "SHOT $n"
}
# Poll for up to 15s looking for dialog - just keep typing into focused dialog
for ($i=0; $i -lt 20; $i++) {
  Start-Sleep -Milliseconds 500
  $proc = Get-Process UE4Editor | Select-Object -First 1
  [UA]::Force($proc.MainWindowHandle)
  if ($i -eq 2 -or $i -eq 6 -or $i -eq 10) { Shot ("bs_d_" + $i + ".png") }
  if ($i -eq 4) {
    $rect = New-Object UA+RECT
    [UA]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
    $cx = [int](($rect.Left + $rect.Right)/2)
    $cy = [int](($rect.Top + $rect.Bottom)/2)
    Write-Host "Click search $cx $($cy-60)"
    [UA]::Click($cx, $cy - 60)
    Start-Sleep -Milliseconds 300
    [System.Windows.Forms.SendKeys]::SendWait("KayKitKnight_Skeleton")
    Start-Sleep -Milliseconds 700
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Start-Sleep -Milliseconds 400
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
  }
}
Shot "bs_d_final.png"
Write-Host "UI_DONE"