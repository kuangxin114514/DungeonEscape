$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
Add-Type -ReferencedAssemblies $drawing -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class UAuto2 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, IntPtr pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
  [DllImport("user32.dll")] public static extern void mouse_event(int flags, int dx, int dy, int data, int extra);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  public static void Force(IntPtr h) {
    ShowWindow(h, 3);
    IntPtr fg = GetForegroundWindow();
    uint a = GetWindowThreadProcessId(fg, IntPtr.Zero);
    uint b = GetCurrentThreadId();
    AttachThreadInput(b, a, true);
    BringWindowToTop(h); SetForegroundWindow(h);
    AttachThreadInput(b, a, false);
    System.Threading.Thread.Sleep(120);
  }
  public static void Click(int x, int y) {
    SetCursorPos(x,y); System.Threading.Thread.Sleep(100);
    mouse_event(0x0002,0,0,0,0); System.Threading.Thread.Sleep(70);
    mouse_event(0x0004,0,0,0,0);
  }
  public static Bitmap Capture(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    Bitmap bmp = new Bitmap(r.Right-r.Left, r.Bottom-r.Top);
    using (Graphics g = Graphics.FromImage(bmp)) g.CopyFromScreen(r.Left, r.Top, 0, 0, bmp.Size);
    return bmp;
  }
  // Centroid of green button pixels
  public static int[] GreenCentroid(Bitmap bmp) {
    long sx=0,sy=0,n=0;
    int minX=9999,maxX=0,minY=9999,maxY=0;
    for (int y=100; y<200; y++) {
      for (int x=10; x<280; x++) {
        Color c=bmp.GetPixel(x,y);
        if (c.G>140 && c.G>c.R+40 && c.R<120) {
          sx+=x; sy+=y; n++;
          if (x<minX) minX=x; if (x>maxX) maxX=x;
          if (y<minY) minY=y; if (y>maxY) maxY=y;
        }
      }
    }
    if (n==0) return new int[]{-1,-1,0,0,0,0,0};
    return new int[]{(int)(sx/n),(int)(sy/n),(int)n,minX,maxX,minY,maxY};
  }
}
"@

