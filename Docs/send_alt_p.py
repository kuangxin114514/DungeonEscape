import ctypes, time, sys
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
VK_MENU = 0x12  # Alt
VK_P = 0x50
VK_ESCAPE = 0x1B

def enum_windows():
    wins = []
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            if title:
                wins.append((hwnd, title))
        return True
    user32.EnumWindows(EnumWindowsProc(cb), 0)
    return wins

wins = enum_windows()
ue = None
for hwnd, title in wins:
    if "DungeonEscape" in title or "虚幻编辑器" in title:
        print("WIN", hex(hwnd), title)
        if "DungeonEscape" in title:
            ue = hwnd
if ue is None:
    for hwnd, title in wins:
        if "虚幻编辑器" in title:
            ue = hwnd; break
if ue is None:
    print("NO_UE_WINDOW"); sys.exit(2)
print("TARGET", hex(ue))

# End play first with Escape then request stop via remote briefly
user32.ShowWindow(ue, 9)  # SW_RESTORE
user32.SetForegroundWindow(ue)
time.sleep(0.4)

# Send Alt+P (PIE play). Also try F8 stop then Alt+P
def key_down(vk, syskey=False):
    msg = WM_SYSKEYDOWN if syskey else WM_KEYDOWN
    user32.PostMessageW(ue, msg, vk, 0)

def key_up(vk, syskey=False):
    msg = WM_SYSKEYUP if syskey else WM_KEYUP
    user32.PostMessageW(ue, msg, vk, 0)

# Prefer SendInput for Alt+P reliability
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]
class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]
class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

EXTRA = ctypes.c_ulong(0)
def press(vk, flags=0):
    ii_ = Input_I()
    ii_.ki = KeyBdInput(vk, 0, flags, 0, ctypes.pointer(EXTRA))
    x = Input(ctypes.c_ulong(1), ii_)
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))

KEYEVENTF_KEYUP = 0x0002
# Focus
user32.SetForegroundWindow(ue)
time.sleep(0.3)
# Alt down, P down, P up, Alt up
press(VK_MENU, 0)
time.sleep(0.05)
press(VK_P, 0)
time.sleep(0.05)
press(VK_P, KEYEVENTF_KEYUP)
time.sleep(0.05)
press(VK_MENU, KEYEVENTF_KEYUP)
print("sent Alt+P")
time.sleep(2.5)
print("done")
