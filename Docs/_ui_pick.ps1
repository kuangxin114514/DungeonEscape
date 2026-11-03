$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UC.cs"
try { Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs } catch {}
[UC]::InitDpi()
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
function SaveCrop($bmp,$name,$x,$y,$w,$h){ if($x -lt 0){$x=0}; if($y -lt 0){$y=0}; $mw=$bmp.Width-$x; $mh=$bmp.Height-$y; if($w -gt $mw){$w=$mw}; if($h -gt $mh){$h=$mh}; $rect=New-Object System.Drawing.Rectangle($x,$y,$w,$h); $crop=$bmp.Clone($rect,$bmp.PixelFormat); $crop.Save((Join-Path $docs $name),[System.Drawing.Imaging.ImageFormat]::Png); $crop.Dispose(); Write-Host "CROP $name" }
function SaveHalf($bmp,$name){ $bw=[int]($bmp.Width*0.4); $bh=[int]($bmp.Height*0.4); $b2=New-Object System.Drawing.Bitmap $bw,$bh; $g=[System.Drawing.Graphics]::FromImage($b2); $g.DrawImage($bmp,0,0,$bw,$bh); $b2.Save((Join-Path $docs $name),[System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $b2.Dispose(); Write-Host "SAVE $name" }

function OpenMenuAndPickSword {
  param($label)
  & $py "$docs\_run_sync_sword2.py" | Out-Host
  Start-Sleep -Milliseconds 2000
  $proc = Get-Process UE4Editor | Select-Object -First 1
  [UC]::Force($proc.MainWindowHandle)
  $rect = New-Object UC+RECT
  [UC]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
  $bmp = [UC]::Cap($proc.MainWindowHandle)
  $gc = [UC]::GreenBtn($bmp)
  Write-Host "$label Green cx=$($gc[0]) cy=$($gc[1]) maxX=$($gc[3])"
  $bmp.Dispose()
  if ($gc[0] -lt 0) { throw "no green" }

  # Select CharacterMesh0 - try y=290 (below Arrow~260)
  [UC]::ClickAt(($rect.Left+140), ($rect.Top+290))
  Start-Sleep -Milliseconds 400

  # Open add menu - click green text center-left
  $gx = $rect.Left + [int](($gc[4]+$gc[0])/2)
  $gy = $rect.Top + $gc[1]
  [UC]::Force($proc.MainWindowHandle)
  [UC]::ClickAt($gx, $gy)
  Start-Sleep -Milliseconds 1000
  $bmp = [UC]::Cap($proc.MainWindowHandle)
  SaveCrop $bmp ("ue_pick_"+$label+"_menu.png") 0 70 480 750

  # Find row with mesh-like icon: look for pixels that are mid-gray cube icons near left of menu
  # Heuristic: scan y from 200 to 520, x 30-60 for non-dark icon, and prefer rows after "common"
  # Better: look for yellowish/orange selection or unique - SM entry often has static mesh icon (gray box)
  # Scan for rows where average brightness in text area spikes - or find green-ish from selected CB asset tint
  $candidates = @()
  for ($y=200; $y -lt 520; $y++) {
    # icon area
    $icon = $bmp.GetPixel(40, $y)
    $text = $bmp.GetPixel(120, $y)
    $bright = ($text.R + $text.G + $text.B)
    # menu text is light gray ~180
    if ($bright -gt 400 -and $bright -lt 700) {
      # check if this looks like a text row (neighbor rows similar)
      $candidates += $y
    }
  }
  # Cluster consecutive y into row centers
  $rows = @(); $start=-1; $prev=-99
  foreach ($y in $candidates) {
    if ($y -gt $prev+2) {
      if ($start -ge 0) { $rows += [int](($start+$prev)/2) }
      $start = $y
    }
    $prev = $y
  }
  if ($start -ge 0) { $rows += [int](($start+$prev)/2) }
  Write-Host "$label textRows=$($rows -join ',')"

  # From known menu structure, SM_KayKitSword is ~4th in Common after Chaos,Niagara,Scene = roughly row index
  # Scripts: 2 items, Common starts: Chaos, Niagara, Scene, SM_KayKitSword = about 7th text row
  # Click several likely Ys: try row that is 4th in common - empirically click y around 330-380
  # Also try detecting "cube" icon: more mid luminance in icon column
  $bestY = -1; $bestScore = -1
  foreach ($ry in $rows) {
    $score = 0
    for ($dx=28; $dx -le 55; $dx++) {
      $c = $bmp.GetPixel($dx, $ry)
      $avg = ($c.R+$c.G+$c.B)/3
      if ($avg -gt 70 -and $avg -lt 160) { $score++ } # mesh icon gray
      if ($c.R -gt 100 -and $c.G -gt 80 -and $c.B -lt 70) { $score += 3 } # possible sword tint/orange
    }
    # Prefer rows in 280-420 band
    if ($ry -ge 280 -and $ry -le 420) { $score += 5 }
    if ($score -gt $bestScore) { $bestScore = $score; $bestY = $ry }
  }
  Write-Host "$label bestY=$bestY score=$bestScore"
  # Fallback fixed guesses if needed
  $tryYs = @()
  if ($bestY -gt 0) { $tryYs += $bestY }
  $tryYs += 320, 340, 355, 370, 390
  $tryYs = $tryYs | Select-Object -Unique
  $bmp.Dispose()

  foreach ($ty in $tryYs) {
    Write-Host "$label try click menu item y=$ty"
    [UC]::Force($proc.MainWindowHandle)
    # Re-open menu each try if needed - first try uses open menu
    [UC]::ClickAt(($rect.Left+160), ($rect.Top+$ty))
    Start-Sleep -Milliseconds 900
    $bmp = [UC]::Cap($proc.MainWindowHandle)
    SaveCrop $bmp ("ue_pick_"+$label+"_try$ty.png") 0 70 480 650
    # Check if new component appeared: look for non-inherited component name patterns / more rows
    # Simple: count component rows by light text in x=80-250, y=170-400
    $compRows = 0
    for ($y=170; $y -lt 420; $y+=14) {
      $c=$bmp.GetPixel(100,$y); if (($c.R+$c.G+$c.B) -gt 380) { $compRows++ }
    }
    Write-Host "$label after try$ty compRowSamples=$compRows"
    # Detect if menu still open (menu search bar area) vs closed with new item
    # If hierarchy got a new item, StaticMesh often shows without (继承)
    SaveHalf $bmp ("ue_pick_"+$label+"_full$ty.png")
    $bmp.Dispose()
    # Probe via python whether SCS grew
    break  # first attempt only; evaluate then continue if needed
  }
  return $tryYs[0]
}

$y = OpenMenuAndPickSword "s1"
Write-Host "pickedY=$y DONE_PICK1"