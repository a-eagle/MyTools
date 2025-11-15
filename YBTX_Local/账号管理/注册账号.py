import peewee as pw, json, requests, datetime, time, urllib.parse, os, re, sys

print(__file__)
sys.path.append(__file__[0 : __file__.upper().index('账号管理')])
import decrypt, login

decryptKey = '3152365a55727a3764524d3759304b5a'
authorization = login.login(decryptKey)
# authorization = 'Bearer 5b0a8ad5245642f0a300b1426fc74d6e'
print(authorization)

headers = {'authorization': authorization, 'accept': "application/json, text/plain, */*"}


def listDeptUsers(deptId, deptName = None):
    url = f'http://10.8.52.17:8088/ledger-be/system/user/page?searchDepId={deptId}&includeChildrenDept=true&current=1&size=100'
    resp = requests.post(url, headers = headers)
    text = resp.text
    js = json.loads(text)
    if js['code'] != 200:
        print('[listAllUsers] Fail: ', resp.text)
        return
    data = decrypt.decrypt(js['data'], decryptKey)
    js = json.loads(data)
    rs = js['records']
    # print(rs)
    users = {}
    for it in rs:
        users[it['nickname']] = it['username']
    print(deptName, 'server users=', users)
    return users

def createDeptUser(deptId, nickName, phone):
    if not nickName or not phone:
        return False
    phone = phone.replace('+86-', '')
    reqs = {"username": phone, "nickname": nickName,
            "phonenumber": phone,"status":"0","postIds":[],"roleIds":[58],"deptIds":[deptId]
            }
    resp = requests.post('http://10.8.52.17:8088/ledger-be/system/user/create', json = reqs, headers = headers)
    text = resp.text
    js = json.loads(text)
    if js['code'] != 200:
        print('[createDeptUser] Fail: ', resp.text)
        return False
    userId = decrypt.decrypt(js['data'], decryptKey)
    return userId

def loadDepts():
    resp = requests.get('http://10.8.52.17:8088/ledger-be/system/dept/list-current?id=486770361569336', headers = headers)
    text = resp.text
    js = json.loads(text)
    if js['code'] != 200:
        print('[loadDepts] Fail: ', resp.text)
        return None
    return js['data']

def findDeptId(deptName, depts):
    for d in depts:
        if deptName in d['deptName']:
            return d['id']
    return None

def loadLocalUsers():
    f = open('账号管理/账号.data', 'r', encoding = 'utf-8')
    lines = f.readlines()
    f.close()
    rs = []
    for ln in lines:
        ln = ln.strip()
        items = re.split('\s+|、', ln)
        # check user name
        for i in range(1, len(items)):
            if len(items[i]) > 3:
                raise Exception('User name invalid: ', items)
        rs.append({'dept': items[0], 'users': items[1 : ]})
    return rs

def compareLocalServerUsers(localUsers, depts):
    noExistsUsers = []
    for lu in localUsers:
        no = set()
        deptName = lu['dept']
        us = lu['users']
        deptId = findDeptId(deptName, depts)
        if not deptId:
            raise Exception('Not find deptId:', deptName)
        existsUsers = listDeptUsers(deptId, deptName)
        for u in us:
            if u not in existsUsers:
                no.add(u)
        if no:
            users = {}
            for u in no: users[u] = ''
            noExistsUsers.append({'deptName': deptName, 'deptId': deptId, 'users': users})
    return noExistsUsers

# 更新赣政通
def updateGztUsers(userIds : list):
    resp = requests.post('http://10.8.52.17:8088/ledger-be/system/user/updateGztAccount', headers = headers, json = userIds)
    text = resp.text
    js = json.loads(text)
    if js['code'] != 200:
        print('[updateGztUsers] Fail: ', resp.text)
        return False
    return js['success']

def buildNeedAddUsers():
    localUsers = loadLocalUsers()
    depts = loadDepts()
    needAddUsers = compareLocalServerUsers(localUsers, depts)
    f = open('账号管理/账号_新.json', 'w', encoding = 'utf-8')
    f.write('[\n')
    for idx, u in enumerate(needAddUsers):
        rs = json.dumps(u, ensure_ascii = False)
        f.write(rs)
        if idx != len(needAddUsers) - 1:
            f.write(',\n')
        else:
            f.write('\n')
    f.write(']')
    f.close()

def createLocalUsers():
    f = open('账号管理/账号_新.json', 'r', encoding = 'utf-8')
    txt = f.read()
    f.close()
    js = json.loads(txt)
    
    for item in js:
        print('[createLocalUsers] ', item['deptName'])
        users = item['users']
        for k in users:
            if not users[k]:
                print('    ', k, ' has no phone')
                break
            ok = createDeptUser(item['deptId'], k, users[k])
            print('   创建用户：', k, '-->',  ok, end = ' ')
            if ok:
                userId = ok
                ok = updateGztUsers([userId])
                print(' 更新赣政通 -> ', ok, end = '')
            print('')

if __name__ == '__main__':
    STEP = 2

    if STEP == 1:
        #根据 账号.data 生成需要创建的用户 -> 账号_新.json
        buildNeedAddUsers()

    if STEP == 2:
        # 根据账号_新.json， 创建用户（需要先填写电话号码）
        createLocalUsers()
        
    pass

    

