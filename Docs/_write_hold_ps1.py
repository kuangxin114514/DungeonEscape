# -*- coding: utf-8 -*-
import pathlib
docs = pathlib.Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs")
ps1 = r'''$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
Add-Type -ReferencedAssemblies $drawing -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class UDrag {
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
  static int AbsX(int x) {
    int vx=GetSystemMetrics(78), vl=GetSystemMetrics(76);
    if (vx<=0){vx=GetSystemMetrics(0);vl=0;}
    return (int)(((x-vl)*65535.0)/Math.Max(1,vx-1));
  }
  static int AbsY(int y) {
    int vy=GetSystemMetrics(79), vt=GetSystemMetrics(77);
    if (vy<=0){vy=GetSystemMetrics(1);vt=0;}
    return (int)(((y-vt)*65535.0)/Math.Max(1,vy-1));
  }
  static INPUT MoveTo(int x, int y) {
    INPUT i = new INPUT(); i.type=0;
    i.U.mi.dx=AbsX(x); i.U.mi.dy=AbsY(y);
    i.U.mi.dwFlags=0x0001|0x8000|0x4000;
    return i;
  }
  public static void Force(IntPtr h) {
    ShowWindow(h, 3);
    IntPtr fg=GetForegroundWindow();
    uint a=GetWindowThreadProcessId(fg,IntPtr.Zero);
    uint b=GetCurrentThreadId();
    AttachThreadInput(b,a,true);
    BringWindowToTop(h); SetForegroundWindow(h);
    AttachThreadInput(b,a,false);
    System.Threading.Thread.Sleep(120);
  }
  public static void Move(int x, int y) {
    INPUT[] ins=new INPUT[]{MoveTo(x,y)};
    SendInput(1,ins,Marshal.SizeOf(typeof(INPUT)));
  }
  public static void Down() {
    INPUT[] ins=new INPUT[1]; ins[0].type=0; ins[0].U.mi.dwFlags=0x0002;
    SendInput(1,ins,Marshal.SizeOf(typeof(INPUT)));
  }
  public static void Up() {
    INPUT[] ins=new INPUT[1]; ins[0].type=0; ins[0].U.mi.dwFlags=0x0004;
    SendInput(1,ins,Marshal.SizeOf(typeof(INPUT)));
  }
  public static void Click(int x, int y) {
    Move(x,y); System.Threading.Thread.Sleep(80);
    Down(); System.Threading.Thread.Sleep(120);
    Up();
    POINT p; GetCursorPos(out p);
    Console.WriteLine("Click "+x+","+y+" now="+p.X+","+p.Y);
  }
  public static void ClickHold(int x, int y, int holdMs) {
    Move(x,y); System.Threading.Thread.Sleep(80);
    Down(); System.Threading.Thread.Sleep(holdMs);
    Up();
    Console.WriteLine("ClickHold "+x+","+y+" "+holdMs+"ms");
  }
  public static void Drag(int x1,int y1,int x2,int y2,int steps) {
    Move(x1,y1); System.Threading.Thread.Sleep(100);
    Down(); System.Threading.Thread.Sleep(150);
    for (int i=1;i<=steps;i++) {
      int x=x1+(x2-x1)*i/steps;
      int y=y1+(y2-y1)*i/steps;
      Move(x,y);
      System.Threading.Thread.Sleep(30);
    }
    System.Threading.Thread.Sleep(100);
    Up();
    Console.WriteLine("Drag "+x1+","+y1+" -> "+x2+","+y2);
  }
  public static Bitmap Capture(IntPtr h) {
    RECT r; GetWindowRect(h, out r);
    Bitmap bmp=new Bitmap(Math.Max(1,r.Right-r.Left), Math.Max(1,r.Bottom-r.Top));
    using (Graphics g=Graphics.FromImage(bmp)) g.CopyFromScreen(r.Left,r.Top,0,0,bmp.Size);
    return bmp;
  }
  public static int[] GreenCentroid(Bitmap bmp) {
    long sx=0,sy=0,n=0; int maxX=0;
    for (int y=90;y<210;y++) for (int x=5;x<300;x++) {
      if (x>=bmp.Width||y>=bmp.Height) continue;
      Color c=bmp.GetPixel(x,y);
      if (c.G>140 && c.G>c.R+40 && c.R<120) { sx+=x; sy+=y; n++; if(x>maxX)maxX=x; }
    }
    if (n==0) return new int[]{-1,-1,0,0};
    return new int[]{(int)(sx/n),(int)(sy/n),(int)n,maxX};
  }
}
"@

$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function Shot($name,$h) {
  $bmp=[UDrag]::Capture($h)
  $bw=[int]($bmp.Width*0.5); $bh=[int]($bmp.Height*0.5)
  $b2=New-Object System.Drawing.Bitmap $bw,$bh
  $g=[System.Drawing.Graphics]::FromImage($b2)
  $g.DrawImage($bmp,0,0,$bw,$bh)
  $b2.Save((Join-Path $docs $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $g.Dispose();$bmp.Dispose();$b2.Dispose()
  Write-Host "SHOT $name"
}

$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_sync_sword2.py" | Out-Host
Start-Sleep -Milliseconds 1500

$proc = Get-Process UE4Editor | Select-Object -First 1
[UDrag]::Force($proc.MainWindowHandle)
$rect = New-Object UDrag+RECT
[UDrag]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
Write-Host "RECT $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top)"

[UDrag]::Click(($rect.Left+480), ($rect.Top+40))
Start-Sleep -Milliseconds 400
[UDrag]::Click(($rect.Left+420), ($rect.Top+140))
Start-Sleep -Milliseconds 400
[UDrag]::Force($proc.MainWindowHandle)

$bmp=[UDrag]::Capture($proc.MainWindowHandle)
$gc=[UDrag]::GreenCentroid($bmp)
$bmp.Dispose()
Write-Host "Green $($gc[0]),$($gc[1]) n=$($gc[2]) maxX=$($gc[3])"
if ($gc[0] -lt 0) { Write-Host "NO GREEN"; exit 1 }

$rx = $rect.Left + [Math]::Max($gc[3]-12, $gc[0]+35)
$ry = $rect.Top + $gc[1]
Write-Host "Hold-click chevron $rx,$ry"
[UDrag]::ClickHold($rx, $ry, 280)
Start-Sleep -Milliseconds 1100
Shot "ue_hold_menu.png" $proc.MainWindowHandle

$bmp=[UDrag]::Capture($proc.MainWindowHandle)
$menu=$false
for ($y=($gc[1]+15); $y -lt ($gc[1]+90); $y++) {
  for ($x=20; $x -lt 260; $x++) {
    $c=$bmp.GetPixel($x,$y)
    if ($c.R -gt 240 -and $c.G -gt 240 -and $c.B -gt 240) { $menu=$true; break }
  }
  if ($menu) { break }
}
Write-Host "menu_white=$menu"
$bmp.Dispose()

if (-not $menu) {
  Write-Host "Retry center hold"
  [UDrag]::ClickHold(($rect.Left+$gc[0]), ($rect.Top+$gc[1]), 350)
  Start-Sleep -Milliseconds 1100
  Shot "ue_hold_menu2.png" $proc.MainWindowHandle
}

[System.Windows.Forms.Clipboard]::SetText("Static Mesh")
Start-Sleep -Milliseconds 100
[System.Windows.Forms.SendKeys]::SendWait("^v")
Start-Sleep -Milliseconds 800
Shot "ue_hold_filter.png" $proc.MainWindowHandle
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1200
Shot "ue_hold_added.png" $proc.MainWindowHandle
Write-Host "DONE"
'''
(docs / "_ui_hold_add.ps1").write_text(ps1, encoding="utf-8")
print("wrote ps1", len(ps1))