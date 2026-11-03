$ErrorActionPreference="Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing=[System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
Add-Type -ReferencedAssemblies $drawing -TypeDefinition (Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UA.cs")
$docs="C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function Shot($n){$p=Get-Process UE4Editor|Select -First 1; $b=[UA]::Cap($p.MainWindowHandle); $bw=[int]($b.Width*0.45); $bh=[int]($b.Height*0.45); $b2=New-Object System.Drawing.Bitmap $bw,$bh; $g=[System.Drawing.Graphics]::FromImage($b2); $g.DrawImage($b,0,0,$bw,$bh); $b2.Save((Join-Path $docs $n),[System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose();$b.Dispose();$b2.Dispose(); Write-Host "SHOT $n"}
Start-Sleep -Seconds 2
for($i=0;$i -lt 30;$i++){
  $p=Get-Process UE4Editor|Select -First 1
  [UA]::Force($p.MainWindowHandle)
  if($i -in 3,8,15){Shot "att_$i.png"}
  if($i -eq 5){
    $r=New-Object UA+RECT; [UA]::GetWindowRect($p.MainWindowHandle,[ref]$r)|Out-Null
    $cx=[int](($r.Left+$r.Right)/2); $cy=[int](($r.Top+$r.Bottom)/2)
    [UA]::Click($cx, $cy-50)
    Start-Sleep -Milliseconds 250
    [System.Windows.Forms.SendKeys]::SendWait("SK_KayKitKnight_Skeleton")
    Start-Sleep -Milliseconds 800
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Start-Sleep -Milliseconds 500
    [System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
    Write-Host "TYPED"
  }
  Start-Sleep -Milliseconds 400
}
Shot "att_final.png"