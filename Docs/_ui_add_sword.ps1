$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
Add-Type -ReferencedAssemblies $drawing -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class UAuto {
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
  [DllImport("user32.dll")] public static extern short GetAsyncKeyState(int vKey);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  public static void Force(IntPtr h) {
    ShowWindow(h, 3);
    IntPtr fg = GetForegroundWindow();
    uint a = GetWindowThreadProcessId(fg, IntPtr.Zero);
    uint b = GetCurrentThreadId();
    AttachThreadInput(b, a, true);
    BringWindowToTop(h); SetForegroundWindow(h);
    AttachThreadInput(b, a, false);
    System.Threading.Thread.Sleep(100);
  }
  public static void Click(int x, int y) {
    SetCursorPos(x,y); System.Threading.Thread.Sleep(80);
    mouse_event(0x0002,0,0,0,0); System.Threading.Thread.Sleep(60);
    mouse_event(0x0004,0,0,0,0);
  }
  public static void DblClick(int x, int y) {
    SetCursorPos(x,y); System.Threading.Thread.Sleep(50);
    mouse_event(0x0002,0,0,0,0); System.Threading.Thread.Sleep(30);
    mouse_event(0x0004,0,0,0,0); System.Threading.Thread.Sleep(40);
    mouse_event(0x0002,0,0,0,0); System.Threading.Thread.Sleep(30);
    mouse_event(0x0004,0,0,0,0);
  }
  public static Bitmap Capture(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    Bitmap bmp = new Bitmap(r.Right-r.Left, r.Bottom-r.Top);
    using (Graphics g = Graphics.FromImage(bmp)) g.CopyFromScreen(r.Left, r.Top, 0, 0, bmp.Size);
    return bmp;
  }
  public static int[] FindGreen(Bitmap bmp) {
    long best=0; int bx=-1,by=-1;
    int maxX=Math.Min(300,bmp.Width), maxY=Math.Min(220,bmp.Height);
    for (int y=100; y<maxY; y++) {
      for (int x=10; x<maxX; x++) {
        Color c=bmp.GetPixel(x,y);
        if (c.G>140 && c.G>c.R+40 && c.R<120) {
          long s=0;
          for (int dy=-3;dy<=3;dy++) for (int dx=-12;dx<=12;dx++) {
            int xx=x+dx,yy=y+dy;
            if (xx<0||yy<0||xx>=bmp.Width||yy>=bmp.Height) continue;
            Color c2=bmp.GetPixel(xx,yy);
            if (c2.G>140 && c2.G>c2.R+40) s++;
          }
          if (s>best){best=s;bx=x;by=y;}
        }
      }
    }
    return new int[]{bx,by,(int)best};
  }
}
"@

$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function Shot([string]$name, $h, $markX=-1, $markY=-1) {
  $bmp = [UAuto]::Capture($h)
  $bw=[int]($bmp.Width*0.5); $bh=[int]($bmp.Height*0.5)
  $bmp2=New-Object System.Drawing.Bitmap $bw,$bh
  $g=[System.Drawing.Graphics]::FromImage($bmp2)
  $g.DrawImage($bmp,0,0,$bw,$bh)
  if ($markX -ge 0) {
    $g.FillEllipse((New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::Red)), [int]($markX*0.5)-5, [int]($markY*0.5)-5, 10, 10)
  }
  $path = Join-Path $docs $name
  $bmp2.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose(); $bmp.Dispose(); $bmp2.Dispose()
  Write-Host "SHOT $name"
}

# Open BP via remote python
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_open_bp.py" | Write-Host
Start-Sleep -Milliseconds 1200

$proc = Get-Process UE4Editor | Select-Object -First 1
[UAuto]::Force($proc.MainWindowHandle)
Start-Sleep -Milliseconds 500
$rect = New-Object UAuto+RECT
[UAuto]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
Write-Host "RECT $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top)"

# Click Viewport tab
[UAuto]::Click(($rect.Left+420), ($rect.Top+140))
Start-Sleep -Milliseconds 400
[UAuto]::Force($proc.MainWindowHandle)

$bmp = [UAuto]::Capture($proc.MainWindowHandle)
$gfind = [UAuto]::FindGreen($bmp)
$bmp.Dispose()
Write-Host "GREEN $($gfind[0]),$($gfind[1]) score=$($gfind[2])"
if ($gfind[0] -lt 0) { Write-Host "FAIL no green"; exit 1 }

# Select CharacterMesh0 - orange row around y=285
[UAuto]::Click(($rect.Left+90), ($rect.Top+285))
Start-Sleep -Milliseconds 400

# Click Add Component
$ax = $rect.Left + $gfind[0]
$ay = $rect.Top + $gfind[1]
Write-Host "Click Add at $ax,$ay"
[UAuto]::Force($proc.MainWindowHandle)
Start-Sleep -Milliseconds 150
[UAuto]::Click($ax, $ay)
Start-Sleep -Milliseconds 1000
Shot "ue_add_dropdown.png" $proc.MainWindowHandle $gfind[0] $gfind[1]

# Check dropdown: sample pixels below button for light/menu colors
$bmp = [UAuto]::Capture($proc.MainWindowHandle)
$menuOpen = $false
for ($y=($gfind[1]+25); $y -lt ($gfind[1]+250); $y+=5) {
  $c = $bmp.GetPixel([Math]::Min($gfind[0], $bmp.Width-1), [Math]::Min($y,$bmp.Height-1))
  # menu items often light gray or white text on dark, or highlighted blue
  if ($c.R -gt 180 -or ($c.B -gt 150 -and $c.B -gt $c.R)) { $menuOpen = $true; Write-Host "menu hint at y=$y $($c.R),$($c.G),$($c.B)"; break }
}
# Also check for search box white
for ($x=20; $x -lt 250; $x+=10) {
  $c = $bmp.GetPixel($x, $gfind[1]+20)
  if ($c.R -gt 200 -and $c.G -gt 200) { $menuOpen = $true; Write-Host "searchbox? $x $($c.R)"; break }
}
$bmp.Dispose()
Write-Host "menuOpen=$menuOpen"

# Type filter - try English first (UE often keeps English class names in picker)
[System.Windows.Forms.SendKeys]::SendWait("Static Mesh")
Start-Sleep -Milliseconds 800
Shot "ue_add_filtered.png" $proc.MainWindowHandle

# Down arrow to first result then Enter, or just Enter
[System.Windows.Forms.SendKeys]::SendWait("{DOWN}")
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1000
Shot "ue_after_staticmesh.png" $proc.MainWindowHandle

# If still need rename - F2 then SwordMesh
Start-Sleep -Milliseconds 300
[System.Windows.Forms.SendKeys]::SendWait("{F2}")
Start-Sleep -Milliseconds 300
[System.Windows.Forms.SendKeys]::SendWait("SwordMesh")
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 500
Shot "ue_renamed_sword.png" $proc.MainWindowHandle

Write-Host "DONE STEP1"