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
            "password":"04886b8e2d045b12f9f49236a0afa9dbb871c8e6db8b78ae76dd85ef817cbbb56a737f0af1ca596b99c95d125c8820663240bbcff52bbb8bf5989b9a510a78e5b51a9bb7525202ce4e7b6e0e401c5714950b152ecb2de8d985654942b0298e4a7e7e7393009ff73315b4d082",
            "code":captcha, 
            "uuid": uuid}
    resp = session.post('http://10.8.52.17:8088/ledger-be/login', json = params)
    txt = resp.content.decode('utf-8')
    js = json.loads(txt)
    data = decrypt.decrypt(js['data'], decryptKey)
    js = json.loads(data)
    authorization = 'Bearer ' + js['accessToken']
    return authorization

