import traceback, json, os, requests, hashlib
from flask import Flask, make_response, abort, request
from flask_cors import CORS   # pip install -U flask-cors 
from werkzeug.routing import BaseConverter
import base


app = Flask(__name__, instance_relative_config = True, static_folder='download') # template_folder='ui/templates'
cors = CORS(app)
app.config.from_mapping(
    SECRET_KEY = 'xielaic4cE@xef*',
)

logFile = open('download/log-s.txt', 'a+')

DOMAIN = 'http://10.8.52.17:8088/'

def readFile(urlObj):
     path = 'download/' + urlObj.path
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
        furl = base.toStdUrl(DOMAIN + rurl)
        if '#' in furl:
             furl = furl[0 : furl.index('#')]
        obj = base.Urls.get_or_none(url = furl)
        if obj:
             return readFile(obj)
        if '?' not in furl:
             tx = f'[Not Find 1]: {furl}'
             logFile.write(tx + '\n')
             logFile.flush()
             return make_response(tx, 404)
        
        surl = furl[0 : furl.index('?')]
        qr = base.Urls.select().where(base.Urls.url == surl, base.Urls.type_ == 'static')
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
    app.run(host = '0.0.0.0', port = 5555, debug = True)