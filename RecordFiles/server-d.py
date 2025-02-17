import traceback, json, os, requests
import urllib.parse
from flask import Flask, request
from flask_cors import CORS   # pip install -U flask-cors 
import base

app = Flask(__name__, instance_relative_config = True) # template_folder='ui/templates'  , static_folder='download'
cors = CORS(app)
cookies = {} # host: cookie

app.config.from_mapping(
    SECRET_KEY = 'xielaic4cE@xef*',
)

logFile = open(base.DOWNLOAD_DIR + 'd-log.txt', 'a+')

@app.route("/set-cookie", methods = ['POST'])
def setCookie():
    try:
        if not request.data:
            return '{"code": 1, "msg": "No data"}'
        data = request.data.decode('utf-8')
        data = json.loads(data)
        cookies.update(data)
        logFile.write(f'[Cookie] {json.dumps(data)}\n')
        logFile.flush()
        return '{"code": 0, "msg": "success"}'
    except Exception as e:
        traceback.print_exc()
        logFile.write(f'Exception: set-cookie {str(e)}\n')
        logFile.flush()
        return '{"code": 2, "msg": "' + str(e) + '"}'

# POST {method: GET|POST, url: str, type = 'static | xhr | frame', headers: object, body?:any }
@app.route("/download-file", methods = ['POST'])
def downloadFile():
    try:
        if not request.data:
            return '{"code": 1, "msg": "No data"}'
        data = request.data.decode('utf-8')
        data = json.loads(data)
        url = data['url']
        return saveOneFile(url, data)
    except Exception as e:
        traceback.print_exc()
        logFile.write(f'       Exception: downloadFile [{url}] {str(e)}\n')
        logFile.flush()
        return '{"code": 2, "msg": "' + str(e) + '"}'

# POST {method: GET|POST, url: str, type = 'xhr', headers: object, body?:any , response}
@app.route("/save-xhr", methods = ['POST'])
def saveXhr():
    try:
        if not request.data:
            return '{"code": 1, "msg": "No data"}'
        data = request.data.decode('utf-8')
        data = json.loads(data)
        url = data['url']
        method = data['method'].upper()
        bbody = data['body'] or ''
        if bbody: bbody = bbody.encode('utf-8')
        paths = base.urlToPaths(url, data['type'], bbody)
        newPath = '/'.join(paths)
        dirs = '/'.join(paths[0 : -1])
        os.makedirs(base.DOWNLOAD_DIR + dirs, exist_ok = True)
        print('[XHR] ==>', method, url, file = logFile)
        print('      -->', newPath, file = logFile)
        logFile.flush()
        if type(data['response']) == str:
            encoding = 'utf-8'
            f = open(base.DOWNLOAD_DIR + newPath, 'w', encoding = encoding)
        else:
            encoding = ''
            f = open(base.DOWNLOAD_DIR + newPath, 'wb')
        f.write(data['response'])
        f.close()
        base.saveUrl(method, url, data['type'], data['headers'], data['body'], newPath, encoding, data['contentType'], data['respHeaders'])
        return '{"code": 0, "msg": "Success"}'
    except Exception as e:
        traceback.print_exc()
        logFile.write(f'Exception: {str(e)}\n')
        logFile.flush()
        return '{"code": 2, "msg": "' + str(e) + '"}'

def saveOneFile(url, data):
    method = data['method'].upper()
    bbody = data['body'] or ''
    if bbody: bbody = bbody.encode('utf-8')
    paths = base.urlToPaths(url, data['type'], bbody)
    newPath = '/'.join(paths)
    dirs = '/'.join(paths[0 : -1])
    dd = base.DOWNLOAD_DIR + dirs
    if not os.path.exists(dd):
        os.makedirs(dd, exist_ok = True)
    print('[File] ==>', method, url, file = logFile)
    print('       -->', newPath, file = logFile)
    logFile.flush()
    hds = base.formatHeaders(data['headers'])
    _, host, *_ = urllib.parse.urlparse(url)
    global cookies
    if host in cookies:
        if hds is None: hds = {}
        if 'Cookie' not in hds:
            hds['Cookie'] = cookies[host]
    if method == 'GET':
        resp = requests.get(base.toStdUrl(url), headers = hds, data = data['body'])
    elif method == 'POST':
        resp = requests.post(base.toStdUrl(url), headers = hds, data = data['body'])
    if resp.status_code != 200:
        print('Net Error: ', resp, url)
        print('Net Error:', resp, newPath, file = logFile)
        return '{"code": 2, "msg": "Net Error, status code = ' + str(resp.status_code) + '"}'
    f = open(base.DOWNLOAD_DIR + newPath, 'wb')
    f.write(resp.content)
    f.close()
    cntType = resp.headers.get('Content-Type', '') # encoding
    encoding = resp.encoding or resp.apparent_encoding or ''
    rh = {}
    for k in resp.headers:
        rh[k] = resp.headers[k]
    rh = json.dumps(rh)
    base.saveUrl(method, url, data['type'], data['headers'], data['body'], newPath, encoding, cntType, rh)
    return '{"code": 0, "msg": "Success"}'
    
# POST {method: GET, urls: str, type = 'static', headers: object, body?:any }
@app.route("/download-file-s", methods = ['POST'])
def downloadFile_s():
    try:
        if not request.data:
            return '{"code": 1, "msg": "No data"}'
        data = request.data.decode('utf-8')
        data = json.loads(data)
        urls = data['urls']
        logFile.write(f'[File-s] {urls}\n')
        logFile.flush()
        if not urls:
            return '{"code": 1, "msg": "No urls data"}'
        for url in urls:
            try:
                saveOneFile(url, data)
            except Exception as e:
                traceback.print_exc()
                logFile.write(f'       Exception: load one file [{url}], {str(e)}\n')
                logFile.flush()
        return '{"code": 0, "msg": "Success"}'
    except Exception as e:
        traceback.print_exc()
        logFile.write(f'Exception: {str(e)}\n')
        logFile.flush()
        return '{"code": 2, "msg": "' + str(e) + '"}'


if __name__ == '__main__':
    PORT = 5585 # 需同步修改extentinos/config.js
    print('Default local port = ', PORT)
    #px = input('Input local port, if no changed, press enter: ').strip()
    #if px: PORT = int(px)
    app.run(host = '0.0.0.0', port = PORT, debug = True, use_reloader = False) # use_reloader  禁止启动2次