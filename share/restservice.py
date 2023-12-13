import requests, json, hashlib, re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/json;charset=UTF-8',
    'Cookie': 'JSESSIONID=586E163742AB2C9CC90A42350E8E2974', # 需要设置
    'Auth': 'dgq4Ge9SuNO49CaHkt9IiCrP7S5hJFQwtDnjw3ESp4o='
}

def createTable(tabNameCN, tabNameEN):
    url = 'http://10.119.81.36:8059/RestService/rest/tableprototype'
    params = [{"_name_cn": tabNameCN, "_name": tabNameEN, "_type": 1, "_owner": tabNameEN, "_dept_id": "35"}]
    resp = requests.post(url, json=params, headers=headers)
    js = json.loads(resp.text)
    if js['status'] != 'OK':
        print('[REST:createTable] ', js)
        raise Exception('[REST:createTable] error:' + resp.text)

# colNameEN = _c01
def createColumn(tabNameEN, colNameCN, colNameEN):
    url = 'http://10.119.81.36:8059/RestService/rest/tableprototype'
    params = [{"_name_cn" : colNameCN, "_name" : colNameEN, "_type" : 2, "_data_type": "str","_max_len":"100", "_owner" : tabNameEN}]
    resp = requests.post(url, json=params, headers=headers)
    js = json.loads(resp.text)
    if js['status'] != 'OK':
        print('[REST:createColumn] ', js)
        raise Exception('[REST:createColumn] error')
    
def createColNameEN(idx):
    idx = f'c{idx + 1 :02d}'
    return idx

def createNewRest(resName, cols):
    bb = resName.encode(encoding='UTF-8')
    interfaceName = 'e' + hashlib.md5(bb).hexdigest()
    createTable(resName, interfaceName)
    cols = re.split('\s+|、', cols.strip())
    for idx, c in enumerate(cols):
        en = createColNameEN(idx)
        createColumn(interfaceName, c, en)
    print('REST.createNewRest success ', resName, interfaceName)

if __name__ == '__main__':
    #createNewRest("纺织AA", "项目名称、建设规模、总投资 项目资金来源 是否开工、是否竣工")
    pass