import peewee as pw, json, requests, datetime, time, urllib.parse, os, re, sys

print(__file__)
sys.path.append(__file__[0 : __file__.upper().index('账号管理')])
import decrypt, login, 注册账号

def buildUserAdmin():
    f = open('账号管理/temp.data', 'r', encoding = 'utf-8')
    lns = f.readlines()
    f.close()
    rs = []
    for ln in lns:
        items = ln.strip().split('\t')
        dept = items[0]
        if len(items) == 2:
            lxr = items[1]
            info = {'dept': dept, 'user': lxr, 'role': '部门联系人'}
            rs.append(info)
            print(info, ',')
        elif len(items) == 3:
            lxr, gly = items[1], items[2]
            if lxr == gly:
                info = {'dept': dept, 'user': gly, 'role': '部门联系人，部门管理员'}
                rs.append(info)
                print(info, ',')
            else:
                info = {'dept': dept, 'user': lxr, 'role': '部门联系人'}
                rs.append(info)
                print(info, ',')
                info = {'dept': dept, 'user': gly, 'role': '部门管理员'}
                rs.append(info)
                print(info, ',')

# temp.json --> temp-2.json
def decryptFile():
    f = open('账号管理/temp.json', 'r', encoding = 'utf-8')
    txt = f.read()
    f.close()
    a = json.loads(txt)
    data = decrypt.decrypt(a['data'])
    data = json.loads(data)
    # records = data['records']
    txt = json.dumps(data, ensure_ascii = False)
    f = open('账号管理/temp-2.json', 'w', encoding = 'utf-8')
    f.write(txt)
    f.close()
    pass

def searchUser(deptName, nickName):
    s = urllib.parse.quote(nickName)
    resp = requests.post(f'http://10.8.52.17:8088/ledger-be/system/user/page?username={s}&includeChildrenDept=true&current=1&size=15', headers = 注册账号.headers)
    js = resp.json()
    txt = decrypt.decrypt(js['data'])
    js = json.loads(txt)
    rs = js['records']
    fu = None
    for user in rs:
        if user['nickname'] != nickName:
            continue
        for dept in user['depts']:
            if (dept['deptName'] in deptName) or (deptName in dept['deptName']):
                fu = user
                break
    return fu

def loadUser(userId):
    resp = requests.get(f'http://10.8.52.17:8088/ledger-be/system/user/{userId}', headers = 注册账号.headers)
    rs = resp.json()
    dx = rs['data']
    txt = decrypt.decrypt(dx)
    js = json.loads(txt)
    user = js['user']
    user['roleIds'] = js['roleIds']
    user['postIds'] = js['postIds']
    return user

# userPosition
def updateUser(user):
    resp = requests.post(f'http://10.8.52.17:8088/ledger-be/system/user/update', headers = 注册账号.headers, json = user)
    js = resp.json()
    if js['code'] != 200 or js['success'] != True:
        raise Exception('[updateUser] fail, ', user['nickname'], user['username'], '==>',  js)
    return True

ADMIN_ROLE = 702745531766359 # 管理员

def addRoleAdmin(user, add : bool):
    roleIds : list = user['roleIds']
    findIdx = -1
    for idx, r in enumerate(roleIds):
        if str(r) == str(ADMIN_ROLE):
            findIdx = idx
    if add and findIdx < 0:
        roleIds.append(ADMIN_ROLE)
        return True
    if not add and findIdx >= 0:
        roleIds.pop(findIdx)
        return True
    return False

# 添加岗位
# return False: 没有变化
# return str: 更新后的岗位
def addGangWei(srcGangWei, newGangWei):
    srcGangWei = (srcGangWei or '').strip()
    newGangWei = (newGangWei or '').strip()
    if not newGangWei:
        return False
    if newGangWei in srcGangWei:
        return False
    if srcGangWei:
        srcGangWei += '，' + newGangWei
    else:
        srcGangWei = newGangWei
    return srcGangWei

def addGangWeiList(srcGangWei, newGangWeiList : list):
    gw = srcGangWei
    for n in newGangWeiList:
        tmp = addGangWei(gw, n)
        if type(tmp) == str:
            gw = tmp
    if srcGangWei == gw:
        return False
    return gw

def isEmpty(strs):
    return strs == None or strs.strip() == ''

def isNotEmpty(strs):
    return not isEmpty(strs)

# isAdmin 是否是管理员, None: 不更新角色
# setGangWei 设置岗位, None: 不更新岗位
# _addGangWei str | list 添加岗位
# return False: 没有更改  True: 更改成功
def changeUser(deptName, userName, isAdmin = None, setGangWei = None, _addGangWei = None):
    print('[changeUser] ', deptName, userName, '==>', f'isAdmin=[{isAdmin}]  setGangWei=[{setGangWei}]  _addGangWei=[{_addGangWei}]')
    if isAdmin == None and setGangWei == None and _addGangWei == None:
        return False
    user = searchUser(deptName, userName)
    if not user:
        print('[updateUser] not find user:', deptName, userName)
        raise Exception('[changeUser] not find user')
    user2 = loadUser(user['id'])
    roleChanged = False
    gwChanged = False
    oldGW = user2['userPosition']
    if type(isAdmin) == bool:
        roleChanged = addRoleAdmin(user2, isAdmin)
        if roleChanged:
            print(f'    Set AdminRole:', isAdmin)
    if setGangWei:
        if not (isEmpty(user2['userPosition']) and isEmpty(setGangWei)) and (user2['userPosition'] != setGangWei):
            gwChanged =  True
            user2['userPosition'] = setGangWei
    elif _addGangWei:
        if type(_addGangWei) == list:
            newGW = addGangWeiList(user2['userPosition'], _addGangWei)
        else:
            newGW = addGangWei(user2['userPosition'], _addGangWei)
        user2['userPosition'] = newGW
        gwChanged = newGW != False
    if not roleChanged and not gwChanged:
        print('    Not changed')
        return False # no need change
    print(f'    Old GangWei=[{oldGW}]   New GangWei=[{user2["userPosition"]}]')
    ok = updateUser(user2)
    return ok

def loadLocalUsersGangWeiFile():
    f = open('账号管理/temp.data', 'r', encoding = 'utf-8')
    lns = f.readlines()
    f.close()
    rs = []
    for ln in lns:
        items = re.split(r'\t+', ln.strip())
        if len(items) < 3:
            continue
        if len(items) != 3:
            raise Exception('Error ', items)
        gw = re.split('\s+|、', items[2].strip())
        gw = [d.strip() for d in gw]
        u = {'dept': items[0], 'name': items[1], 'gw': gw}
        print(u)
        rs.append(u)
    return rs

def changeLocalUserGangWei():
    users = loadLocalUsersGangWeiFile()
    for idx, u in enumerate(users):
        print(idx, '--->', u)
        # if idx < 11: continue
        changeUser(u['dept'], u['name'], _addGangWei = u['gw'])
        time.sleep(2)

if __name__ == '__main__':
    # ok = changeUser('司法局', '林君', isAdmin = None, setGangWei = '公共法律服务管理股工作人员')
    changeLocalUserGangWei()
    pass