$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function Shot([string]$name, $h, $mx=-1, $my=-1) {
  $bmp = [UAuto2]::Capture($h)
  $bw=[int]($bmp.Width*0.55); $bh=[int]($bmp.Height*0.55)
  $bmp2=New-Object System.Drawing.Bitmap $bw,$bh
  $g=[System.Drawing.Graphics]::FromImage($bmp2)
  $g.DrawImage($bmp,0,0,$bw,$bh)
  if ($mx -ge 0) { $g.FillEllipse((New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::Magenta)), [int]($mx*0.55)-6, [int]($my*0.55)-6, 12, 12) }
  $bmp2.Save((Join-Path $docs $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose(); $bmp2.Dispose()
  Write-Host "SHOT $name"
}

$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_open_bp.py" | Out-Host
Start-Sleep -Milliseconds 1000

$proc = Get-Process UE4Editor | Select-Object -First 1
[UAuto2]::Force($proc.MainWindowHandle)
Start-Sleep -Milliseconds 400
$rect = New-Object UAuto2+RECT
[UAuto2]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null

# Viewport tab
[UAuto2]::Click(($rect.Left+420), ($rect.Top+140))
Start-Sleep -Milliseconds 350
[UAuto2]::Force($proc.MainWindowHandle)

$bmp = [UAuto2]::Capture($proc.MainWindowHandle)
$gc = [UAuto2]::GreenCentroid($bmp)
$bmp.Dispose()
Write-Host "Green centroid x=$($gc[0]) y=$($gc[1]) n=$($gc[2]) bbox $($gc[3])-$($gc[4]),$($gc[5])-$($gc[6])"
if ($gc[0] -lt 0) { Write-Host "NO GREEN"; exit 1 }

# Select CharacterMesh0
[UAuto2]::Click(($rect.Left+100), ($rect.Top+285))
Start-Sleep -Milliseconds 400

# Click CENTER of green button
$cx = $rect.Left + $gc[0]
$cy = $rect.Top + $gc[1]
Write-Host "Clicking Add center $cx,$cy"
[UAuto2]::Force($proc.MainWindowHandle)
Start-Sleep -Milliseconds 200
[UAuto2]::Click($cx, $cy)
Start-Sleep -Milliseconds 1200
Shot "ue_dd1.png" $proc.MainWindowHandle $gc[0] $gc[1]

# Detect real dropdown: look for many distinct rows under button with lighter panels
$bmp = [UAuto2]::Capture($proc.MainWindowHandle)
# UE Add Component popup often extends to the right and down; look for border or category headers
# Sample a vertical strip at x=120 from y=160 to 500 for variance
$colors = @{}
for ($y=160; $y -lt 450; $y++) {
  $c = $bmp.GetPixel(120, $y)
  $key = "$([int]($c.R/20))_$([int]($c.G/20))_$([int]($c.B/20))"
  if (-not $colors.ContainsKey($key)) { $colors[$key]=0 }
  $colors[$key]++
}
Write-Host "color buckets under menu area: $($colors.Count)"
$colors.GetEnumerator() | Sort-Object Value -Descending | Select-Object -First 8 | ForEach-Object { Write-Host "  $($_.Key) = $($_.Value)" }

# Crop left panel for clearer shot of dropdown
$crop = New-Object System.Drawing.Bitmap 400, 500
$g2 = [System.Drawing.Graphics]::FromImage($crop)
$g2.DrawImage($bmp, 0, 0, (New-Object System.Drawing.Rectangle 0,0,400,500), (New-Object System.Drawing.Rectangle 0,90,400,500), [System.Drawing.GraphicsUnit]::Pixel)
$crop.Save((Join-Path $docs "ue_dd1_crop.png"), [System.Drawing.Imaging.ImageFormat]::Png)
$g2.Dispose(); $crop.Dispose(); $bmp.Dispose()
Write-Host "crop saved"

# Type 静态网格体 using unicode SendKeys is hard; use clipboard paste
[System.Windows.Forms.Clipboard]::SetText("Static Mesh")
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("^a")
Start-Sleep -Milliseconds 100
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 900
Shot "ue_dd2_filter.png" $proc.MainWindowHandle

$bmp = [UAuto2]::Capture($proc.MainWindowHandle)
$crop = New-Object System.Drawing.Bitmap 450, 550
$g2 = [System.Drawing.Graphics]::FromImage($crop)
$g2.DrawImage($bmp, 0, 0, (New-Object System.Drawing.Rectangle 0,0,450,550), (New-Object System.Drawing.Rectangle 0,90,450,550), [System.Drawing.GraphicsUnit]::Pixel)
$crop.Save((Join-Path $docs "ue_dd2_crop.png"), [System.Drawing.Imaging.ImageFormat]::Png)
$g2.Dispose(); $crop.Dispose(); $bmp.Dispose()

# Press Enter to confirm first item
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1200
Shot "ue_dd3_added.png" $proc.MainWindowHandle

$bmp = [UAuto2]::Capture($proc.MainWindowHandle)
$crop = New-Object System.Drawing.Bitmap 350, 450
$g2 = [System.Drawing.Graphics]::FromImage($crop)
$g2.DrawImage($bmp, 0, 0, (New-Object System.Drawing.Rectangle 0,0,350,450), (New-Object System.Drawing.Rectangle 0,90,350,450), [System.Drawing.GraphicsUnit]::Pixel)
$crop.Save((Join-Path $docs "ue_dd3_crop.png"), [System.Drawing.Imaging.ImageFormat]::Png)
$g2.Dispose(); $crop.Dispose(); $bmp.Dispose()
Write-Host "DONE"