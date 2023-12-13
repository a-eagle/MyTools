import requests, time, datetime, random, math, json, os, re, hashlib
from datetime import datetime
from urllib.parse import urlencode
from urllib.parse import quote

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',

    'Cookie': 'easyuiThemeName=2; JSESSIONID=7A31AF8F300AC12785D9735FAE3C72E2' # 需要设置
}

def generateUUID():
    d = time.time() * 1000
    cs = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
    m = '0123456789abcdef'
    rs = ''
    for s in cs:
        if s == 'x' or s == 'y':
            r = int(d + random.random() * 16) % 16 | 0
            d = math.floor(d / 16)
            if s == 'x':
                rs += m[r]
            else:
                rs += m[r & 0x3 | 0x8]
        elif s != '-':
            rs += s
    return rs

# return rdId
def findResourceDir(resName):
    url = 'http://10.97.10.42:8082/govportal/myRes/registerRes/registerFile!showAvailableDir.action'
    edata = {'rdCode': '', 'infoName': resName, 'page':'1', 'rows':'10'}
    edata = urlencode(edata)
    response = requests.post(url, data=edata, headers=headers)
    js = json.loads(response.text)
    #print('[findResourceDir]:', js)
    for row in js['rows']:
        if row['infoName'] == resName:
            return row['rdId']
    raise Exception('[findResource]未找到目录资源：' + resName)

def checkInfoName(rdId, fileName):
    url = 'http://10.97.10.42:8082/govportal/myRes/registerRes/registerFile!checkFileName.action'
    edata = {'rdId': rdId, 'resourceName': fileName}
    edata = urlencode(edata)
    response = requests.post(url, data=edata, headers=headers)
    print('[checkInfoName] ', response.text)
    if response.text.strip() == 'true':
        print('[checkInfoName] ok: ', fileName)
        return True
    print('[checkFileName]文件名错误: ', rdId, response.text)
    return False

def buildInfoName(fileName, magic = False):
    fileName = os.path.splitext(fileName)[0]
    bn = ''
    for n in fileName:
        if n == '.' or n == '-':
            n = '_'
        if (ord(n) >= 0x40E0 and ord(n) <= 0x9fa5) or (n >= '0' and n <= '9') or (n >= 'A' and n <= 'z') or (n >= 'a' and n <= 'z') or (n == '_'):
            bn += n
    if magic:
        bn += '_' + str(int(random.random() * 1000))
    return bn

# return fileUploadedId
def uploadFile(rdId, filePath):
    cts = { '.doc' : 'application/msword', 
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
            '.pdf': 'application/pdf', '.rar': 'application/vnd.rar', '.txt': 'text/plain', '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.zip': 'application/zip'}
    fileName = os.path.basename(filePath)
    fileName = fileName.replace('"', '')
    fileName = fileName.replace("'", '')
    fileName = fileName.replace(" ", '')
    fileExt = os.path.splitext(fileName)[1].lower()
    if fileExt not in cts:
        raise Exception('[uploadFile]不支持的文件类型：' + fileExt)
    
    url = 'http://10.97.10.42:8082/govportal/myRes/registerRes/uploadFile!upLoadFileTemp.action'
    fb = open(filePath, 'rb')
    files = {'upfile': (fileName, fb, cts[fileExt])}
    fileType = fileExt[1 : ]
    formData = {'fileSize': str(os.stat(filePath).st_size), 'rdId': rdId, 'fileId': generateUUID(), 'fileType': fileType, 'fileUploadCompleted': '0', 'displayFileName': fileName}
    hd = headers.copy()
    del hd['Content-Type']
    del hd['X-Requested-With']
    resp = requests.post(url, data = formData, files = files, headers = hd)
    fb.close()
    if not resp.ok:
        raise Exception('[uploadFile]上传出错：' + resp.reason)
    js = json.loads(resp.text)
    print('[uploadFile]: ', js)
    if js['code'] != 1:
        raise Exception('[uploadFile]上传出错：' + resp.text)
    rr = js['obj']['fileUploadedId'], formData['fileId'], formData['fileSize']
    print('[uploadFile] ', rr)
    return rr

# return json object
def getFileListByRdId(rdId):
    url = 'http://10.97.10.42:8082/govportal/myRes/registerRes/registerFile!getFileListByRdId.action'
    data = {'rdId' : rdId}
    resp = requests.post(url, data = data, headers = headers)
    js = json.loads(resp.text)
    print('[getFileListByRdId]', js)
    return js

