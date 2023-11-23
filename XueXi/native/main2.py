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


def mouseClick_2(x, y):
    windll.user32.SetCursorPos(x, y)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.05)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

def mouseClick(x, y):
    win32api.SetCursorPos((x, y))
    # windll.user32.SetCursorPos(x, y)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    #time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

def keyPress(keyCode):
    win32api.keybd_event(keyCode, 0, 0, 0)
    win32api.keybd_event(keyCode, 0, win32con.KEYEVENTF_KEYUP, 0)

def pressSpace():
    keyPress(32)

def pressDownArrow():
    #for i in range(0, 4):
    keyPress(40)
    #    time.sleep(0.5)

def wait(s):
    time.sleep(s)
        
def mouseWheelDown():
    #for i in range(0, 4):
        # -1 : move down    1 : move up
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -100)
    #    time.sleep(0.3)


def send_message(msg):
    if not msg:
        msg = ''
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
    
def main():
    log('start main app')
    while (True):
        action = read_message()
        if action == 'Read_Msg_Error':
            continue
        if len(action) > 0 and action[0] == '"' and action[len(action) - 1] == '"':
            action = action[1 : -1]
        log('read msg:[' + action + ']')
        res = eval(action)
        send_message(res)
        log('send msg: [' + str(res) + ']')
        
    
if __name__ == '__main__':
    try:
        main()
    except:
        log('Occour Error')
        traceback.print_exc(file = lf)
        
    log('\nApp Exit')    