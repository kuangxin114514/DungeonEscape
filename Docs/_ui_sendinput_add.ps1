$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
Add-Type -ReferencedAssemblies $drawing -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class USend2 {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, IntPtr pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT lpPoint);
  [DllImport("user32.dll")] public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
  [DllImport("user32.dll")] public static extern int GetSystemMetrics(int nIndex);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
  [StructLayout(LayoutKind.Sequential)] public struct INPUT { public uint type; public InputUnion U; }
  [StructLayout(LayoutKind.Explicit)] public struct InputUnion { [FieldOffset(0)] public MOUSEINPUT mi; }
  [StructLayout(LayoutKind.Sequential)] public struct MOUSEINPUT {
    public int dx; public int dy; public uint mouseData; public uint dwFlags; public uint time; public IntPtr dwExtraInfo;
  }
  public static void Force(IntPtr h) {
    ShowWindow(h, 3);
    IntPtr fg = GetForegroundWindow();
    uint a = GetWindowThreadProcessId(fg, IntPtr.Zero);
    uint b = GetCurrentThreadId();
    AttachThreadInput(b, a, true);
    BringWindowToTop(h); SetForegroundWindow(h);
    AttachThreadInput(b, a, false);
    System.Threading.Thread.Sleep(150);
  }
  public static void ClickScreen(int x, int y) {
    int vx = GetSystemMetrics(78); int vy = GetSystemMetrics(79);
    int vl = GetSystemMetrics(76); int vt = GetSystemMetrics(77);
    if (vx<=0) { vx=GetSystemMetrics(0); vy=GetSystemMetrics(1); vl=0; vt=0; }
    int ax = (int)(((x - vl) * 65535.0) / Math.Max(1, vx - 1));
    int ay = (int)(((y - vt) * 65535.0) / Math.Max(1, vy - 1));
    INPUT[] inputs = new INPUT[3];
    inputs[0].type = 0; inputs[0].U.mi.dx = ax; inputs[0].U.mi.dy = ay;
    inputs[0].U.mi.dwFlags = 0x0001 | 0x8000 | 0x4000; // MOVE|ABSOLUTE|VIRTUALDESK
    inputs[1].type = 0; inputs[1].U.mi.dwFlags = 0x0002; // LEFTDOWN
    inputs[2].type = 0; inputs[2].U.mi.dwFlags = 0x0004; // LEFTUP
    uint sent = SendInput(3, inputs, Marshal.SizeOf(typeof(INPUT)));
    POINT p; GetCursorPos(out p);
    Console.WriteLine("Click sent="+sent+" at "+x+","+y+" now="+p.X+","+p.Y);
  }
  public static Bitmap Capture(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    Bitmap bmp = new Bitmap(Math.Max(1,r.Right-r.Left), Math.Max(1,r.Bottom-r.Top));
    using (Graphics g = Graphics.FromImage(bmp)) g.CopyFromScreen(r.Left, r.Top, 0, 0, bmp.Size);
    return bmp;
  }
  public static int[] GreenCentroid(Bitmap bmp) {
    long sx=0,sy=0,n=0;
    for (int y=90; y<210; y++) for (int x=5; x<300; x++) {
      if (x>=bmp.Width||y>=bmp.Height) continue;
      Color c=bmp.GetPixel(x,y);
      if (c.G>140 && c.G>c.R+40 && c.R<120) { sx+=x; sy+=y; n++; }
    }
    if (n==0) return new int[]{-1,-1,0};
    return new int[]{(int)(sx/n),(int)(sy/n),(int)n};
  }
}
"@

$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function Shot($name,$h,$mx=-1,$my=-1) {
  $bmp=[USend2]::Capture($h)
  $bw=[int]($bmp.Width*0.5); $bh=[int]($bmp.Height*0.5)
  $b2=New-Object System.Drawing.Bitmap $bw,$bh
  $g=[System.Drawing.Graphics]::FromImage($b2)
  $g.DrawImage($bmp,0,0,$bw,$bh)
  if ($mx -ge 0) {
    $g.DrawEllipse((New-Object System.Drawing.Pen ([System.Drawing.Color]::Magenta,3)), [int]($mx*0.5)-10, [int]($my*0.5)-10, 20, 20)
  }
  $b2.Save((Join-Path $docs $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose();$bmp.Dispose();$b2.Dispose()
  Write-Host "SHOT $name"
}

$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_open_bp.py" | Out-Host
Start-Sleep -Milliseconds 1200

$proc = Get-Process UE4Editor | Select-Object -First 1
[USend2]::Force($proc.MainWindowHandle)
$rect = New-Object USend2+RECT
[USend2]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
Write-Host "RECT $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top)"

# Click viewport tab first
[USend2]::ClickScreen(($rect.Left+420), ($rect.Top+140))
Start-Sleep -Milliseconds 500
[USend2]::Force($proc.MainWindowHandle)

$bmp = [USend2]::Capture($proc.MainWindowHandle)
$gc = [USend2]::GreenCentroid($bmp)
Write-Host "Green $($gc[0]),$($gc[1]) n=$($gc[2]) size=$($bmp.Width)x$($bmp.Height)"
# Sample pixel at centroid in bitmap
if ($gc[0] -ge 0) {
  $c=$bmp.GetPixel($gc[0],$gc[1])
  Write-Host "Bitmap pixel at green $($c.R),$($c.G),$($c.B)"
}
$bmp.Dispose()
if ($gc[0] -lt 0) { Write-Host "NO GREEN"; exit 1 }

# Select mesh
[USend2]::ClickScreen(($rect.Left+100), ($rect.Top+285))
Start-Sleep -Milliseconds 400

# Click green Add Component
$sx = $rect.Left + $gc[0]
$sy = $rect.Top + $gc[1]
Write-Host "Clicking green screen $sx,$sy"
[USend2]::Force($proc.MainWindowHandle)
Start-Sleep -Milliseconds 200
[USend2]::ClickScreen($sx, $sy)
Start-Sleep -Milliseconds 300
# Second click in case first was focus-only
[USend2]::ClickScreen($sx, $sy)
Start-Sleep -Milliseconds 1000

# Verify cursor pixel is green-ish or menu open
$pt=New-Object USend2+POINT
[USend2]::GetCursorPos([ref]$pt) | Out-Null
$bmp=New-Object System.Drawing.Bitmap 1,1
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($pt.X,$pt.Y,0,0,(New-Object System.Drawing.Size 1,1))
$c=$bmp.GetPixel(0,0)
Write-Host "Cursor $($pt.X),$($pt.Y) pixel $($c.R),$($c.G),$($c.B)"
$g.Dispose();$bmp.Dispose()

Shot "ue_si_dropdown.png" $proc.MainWindowHandle $gc[0] $gc[1]

# Paste Static Mesh into search
[System.Windows.Forms.Clipboard]::SetText("Static Mesh")
Start-Sleep -Milliseconds 150
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 800
Shot "ue_si_filter.png" $proc.MainWindowHandle

[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1200
Shot "ue_si_added.png" $proc.MainWindowHandle
Write-Host "DONE"