import json, os, sys, datetime, threading, time, inspect, platform, base64
import traceback, win32gui, win32con
import requests, json, logging
import peewee as pw, flask, flask_cors

class ServerUI:
    def __init__(self):
        pass

    def click(self):
        x = flask.request.args.get('x', None)
        y = flask.request.args.get('y', None)
        if x is None or y is None:
            return {'status': 'Error', 'msg': f'position is error ({x},{y})'}
        winds = svr.findChromeWnd()
        x = int(x)
        y = int(y)
        for win in winds:
            win32gui.PostMessage(win, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, (y << 16) | x)
            time.sleep(0.1)
            win32gui.PostMessage(win, win32con.WM_LBUTTONUP, 0, (y << 16) | x)
        return {'status': 'OK', 'msg': f'click ({x},{y})'}

    def findChromeWnd(self):
        topWins = []
        def cb(hwnd, params):
            className = win32gui.GetClassName(hwnd)
            if className == 'Chrome_WidgetWin_1':
                topWins.append(hwnd)
            return True
        win32gui.EnumWindows(cb, None)
        return topWins

    def start(self):
        self.app = flask.Flask(__name__)
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
        # log.disabled = True
        flask_cors.CORS(self.app)
        self.app.add_url_rule('/click', view_func = self.click, methods = ['GET'])
        self.app.run('0.0.0.0', 9000, use_reloader = False, debug = False)


if __name__ == '__main__':
    svr = ServerUI()
    svr.start()
    