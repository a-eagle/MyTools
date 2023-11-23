import create_dir, upload_file
import os, json

def loadConfig(filePath):
    filePath = os.path.abspath(filePath)
    curDir = os.path.dirname(filePath)
    print(curDir)

    ff = open(filePath, 'r', encoding='utf-8')
    s = ff.read(4096)
    print(s)
    ff.close()
    js = json.loads(s)
    for item in js:
        if 'files' in item:
            for i, f in enumerate(item['files']):
                item['files'][i] = os.path.join(curDir, f)
        if 'dirs' in item:
            for i, f in enumerate(item['dirs']):
                item['dirs'][i] = os.path.join(curDir, f)
    print(js)
    return js

def createDir(js):
    for item in js:
        b = ('exists' not in item) or (item['exists'] == False)
        if b and item['cols']:
            create_dir.createResDir(item['resName'], item['cols'])

def createFile(js):
    for item in js:
        if 'files' in item:
            fs = item['files']
            for f in fs:
                upload_file.uploadOneFile(item['resName'], f)

        if 'dirs' in item:
            fs = item['dirs']
            for f in fs:
                upload_file.uploadOneDir(item['resName'], f)

        if ('interface' in item) and item['interface']:
            upload_file.uploadOneInterface(item['resName'], item['interface'])

if __name__ == '__main__':
    cookie = 'easyuiThemeName=2; JSESSIONID=2901D5569ECDFE93B7A066688B2AE5DA'
    create_dir.headers['Cookie'] = cookie
    upload_file.headers['Cookie'] = cookie

    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\1. 超限数据统计\config.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\2. 工信局\config.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\5. 林业局\config.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\9. 市监局\config.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\13. 档案馆\config.json')

    #createDir(js)
    #createFile(js)