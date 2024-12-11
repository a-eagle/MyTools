import traceback, json, os, requests, hashlib, sys
from flask import Flask, request, jsonify
from flask_cors import CORS   # pip install -U flask-cors 
import peewee as pw
import base

app = Flask(__name__, instance_relative_config = True) # template_folder='ui/templates'  , static_folder='download'
cors = CORS(app)

app.config.from_mapping(
    SECRET_KEY = 'xielaic4cE@xef*',
)

logFile = open('download/d-log.txt', 'a+')


# POST {method: GET|POST, url: str, type = 'static | xhr | frame', headers: object, body?:any }
@app.route("/download-file", methods = ['POST'])
def downloadFile():
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
        os.makedirs('download/' + dirs, exist_ok = True)
        print('[File] ==>', method, url, file = logFile)
        print('       -->', newPath, file = logFile)
        logFile.flush()
        if method == 'GET':
            resp = requests.get(base.toStdUrl(url), headers = base.formatHeaders(data['headers']), data = data['body'])
        elif method == 'POST':
            resp = requests.post(base.toStdUrl(url), headers = base.formatHeaders(data['headers']), data = data['body'])
        if resp.status_code != 200:
            print('Net Error: ', resp, url)
            return '{"code": 2, "msg": "Net Error, status code = ' + str(resp.status_code) + '"}'
        f = open('download/' + newPath, 'wb')
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
    except Exception as e:
        traceback.print_exc()
        logFile.write(f'Exception: {str(e)}\n')
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
        os.makedirs('download/' + dirs, exist_ok = True)
        print('[XHR] ==>', method, url, file = logFile)
        print('      -->', newPath, file = logFile)
        logFile.flush()
        if type(data['response']) == str:
            encoding = 'utf-8'
            f = open('download/' + newPath, 'w', encoding = encoding)
        else:
            encoding = ''
            f = open('download/' + newPath, 'wb')
        f.write(data['response'])
        f.close()
        base.saveUrl(method, url, data['type'], data['headers'], data['body'], newPath, encoding, data['contentType'], data['respHeaders'])
        return '{"code": 0, "msg": "Success"}'
    except Exception as e:
        traceback.print_exc()
        logFile.write(f'Exception: {str(e)}\n')
        logFile.flush()
        return '{"code": 2, "msg": "' + str(e) + '"}'

if __name__ == '__main__':
    print('download-server -port xxxx')
    port = 5585
    argv = sys.argv[1 : ]
    if len(argv) >= 2 and argv[0] == '-port':
        port = int(argv[1])
    app.run(host = '0.0.0.0', port = port, debug = True)