Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UB.cs"
try { Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs } catch {}
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_sync_sword2.py" | Out-Host
Start-Sleep -Milliseconds 2000
$proc = Get-Process UE4Editor | Select-Object -First 1
[UB]::Force($proc.MainWindowHandle)
Start-Sleep -Milliseconds 500
$bmp = [UB]::Cap($proc.MainWindowHandle)
# save half-res full
$bw=[int]($bmp.Width*0.55); $bh=[int]($bmp.Height*0.55)
$b2=New-Object System.Drawing.Bitmap $bw,$bh
$g=[System.Drawing.Graphics]::FromImage($b2)
$g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
$g.DrawImage($bmp,0,0,$bw,$bh)
$b2.Save("$docs\ue_layout_now.png", [System.Drawing.Imaging.ImageFormat]::Png)
# also search green anywhere
$found=@()
for($y=40;$y -lt [Math]::Min(400,$bmp.Height);$y+=2){
  for($x=0;$x -lt [Math]::Min(800,$bmp.Width);$x+=2){
    $c=$bmp.GetPixel($x,$y)
    if($c.G -gt 140 -and $c.G -gt ($c.R+40) -and $c.R -lt 120){ $found += "$x,$y" }
  }
}
Write-Host "Green samples count=$($found.Count) first=$($found | Select -First 5) last=$($found | Select -Last 5)"
# find green bounding box
$minx=9999;$miny=9999;$maxx=0;$maxy=0;$n=0
for($y=40;$y -lt [Math]::Min(500,$bmp.Height);$y++){
  for($x=0;$x -lt [Math]::Min(900,$bmp.Width);$x++){
    $c=$bmp.GetPixel($x,$y)
    if($c.G -gt 140 -and $c.G -gt ($c.R+40) -and $c.R -lt 120){
      if($x -lt $minx){$minx=$x}; if($y -lt $miny){$miny=$y}
      if($x -gt $maxx){$maxx=$x}; if($y -gt $maxy){$maxy=$y}; $n++
    }
  }
}
Write-Host "GreenBB n=$n min=$minx,$miny max=$maxx,$maxy"
$g.Dispose(); $bmp.Dispose(); $b2.Dispose()
Write-Host "saved layout"