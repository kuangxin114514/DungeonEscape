using System;
using System.Runtime.InteropServices;
using System.Drawing;
public class UC2 {
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
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
  [DllImport("user32.dll")] public static extern int GetSystemMetrics(int nIndex);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
  public static void InitDpi(){ SetProcessDPIAware(); }
  public static void Force(IntPtr h){
    ShowWindow(h, 3);
    IntPtr fg=GetForegroundWindow();
    uint a=GetWindowThreadProcessId(fg,IntPtr.Zero);
    uint b=GetCurrentThreadId();
    AttachThreadInput(b,a,true);
    BringWindowToTop(h);
    SetForegroundWindow(h);
    AttachThreadInput(b,a,false);
    System.Threading.Thread.Sleep(150);
  }
  public static string Cur(){ POINT p; GetCursorPos(out p); return p.X+","+p.Y; }
  public static void ClickAt(int x, int y){
    SetCursorPos(x,y);
    System.Threading.Thread.Sleep(40);
    SetCursorPos(x,y);
    System.Threading.Thread.Sleep(40);
    Console.WriteLine("CurBefore="+Cur()+" target="+x+","+y);
    mouse_event(0x0002,0,0,0,UIntPtr.Zero);
    System.Threading.Thread.Sleep(80);
    mouse_event(0x0004,0,0,0,UIntPtr.Zero);
    System.Threading.Thread.Sleep(40);
    Console.WriteLine("CurAfter="+Cur());
  }
  public static void Tap(byte vk){
    keybd_event(vk,0,0,UIntPtr.Zero); System.Threading.Thread.Sleep(30);
    keybd_event(vk,0,2,UIntPtr.Zero); System.Threading.Thread.Sleep(40);
  }
  public static Bitmap Cap(IntPtr h){
    RECT r; GetWindowRect(h,out r);
    Console.WriteLine("CapRect "+r.Left+","+r.Top+" "+(r.Right-r.Left)+"x"+(r.Bottom-r.Top));
    Bitmap b=new Bitmap(Math.Max(1,r.Right-r.Left), Math.Max(1,r.Bottom-r.Top));
    using(Graphics g=Graphics.FromImage(b)) g.CopyFromScreen(r.Left,r.Top,0,0,b.Size);
    return b;
  }
  public static int[] GreenBtn(Bitmap bmp){
    long sx=0,sy=0,n=0; int maxX=0,minX=9999,maxY=0,minY=9999;
    for(int y=85;y<180;y++) for(int x=5;x<230;x++){
      if(x>=bmp.Width||y>=bmp.Height) continue;
      Color c=bmp.GetPixel(x,y);
      if(c.G>145 && c.G>c.R+45 && c.R<110 && c.B<110){
        sx+=x; sy+=y; n++;
        if(x>maxX)maxX=x; if(x<minX)minX=x; if(y>maxY)maxY=y; if(y<minY)minY=y;
      }
    }
    if(n<40) return new int[]{-1,-1,0,0,0,0,0};
    return new int[]{(int)(sx/n),(int)(sy/n),(int)n,maxX,minX,maxY,minY};
  }
  // Detect if add-component popup is open: bright search field or many light text rows under green
  public static bool MenuOpen(Bitmap bmp, int greenMaxY){
    int brightRows=0;
    for(int y=greenMaxY+20; y<Math.Min(bmp.Height, greenMaxY+420); y+=8){
      int hits=0;
      for(int x=30;x<340 && x<bmp.Width;x+=4){
        Color c=bmp.GetPixel(x,y);
        if((c.R+c.G+c.B)>480) hits++;
      }
      if(hits>18) brightRows++;
    }
    Console.WriteLine("MenuBrightRows="+brightRows);
    return brightRows>=6;
  }
}