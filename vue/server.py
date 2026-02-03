import threading, sys, traceback, datetime, json, logging, copy, os, base64
import flask, flask_cors, requests, mimetypes

class Server:

    def __init__(self) -> None:
        # mimetypes.add_type('application/javascript', '.js')
        # mimetypes.add_type('application/javascript', '.vue')
        self.app = flask.Flask(__name__, static_folder = 'js', template_folder = '')
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
        # log.disabled = True
        flask_cors.CORS(self.app)

    def start(self):
        self.app.run('0.0.0.0', 8081, use_reloader = False, debug = False)

if __name__ == '__main__':
    svr = Server()
    svr.start()