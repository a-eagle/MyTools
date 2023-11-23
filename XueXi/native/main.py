import win32api, win32com.client, win32con, win32gui
import time
from ctypes import windll, Structure, c_uint, sizeof, byref
import sys
import struct
import traceback

CHROME_HWND = None

lf = None
def log(*s):
    global lf
    if lf is None:
        lf = open('a.log', 'a')
    lf.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ' : ')
    lf.write(str(s) + '\n')
    lf.flush()

def log_N(*s):
    pass

def mouseClick(x, y):
    windll.user32.SetCursorPos(x, y)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

def keyPress(keyCode):
    win32api.keybd_event(keyCode, 0, 0, 0)
    win32api.keybd_event(keyCode, 0, win32con.KEYEVENTF_KEYUP, 0)

def send_message(msg):
    # Write message size.
    sys.stdout.buffer.write(struct.pack('I', len(msg)))
    # Write the message itself.
    sys.stdout.buffer.write(msg.encode('utf-8'))
    sys.stdout.buffer.flush()
    
def read_message():
    try:
        # Read the message length (first 4 bytes).
        bs = sys.stdin.buffer.read(4)
        # Unpack message length as 4 byte integer.
        mlen = struct.unpack('i', bs)[0]
        msg = sys.stdin.buffer.read(mlen).decode('utf-8')
        return msg
    except:
        traceback.print_exc()
        return 'Read_Msg_Error'

def showWin(hwnd):
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_SHOWMAXIMIZED)
    # win32gui.SetWindowPos(hwnd, NULL, 0, 0, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOMOVE | win32con.SWP_SHOWWINDOW)
    if win32gui.GetForegroundWindow() != hwnd:
        sh = win32com.client.Dispatch("WScript.Shell")
        sh.SendKeys('%')  # ALT key
        try:
            win32gui.SetForegroundWindow(hwnd)
            win32gui.SetActiveWindow(hwnd)
        except:
            traceback.print_exc()

def chromeTop():
    global CHROME_HWND
    showWin(CHROME_HWND)

def updateChromeWnd():
    global CHROME_HWND
    CHROME_HWND = None
    def get_wnd(hwnd, exta):
        global CHROME_HWND
        title = win32gui.GetWindowText(hwnd)
        if (title and ('我的积分 - Google Chrome' in title)):
            CHROME_HWND = hwnd
            return True
        return True
    win32gui.EnumWindows(get_wnd, 0)

#-----------------------------------------------------------------------
class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]

def pressSpace():
    keyPress(32)

def pressDownArrow():
    for i in range(0, 4):
        keyPress(40)
        time.sleep(0.5)
        
def mouseWheelDown():
    for i in range(0, 4):
        # -1 : move down    1 : move up
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -100)
        time.sleep(0.3)

def mouseRandMove():
    global CHROME_HWND
    l, t, r, b = win32gui.GetWindowRect(CHROME_HWND)
    log('GetWindowRect', l, t, r, b)
    cw = int((r - l) / 2)
    ch = int((b - t) / 2)
    #windll.user32.SetCursorPos(cw, ch)
    win32api.SetCursorPos((cw, ch))
    # pos = win32api.GetCursorPos()  # is an tuple (x, y)
    s = [(10, 10), (5, 5), (8, 8), (7, 7), (10, 10)]
    f = [(-10, -10), (-5, -5), (-8, -8), (-7, -7), (-10, -10)]
    for v in s:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, v[0], v[1], 0)
        time.sleep(0.05)
    for v in f:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, v[0], v[1], 0)
        time.sleep(0.05)


def moveMask(action):
    rect = action[9:]
    log(rect)
    rect = rect.strip().split(' ')
    chromeTop()
    x = int(int(rect[0]) + int(rect[2]) / 2)
    y = int(int(rect[1]) + int(rect[3]) / 2 + 102) # 102 is chrome top header height
    w = int(rect[4]) + 50
    #windll.user32.SetCursorPos(x, y)
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.4)
    mx = 0
    while mx < w:
        win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 5, 0, 0)
        time.sleep(0.02)
        mx += 5
    time.sleep(0.4)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

def mouseClick(x, y):
    win32api.SetCursorPos((x, y))
    # windll.user32.SetCursorPos(x, y)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    #time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def doit(action):
    if action.find('TOP_CHROME') >= 0:
        chromeTop()
        return action
        
    if action.find('PRESS_SPACE') >= 0:
        pressSpace()
        return action
        
    if action.find('IN_PAGE_DOC') >= 0:
        pressDownArrow()
        mouseWheelDown()
        mouseRandMove()
        return action
    
    if action.find('IN_PAGE_VIDEO') >= 0:
        pressDownArrow()
        mouseWheelDown()
        mouseRandMove()
        return action
    
    if action.find('UPDATE_CHROME_HWND') >= 0:
        global CHROME_HWND
        updateChromeWnd()
        if not CHROME_HWND:
            CHROME_HWND = 0
        return action + ' chrome-wnd=%#X' % CHROME_HWND
    
    if action.find('MOVE_MASK') >= 0:
        # 移动验证码
        moveMask(action)
        return action
    
    if action.find('RAND_MOUSE_MOVE') >= 0:
        mouseRandMove()
        return action
    
    if action.find('GET_IDLE_DURATION') >= 0:
        info = LASTINPUTINFO()
        info.cbSize = sizeof(info)
        windll.user32.GetLastInputInfo(byref(info))
        millis = windll.kernel32.GetTickCount() - info.dwTime
        sec = millis // 1000
        return f'GET_IDLE_DURATION {sec}'
    
    if action.find('CLICK') >= 0:
        x, y = action[5 : ].strip().split(' ')
        mouseClick(int(x), int(y))
        return action

    log('unkow action [' + action + ']')
    return action


def main():
    log('start main app')
    while (True):
        action = read_message()
        if action == 'Read_Msg_Error':
            continue
        if len(action) > 0 and action[0] == '"' and action[len(action) - 1] == '"':
            action = action[1 : -1]
        log('read msg:[' + action + ']')
        res = doit(action)
        send_message(res)
        log('send msg: [' + res + ']')
        
    
if __name__ == '__main__':
    try:
        main()
        # chromeTop()
    except:
        log('Occour Error')
        traceback.print_exc(file = lf)
        
    log('\nApp Exit')
