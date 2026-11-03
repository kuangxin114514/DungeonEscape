
using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class UB {
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
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct INPUT { public uint type; public MOUSEINPUT mi; }
  [StructLayout(LayoutKind.Sequential)] public struct MOUSEINPUT {
    public int dx; public int dy; public uint mouseData; public uint dwFlags; public uint time; public IntPtr dwExtraInfo;
  }
  static int AX(int x){int vx=GetSystemMetrics(78),vl=GetSystemMetrics(76); if(vx<=0){vx=GetSystemMetrics(0);vl=0;} return (int)(((x-vl)*65535.0)/Math.Max(1,vx-1));}
  static int AY(int y){int vy=GetSystemMetrics(79),vt=GetSystemMetrics(77); if(vy<=0){vy=GetSystemMetrics(1);vt=0;} return (int)(((y-vt)*65535.0)/Math.Max(1,vy-1));}
  public static void Force(IntPtr h){ ShowWindow(h,3); IntPtr fg=GetForegroundWindow(); uint a=GetWindowThreadProcessId(fg,IntPtr.Zero); uint b=GetCurrentThreadId(); AttachThreadInput(b,a,true); BringWindowToTop(h); SetForegroundWindow(h); AttachThreadInput(b,a,false); System.Threading.Thread.Sleep(100); }
  public static void Move(int x,int y){ INPUT[] a=new INPUT[1]; a[0].type=0; a[0].mi.dx=AX(x); a[0].mi.dy=AY(y); a[0].mi.dwFlags=0x8001|0x4000; SendInput(1,a,Marshal.SizeOf(typeof(INPUT))); }
  public static void Down(){ INPUT[] a=new INPUT[1]; a[0].type=0; a[0].mi.dwFlags=0x0002; SendInput(1,a,Marshal.SizeOf(typeof(INPUT))); }
  public static void Up(){ INPUT[] a=new INPUT[1]; a[0].type=0; a[0].mi.dwFlags=0x0004; SendInput(1,a,Marshal.SizeOf(typeof(INPUT))); }
  public static void Click(int x,int y){ Move(x,y); System.Threading.Thread.Sleep(40); Down(); System.Threading.Thread.Sleep(80); Up(); Console.WriteLine("Click "+x+","+y); }
  public static void Tap(byte vk){ keybd_event(vk,0,0,UIntPtr.Zero); System.Threading.Thread.Sleep(30); keybd_event(vk,0,2,UIntPtr.Zero); System.Threading.Thread.Sleep(40); }
  public static void TypeAscii(string s){ foreach(char ch in s){ bool up=char.IsUpper(ch); char c=char.ToUpper(ch); byte vk=0; if(c>='A'&&c<='Z') vk=(byte)c; else if(c==' ') vk=0x20; else continue; if(up) keybd_event(0x10,0,0,UIntPtr.Zero); Tap(vk); if(up) keybd_event(0x10,0,2,UIntPtr.Zero);} }
  public static Bitmap Cap(IntPtr h){ RECT r; GetWindowRect(h,out r); Bitmap b=new Bitmap(Math.Max(1,r.Right-r.Left),Math.Max(1,r.Bottom-r.Top)); using(Graphics g=Graphics.FromImage(b)) g.CopyFromScreen(r.Left,r.Top,0,0,b.Size); return b; }
  public static int[] Green(Bitmap bmp){ long sx=0,sy=0,n=0; int maxX=0,minX=9999; for(int y=90;y<210;y++)for(int x=5;x<300;x++){ if(x>=bmp.Width||y>=bmp.Height)continue; Color c=bmp.GetPixel(x,y); if(c.G>140&&c.G>c.R+40&&c.R<120){sx+=x;sy+=y;n++; if(x>maxX)maxX=x; if(x<minX)minX=x;} } if(n==0)return new int[]{-1,-1,0,0,0}; return new int[]{(int)(sx/n),(int)(sy/n),(int)n,maxX,minX}; }
  public static int WhiteCount(Bitmap bmp,int x0,int y0,int x1,int y1){ int n=0; for(int y=y0;y<y1&&y<bmp.Height;y++)for(int x=x0;x<x1&&x<bmp.Width;x++){ Color c=bmp.GetPixel(x,y); if(c.R>200&&c.G>200&&c.B>200)n++; } return n; }
}
