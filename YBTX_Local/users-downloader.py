import decrypt, json, requests

class UsersDownloader:
    def __init__(self, authorization, decryptKey) -> None:
        self.authorization = authorization
        self.decryptKey = decryptKey
        self.users = []
        self.usersGW = {}

    def loadAllUsers(self):
        for i in range(1, 6):
            self.loadPageUsers(i)

    def loadPageUsers(self, pageIdx):
        url = f'http://10.8.52.17:8088/ledger-be/system/user/page?searchDepId=486770361569336&includeChildrenDept=true&current={pageIdx}&size=100'
        headers = {'authorization': self.authorization, 'accept': "application/json, text/plain, */*"}
        resp = requests.post(url, headers = headers)
        js = json.loads(resp.text)
        if js['code'] != 200:
            print('Exception: UsersDownloader.loadData', js)
            return
        text = decrypt.decrypt(js['data'], self.decryptKey)
        js  = json.loads(text)
        self.parseUsers(js)

    def parseUsers(self, js):
        for r in js['records']:
            userId = r['id']
            obj = {'id': userId, 'nickname': r['nickname'], 'phone': r['phonenumber'], 'deptName' : r['depts'][0]['ancestorsName']}
            sname = obj['deptName'].replace('江西省>九江市>德安县>德安县', '')
            obj['deptName'] = sname
            self.users.append(obj)
            if userId in self.usersGW:
                fd = self.usersGW[userId]
                obj['gw'] = fd['gw']
        # results.sort(key = lambda k: k.encode('gbk'))

    def loadAllUsers_GangWei(self):
        url = f'http://10.8.52.17:8088/ledger-be/system/dept/getTaskDeptUser?deptId=486770361569336&isPublish=true&excludeSelfRegion=false&isTaskToHandover=false&bizType=elderly'
        headers = {'authorization': self.authorization, 'accept': "application/json, text/plain, */*"}
        resp = requests.get(url, headers = headers)
        js = json.loads(resp.text)
        if js['code'] != 200:
            print('Exception: UsersDownloader.loadAllUsers_GangWei', js)
            return
        text = decrypt.decrypt(js['data'], self.decryptKey)
        js  = json.loads(text)
        self.parseUserGangWei(js[0]['children'], {})
        gwData = self.usersGW
        pass

    def parseUserGangWei(self, children, depts):
        for c in children:
            if c['type'] == 'dept':
                depts[c['id']] = c['name']
            else:
                dp = depts.get(c['deptId'], '#')
                if '（' in dp: dp = dp[0 : dp.index('（')].replace('德安县', '')
                # id deptId  parentId userId type
                userName = c['name']
                gw = ''
                if '（' in userName:
                    b, e = userName.index('（'), userName.index('）')
                    gw = userName[b + 1 : e]
                    userName = userName[0 : b]
                self.usersGW[c['userId']] = {'deptName': dp, 'name': userName, 'gw': gw}
            if c['children']:
                self.parseUserGangWei(c['children'], depts)


ud = UsersDownloader('Bearer 0f9652e8ec1c4bc0bb3e8e55e2388b1d', '3152365a55727a3764524d3759304b5a')
#ud.loadAllUsers_GangWei()
ud.loadAllUsers()
f = open('users.txt', 'w')
for r in ud.users:
    dp = r['deptName']
    if dp[-1] in ('乡', '镇', '厂') or '>' in dp:
        print(r['id'], r['deptName'], r['nickname'], r['phone'], r.get('gw', ''), sep='\t', file = f)
f.close()

