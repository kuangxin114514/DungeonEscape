$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
Add-Type -ReferencedAssemblies $drawing -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class USend {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, IntPtr pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT lpPoint);
  [DllImport("user32.dll")] public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
  [DllImport("user32.dll")] public static extern int GetSystemMetrics(int nIndex);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
  [StructLayout(LayoutKind.Sequential)] public struct INPUT {
    public uint type; public InputUnion U;
  }
  [StructLayout(LayoutKind.Explicit)] public struct InputUnion {
    [FieldOffset(0)] public MOUSEINPUT mi;
  }
  [StructLayout(LayoutKind.Sequential)] public struct MOUSEINPUT {
    public int dx; public int dy; public uint mouseData; public uint dwFlags; public uint time; public IntPtr dwExtraInfo;
  }
  public const uint INPUT_MOUSE=0;
  public const uint MOUSEEVENTF_MOVE=0x0001;
  public const uint MOUSEEVENTF_LEFTDOWN=0x0002;
  public const uint MOUSEEVENTF_LEFTUP=0x0004;
  public const uint MOUSEEVENTF_ABSOLUTE=0x8000;
  public const uint MOUSEEVENTF_VIRTUALDESK=0x4000;
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
  public static bool ClickScreen(int x, int y) {
    int vx = GetSystemMetrics(78); // SM_CXVIRTUALSCREEN
    int vy = GetSystemMetrics(79); // SM_CYVIRTUALSCREEN
    int vl = GetSystemMetrics(76); // SM_XVIRTUALSCREEN
    int vt = GetSystemMetrics(77); // SM_YVIRTUALSCREEN
    if (vx<=0) vx=GetSystemMetrics(0);
    if (vy<=0) vy=GetSystemMetrics(1);
    // absolute coords 0..65535 over virtual screen
    int ax = (int)(((x - vl) * 65535.0) / (vx - 1));
    int ay = (int)(((y - vt) * 65535.0) / (vy - 1));
    INPUT[] inputs = new INPUT[3];
    inputs[0].type = INPUT_MOUSE;
    inputs[0].U.mi.dx = ax; inputs[0].U.mi.dy = ay;
    inputs[0].U.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK;
    inputs[1].type = INPUT_MOUSE;
    inputs[1].U.mi.dwFlags = MOUSEEVENTF_LEFTDOWN;
    inputs[2].type = INPUT_MOUSE;
    inputs[2].U.mi.dwFlags = MOUSEEVENTF_LEFTUP;
    uint sent = SendInput(3, inputs, Marshal.SizeOf(typeof(INPUT)));
    POINT p; GetCursorPos(out p);
    Console.WriteLine("SendInput sent="+sent+" cursorNow="+p.X+","+p.Y+" target="+x+","+y+" virt="+vl+","+vt+" "+vx+"x"+vy+" abs="+ax+","+ay);
    return sent==3;
  }
  public static Bitmap Capture(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    Bitmap bmp = new Bitmap(r.Right-r.Left, r.Bottom-r.Top);
    using (Graphics g = Graphics.FromImage(bmp)) g.CopyFromScreen(r.Left, r.Top, 0, 0, bmp.Size);
    return bmp;
  }
  public static int[] GreenCentroid(Bitmap bmp) {
    long sx=0,sy=0,n=0;
    for (int y=100; y<200; y++) for (int x=10; x<280; x++) {
      Color c=bmp.GetPixel(x,y);
      if (c.G>140 && c.G>c.R+40 && c.R<120) { sx+=x; sy+=y; n++; }
    }
    if (n==0) return new int[]{-1,-1,0};
    return new int[]{(int)(sx/n),(int)(sy/n),(int)n};
  }
}
"@

$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function Shot($name, $h) {
  $bmp=[USend]::Capture($h)
  $bw=[int]($bmp.Width*0.5); $bh=[int]($bmp.Height*0.5)
  $b2=New-Object System.Drawing.Bitmap $bw,$bh
  $g=[System.Drawing.Graphics]::FromImage($b2)
  $g.DrawImage($bmp,0,0,$bw,$bh)
  $b2.Save((Join-Path $docs $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose();$bmp.Dispose();$b2.Dispose()
  Write-Host "SHOT $name"
}

# Test SendInput move first
$proc = Get-Process UE4Editor | Select-Object -First 1
[USend]::Force($proc.MainWindowHandle)
$rect = New-Object USend+RECT
[USend]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
Write-Host "UE $($rect.Left),$($rect.Top)-$($rect.Right),$($rect.Bottom)"

# Test click at known green area
$tx = $rect.Left + 92
$ty = $rect.Top + 134
Write-Host "Testing move to $tx,$ty"
$ok = [USend]::ClickScreen($tx, $ty)
Start-Sleep -Milliseconds 300
$pt = New-Object USend+POINT
[USend]::GetCursorPos([ref]$pt) | Out-Null
Write-Host "After click cursor $($pt.X),$($pt.Y)"

# Also try SetCursorPos return
$r1 = [USend]::SetCursorPos($tx, $ty)
Start-Sleep -Milliseconds 100
[USend]::GetCursorPos([ref]$pt) | Out-Null
Write-Host "SetCursorPos returned $r1 cursor now $($pt.X),$($pt.Y)"

# Pixel under cursor
$bmp=New-Object System.Drawing.Bitmap 1,1
$g=[System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($pt.X,$pt.Y,0,0,(New-Object System.Drawing.Size 1,1))
$c=$bmp.GetPixel(0,0)
Write-Host "Pixel at cursor $($c.R),$($c.G),$($c.B)"
$g.Dispose();$bmp.Dispose()