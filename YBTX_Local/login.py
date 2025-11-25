import peewee as pw, json, requests, datetime, time, urllib.parse, os
import decrypt

def login(decryptKey):
    session = requests.session()
    resp = session.get('http://10.8.52.17:8088/ledger-be/system/captcha/get-image')
    txt = resp.content.decode('utf-8')
    js = json.loads(txt)
    img = js['data']['img']
    uuid = js['data']['uuid']
    img = 'data:image/gif;base64,' + img
    params = urllib.parse.urlencode({'img': img})
    resp = requests.get('https://api.vitphp.cn/Yzcode/?' + params)
    txt = resp.content.decode('utf-8')
    js = json.loads(txt)
    captcha = js['captcha']
    params = {"username":"DeAn003",
            "password":"04b812153721cc467260053ddc94228c65784960e20a0d378313db99c02668e0ca4376c606a1d497feed42fc3a21895f3457bc24e03a3a03d58e955148c8c39e0ef48eae37fcd38a5d39d714edfe2965fd4c6302775da1815ead363eae3caebac268bcd2b72c4c93305f97",
            "code":captcha, 
            "uuid": uuid}
    resp = session.post('http://10.8.52.17:8088/ledger-be/login', json = params)
    txt = resp.content.decode('utf-8')
    js = json.loads(txt)
    data = decrypt.decrypt(js['data'], decryptKey)
    js = json.loads(data)
    authorization = 'Bearer ' + js['accessToken']
    return authorization

