import peewee as pw, json, requests, datetime, time, urllib.parse, os, sys, re, copy
import openpyxl
from openpyxl import Workbook

sys.path.append(__file__[0 : __file__.upper().index('任务管理')])
from orm import *
import login, decrypt

class LocalTempalteFile:
    def __init__(self) -> None:
        pass

    def load(self):
        LocalTemplateModel.drop_table()
        db.create_tables([LocalTemplateModel])

        path = r'D:\工作\一表同享\2025\德安县表格目录清单2025.06.16.xlsx'
        wb : Workbook = openpyxl.load_workbook(path, read_only = True)
        ns = wb.sheetnames[0]
        sheet = wb[ns]
        rs = []
        ATTRS = ('name', 'bsds', 'bsxq', 'bscj', 'deptName', 'tbzd', 'tbcj', 'tbfs', 'peroid')
        for row in sheet.rows:
            item = LocalTemplateModel()
            for idx, cell in enumerate(row):
                if idx != 0:
                    setattr(item, ATTRS[idx - 1], cell.value.strip())
            rs.append(item)
        rs.pop(0)
        LocalTemplateModel.bulk_create(rs, 50)

class TaskDownloader:
    # decryptKey = window.key4
    def __init__(self) -> None:
        self.enableUpdate = False

    def _saveTask(self, task):
        obj = TaskModel.get_or_none(taskId = str(task['id']))
        if not obj:
            obj = TaskModel()
        obj.taskId = str(task['id'])
        obj.deptName = task['deptName']
        obj.nickName = task['nickname']
        obj.title = task['title']
        obj.statusDesc = task['statusDesc']
        obj.createTime = task['createTime']
        obj.startTime = task['startTime']
        obj.deadlineTime = task['deadlineTime']
        obj.cnt = json.dumps(task, ensure_ascii = False)
        obj.save()

    def loadTasks(self):
        if not self.enableUpdate:
            return
        print('[loadTasks] begin...')
        page = 1
        total = 0
        datas = []
        MAX_PAGE = 1
        while (page <= 1 or (page <= (total + 99) // 100)) and (page <= MAX_PAGE):
            url = f'http://10.8.52.17:8088/ledger-be/task/manage/operationPageList?current={page}&size=100&includeChildren=true&prop=createTime&order=descending'
            headers = {'authorization': login.getAuthorization(), 'accept': "application/json, text/plain, */*"}
            resp = requests.get(url, headers = headers)
            js = json.loads(resp.text)
            if js['code'] != 200:
                print('[loadTasks] Fail: ', resp.text)
                return
            data = decrypt.decrypt(js['data'])
            js = json.loads(data)
            datas.extend(js['records'])
            total = js['total']
            page += 1
        history = {}
        lastTask = datas[-1]
        qr = TaskModel.select().where(TaskModel.createTime >= lastTask['createTime']).order_by(TaskModel.createTime.desc())
        for it in qr:
            history[it.taskId] = it
        for idx, it in enumerate(datas):
            # print('Downloading ', idx + 1,  it['statusDesc'], it['createTime'], it['title'])
            if it['statusDesc'] != '草稿':
                self._saveTask(it)
            if str(it['id']) in history:
                history.pop(str(it['id']))
        for h in history:
            print('Removed Tasks:', h, history[h].title)
            self.removeTask(history[h])
        print('[loadTasks] end, total=', total)

    def removeTask(self, task):
        d = task.__data__
        DelTaskModel.create(**d)
        task.delete_instance()

    def loadProgress(self, minDeadlineTime = None, maxDeadlineTime = None):
        if not self.enableUpdate:
            return
        qr = TaskModel.select().order_by(TaskModel.createTime.desc())
        for it in qr:
            if minDeadlineTime and it.deadlineTime < minDeadlineTime:
                continue
            if maxDeadlineTime and it.deadlineTime > maxDeadlineTime:
                continue
            tp = TaskProgress(it)
            if it.statusDesc == '已终止':
                continue
            if it.statusDesc == '已完成' and tp.checkFullFinished():
                continue
            self.loadTaskProgress(it)
            time.sleep(0.3)

    def loadTaskProgress(self, task):
        print('[loadTaskProgress]', 'C' + task.createTime[0 : 10], 'E' + task.deadlineTime[0 : 10], task.deptName, task.title)
        url = f'http://10.8.52.17:8088/ledger-be/task/manage/getTaskFillSituation?taskId={task.taskId}'
        headers = {'authorization': login.getAuthorization(), 'accept': "application/json, text/plain, */*"}
        resp = requests.get(url, headers = headers)
        js = json.loads(resp.text)
        if js['code'] != 200:
            print('[loadTaskProgress] Fail: ', resp.text)
            return
        data = decrypt.decrypt(js['data'])
        js = json.loads(data)
        self._saveTaskProgress(js)

    def _saveTaskProgress(self, js):
        if not js:
            return
        taskId = js[0]['taskId']
        qr = TaskModel.select().where(TaskModel.taskId == taskId)
        obj = None
        for q in qr:
            obj = q
            break
        if not obj:
            print('[saveTaskProgress] No Task', taskId)
        obj.progress = json.dumps(js, ensure_ascii = False)
        obj.save()

    def loadTemplate(self, minCreateTime = None, maxCreateTime = None):
        if not self.enableUpdate:
            return
        qr = TaskModel.select().order_by(TaskModel.createTime.desc())
        for it in qr:
            if minCreateTime and it.createTime < minCreateTime:
                continue
            if maxCreateTime and it.createTime > maxCreateTime:
                continue
            self._loadTemplate(it)
    
    def _loadTemplate(self, task):
        if task.refTemplate:
            return
        cnt = json.loads(task.cnt)
        if cnt.get('taskTypeDesc', '') != '自定义任务':
            return
        print('[_loadTemplate] ...', task.taskId, task.createTime, task.title)
        url = f'http://10.8.52.17:8088/ledger-be/task/manage/selectTaskSelectedTemplatePage?current=1&size=1000&taskId={task.taskId}'
        headers = {'authorization': login.getAuthorization(), 'accept': "application/json, text/plain, */*"}
        resp = requests.get(url, headers = headers)
        js = json.loads(resp.text)
        time.sleep(1)
        if js['code'] != 200:
            print('[_loadTemplate] Fail: ', resp.text)
            return
        data = decrypt.decrypt(js['data'])
        js = json.loads(data)
        records = js['records']
        rs = json.dumps(records)
        task.refTemplate = rs
        task.save()

class TaskProgress:
    def __init__(self, task) -> None:
        self.task = task
        self.tree = {}
        self.nodes = None
        if task.cnt and isinstance(task.cnt, str):
            task.cntJson = json.loads(task.cnt)
        self._load()

    def getStatusDesc(self, node):
        childs = node.get('_childs', None)
        if not childs:
            return {node['statusDesc'] : 1}
        sd = node['statusDesc']
        if sd == '已审核':
            return {'已审核' : len(childs)}
        if sd == '':
            pass

    def _load(self):
        if not self.task.progress:
            return
        self.nodes = json.loads(self.task.progress)
        # check is 乡镇下发的任务
        if self.task.deptName[-1] in ('乡', '镇', '厂'):
            # deptName = 柏树村委会（德安县爱民乡>柏树村委会）  德安县聂桥镇（德安县>德安县聂桥镇）
            VIRTUAL_NODE_ID = -1
            for n in self.nodes:
                if n['pnodeId'] == 0:
                    n['pnodeId'] = VIRTUAL_NODE_ID
            virtualNode = {'id': VIRTUAL_NODE_ID, 'nodeId': VIRTUAL_NODE_ID, 'title': 'virtual-node', 'pnodeId': 0,
                           'deptName': f'{self.task.deptName}（德安县>{self.task.deptName}）', 
                           'nickname': self.task.nickName, 'statusDesc': 'Virtual-Val'}
            self.nodes.append(virtualNode)
        tmps : list = self.nodes[:]
        idx = 0
        while tmps:
            idx = idx % len(tmps)
            p = tmps[idx]
            if p['pnodeId'] == 0:
                self.tree[p['nodeId']] = p
                tmps.pop(idx)
                continue
            parent = self.getNode(p['pnodeId'])
            if not parent:
                idx += 1
                continue
            if '_childs' not in parent:
                parent['_childs'] = {}
            parent['_childs'][p['nodeId']] = p
            tmps.pop(idx)
            
    def getNode(self, nodeId):
        return self._findNode(self.tree, nodeId)

    def _findNode(self, ps, nodeId):
        if not ps:
            return None
        for ni in ps:
            if ni == nodeId:
                return ps[ni]
            fcd = self._findNode(ps[ni].get('_childs', None), nodeId)
            if fcd:
                return fcd
        return None

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
    
    def parseNode(self, node, progress):
        if self.task.statusDesc == '已终止':
            return
        dn = self.simpleDeptName(node['deptName'])
        key = f"{dn}_{node['nickname']}"
        if node['nickname'] is None:
            node['nickname'] = '--'
        if key not in progress:
            progress[key] = {'deptName': dn, 'nickName': node['nickname']}
        pitem = progress[key]
        status = node['statusDesc']
        childs = node.get('_childs', None)

        if status == '待处理':
            pitem['待处理'] = pitem.get('待处理', 0) + 1
            if '待处理-明细' not in pitem:
                pitem['待处理-明细'] = []
            pitem['待处理-明细'].append({'task': self.task})
        elif status == '待审核' or status == '已审核':
            pitem['已处理'] = pitem.get('已处理', 0) + 1
        if not childs:
            # 无下级
            return
        # 有下级
        yshList = [childs[k] for k in childs if childs[k]['statusDesc'] == '已审核']
        dshList = [childs[k] for k in childs if childs[k]['statusDesc'] == '待审核']
        wclList = [childs[k] for k in childs if childs[k]['statusDesc'] == '待处理']
        pitem['已审核'] = pitem.get('已审核', 0) + len(yshList)
        pitem['待审核'] = pitem.get('待审核', 0) + len(dshList)
        pitem['下级待处理'] = pitem.get('下级待处理', 0) + len(wclList)
        pitem['下级已处理'] = pitem.get('下级已处理', 0) + len(yshList) + len(dshList)
        if dshList:
            if '待审核-明细' not in pitem:
                pitem['待审核-明细'] = []
            pitem['待审核-明细'].append({'task': self.task})
        if wclList:
            if '下级待处理-明细' not in pitem:
                pitem['下级待处理-明细'] = []
            pitem['下级待处理-明细'].append({'task': self.task, 'users': wclList})

    def parseTask(self, progress):
        if not self.nodes:
            return
        for node in self.nodes:
            self.parseNode(node, progress)

    def checkFullFinished(self):
        if not self.nodes:
            return False
        progress = {}
        self.parseTask(progress)
        for p in progress:
            item = progress[p]
            if item.get('待处理', 0) or item.get('待审核', 0) or item.get('下级待处理', 0):
                return False
        return True

class TaskRecvDownloader:
    def __init__(self, enableUpdate) -> None:
        self.enableUpdate = enableUpdate

    def getAllRecvTasks(self):
        tasks = {}
        for it in RecvTaskModel.select():
            tasks[it.nodeId] = it
        return tasks

    # 接收任务查询（已填报）
    def loadTasksFromRecv(self):
        if not self.enableUpdate:
            return
        total = 0
        existsTasks = self.getAllRecvTasks()
        page = (len(existsTasks) + 99) // 100
        if page == 0: page = 1
        while (page <= (total + 99) // 100) or total == 0:
            url = f'http://10.8.52.17:8088/ledger-be/task/todo/selectByDeptTaskPage?current={page}&size=100&status=task_node_completed&prop=firstSubmitTime&order=ascending' # descending
            headers = {'authorization': login.getAuthorization(), 'accept': "application/json, text/plain, */*"}
            resp = requests.get(url, headers = headers)
            js = json.loads(resp.text)
            if js['code'] != 200:
                print('[loadTasksFromRecv] Fail: ', resp.text)
                return
            data = decrypt.decrypt(js['data'])
            js = json.loads(data)
            total = js['total']
            page += 1
            items = js['records']
            inserts, updates = 0, 0
            for it in items:
                nid = str(it['nodeId'])
                if nid not in existsTasks:
                    RecvTaskModel.create(**it)
                    inserts += 1
                    continue
                cur = existsTasks[nid]
                if cur.statusDesc != it['statusDesc']:
                    cur.statusDesc = it['statusDesc']
                    cur.save()
                    updates += 1
            
            print(f'Download 接收任务查询（已填报）, total={total}, page index={page}, update-num={updates}, insert-num={inserts}')

class DeptDownloader:
    def __init__(self) -> None:
        self.datas = {}

    def loadDatas(self):
        for it in DeptModel.select():
            it.__data__['id'] = it.deptId
            self.datas[it.deptId] = it.__data__
        self._adjustDept()

    def diff(self, local : DeptModel, server : dict):
        KEYS = ('parentId', 'deptName', 'businessType', 'regionCode', 'levelNum', 'ancestors', 'ancestorsName', 'status', 'regionCodeLabel')
        for key in KEYS:
            a1 = getattr(local, key, None)
            a2 = server.get(key, None)
            if a1 == None or a2 == None:
                if a1 != a2:
                    setattr(local, key, a2)
                continue
            if type(a1) == type(a2) and a1 != a2:
                setattr(local, key, a2)
            if type(a1) != type(a2) and a1 != str(a2):
                setattr(local, key, a2)
        return not not local._dirty

    def loadNetDatas(self):
        url = 'http://10.8.52.17:8088/ledger-be/system/dept/page'
        headers = {'authorization': login.getAuthorization(), 'accept': "application/json, text/plain, */*"}
        resp = requests.get(url, headers = headers)
        js = json.loads(resp.text)
        if js['code'] != 200:
            print('[loadDepts] Fail: ', resp.text)
            return
        exdatas = {}
        for d in DeptModel.select():
            exdatas[d.deptId] = d
        ds = js['data']
        for d in ds:
            ex = exdatas.get(str(d['id']), None)
            ndd = copy.copy(d)
            ndd['deptId'] = ndd['id']
            del ndd['id']
            if not ex:
                DeptModel.create(**ndd)
            else:
                if self.diff(ex, ndd):
                    ex.save()
                del exdatas[str(d['id'])]
        keys = exdatas.keys()
        for k in keys:
            exdatas[k].delete_instance()

    def _adjustDept(self):
        dsjDept = None
        zfbDept = None
        for k in self.datas:
            r = self.datas[k]
            if r['deptName'] == '德安县大数据中心':
                dsjDept = r
            elif r['deptName'] == '德安县政府办':
                zfbDept = r
        dsjDept['parentId'] = zfbDept['id']
        
    # 查找所属一级部门
    def getTopDept(self, deptName):
        if deptName[-1] in '乡镇场':
            return '--'
        dd = None
        for rid in self.datas:
            dp = self.datas[rid]
            if deptName == dp['deptName']:
                dd = dp
                break
        while dd:
            parent = self.datas[dd['parentId']]
            if parent['deptName'] == '德安县':
                return dd['deptName']
            dd = parent
        return '--'

    def 部门使用数量(self):
        bm = set()
        createTaskBm = set()
        for it in RecvTaskModel.select():
            if '德安县' in it.taskDeptName and (it.taskDeptName[-1] not in '乡镇场') and it.taskDeptName != '德安县':
                dn = self.getTopDept(it.taskDeptName)
                bm.add(dn)
                createTaskBm.add(dn)
            if '德安县' in it.deptName and (it.deptName[-1] not in '乡镇场'):
                dn = self.getTopDept(it.deptName)
                bm.add(dn)

        bm = list(bm)
        bm.sort(key = lambda k: k.encode('gbk'))
        createTaskBm = list(createTaskBm)
        createTaskBm.sort(key = lambda k: k.encode('gbk'))

        tbm = set(bm) - set(createTaskBm)
        return createTaskBm, tbm

    def get_部门(self):
        bm = []
        for d in self.datas:
            it = self.datas[d]
            if it['deptName'][-1] not in '乡镇场':
                bm.append(it)
        return bm
    
    def get_乡镇(self):
        bm = []
        for d in self.datas:
            it = self.datas[d]
            if it['deptName'][-1] in '乡镇场':
                bm.append(it)
        return bm
    
    def get_村社区(self):
        cun = []
        xz = self.get_乡镇()
        xzIds = [k['id'] for k in xz]
        for k in self.datas:
            it = self.datas[k]
            if it['parentId'] in xzIds:
                cun.append(it)
        return cun

class UserDownloader:
    def __init__(self) -> None:
        pass
    
    # pageIdx = [1...]
    def loadPageData(self, pageIdx):
        url = f'http://10.8.52.17:8088/ledger-be/system/user/page?includeChildrenDept=true&current={pageIdx}&size=100'
        headers = {'authorization': login.getAuthorization(), 'accept': "application/json, text/plain, */*"}
        resp = requests.post(url, headers = headers)
        js = resp.json()
        if js['code'] != 200:
            print('[UserManager.loadPageData]', js)
            raise Exception(js['msg'])
        data = decrypt.decrypt(js['data'])
        js = json.loads(data)
        total = js['total']
        datas = js['records']
        # print(datas[0])
        ds = []
        for data in datas:
            data['userId'] = data['id']
            del data['id']
            data['depts'] = json.dumps(data['depts'], ensure_ascii = False)
            data['roles'] = json.dumps(data['roles'], ensure_ascii = False)
            ds.append(UserModel(**data))
        UserModel.bulk_create(ds, 50)
        return total
    
    def loadDatas(self):
        page = 1
        total = 1
        while page <= (total + 99) // 100:
            print('Load page', page)
            total = self.loadPageData(page)
            page += 1
