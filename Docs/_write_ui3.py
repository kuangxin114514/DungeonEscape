# -*- coding: utf-8 -*-
from pathlib import Path
Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_ui_add3.ps1").write_text(r'''
$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
Add-Type -ReferencedAssemblies $drawing -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class U3 {
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
  static int AbsX(int x) { int vx=GetSystemMetrics(78), vl=GetSystemMetrics(76); if(vx<=0){vx=GetSystemMetrics(0);vl=0;} return (int)(((x-vl)*65535.0)/Math.Max(1,vx-1)); }
  static int AbsY(int y) { int vy=GetSystemMetrics(79), vt=GetSystemMetrics(77); if(vy<=0){vy=GetSystemMetrics(1);vt=0;} return (int)(((y-vt)*65535.0)/Math.Max(1,vy-1)); }
  static INPUT M(int x,int y){ INPUT i=new INPUT(); i.type=0; i.U.mi.dx=AbsX(x); i.U.mi.dy=AbsY(y); i.U.mi.dwFlags=0x8001|0x4000; return i; }
  public static void Force(IntPtr h){ ShowWindow(h,3); IntPtr fg=GetForegroundWindow(); uint a=GetWindowThreadProcessId(fg,IntPtr.Zero); uint b=GetCurrentThreadId(); AttachThreadInput(b,a,true); BringWindowToTop(h); SetForegroundWindow(h); AttachThreadInput(b,a,false); System.Threading.Thread.Sleep(100); }
  public static void Move(int x,int y){ INPUT[] a=new INPUT[]{M(x,y)}; SendInput(1,a,Marshal.SizeOf(typeof(INPUT))); }
  public static void Down(){ INPUT[] a=new INPUT[1]; a[0].type=0; a[0].U.mi.dwFlags=0x0002; SendInput(1,a,Marshal.SizeOf(typeof(INPUT))); }
  public static void Up(){ INPUT[] a=new INPUT[1]; a[0].type=0; a[0].U.mi.dwFlags=0x0004; SendInput(1,a,Marshal.SizeOf(typeof(INPUT))); }
  public static void Click(int x,int y){ Move(x,y); System.Threading.Thread.Sleep(60); Down(); System.Threading.Thread.Sleep(100); Up(); Console.WriteLine("Click "+x+","+y); }
  public static void Hold(int x,int y,int ms){ Move(x,y); System.Threading.Thread.Sleep(60); Down(); System.Threading.Thread.Sleep(ms); Up(); Console.WriteLine("Hold "+x+","+y); }
  public static void Drag(int x1,int y1,int x2,int y2){ Move(x1,y1); System.Threading.Thread.Sleep(80); Down(); System.Threading.Thread.Sleep(120); for(int i=1;i<=20;i++){ Move(x1+(x2-x1)*i/20, y1+(y2-y1)*i/20); System.Threading.Thread.Sleep(25);} System.Threading.Thread.Sleep(80); Up(); Console.WriteLine("Drag "+x1+","+y1+"->"+x2+","+y2); }
  public static Bitmap Cap(IntPtr h){ RECT r; GetWindowRect(h,out r); Bitmap b=new Bitmap(Math.Max(1,r.Right-r.Left),Math.Max(1,r.Bottom-r.Top)); using(Graphics g=Graphics.FromImage(b)) g.CopyFromScreen(r.Left,r.Top,0,0,b.Size); return b; }
  public static int[] Green(Bitmap bmp){ long sx=0,sy=0,n=0; int maxX=0; for(int y=90;y<210;y++)for(int x=5;x<300;x++){ if(x>=bmp.Width||y>=bmp.Height)continue; Color c=bmp.GetPixel(x,y); if(c.G>140&&c.G>c.R+40&&c.R<120){sx+=x;sy+=y;n++; if(x>maxX)maxX=x;} } if(n==0)return new int[]{-1,-1,0,0}; return new int[]{(int)(sx/n),(int)(sy/n),(int)n,maxX}; }
}
"@
$docs="C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function Shot($n,$h,$crop=$false){
  $bmp=[U3]::Cap($h)
  if($crop){ $c=New-Object System.Drawing.Bitmap 320,420; $g=[System.Drawing.Graphics]::FromImage($c); $g.DrawImage($bmp, (New-Object System.Drawing.Rectangle 0,0,320,420), (New-Object System.Drawing.Rectangle 0,80,320,420), [System.Drawing.GraphicsUnit]::Pixel); $c.Save((Join-Path $docs $n), [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $c.Dispose() }
  else { $bw=[int]($bmp.Width*0.45); $bh=[int]($bmp.Height*0.45); $b2=New-Object System.Drawing.Bitmap $bw,$bh; $g=[System.Drawing.Graphics]::FromImage($b2); $g.DrawImage($bmp,0,0,$bw,$bh); $b2.Save((Join-Path $docs $n), [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $b2.Dispose() }
  $bmp.Dispose(); Write-Host "SHOT $n"
}
$py="C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_sync_sword2.py" | Out-Host
Start-Sleep -Milliseconds 1500
$proc=Get-Process UE4Editor | Select-Object -First 1
[U3]::Force($proc.MainWindowHandle)
$rect=New-Object U3+RECT
[U3]::GetWindowRect($proc.MainWindowHandle,[ref]$rect)|Out-Null
# Click BP tab then Viewport
[U3]::Click(($rect.Left+500),($rect.Top+40)); Start-Sleep -Milliseconds 350
[U3]::Click(($rect.Left+300),($rect.Top+140)); Start-Sleep -Milliseconds 350
[U3]::Force($proc.MainWindowHandle)
$bmp=[U3]::Cap($proc.MainWindowHandle); $gc=[U3]::Green($bmp); $bmp.Dispose()
Write-Host "Green $($gc[0]),$($gc[1]) maxX=$($gc[3])"
if($gc[0] -lt 0){Write-Host "NO GREEN"; exit 1}
# Select CharacterMesh0
[U3]::Click(($rect.Left+100),($rect.Top+285)); Start-Sleep -Milliseconds 300
# Hold on right edge of green (chevron)
$rx=$rect.Left+[Math]::Max($gc[3]-10,$gc[0]+40); $ry=$rect.Top+$gc[1]
[U3]::Hold($rx,$ry,300); Start-Sleep -Milliseconds 900
Shot "ue_m1_crop.png" $proc.MainWindowHandle $true
# Type letter by letter (no ctrl)
[System.Windows.Forms.SendKeys]::SendWait("static mesh")
Start-Sleep -Milliseconds 900
Shot "ue_m2_crop.png" $proc.MainWindowHandle $true
[System.Windows.Forms.SendKeys]::SendWait("{DOWN}"); Start-Sleep -Milliseconds 150
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}"); Start-Sleep -Milliseconds 1200
Shot "ue_m3_crop.png" $proc.MainWindowHandle $true
Shot "ue_m3_full.png" $proc.MainWindowHandle $false
Write-Host "DONE"
''', encoding='utf-8')
print('wrote')