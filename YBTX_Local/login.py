import peewee as pw, json, requests, datetime, time, urllib.parse, os, base64
import decrypt
from PIL import Image
import pytesseract, cv2
import ddddocr # pip install ddddocr

FILE_NAME = 'YZM.png'

authorization = None

def loadYzm(session):
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
    return captcha, uuid

def loadYzm2(session):
    resp = session.get('http://10.8.52.17:8088/ledger-be/system/captcha/get-image')
    txt = resp.content.decode('utf-8')
    js = json.loads(txt)
    img64 = js['data']['img']
    uuid = js['data']['uuid']
    raw = base64.b64decode(img64)
    f = open(FILE_NAME, 'wb')
    f.write(raw)
    f.close()
    # captcha = ocr(FILE_NAME)
#     os.remove(FILE_NAME)
    return uuid

def login(decryptKey = decrypt.DECRYPT_KEY):
    global authorization
    session = requests.session()
    uuid = loadYzm2(session)
    captcha = ddocr(FILE_NAME)
    if not captcha or len(captcha) != 4:
        imgf = Image.open(FILE_NAME)
        imgf.show()
        captcha = input('Input Yzm:')
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

def getAuthorization():
    global authorization
    if not authorization:
        login()
    return authorization

def ocr(path):
    # img = Image.open(path)
    src = cv2.imread(path)
    dst = cv2.pyrMeanShiftFiltering(src, sp = 30, sr = 50)
    gray = cv2.cvtColor(dst, cv2.COLOR_RGB2GRAY)
    ret, binary = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
    # erode = cv2.erode(binary, None, iterations = 2)
    # dilate = cv2.dilate(erode, None, iterations = 1)
    # cv2.bitwise_not(binary, binary)
    img = Image.fromarray(binary)
    img.show()
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    cfg = f'-c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    rs = pytesseract.image_to_string(img, config = cfg)
    print('rs=', rs)
    return rs.strip()

_docr = ddddocr.DdddOcr()
def ddocr(path):
    f = open(path, "rb")
    image = f.read()
    f.close()
    result = _docr.classification(image)
    # print('result=', result)
    return result or ''

if __name__ == '__main__':
    loadYzm2(requests.session())
    print(ddocr(FILE_NAME))
