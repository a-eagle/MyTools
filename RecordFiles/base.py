import traceback, json, os, requests, hashlib
import peewee as pw

PROJECT_DIR_NAME = 'RecordFiles'
PROEJCT_ABS_DIR = __file__[0 : __file__.index(PROJECT_DIR_NAME) + len(PROJECT_DIR_NAME)].replace('\\', '/')
DOWNLOAD_DIR = PROEJCT_ABS_DIR + '/download/'
if not os.path.exists(DOWNLOAD_DIR):
    os.mkdir(DOWNLOAD_DIR)

db = pw.SqliteDatabase(DOWNLOAD_DIR + 'cache.db')
class Urls(pw.Model):
    method_ = pw.CharField(null = True) # GET | POST
    url = pw.CharField()
    ftype = pw.CharField() # static | xhr | frame
    headers = pw.CharField(null = True)
    body = pw.CharField(null = True)
    path = pw.CharField() # disk file path
    encoding = pw.CharField(null = True) # response encoding
    contentType = pw.CharField(null = True) # response contentType
    respHeaders = pw.CharField(null = True) # response headers(custon headers)
    class Meta:
        database = db

db.create_tables([Urls])

def formatHeaders(headers):
    if not headers:
        return None
    if isinstance(headers, str):
        headers = json.loads(headers)
    if isinstance(headers, dict):
        return headers
    if not isinstance(headers, list):
        rs = {}
        for h in headers:
            rs[h['name']] = h['value']
        return rs
    return None

def md5(params):
    m = hashlib.md5()
    m.update(params)
    params = m.hexdigest()
    return params

def toPathUrl(url, ftype):
    if '://' in url:
        url = url[url.index('://') + 3 : ]
    if '#' in url:
        url = url[0 : url.index('#')]
    if ftype == 'static' and '?' in url:
        url = url[0 : url.index('?')]
    return url

def toStdUrl(url):
    if '#' in url:
        url = url[0 : url.index('#')]
    return url

def urlToPaths(url, ftype, body : bytes):
    url = toPathUrl(url, ftype)
    params = ''
    if '?' in url:
        i = url.index('?')
        params : str = url[i + 1 : ]
        params = md5(params.encode('utf-8'))
        url = url[0 : i]
    paths = url.split('/') or []
    if len(url) == 1:
        paths.append('.home')
    elif not paths[-1]:
        paths[-1] = '.home'
    if params and ftype != 'static':
        paths[-1] = paths[-1] + '!' + params
    if body and ftype != 'static':
        paths[-1] = paths[-1] + '#' + md5(body)

    deamon = paths[0]
    paths[0] = deamon.replace(':', "_")
    return paths

def saveUrl(method_, url, ftype, headers, body, path, encoding, contentType, respHeaders):
    if '#' in url:
        url = url[0 : url.index('#')]
    if ftype == 'static' and '?' in url:
        url = url[0 : url.index('?')]
    obj = Urls.get_or_none(path = path)
    encoding = encoding or ''
    contentType = contentType or ''
    if obj:
        obj.method_ = method_
        obj.url = url
        obj.ftype = ftype
        obj.headers = headers
        obj.body = body
        obj.encoding = encoding
        obj.contentType = contentType
        obj.respHeaders = respHeaders
        obj.save()
    else:
        Urls.create(url = url, method_ = method_, ftype = ftype, headers = headers, body = body, path = path, 
                    encoding = encoding, contentType = contentType, respHeaders = respHeaders)