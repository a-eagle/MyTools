import traceback, json, os, requests, hashlib, sys
from flask import Flask, make_response, abort, request
from flask_cors import CORS   # pip install -U flask-cors 
from werkzeug.routing import BaseConverter
import base


app = Flask(__name__, instance_relative_config = True, static_folder='download') # template_folder='ui/templates'
cors = CORS(app)
app.config.from_mapping(
    SECRET_KEY = 'xielaic4cE@xef*',
)

logFile = open(base.DOWNLOAD_DIR + 's-log.txt', 'a+')

HOST_URL =  ''

def readFile(urlObj):
    path = base.DOWNLOAD_DIR + urlObj.path
    f = open(path, 'rb')
    cnt = f.read()
    f.close()
    resp = make_response(cnt, 200)
    ct = urlObj.contentType
    if urlObj.encoding:
        ct += '; charset=' + urlObj.encoding
    resp.headers = {
         'content-type':  ct
    }
    return resp


# POST {method: GET|POST, url: str, type = 'xhr', headers: object, body?:any }
@app.route("/<path:urlx>", methods = ['POST', 'GET'])
def list_file(urlx):
    try:
        rurl = request.url[len(request.host_url) : ]
        furl = base.toStdUrl(HOST_URL + rurl)
        if '#' in furl:
            furl = furl[0 : furl.index('#')]
        objU : base.Urls = base.Urls.get_or_none(url = furl)
        body = request.data
        if objU:  # 准确的应该通过path查找
            paths = base.urlToPaths(furl, objU.ftype, body)
            path = '/'.join(paths)
            objP = base.Urls.get_or_none(path = path)
            if objP: return readFile(objP)
        if objU:
            return readFile(objU)
        if '?' not in furl:
            tx = f'[Not Find 1]: {furl}'
            logFile.write(tx + '\n')
            logFile.flush()
            return make_response(tx, 404)

        surl = furl[0 : furl.index('?')]
        qr = base.Urls.select().where(base.Urls.url == surl, base.Urls.ftype == 'static')
        for q in qr:
            return readFile(q)
        tx = f'[Not Find 2]: {furl}'
        logFile.write(tx + '\n')
        logFile.flush()
        return make_response(tx, 404)
    except Exception as e:
        traceback.print_exc()
        logFile.write(f'Exception: {str(e)}\n')
        logFile.flush()
        return make_response(str(e), 500)

if __name__ == '__main__':
    HOST_URL = 'http://10.97.10.42:8082/'
    #print('server -port xxxx -hosturl http://xxx/')
    PORT = 5555
    print('Default local port = ', PORT)
    print('Default hosturl = ', HOST_URL)

    px = input('Input local port, if no changed, press enter: ').strip()
    if px: PORT = int(px)
    pu = input('Input hosturl(http://xxxx/), if no changed, press enter: ').strip()
    if pu: 
        HOST_URL = pu
        print(f'  Use hosturl=[{HOST_URL}]')

    app.run(host = '0.0.0.0', port = PORT, debug = True, use_reloader = False)  # use_reloader  禁止启动2次