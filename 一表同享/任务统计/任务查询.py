import peewee as pw, json, requests
import decrypt

db = pw.SqliteDatabase('tasks.db')

class Task(pw.Model):
    taskId = pw.CharField()
    deptName = pw.CharField()
    nickName = pw.CharField() #创建者
    title = pw.CharField()
    statusDesc = pw.CharField()
    cnt = pw.CharField()
    progress = pw.CharField(null = True)

    class Meta:
        database = db

db.create_tables([Task])

class TaskMgr:
    def __init__(self, authorization) -> None:
        self.authorization = authorization

    def _saveTask(self, task):
        qr = Task.select().where(Task.taskId == str(task['id']))
        obj = None
        for q in qr:
            obj = q
            break
        if not obj:
            obj = Task()
        obj.taskId = str(task['id'])
        obj.deptName = task['deptName']
        obj.nickName = task['nickname']
        obj.title = task['title']
        obj.statusDesc = task['statusDesc']
        obj.cnt = json.dumps(task, ensure_ascii = False)
        obj.save()

    def loadTasks(self):
        print('[loadTasks] begin...')
        url = 'http://10.8.52.17:8088/ledger-be/task/manage/operationPageList?current=1&size=100'
        headers = {'authorization': self.authorization, 'accept': "application/json, text/plain, */*"}
        resp = requests.get(url, headers = headers)
        js = json.loads(resp.text)
        if js['code'] != 200:
            print('[loadTasks] Fail: ', resp.text)
            return
        data = decrypt.decrypt(js['data'])
        js = json.loads(data)
        for it in js['records']:
            if it['statusDesc'] == '填报中' or it['statusDesc'] == '已完成':
                self._saveTask(it)
        print('[loadTasks] end')

    def loadProgress(self):
        qr = Task.select()
        for it in qr:
            self.loadTaskProgress(it)

    def loadTaskProgress(self, task):
        print('[loadTaskProgress] ...', task.taskId, task.title)
        url = f'http://10.8.52.17:8088/ledger-be/task/manage/getTaskFillSituation?taskId={task.taskId}'
        headers = {'authorization': self.authorization, 'accept': "application/json, text/plain, */*"}
        resp = requests.get(url, headers = headers)
        js = json.loads(resp.text)
        if js['code'] != 200:
            print('[loadTaskProgress] Fail: ', resp.text)
            return
        data = decrypt.decrypt(js['data'])
        js = json.loads(data)
        self._saveTaskProgress(js)
        print('[loadTaskProgress] end')

    def _saveTaskProgress(self, js):
        if not js:
            return
        taskId = js[0]['taskId']
        qr = Task.select().where(Task.taskId == taskId)
        obj = None
        for q in qr:
            obj = q
            break
        if not obj:
            print('[saveTaskProgress] No Task', taskId)
        obj.progress = json.dumps(js, ensure_ascii = False)
        obj.save()

class PraseProgress:
    def __init__(self) -> None:
        self.tasks = []
        self.results = None

    def simpleDeptName(self, deptName : str):
        if '>' not in deptName:
            return deptName
        idx1 = deptName.index('（')
        idx2 = deptName.index('）')
        idx3 = deptName.index('>')
        p1 = deptName[idx1 + 1 : idx3]
        p2 = deptName[idx3 + 1 : idx2]
        if p1 == '德安县':
            return p2
        return p1 + '-' + p2
    
    def getByNodeId(self, ts, nodeId):
        for t in ts:
            if t['nodeId'] == nodeId:
                return t
        return None
    
    def parseTask(self, task, progress):
        px = json.loads(task.progress)
        for p in px:
            dn = self.simpleDeptName(p['deptName'])
            key = f"{dn}_{p['nickname']}"
            if key not in progress:
                progress[key] = {'deptName': dn, 'nickName': p['nickname']}
            status = p['statusDesc']
            if status in ('已转发', '待处理'):
                if status not in progress[key]:
                    progress[key][status] = []
                progress[key][status].append(p)
            elif status == '待审核':
                # find parent
                if not p['pnodeId']:
                    pp = task
                    dpn = self.simpleDeptName(pp.deptName)
                    nk = pp.nickName
                    key2 = f"{dpn}_{nk}"
                else:
                    pp = self.getByNodeId(px, p['pnodeId'])
                    dpn = self.simpleDeptName(pp['deptName'])
                    nk = pp['nickname']
                    key2 = f"{dpn}_{nk}"
                if key2 not in progress:
                    progress[key2] = {'deptName': dpn, 'nickName': nk}
                if status not in progress[key2]:
                    progress[key2][status] = []
                progress[key2][status].append(p)

    # maxStartTime = YYYY-MM-DD
    def parse(self, maxStartTime):
        # filter
        for q in Task.select():
            js = json.loads(q.cnt)
            st = js['startTime']
            if st: st = st[0 : 10]
            if st <= maxStartTime:
                self.tasks.append(q)
            else:
                print('skip ', q.nickName, q.title)

        progress = {}
        for t in self.tasks:
            self.parseTask(t, progress)
        slistXZ = []
        slistDM = []
        for k in progress:
            if '乡' in k or '镇' in k or '场' in k:
                slistXZ.append(progress[k])
            else:
                slistDM.append(progress[k])
        slistXZ.sort(key = lambda x: x['deptName'])
        slistDM.sort(key = lambda x: x['deptName'])
        self.results = slistDM + slistXZ

    def getNum(self, obj, k):
        if (k not in obj) or (not obj[k]):
            return ''
        return len(obj[k])
    
    def getNum_s(self, obj, ks):
        num = 0
        for k in ks:
            v = self.getNum(obj, k)
            if v: num += 1
        return num

    def log(self, all = False):
        f = open('rs.log', 'w')
        print('\t单位\t填报人员\t待处理\t已转发\t待审核', file = f)
        no = 0
        for k in self.results:
            if (not all) and (not self.getNum_s(k, ['待处理', '已转发', '待审核'])):
                continue
            if '测试' in k['nickName']:
                continue
            no += 1
            print(no, k['deptName'], k['nickName'], self.getNum(k, '待处理'),
                  self.getNum(k, '已转发'), self.getNum(k, '待审核'), sep = '\t', file = f)
        f.close()

def main():
    tl = TaskMgr("Bearer 4fd586507a0d44d9a1a216533718d727")
    tl.loadTasks()
    tl.loadProgress()

    p = PraseProgress()
    p.parse('2025-02-11')
    p.log()

if __name__ == '__main__':
    main()