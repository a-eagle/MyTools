import create_dir, upload_file, restservice
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

def createFileOrInterface(js):
    for item in js:
        if 'files' in item:
            fs = item['files']
            for f in fs:
                upload_file.uploadOneFile(item['resName'], f)

        if 'dirs' in item:
            fs = item['dirs']
            for f in fs:
                upload_file.uploadOneDir(item['resName'], f)

        if item.get('interface', '') == 'auto':
            upload_file.uploadOneInterface(item['resName'])
            restservice.createNewRest(item)

if __name__ == '__main__':
    # 数据共享平台
    cookie = 'easyuiThemeName=2; JSESSIONID=83C0ACB88A16242E54547AFA95C5EBDC'
    create_dir.headers['Cookie'] = cookie
    upload_file.headers['Cookie'] = cookie
    # 我的共享平台
    restservice.headers['Cookie'] = 'JSESSIONID=6B3B085EE12FA961687D0187BDF16D68'
    restservice.headers['Auth'] = 'dgq4Ge9SuNO49CaHkt9IiE9hYoiWzUvt7a3weuxGvww='

    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\1. 超限数据统计\config.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\2. 工信局\config.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\5. 林业局\config.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\7. 农业农村局\config.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\8. 人社局\config.json') # ---------未上传
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\9. 市监局\config.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\11. 卫健委\config_接口.json') # ---------未上传
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\13. 档案馆\config.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\43. 长运\config_2.json')
    #js = loadConfig(r'C:\Users\GaoYan\Desktop\2023\共享数据\42. 一屏总览\config.json') # ---------未上传

    #createDir(js)
    #createFileOrInterface(js)