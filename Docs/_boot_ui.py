# -*- coding: utf-8 -*-
from pathlib import Path
docs = Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs")
csharp = """
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class UA {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, IntPtr pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
  [DllImport("user32.dll")] public static extern int GetSystemMetrics(int nIndex);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct INPUT { public uint type; public MOUSEINPUT mi; }
  [StructLayout(LayoutKind.Sequential)] public struct MOUSEINPUT {
    public int dx; public int dy; public uint mouseData; public uint dwFlags; public uint time; public IntPtr dwExtraInfo;
  }
  static int AX(int x){int vx=GetSystemMetrics(78),vl=GetSystemMetrics(76); if(vx<=0){vx=GetSystemMetrics(0);vl=0;} return (int)(((x-vl)*65535.0)/Math.Max(1,vx-1));}
  static int AY(int y){int vy=GetSystemMetrics(79),vt=GetSystemMetrics(77); if(vy<=0){vy=GetSystemMetrics(1);vt=0;} return (int)(((y-vt)*65535.0)/Math.Max(1,vy-1));}
  public static void Force(IntPtr h){ ShowWindow(h,3); IntPtr fg=GetForegroundWindow(); uint a=GetWindowThreadProcessId(fg,IntPtr.Zero); uint b=GetCurrentThreadId(); AttachThreadInput(b,a,true); BringWindowToTop(h); SetForegroundWindow(h); AttachThreadInput(b,a,false); System.Threading.Thread.Sleep(80); }
  public static void Move(int x,int y){ INPUT[] a=new INPUT[1]; a[0].type=0; a[0].mi.dx=AX(x); a[0].mi.dy=AY(y); a[0].mi.dwFlags=0x8001|0x4000; SendInput(1,a,Marshal.SizeOf(typeof(INPUT))); }
  public static void Down(){ INPUT[] a=new INPUT[1]; a[0].type=0; a[0].mi.dwFlags=0x0002; SendInput(1,a,Marshal.SizeOf(typeof(INPUT))); }
  public static void Up(){ INPUT[] a=new INPUT[1]; a[0].type=0; a[0].mi.dwFlags=0x0004; SendInput(1,a,Marshal.SizeOf(typeof(INPUT))); }
  public static void Click(int x,int y){ Move(x,y); System.Threading.Thread.Sleep(50); Down(); System.Threading.Thread.Sleep(90); Up(); Console.WriteLine("Click "+x+","+y); }
  public static void Hold(int x,int y,int ms){ Move(x,y); System.Threading.Thread.Sleep(50); Down(); System.Threading.Thread.Sleep(ms); Up(); Console.WriteLine("Hold "+x+","+y+" "+ms); }
  public static Bitmap Cap(IntPtr h){ RECT r; GetWindowRect(h,out r); Bitmap b=new Bitmap(Math.Max(1,r.Right-r.Left),Math.Max(1,r.Bottom-r.Top)); using(Graphics g=Graphics.FromImage(b)) g.CopyFromScreen(r.Left,r.Top,0,0,b.Size); return b; }
  public static int[] Green(Bitmap bmp){ long sx=0,sy=0,n=0; int maxX=0,minX=9999; for(int y=90;y<210;y++)for(int x=5;x<300;x++){ if(x>=bmp.Width||y>=bmp.Height)continue; Color c=bmp.GetPixel(x,y); if(c.G>140&&c.G>c.R+40&&c.R<120){sx+=x;sy+=y;n++; if(x>maxX)maxX=x; if(x<minX)minX=x;} } if(n==0)return new int[]{-1,-1,0,0,0}; return new int[]{(int)(sx/n),(int)(sy/n),(int)n,maxX,minX}; }
}
"""
(docs/"_UA.cs").write_text(csharp, encoding="utf-8")
ps1 = r"""$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UA.cs"
Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
function SaveCrop($name, $h, $x, $y, $w, $hh) {
  $bmp = [UA]::Cap($h)
  $w = [Math]::Min($w, $bmp.Width-$x); $hh=[Math]::Min($hh,$bmp.Height-$y)
  $rect = New-Object System.Drawing.Rectangle $x,$y,$w,$hh
  $crop = $bmp.Clone($rect, $bmp.PixelFormat)
  $crop.Save((Join-Path $docs $name), [System.Drawing.Imaging.ImageFormat]::Png)
  $crop.Dispose(); $bmp.Dispose()
  Write-Host "CROP $name"
}
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_sync_sword2.py" | Out-Host
Start-Sleep -Milliseconds 1200
$proc = Get-Process UE4Editor | Select-Object -First 1
[UA]::Force($proc.MainWindowHandle)
$rect = New-Object UA+RECT
[UA]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
Write-Host "RECT $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top)"
$bmp = [UA]::Cap($proc.MainWindowHandle)
$gc = [UA]::Green($bmp)
$bmp.Dispose()
Write-Host "Green cx=$($gc[0]) cy=$($gc[1]) n=$($gc[2]) maxX=$($gc[3]) minX=$($gc[4])"
if ($gc[0] -lt 0) { Write-Host "FAIL no green"; exit 1 }
[UA]::Click(($rect.Left + 110), ($rect.Top + 290))
Start-Sleep -Milliseconds 350
$rx = $rect.Left + $gc[3] - 8
$ry = $rect.Top + $gc[1]
Write-Host "Hold chevron $rx,$ry"
[UA]::Hold($rx, $ry, 320)
Start-Sleep -Milliseconds 1000
SaveCrop "ue_menu_crop.png" $proc.MainWindowHandle 0 80 360 450
[System.Windows.Forms.SendKeys]::SendWait("static mesh")
Start-Sleep -Milliseconds 800
SaveCrop "ue_filter_crop.png" $proc.MainWindowHandle 0 80 360 450
[System.Windows.Forms.SendKeys]::SendWait("{DOWN}")
Start-Sleep -Milliseconds 200
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Start-Sleep -Milliseconds 1200
SaveCrop "ue_added_crop.png" $proc.MainWindowHandle 0 80 360 450
$bmp = [UA]::Cap($proc.MainWindowHandle)
$bw=[int]($bmp.Width*0.45); $bh=[int]($bmp.Height*0.45)
$b2=New-Object System.Drawing.Bitmap $bw,$bh
$g=[System.Drawing.Graphics]::FromImage($b2)
$g.DrawImage($bmp,0,0,$bw,$bh)
$b2.Save((Join-Path $docs "ue_added_full.png"), [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose();$bmp.Dispose();$b2.Dispose()
Write-Host "DONE"
"""
(docs/"_ui_add_final.ps1").write_text(ps1, encoding="utf-8")
print("ok")