def saveResource(rdId, resName, files):
    print('[saveResource] resName=', resName)
    url = 'http://10.97.10.42:8082/govportal/myRes/registerRes/registerFile!saveFile.action'
    files = seq(files)
    data = {'infoName': resName, 'rdId': rdId, 'colArr': files}
    data = urlencode(data)
    #print('[saveResource] econde-data=', data)
    hd = headers.copy()
    hd['Referer'] = 'http://10.97.10.42:8082/govportal/myRes/registerRes/registerFile!add.action'
    hd['Origin'] = 'http://10.97.10.42:8082'
    hd['Cache-Control'] = 'max-age=0'
    hd['Upgrade-Insecure-Requests'] = '1'
    hd['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
    hd['X-Requested-With'] = ''
    hd['Accept-Encoding'] = 'gzip, deflate'
    hd['Accept-Language'] = 'zh-CN,zh;q=0.9'

    resp = requests.post(url, data = data, headers = hd)
    js = json.loads(resp.text)
    print('[saveResource]: ', js)
    if js['code'] == '1':
        return True
    raise Exception('[saveResource]保存失败：' + resp.text)

def seq(data):
    rs = '['
    lv = []
    for d in data:
        item = '{'
        for k, v in d.items():
            if type(v) == str:
                item += f'"{k}":"{str(v)}",'
            elif type(v) == bool:
                item += f'"{k}":' + ('true' if v else 'false') + ','
            elif type(v) == int:
                item += f'"{k}":{str(v)},'
            else:
                raise Exception('[seq] error type')
        item = item[0 : -1] + '}'
        lv.append(item)
    xn = ','.join(lv)
    rs += xn + ']'
    return rs

def uploadOneFile(resName, filePath):
    rdId = findResourceDir(resName)
    fileName = os.path.basename(filePath)
    fileExt = os.path.splitext(fileName)[1].lower()
    magic = False
    while True:
        infoName = buildInfoName(fileName, magic)
        ck = checkInfoName(rdId, infoName)
        if ck:
            break
        magic = True
    print('[uploadOneFile] infoName: ', infoName, fileName)
    oldFileList = getFileListByRdId(rdId)
    uploadCompleteId, fileUploadedId, fileSize = uploadFile(rdId, filePath)
    
    nowFileInfo = {'resourceName': infoName, 'openType' : "0", 'description' : "", 'fileType' : fileExt[1:], 'fileSize' : fileSize, 
                   'displayFileName': fileName, 'uploadCompleteId': uploadCompleteId, 'uploadtime': datetime.now().strftime('%Y-%m-%d %H:%m:%S'), 
                   'fileUploadState' : "1", 'upType' : "1", 'isSign' : "", 'fileUpLoadId' : fileUploadedId, 'fileIndex' : 0, 
                   'uploadCompleteId1' : "", 'orderContent' : ""}
    print('[uploadOneFile] nowFileInfo=', nowFileInfo)
    files = oldFileList
    files.append(nowFileInfo)
    saveResource(rdId, resName, files)
    time.sleep(3)

def uploadOneDir(resName, dirPath):
    files = os.listdir(dirPath)
    for f in files:
        fn = os.path.join(dirPath, f)
        uploadOneFile(resName, fn)
        print('\n')

def uploadOneInterface(resName):
    rdId = findResourceDir(resName)
    interfaceResName = '查询' + resName
    bb = resName.encode(encoding='UTF-8')
    interfaceName = 'e' + hashlib.md5(bb).hexdigest()
    print('[uploadOneInterface]', resName, interfaceName)
    # 检查service name
    url = 'http://10.97.10.42:8082/govportal/myRes/registerRes/registerSrv!checkSrvName.action'
    params = {'rdId': rdId, 'resourceName': interfaceResName, 'oldResourceName': ''}
    params = urlencode(params)
    resp = requests.post(url, data = params, headers = headers)
    if resp.text != 'true':
        raise Exception('[uploadOneInterface]: service name error, ' + resp.text)
    
    url = 'http://10.97.10.42:8082/govportal/myRes/registerRes/registerSrv!saveSrv.action'
    params = {'infoName': resName, 'rdId': rdId, 'resOpenScore': '', 'resourceName': interfaceResName, 'interfaceType': 'REST', 'openType': '0', 
            'serviceUrl': 'http://10.119.81.36:8058/RestService/rest/api/', 'procotol': '1', 'serviceVersion': '1.0', 'authOrizattionMode': '2',
            'authType': '', 'authUserName': '', 'authPassword': '', 'algorithmName': '', 'callFrequency': '50', 'timeOut' : '', 'serviceUserTimes': '',
            'suppotUnit': '德安信息办', 'supportUnitContact': '高炎', 'supportUnitPhone': '18879269788', 'description' : '', 'serviceOriginFile': '',
            'uploadCompleteId': '', 'upfileIsCompleted': '', 'orderContent': '', 'originFile': '', 'uploadCompleteId1': '', 'upfileIsCompleted1': '', 
            'listVoFunc[0].funcName': interfaceName, 'listVoFunc[0].requestMethod': 'GET', 'listVoFunc[0].returnType': 'JSON', 'listVoFunc[0].desc': '',
            'listVoFunc[0].requestExample': '', 'listVoFunc[0].responseExampleSucc': '', 'listVoFunc[0].responseExampleFail': ''}
    params = urlencode(params)
    resp = requests.post(url, data = params, headers = headers)
    js = json.loads(resp.text)
    print('[uploadOneInterface] ', resp.text)
    if js['code'] != '1':
        raise Exception('[uploadOneInterface] error: ' + resp.text)

if __name__ == '__main__':
    headers['Cookie'] = 'easyuiThemeName=2; JSESSIONID=2901D5569ECDFE93B7A066688B2AE5DA'

    # 上传文件
    BASE_FILE_PATH = 'C:\\Users\\GaoYan\\Desktop\\2023\\共享\\数据\\'
    #uploadOneDir('德安县一般救助', BASE_FILE_PATH + '孙法俊\\2022\\城镇低保资金')

    #uploadOneFile('德安县纺织服装产业重点项目', r'C:\Users\\GaoYan\Desktop\2023\共享数据\工信局\补充材料\纺织服装四图五清单\2022年德安县纺织服装产业重点项目.xls')

    #uploadOneInterface('德安县纺织服装产业重点项目')