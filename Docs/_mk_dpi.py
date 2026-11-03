# -*- coding: utf-8 -*-
from pathlib import Path
docs = Path(r"C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs")
cs = r'''
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class UC {
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
  [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, IntPtr pid);
  [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
  [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT lpPoint);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern uint SendInput(uint nInputs, INPUT[] pInputs, int cbSize);
  [DllImport("user32.dll")] public static extern int GetSystemMetrics(int nIndex);
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
  [StructLayout(LayoutKind.Sequential)] public struct INPUT { public uint type; public MOUSEINPUT mi; }
  [StructLayout(LayoutKind.Sequential)] public struct MOUSEINPUT {
    public int dx; public int dy; public uint mouseData; public uint dwFlags; public uint time; public IntPtr dwExtraInfo;
  }
  static int AX(int x){int vx=GetSystemMetrics(78),vl=GetSystemMetrics(76); if(vx<=0){vx=GetSystemMetrics(0);vl=0;} return (int)(((x-vl)*65535.0)/Math.Max(1,vx-1));}
  static int AY(int y){int vy=GetSystemMetrics(79),vt=GetSystemMetrics(77); if(vy<=0){vy=GetSystemMetrics(1);vt=0;} return (int)(((y-vt)*65535.0)/Math.Max(1,vy-1));}
  public static void InitDpi(){ SetProcessDPIAware(); }
  public static void Force(IntPtr h){ ShowWindow(h,3); IntPtr fg=GetForegroundWindow(); uint a=GetWindowThreadProcessId(fg,IntPtr.Zero); uint b=GetCurrentThreadId(); AttachThreadInput(b,a,true); BringWindowToTop(h); SetForegroundWindow(h); AttachThreadInput(b,a,false); System.Threading.Thread.Sleep(120); }
  public static void MoveSI(int x,int y){ INPUT[] a=new INPUT[1]; a[0].type=0; a[0].mi.dx=AX(x); a[0].mi.dy=AY(y); a[0].mi.dwFlags=0x8001|0x4000; SendInput(1,a,Marshal.SizeOf(typeof(INPUT))); }
  public static void MoveCP(int x,int y){ SetCursorPos(x,y); }
  public static string Cur(){ POINT p; GetCursorPos(out p); return p.X+","+p.Y; }
  public static void Down(){ mouse_event(0x0002,0,0,0,UIntPtr.Zero); }
  public static void Up(){ mouse_event(0x0004,0,0,0,UIntPtr.Zero); }
  public static void ClickAt(int x,int y){ MoveSI(x,y); System.Threading.Thread.Sleep(30); MoveCP(x,y); System.Threading.Thread.Sleep(30); Console.WriteLine("CurBeforeClick="+Cur()); Down(); System.Threading.Thread.Sleep(70); Up(); Console.WriteLine("Click "+x+","+y+" after="+Cur()); }
  public static void Drag(int x0,int y0,int x1,int y1){
    MoveSI(x0,y0); System.Threading.Thread.Sleep(40); MoveCP(x0,y0); System.Threading.Thread.Sleep(40);
    Console.WriteLine("DragStart "+Cur());
    Down(); System.Threading.Thread.Sleep(80);
    int steps=18;
    for(int i=1;i<=steps;i++){
      int x=x0+(x1-x0)*i/steps; int y=y0+(y1-y0)*i/steps;
      MoveSI(x,y); MoveCP(x,y); System.Threading.Thread.Sleep(25);
    }
    System.Threading.Thread.Sleep(80);
    Console.WriteLine("DragEnd "+Cur());
    Up(); System.Threading.Thread.Sleep(100);
  }
  public static void Tap(byte vk){ keybd_event(vk,0,0,UIntPtr.Zero); System.Threading.Thread.Sleep(25); keybd_event(vk,0,2,UIntPtr.Zero); System.Threading.Thread.Sleep(35); }
  public static void TypeAscii(string s){ foreach(char ch in s){ char c=char.ToUpper(ch); byte vk=0; if(c>='A'&&c<='Z') vk=(byte)c; else if(c==' ') vk=0x20; else continue; Tap(vk);} }
  public static Bitmap Cap(IntPtr h){ RECT r; GetWindowRect(h,out r); Console.WriteLine("CapRect "+r.Left+","+r.Top+" "+(r.Right-r.Left)+"x"+(r.Bottom-r.Top)+" screen="+GetSystemMetrics(0)+"x"+GetSystemMetrics(1)+" virt="+GetSystemMetrics(78)+"x"+GetSystemMetrics(79)); Bitmap b=new Bitmap(Math.Max(1,r.Right-r.Left),Math.Max(1,r.Bottom-r.Top)); using(Graphics g=Graphics.FromImage(b)) g.CopyFromScreen(r.Left,r.Top,0,0,b.Size); return b; }
  public static int[] GreenBtn(Bitmap bmp){
    long sx=0,sy=0,n=0; int maxX=0,minX=9999,maxY=0,minY=9999;
    for(int y=85;y<175;y++) for(int x=5;x<220;x++){
      if(x>=bmp.Width||y>=bmp.Height) continue;
      Color c=bmp.GetPixel(x,y);
      if(c.G>145 && c.G>c.R+45 && c.R<110 && c.B<110){
        sx+=x; sy+=y; n++;
        if(x>maxX)maxX=x; if(x<minX)minX=x; if(y>maxY)maxY=y; if(y<minY)minY=y;
      }
    }
    if(n<50) return new int[]{-1,-1,0,0,0,0,0};
    return new int[]{(int)(sx/n),(int)(sy/n),(int)n,maxX,minX,maxY,minY};
  }
  public static int[] FindOrangeBottom(Bitmap bmp){
    // look for content browser selection (orange) in bottom 40%
    int y0=(int)(bmp.Height*0.55);
    long sx=0,sy=0,n=0; int maxX=0,minX=9999;
    for(int y=y0;y<bmp.Height-20;y++) for(int x=200;x<bmp.Width-50;x++){
      Color c=bmp.GetPixel(x,y);
      // UE orange selection ~ (255,140,0) to (200,100,40)
      if(c.R>160 && c.G>70 && c.G<180 && c.B<80 && c.R>c.G+30){
        sx+=x; sy+=y; n++; if(x>maxX)maxX=x; if(x<minX)minX=x;
      }
    }
    if(n<20) return new int[]{-1,-1,0,0,0};
    return new int[]{(int)(sx/n),(int)(sy/n),(int)n,maxX,minX};
  }
}
'''
(docs/'_UC.cs').write_text(cs, encoding='utf-8')
ps1 = r'''$ErrorActionPreference = "Continue"
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
$drawing = [System.Reflection.Assembly]::LoadWithPartialName("System.Drawing").Location
$cs = Get-Content -Raw "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs\_UC.cs"
Add-Type -ReferencedAssemblies $drawing -TypeDefinition $cs
[UC]::InitDpi()
$docs = "C:\Users\86178\Documents\Unreal Projects\DungeonEscape\Docs"
$py = "C:\Program Files\Epic Games\UE_4.27\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
& $py "$docs\_run_sync_sword2.py" | Out-Host
Start-Sleep -Milliseconds 2500
$proc = Get-Process UE4Editor | Select-Object -First 1
[UC]::Force($proc.MainWindowHandle)
$rect = New-Object UC+RECT
[UC]::GetWindowRect($proc.MainWindowHandle, [ref]$rect) | Out-Null
Write-Host "RECT $($rect.Left),$($rect.Top) $($rect.Right-$rect.Left)x$($rect.Bottom-$rect.Top) dpiAware metrics SM=$([UC]::GetSystemMetrics(0))x$([UC]::GetSystemMetrics(1))"
$bmp = [UC]::Cap($proc.MainWindowHandle)
$gc = [UC]::GreenBtn($bmp)
Write-Host "Green cx=$($gc[0]) cy=$($gc[1]) n=$($gc[2]) maxX=$($gc[3]) minX=$($gc[4]) maxY=$($gc[5]) minY=$($gc[6])"
$or = [UC]::FindOrangeBottom($bmp)
Write-Host "Orange cx=$($or[0]) cy=$($or[1]) n=$($or[2])"
# save half layout
$bw=[int]($bmp.Width*0.5); $bh=[int]($bmp.Height*0.5)
$b2=New-Object System.Drawing.Bitmap $bw,$bh
$g=[System.Drawing.Graphics]::FromImage($b2)
$g.DrawImage($bmp,0,0,$bw,$bh)
$b2.Save("$docs\ue_dpi_layout.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $b2.Dispose()
if ($gc[0] -lt 0) { Write-Host "FAIL no green"; $bmp.Dispose(); exit 1 }

# Color under planned click points
function Sample($bmp,$x,$y,$label){ $c=$bmp.GetPixel($x,$y); Write-Host "Sample $label $x,$y = $($c.R),$($c.G),$($c.B)" }
Sample $bmp $gc[0] $gc[1] "greenCenter"
Sample $bmp 120 235 "meshGuess"
$bmp.Dispose()

# 1) Select CharacterMesh0
$meshAbsX = $rect.Left + 120
$meshAbsY = $rect.Top + 235
[UC]::ClickAt($meshAbsX, $meshAbsY)
Start-Sleep -Milliseconds 400

# 2) Click green Add Component center
$gx = $rect.Left + $gc[0]
$gy = $rect.Top + $gc[1]
[UC]::Force($proc.MainWindowHandle)
[UC]::ClickAt($gx, $gy)
Start-Sleep -Milliseconds 1000
$bmp = [UC]::Cap($proc.MainWindowHandle)
$crop=$bmp.Clone((New-Object System.Drawing.Rectangle 0,80,[Math]::Min(420,$bmp.Width),[Math]::Min(520,$bmp.Height-80)), $bmp.PixelFormat)
$crop.Save("$docs\ue_dpi_menu.png", [System.Drawing.Imaging.ImageFormat]::Png)
$crop.Dispose()
# count bright-ish menu rows (dark theme menus still have lighter hover)
$bright=0
for($y=150;$y -lt 480 -and $y -lt $bmp.Height;$y++){ for($x=20;$x -lt 300 -and $x -lt $bmp.Width;$x++){ $c=$bmp.GetPixel($x,$y); if(($c.R+$c.G+$c.B) -gt 420){ $bright++ } } }
Write-Host "BrightPixelsInMenuArea=$bright"
$bmp.Dispose()

# Type filter
[UC]::Force($proc.MainWindowHandle)
Start-Sleep -Milliseconds 150
[UC]::TypeAscii("static mesh")
Start-Sleep -Milliseconds 800
$bmp = [UC]::Cap($proc.MainWindowHandle)
$crop=$bmp.Clone((New-Object System.Drawing.Rectangle 0,80,[Math]::Min(420,$bmp.Width),[Math]::Min(520,$bmp.Height-80)), $bmp.PixelFormat)
$crop.Save("$docs\ue_dpi_filter.png", [System.Drawing.Imaging.ImageFormat]::Png)
$crop.Dispose(); $bmp.Dispose()
[UC]::Tap(0x28)
Start-Sleep -Milliseconds 120
[UC]::Tap(0x0D)
Start-Sleep -Milliseconds 1400
$bmp = [UC]::Cap($proc.MainWindowHandle)
$crop=$bmp.Clone((New-Object System.Drawing.Rectangle 0,80,[Math]::Min(420,$bmp.Width),[Math]::Min(520,$bmp.Height-80)), $bmp.PixelFormat)
$crop.Save("$docs\ue_dpi_after.png", [System.Drawing.Imaging.ImageFormat]::Png)
$crop.Dispose()
$bw=[int]($bmp.Width*0.5); $bh=[int]($bmp.Height*0.5)
$b2=New-Object System.Drawing.Bitmap $bw,$bh
$g=[System.Drawing.Graphics]::FromImage($b2)
$g.DrawImage($bmp,0,0,$bw,$bh)
$b2.Save("$docs\ue_dpi_after_full.png", [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $b2.Dispose(); $bmp.Dispose()
Write-Host "DONE"
'''
(docs/'_ui_dpi.ps1').write_text(ps1, encoding='utf-8')
print('ok')