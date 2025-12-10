import peewee as pw, json, requests, datetime, time, urllib.parse, os, sys

import openpyxl
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font, GradientFill

sys.path.append(__file__[0 : __file__.upper().index('任务管理')])
import decrypt, login

db = pw.SqliteDatabase('任务管理/tasks.db')

class LocalTemplate(pw.Model):
    name = pw.CharField(column_name = '报表名称')
    bsds = pw.CharField(column_name = '报送地市')
    bsxq = pw.CharField(column_name = '报送区县')
    bscj = pw.CharField(column_name = '报送层级')
    deptName = pw.CharField(column_name = '所属部门')
    tbzd = pw.CharField(column_name = '填报字段')
    tbcj = pw.CharField(column_name = '填报层级')
    tbfs = pw.CharField(column_name = '填报方式')
    peroid = pw.CharField(column_name = '更新频率')
    class Meta:
        database = db

class Task(pw.Model):
    taskId = pw.CharField()
    deptName = pw.CharField()
    nickName = pw.CharField() #创建者
    title = pw.CharField()
    statusDesc = pw.CharField()
    createTime = pw.CharField()
    startTime = pw.CharField()
    deadlineTime = pw.CharField()
    cnt = pw.CharField()
    progress = pw.CharField(null = True)
    refTemplate = pw.CharField(null = True, default = None)

    class Meta:
        database = db

# 接收任务(已完成)
class RecvTask(pw.Model):
    taskId = pw.CharField(null = True)
    title = pw.CharField(null = True)
    nodeId = pw.CharField(null = True)
    taskDeptName = pw.CharField(null = True)  #创建部门
    createUserNickname = pw.CharField(null = True) # 创建人员
    deptName = pw.CharField(null = True) # 填报单位
    nickName = pw.CharField(null = True) # 填报人员
    statusDesc = pw.CharField(null = True)

    createTime = pw.CharField(null = True)
    startTime = pw.CharField(null = True)
    deadlineTime = pw.CharField(null = True)
    firstSubmitTime = pw.CharField(null = True) #提交时间
    isDelete = pw.BooleanField(default = False)

    class Meta:
        database = db        

class DelTask(pw.Model):
    taskId = pw.CharField()
    deptName = pw.CharField()
    nickName = pw.CharField() #创建者
    title = pw.CharField()
    statusDesc = pw.CharField(null = True)
    createTime = pw.CharField(null = True)
    startTime = pw.CharField(null = True)
    deadlineTime = pw.CharField(null = True)
    cnt = pw.CharField(null = True)
    progress = pw.CharField(null = True)
    refTemplate = pw.CharField(null = True, default = None)

    class Meta:
        database = db        

db.create_tables([Task, LocalTemplate, DelTask, RecvTask])

class LocalFile:
    def __init__(self) -> None:
        pass

    def load(self):
        LocalTemplate.drop_table()
        db.create_tables([LocalTemplate])

        path = r'D:\工作\一表同享\2025\德安县表格目录清单2025.06.16.xlsx'
        wb : Workbook = openpyxl.load_workbook(path, read_only = True)
        ns = wb.sheetnames[0]
        sheet = wb[ns]
        rs = []
        ATTRS = ('name', 'bsds', 'bsxq', 'bscj', 'deptName', 'tbzd', 'tbcj', 'tbfs', 'peroid')
        for row in sheet.rows:
            item = LocalTemplate()
            for idx, cell in enumerate(row):
                if idx != 0:
                    setattr(item, ATTRS[idx - 1], cell.value.strip())
            rs.append(item)
        rs.pop(0)
        LocalTemplate.bulk_create(rs, 50)

class TaskDownloader:
    # decryptKey = window.key4
    def __init__(self, decryptKey = '3152365a55727a3764524d3759304b5a') -> None:
        self.authorization = None # "Bearer 461819acc5ca44d0b616fcef055c105c"
        self.decryptKey = decryptKey
        self.enableUpdate = False

    def login(self):
        if not self.enableUpdate:
            return
        self.authorization = login.login(self.decryptKey)

    def _saveTask(self, task):
        obj = Task.get_or_none(taskId = str(task['id']))
        if not obj:
            obj = Task()
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
        while page <= 1 or (page <= (total + 99) // 100):
            url = f'http://10.8.52.17:8088/ledger-be/task/manage/operationPageList?current={page}&size=100&includeChildren=true&prop=createTime&order=descending'
            headers = {'authorization': self.authorization, 'accept': "application/json, text/plain, */*"}
            resp = requests.get(url, headers = headers)
            js = json.loads(resp.text)
            if js['code'] != 200:
                print('[loadTasks] Fail: ', resp.text)
                return
            data = decrypt.decrypt(js['data'], self.decryptKey)
            js = json.loads(data)
            datas.extend(js['records'])
            total = js['total']
            page += 1
        history = {}
        lastTask = datas[-1]
        qr = Task.select().where(Task.createTime >= lastTask['createTime']).order_by(Task.createTime.desc())
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
        DelTask.create(**d)
        task.delete_instance()

    def loadProgress(self, minDeadlineTime = None, maxDeadlineTime = None):
        if not self.enableUpdate:
            return
        qr = Task.select().order_by(Task.createTime.desc())
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
        print('[loadTaskProgress]', 'C' + task.createTime[0 : 10], 'E' + task.deadlineTime[0 : 10], task.title)
        url = f'http://10.8.52.17:8088/ledger-be/task/manage/getTaskFillSituation?taskId={task.taskId}'
        headers = {'authorization': self.authorization, 'accept': "application/json, text/plain, */*"}
        resp = requests.get(url, headers = headers)
        js = json.loads(resp.text)
        if js['code'] != 200:
            print('[loadTaskProgress] Fail: ', resp.text)
            return
        data = decrypt.decrypt(js['data'], self.decryptKey)
        js = json.loads(data)
        self._saveTaskProgress(js)

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

    def loadTemplate(self, minCreateTime = None, maxCreateTime = None):
        if not self.enableUpdate:
            return
        qr = Task.select().order_by(Task.createTime.desc())
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
        headers = {'authorization': self.authorization, 'accept': "application/json, text/plain, */*"}
        resp = requests.get(url, headers = headers)
        js = json.loads(resp.text)
        time.sleep(1)
        if js['code'] != 200:
            print('[_loadTemplate] Fail: ', resp.text)
            return
        data = decrypt.decrypt(js['data'], self.decryptKey)
        js = json.loads(data)
        records = js['records']
        rs = json.dumps(records)
        task.refTemplate = rs
        task.save()

    def getAllRecvTasks(self):
        tasks = {}
        for it in RecvTask.select():
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
            url = f'http://10.8.52.17:8088/ledger-be/task/todo/selectByDeptTaskPage?current={page}&size=100&status=task_node_completed&prop=firstSubmitTime&order=ascending'
            headers = {'authorization': self.authorization, 'accept': "application/json, text/plain, */*"}
            resp = requests.get(url, headers = headers)
            js = json.loads(resp.text)
            if js['code'] != 200:
                print('[loadTasksFromRecv] Fail: ', resp.text)
                return
            data = decrypt.decrypt(js['data'], self.decryptKey)
            js = json.loads(data)
            total = js['total']
            page += 1
            items = js['records']
            for it in items:
                nid = str(it['nodeId'])
                if nid not in existsTasks:
                    RecvTask.create(**it)
                    continue
                cur = existsTasks[nid]
                if cur.statusDesc != it['statusDesc']:
                    cur.statusDesc = it['statusDesc']
                    cur.save()

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

class ProgressMgr:
    def __init__(self) -> None:
        self.tasks = []

    def filter(self, *filters):
        # filter
        num = 0
        for q in Task.select().order_by(Task.createTime.desc()):
            js = json.loads(q.cnt)
            cnd = True
            for f in filters:
                cnd = cnd and f(js)
            if cnd:
                self.tasks.append(q)
                num += 1
                # print(f'[filter] accept [{num :2d}]', 'C' + q.createTime[0 : 10], 'E' + q.deadlineTime[0 : 10], q.statusDesc, q.title)

    def parse(self):
        progress = {}
        for t in self.tasks:
            tp = TaskProgress(t)
            tp.parseTask(progress)
        slistXZ = []
        slistDM = []
        for k in progress:
            if '乡' in k or '镇' in k or '场' in k:
                slistXZ.append(progress[k])
            else:
                slistDM.append(progress[k])
        slistXZ.sort(key = lambda x: x['deptName'])
        slistDM.sort(key = lambda x: x['deptName'])
        results = slistDM + slistXZ
        return results

    def getNum(self, obj, k):
        if (k not in obj) or (not obj[k]):
            return 0
        return obj[k]
    
    def calcCommentWidth(self, row):
        w = 0
        for ch in row:
            if ord(ch) < 255:
                w += 8
            else:
                w += 14
        return w
    
    def addComment(self, cell, obj, k):
        if k not in obj:
            return
        rows = []
        for idx, info in enumerate(obj[k]):
            task = info['task']
            users = info.get('users', None)
            row = f'【{idx + 1}】任务创建时间：{task.createTime[0 : 10]}  任务名称：{task.title} '
            if users:
                row += '未填报人员：(' + '、'.join([u['nickname'] for u in users]) + ')   '
            rows.append(row)
        rowsWidth = [self.calcCommentWidth(row) for row in rows]
        txt = ' | '.join(rows)
        width = max(rowsWidth)
        if width > 650: width = 650
        cell.comment = Comment(txt, None, height = 17 * len(obj[k]), width = width)

    def getNum_s(self, obj, ks):
        num = 0
        for k in ks:
            v = self.getNum(obj, k)
            if v: num += 1
        return num

    def log(self, all = False):
        f = open('任务统计/rs.log', 'w')
        print('\t单位\t填报人员\t待处理\t已转发\t待审核', file = f)
        no = 0
        for k in self.results:
            if (not all) and (not self.getNum_s(k, ['待处理', '已转发', '待审核', '已审核'])):
                continue
            if '测试' in k['nickName']:
                continue
            no += 1
            print(no, k['deptName'], k['nickName'], self.getNum(k, '待处理'),
                  self.getNum(k, '已转发'), self.getNum(k, '待审核'), sep = '\t', file = f)
        f.close()

    def writeExcel_乡镇填报情况(self, wb : Workbook, results, startTime, endTime, sheetName, mainTitle):
        results = [r for r in results if r['deptName'][-1] in ('乡', '镇', '场')]
        results.sort(key = lambda x : x['deptName'].encode('gbk'))
        day = datetime.date.today().strftime('%Y-%m-%d')
        ws = wb.create_sheet(sheetName)
        side = Side(border_style='thin', color='000000')
        bfont = Font(name='宋体', size=12)
        bfont2 = Font(name='宋体', size=12, color='ff0000', bold=True)
        bfont3 = Font(name='宋体', size=12, color='00B050', bold=True)
        border = Border(left=side, right=side, top=side, bottom=side)
        alignCenter = Alignment(horizontal='center', vertical='center')
        ws.merge_cells("A1:I1")
        a1 = ws['A1']
        a1.value = mainTitle
        a1.font = Font(name='宋体', size=14, bold=True)
        a1.alignment = alignCenter
        ws.row_dimensions[1].height = 30
        ws.row_dimensions[2].height = 33
        ws.column_dimensions['B'].width = 32
        ws.column_dimensions['C'].width = 12
        ws.column_dimensions['D'].width = 12
        ws.column_dimensions['E'].width = 15
        ws.column_dimensions['F'].width = 12
        ws.column_dimensions['G'].width = 12
        ws.column_dimensions['H'].width = 12
        ws.column_dimensions['I'].width = 12

        ws.merge_cells("A2:I2")
        a2 = ws['A2']
        a2.value = f'(统计范围: 任务结束时间在{startTime}至{endTime}之间)'
        a2.font = bfont2
        a2.alignment = alignCenter

        for idx, title in enumerate(['', '单位', '填报人员', '待处理', '已填报', '待审核', '已审核', '村(社区)\n未填报', '村(社区)\n已填报']):
            c = ws.cell(row=3, column=idx+1, value=title)
            c.fill = GradientFill(stop = ('FFFF00', 'FFFF00'))
            c.border = border
            c.font = Font(name='宋体', size = 12, bold = True)
            c.alignment = alignCenter
        no = 0
        START_ROW = 3
        for idx, k in enumerate(results):
            # if (not all) and (not self.getNum_s(k, ['待处理', '已转发', '待审核', '已审核'])):
            #     continue
            if '测试' in k['nickName']:
                continue
            # check is empty line
            allNum = 0
            for x in ('待处理', '已处理', '待审核', '已审核', '下级待处理', '下级已处理'):
                allNum += self.getNum(k, x)
            if allNum == 0:
                continue
            no += 1
            c1 = ws.cell(row=no + START_ROW, column=1, value=no)
            c2 = ws.cell(row=no + START_ROW, column=2, value=k['deptName'])
            c3 = ws.cell(row=no + START_ROW, column=3, value=k['nickName'])
            c4 = ws.cell(row=no + START_ROW, column=4, value=self.getNum(k, '待处理'))
            c5 = ws.cell(row=no + START_ROW, column=5, value=self.getNum(k, '已处理'))
            c6 = ws.cell(row=no + START_ROW, column=6, value=self.getNum(k, '待审核'))
            c7 = ws.cell(row=no + START_ROW, column=7, value=self.getNum(k, '已审核'))
            c8 = ws.cell(row=no + START_ROW, column=8, value=self.getNum(k, '下级待处理'))
            c9 = ws.cell(row=no + START_ROW, column=9, value=self.getNum(k, '下级已处理'))
            self.addComment(c4, k, '待处理-明细')
            self.addComment(c6, k, '待审核-明细')
            self.addComment(c8, k, '下级待处理-明细')
            for cx in (c1, c2, c3, c4, c5, c6, c7, c8, c9):
                cx.font = bfont
                cx.border = border
            for cx in (c1, c3, c4, c5, c6, c7, c8, c9):
                cx.alignment = alignCenter
            for cx in (c4, c6, c8):
                if cx.value != 0:
                    cx.font = bfont2
            for cx in (c5, c7, c9):
                if cx.value != 0:
                    cx.font = bfont3

    def print_乡镇填报人员汇总(self, results):
        results = [r for r in results if r['deptName'][-1] in ('乡', '镇', '场')]
        rs = {}
        for d in results:
            dept = d['deptName']
            user = d['nickName']
            if dept not in rs: rs[dept] = {'未完成': set(), '已完成':set()}
            if d.get('待处理', 0) or d.get('待审核', 0) or d.get('下级待处理', 0):
                rs[dept]['未完成'].add(user)
            else:
                rs[dept]['已完成'].add(user)
        depts = list(rs.keys())
        depts.sort(key = lambda x : x.encode('gbk'))
        for k in depts:
            deptName = k.replace('德安县', '')
            deptName = f'【{deptName}】'
            print(deptName, '  填报已完成(', '、'.join(rs[k]['已完成']),')', ';  填报未完成(', '、'.join(rs[k]['未完成']),')', sep='')

    def print_部门审核情况(self):
        progress = {}
        for t in self.tasks:
            deptName = t.deptName + '-' + t.nickName # 任务下发单位 + 姓名
            if deptName not in progress:
                progress[deptName] = {}
            tp = TaskProgress(t)
            for n in tp.nodes:
                if n['pnodeId']: continue
                if n['statusDesc'] != '待审核': continue
                key = str(n['taskId']) + '/' + t.title
                if key not in progress[deptName]:
                    progress[deptName][key] = []
                dname = n['deptName']
                if '（' in dname: dname = dname[0 : dname.index('（')]
                progress[deptName][key].append(dname)
        print('-------------------部门待审核数-----------------------------')
        for p in progress:
            info = progress[p]
            if not info:
                continue
            print(p, '-->', progress[p])
            num = 0
            for k in info:
                num += len(info[k])
            print(p.replace('德安县委', '').replace('德安县', ''), ': ', '待审核数', num)
        pass

    def print_任务完成率(self, tag):
        if not self.tasks:
            print(f'{tag}任务总数: 0')
            return
        num = 0
        for t in self.tasks:
            if t.statusDesc == '已完成':
                num += 1
        print(f'{tag}任务总数：{len(self.tasks)} 已完成：{num} 完成率：{int(num / len(self.tasks) * 100)}%')

class TaskMgr:
    def __init__(self) -> None:
        self.tasks = []

    def filter(self, *filters):
        # filter
        self.tasks = []
        for q in Task.select():
            js = json.loads(q.cnt)
            cnd = True
            for f in filters:
                cnd = cnd and f(js)
            if cnd:
                self.tasks.append(q)

    # 统计任务下发情况
    def print_部门任务汇总(self):
        rs = {}
        for r in self.tasks:
            if r.deptName[-1] in '乡镇场':
                continue
            if r.deptName not in rs:
                rs[r.deptName] = []
            #print(r.deptName, json.loads(r.cnt)['createTime'], r.title)
            rs[r.deptName].append(r.title)
        print('----------部门任务下发情况--------------------')
        print(' ' * 30, '月量')
        total = 0
        for dept in rs:
            item = rs[dept]
            total += len(item)
            dept = dept + ' ' * ((12 - len(dept)) * 2)
            if item:
                print(dept, len(item), sep = '\t')
            else:
                print(dept, 0, sep = '\t')
        print('总数：', total)

    def print_非临时任务(self):
        self.tasks.sort(key = lambda t : t.createTime, reverse= True)
        fls, ls, nf = [], [], []
        for task in self.tasks:
            cnt = json.loads(task.cnt)
            taskTypeDesc = cnt.get('taskTypeDesc', '')
            if taskTypeDesc == '高频报表任务':
                fls.append((task.createTime, taskTypeDesc, task.title))
                continue
            if taskTypeDesc != '自定义任务':
                continue
            tmps = json.loads(task.refTemplate)
            tmp = tmps[0]
            find = LocalTemplate.get_or_none(name = tmp['templateTitle'])
            if find:
                if find.peroid != '临时性':
                    fls.append((task.createTime, taskTypeDesc, find.peroid, task.title))
                else:
                    ls.append((task.createTime, taskTypeDesc, find.peroid, task.title, '|||', tmp['templateTitle'], task.deptName))
            else:
                nf.append((task.createTime, taskTypeDesc, task.title, '///', tmp['templateTitle']))
        print('【非临时任务数】', len(fls))
        print('【临时任务数】', len(ls))
        for r in ls:
            print('\t', r)
        print('【未知任务数】', len(nf))
        for r in nf:
            print('\t', r)

def print_村社区填报任务量():
    cun = {}
    for task in Task.select().order_by(Task.createTime.desc()):
        if not task.progress:
            continue
        ps = json.loads(task.progress)
        for p in ps:
            deptName = p['deptName']
            sname : str = deptName[deptName.index('（') + 1 : deptName.index('）')]
            if sname.startswith('德安县>'):
                continue
            sname = sname.replace('德安县', '')
            item = cun.get(sname, None)
            if not item: item = cun[sname] = {'任务总数' : 0, '填报数量': 0}
            item['任务总数'] += 1
            if p['firstSubmitTime']:
                item['填报数量'] += 1
    cunList = []
    for c in cun:
        tt = {'name': c}
        tt.update(cun[c])
        cunList.append(tt)
    cunList.sort(key= lambda k : k['任务总数'], reverse= True)
    for i, c in enumerate(cunList):
        print(c)
    import 任务管理.dept as dept
    cunNames = []
    for c in dept.Cun.select():
        cunNames.append(c.xzName + '>' + c.cunName)
    for c in cunList:
        if c['name'] in cunNames and c['填报数量']:
            cunNames.remove(c['name'])
    print('未填报村：', cunNames)
    cunList.sort(key= lambda k : k['name'].encode('gbk'), reverse= False)
    pass

def print_村社区使用模板最多():
    cun = {} # key = templateTitle , val: num
    for task in Task.select().order_by(Task.createTime.desc()):
        if not task.progress or not task.refTemplate:
            continue
        temp = json.loads(task.refTemplate)
        if not temp:
            continue
        temp = temp[0]
        ps = json.loads(task.progress)
        num = 0
        for p in ps:
            deptName = p['deptName']
            sname : str = deptName[deptName.index('（') + 1 : deptName.index('）')]
            if sname.startswith('德安县>'):
                continue
            num += 1
        cun[temp['templateTitle']] = cun.get(temp['templateTitle'], 0) + num
    cs = [(k, cun[k]) for k in cun]
    cs.sort(key = lambda c : c[1], reverse = True)
    for i in range(0, 10):
        print(cs[i])
    pass

def fmtDate(day):
    if not day:
        return None
    if isinstance(day, datetime.date):
        day = day.strftime('%Y-%m-%d')
    day = day.strip()
    if len(day) == 8:
        return day[0 : 4] + '-' + day[4 : 6] + '-' + day[6 : 8]
    if len(day) == 10:
        return day
    return None

def print_乡镇统计时间段(startTime, endTime, soonEndTime = None):
    startTime = fmtDate(startTime)
    endTime = fmtDate(endTime)
    soonEndTime = fmtDate(soonEndTime)
    if not startTime or not endTime or startTime > endTime:
        print('开始日期/结束日期错误')
        return
    TODAY = datetime.date.today().strftime('%Y-%m-%d')
    proMgr = ProgressMgr()
    proMgr.filter(
             lambda x: x['deadlineTime'][0 : 10] >= startTime,
             lambda x: x['deadlineTime'][0 : 10] <= endTime,
             lambda x: x['statusDesc'] in ('填报中', '已完成'),
             )
    results = proMgr.parse()
    wb = Workbook()
    wb.remove(wb.active)
    proMgr.writeExcel_乡镇填报情况(wb, results, startTime, endTime, '全部', f'乡镇"一表同享"填报任务完成情况({TODAY})')
    proMgr.print_乡镇填报人员汇总(results)
    unResults = [r for r in results if r.get('待处理', 0) or r.get('待审核', 0) or r.get('下级待处理', 0) ]
    proMgr.writeExcel_乡镇填报情况(wb, unResults, startTime, endTime, '未完成', '已超期任务填报情况')
    proMgr.print_任务完成率(f'乡镇{startTime}至{endTime} ')

    if soonEndTime and soonEndTime > endTime:
        proMgr = ProgressMgr()
        et = datetime.datetime.strptime(endTime, '%Y-%m-%d') + datetime.timedelta(days = 1)
        ets = et.strftime('%Y-%m-%d')
        proMgr.filter(
             lambda x: x['deadlineTime'][0 : 10] >= ets,
             lambda x: x['deadlineTime'][0 : 10] <= soonEndTime,
             lambda x: x['statusDesc'] in ('填报中', '已完成'),
             )
        results = proMgr.parse()
        proMgr.writeExcel_乡镇填报情况(wb, results, ets, soonEndTime, '即将到期', '即将到期任务填报情况')
        proMgr = ProgressMgr()
        proMgr.filter(
             lambda x: x['deadlineTime'][0 : 10] >= startTime,
             lambda x: x['deadlineTime'][0 : 10] <= soonEndTime,
             lambda x: x['statusDesc'] in ('填报中', '已完成'),
             )
        proMgr.print_任务完成率(f'乡镇{startTime}至{soonEndTime} ')
    wb.save(f'files/乡镇填报任务完成情况({TODAY}).xlsx')

def print_县直部门待审核任务(startTime, endTime):
    proMgr = ProgressMgr()
    proMgr.filter(
             lambda x: x['deadlineTime'][0 : 10] >= startTime,
             lambda x: x['deadlineTime'][0 : 10] <= endTime,
             lambda x: x['statusDesc'] in ('填报中'),
             )
    proMgr.tasks.sort(key = lambda task: task.deptName + '-' + task.nickName)
    no = 1
    for task in proMgr.tasks:
        tp = TaskProgress(task)
        if tp.checkFullFinished():
            print(f'[{no :2d}]', '待审核已完成任务->', task.deptName, task.nickName, 'C' + task.createTime[0 : 10], 'E' + task.deadlineTime[0 : 10], task.title)
            no += 1
    print('------------------------------------------------------')

def 部门使用数量(startDay = '2025-01-01', endDay = datetime.date.today().strftime('%Y-%m-%d')):
    xzCun = set()
    bm = set()
    createTaskDepts = set()
    from 任务管理.dept import Cun
    for cun in Cun.select():
        xzCun.add(cun.xzName)
        xzCun.add(cun.cunName)
    xzCun.add('向阳山生态林场')
    for task in Task.select().where(Task.createTime >= startDay, Task.createTime <= endDay, Task.statusDesc != '已终止'): # 已终止
        dp = task.deptName.replace('德安县', '')
        if dp and (dp not in xzCun):
            # is bu meng
            bm.add(task.deptName)
            createTaskDepts.add(task.deptName)
        if not task.progress:
            continue
        nodes = json.loads(task.progress)
        for node in nodes:
            if node['statusDesc'] != '已审核':
                continue
            dp = node['deptName']
            dpf = dp[0 : dp.index('（')]
            dp = dpf.replace('德安县', '')
            if dp and (dp not in xzCun):
                bm.add(dpf)
    bm = list(bm)
    bm.sort(key = lambda k: k.encode('gbk'))
    createTaskDepts = list(createTaskDepts)
    createTaskDepts.sort(key = lambda k: k.encode('gbk'))
    return bm, createTaskDepts

def 部门使用数量_2():
    xzCun = set()
    bm = set()
    createTaskBm = set()
    xzCun.add('德安县向阳山生态林场')
    for it in RecvTask.select():
        if '德安县' in it.taskDeptName and (it.taskDeptName[-1] not in '乡镇场') and it.taskDeptName != '德安县':
            bm.add(it.taskDeptName)
            createTaskBm.add(it.taskDeptName)
        if '德安县' in it.deptName and (it.deptName[-1] not in '乡镇场'):
            bm.add(it.deptName)

    bm = list(bm)
    bm.sort(key = lambda k: k.encode('gbk'))
    createTaskBm = list(createTaskBm)
    createTaskBm.sort(key = lambda k: k.encode('gbk'))
    return bm, createTaskBm

def print_市周报表数据(year, month, weekStart, weekEnd):
    TODAY = datetime.date.today().strftime('%Y-%m-%d')
    month = f'{int(month) :02d}'
    yearTaskNum = Task.select(pw.fn.count()).where(Task.createTime >= str(year), Task.statusDesc != '已终止').scalar()
    monthTaskNum = Task.select(pw.fn.count()).where(Task.createTime >= f'{year}-{month}', Task.statusDesc != '已终止').scalar()
    weekTaskNum = Task.select(pw.fn.count()).where(Task.createTime >= weekStart, Task.createTime <= weekEnd, Task.statusDesc != '已终止').scalar()
    print('-------------------市周报数据----------------------------')
    print('年度任务分发数量: ', yearTaskNum)
    print('本月新增任务数量: ', monthTaskNum)
    print('本周新增任务数量: ', weekTaskNum)
    bm, cbm = 部门使用数量_2()
    print('----年度部门使用数量（全部）------------\n', f'【{len(bm)}】', '、'.join(bm))
    print('----年度部门使用数量（创建任务）-------- \n', f'【{len(cbm)}】', '、'.join(cbm))
    xbm = set(bm) - set(cbm)
    print('----年度部门使用数量（仅填报）---------- \n', f'【{len(xbm)}】', '、'.join(xbm))

    #taskMgr.print_非临时任务()

class DeptTaskMgr:
    def __init__(self) -> None:
        self.jcbbData = self.loadServerJcbb()

    def loadServerJcbb(self):
        def strToHex(s : str):
            HEX = '0123456789ABCDEF'
            bs = s.encode()
            vals = []
            for b in bs:
                b = int(b)
                l, h = b & 0xf, (b >> 4) & 0xf
                vals.append(HEX[h])
                vals.append(HEX[l])
            return ''.join(vals)
        filters = strToHex(json.dumps([
            {'col': 'fbcj', 'op': '==', 'val': '县区级'}, {'col': 'isDelete', 'op': '==', 'val': '0'},
        ]))
        resp = requests.get(f'http://113.44.136.221:8010/api/list/JcbdModel?filters={filters}')
        js = resp.json()
        rs = {}
        for it in js:
            key = it['bm']
            if not rs.get(key, None):
                rs[key] = {'任务模板': [], 'flag': 1, 'tasks': []}
            rs[key]['任务模板'].append(it)
        for r in rs:
            rs[r]['更新频率'] = self.get_更新频率(rs[r]['任务模板'])
        return rs
    
    def get_更新频率(self, temps):
        SS = ['年报', '半年报', '季报', '月报', '阶段性', '临时性', '实时更新']
        rs = {}
        for s in SS:
            for t in temps:
                if t['gxpl'] == s:
                    rs[s] = rs.get(s, 0) + 1
        for t in temps:
            if t['gxpl'] not in SS:
                rs['未知'] = rs.get('未知', 0) + 1
        return rs

    def calc_部门任务下发统计(self, month):
        taskMgr = TaskMgr()
        taskMgr.filter(
                lambda x: x['createTime'] >= f'2025-{int(month) :02d}-01',
                lambda x: x['createTime'] <= f'2025-{int(month) :02d}-31',
                lambda x: x['statusDesc'] in ('填报中', '已完成', '已下发，未开始'),
                )
        for r in taskMgr.tasks:
            dn = r.deptName
            if dn[-1] in '乡镇场':
                continue
            sdn = self.simpleDeptName(dn)
            if sdn not in self.jcbbData:
                self.jcbbData[sdn] = {'任务模板': [], 'flag': 0, 'tasks': []}
            self.jcbbData[sdn]['tasks'].append(r)

        # for deptName in self.jcbbData:
            # print(deptName, len(self.jcbbData[deptName]['任务模板']), len(self.jcbbData[deptName]['tasks']))

    # 应发任务数
    def getTaskNumOfMonth(self, month, temps):
        if not temps:
            return 0
        num = 0
        month = int(month)
        num += temps.get('月报', 0)
        if month in (3, 6, 9, 12):
            num += temps.get('季报', 0)
        return num

    def writeExcel(self, month):
        self.calc_部门任务下发统计(month)
        wb = Workbook()
        ws = wb.active
        side = Side(border_style='thin', color='000000')
        bfont = Font(name='宋体', size=11)
        bfont2 = Font(name='宋体', size=11, color='ff0000', bold=True)
        bfont3 = Font(name='宋体', size=11, color='00B050', bold=True)
        bfont4 = Font(name='黑体', size=11)
        border = Border(left=side, right=side, top=side, bottom=side)
        alignCenter = Alignment(horizontal='center', vertical='center')
        alignCenter2 = Alignment(horizontal='center', vertical='center', wrapText = True)
        alignCenter3 = Alignment(horizontal='left', vertical='center')
        ws.merge_cells("A1:I1")
        a1 = ws['A1']
        today = datetime.date.today()
        a1.value = f'德安县“一表同享”业务表单、部门任务下发统计（{today.year}年{today.month}月{today.day}日）'
        a1.font = Font(name='方正小标宋简体', size=16, bold=False)
        a1.alignment = alignCenter
        ws.row_dimensions[1].height = 30
        ws.row_dimensions[2].height = 25
        ws.row_dimensions[3].height = 30
        ws.row_dimensions[4].height = 70
        ws.row_dimensions[5].height = 30
        ws.row_dimensions[6].height = 30
        ws.row_dimensions[7].height = 30

        def COL(idx): return chr(ord('A') + idx)

        ws.column_dimensions['A'].width = 15
        for i in range(len(self.jcbbData)):
            ws.column_dimensions[COL(i + 1)].width = 10

        ws.merge_cells(f"A2:{COL(len(self.jcbbData))}2")
        a2 = ws[f'A2']
        a2.value = f'（县区级）'
        a2.font = Font(name='方正小标宋简体', size=15, color='000000', bold=False)
        a2.fill = GradientFill(stop = ('acb9ca', 'acb9ca'))
        a2.alignment = alignCenter3
        a2.border = border
        for am in ws[f'A2:{COL(len(self.jcbbData))}2'][0]:
            am.border = border

        row = 3
        for idx, title in enumerate(['责任单位', '表单总数', f'{month}月应发\n任务数', f'{month}月实发\n任务数', f'{month}月\n完成率']):
            c = ws.cell(row=row, column=1, value=title)
            c.fill = GradientFill(stop = ('FFFF00', 'FFFF00'))
            c.border = border
            c.font = Font(name='宋体', size = 11, bold = True)
            c.alignment = alignCenter2
            row += 1

        def GXPL(s):
            rr = ''
            for k in s:
                k2 = k
                if k == '实时更新': k2 = '实时'
                rr += k2 +  str(s[k]) + '\n'
            return rr.strip()
        
        def finishRate(m, c):
            if m == 0:
                return '' if c == 0 else '100%'
            if c >= m:
                return '100%'
            return f'{int(c / m * 100)}%'

        for idx, dept in enumerate(self.jcbbData):
            row = 3
            cur = self.jcbbData[dept]
            m = self.getTaskNumOfMonth(month, cur.get('更新频率', None))
            c = len(cur['tasks'])
            fp = finishRate(m, c)
            if m == 0: m = ''
            if not c and not m:
                c = ''
            vals = [dept, GXPL(cur.get('更新频率', [])), m, c, fp]
            for v in vals:
                c = ws.cell(row=row, column=idx+2, value=v)
                c.border = border
                if row == 3:
                    c.font = Font(name='黑体', size = 11, bold = False)
                    c.fill = GradientFill(stop = ('acb9ca', 'acb9ca'))
                else:
                    c.font = Font(name='宋体', size = 11, bold = True)
                c.alignment = alignCenter2
                row += 1
        wb.save(f'files/任务下发统计表_{datetime.date.today()}.xlsx')
        
    def simpleDeptName(self, n):
        if '人力资源和社会保障局' in n: return '县人社局'
        if '住房与城乡建设局' in n: return '县住建局'
        if '县卫生健康委员会' in n: return '县卫健委'
        return n.replace('德安', '')


def main():
    def addDay(day, daysNum):
        return day + datetime.timedelta(days = daysNum)
    TODAY = datetime.date.today()
    #print_村社区填报任务量()
    #print_村社区使用模板最多()

    # lf = LocalFile()
    # lf.load()

    # 下载任务、进度
    # authorization, decryptKey = window.key4
    downloader = TaskDownloader()
    downloader.enableUpdate = 1
    downloader.login()

    downloader.loadTasks()
    downloader.loadTemplate()
    downloader.loadProgress()

    if False:
        # startTime = input('开始日期:')
        # endTime = input('结束日期:') or TODAY
        # soonEndTime = input('即将到期日期:') or addDay(TODAY, 2)
        print_乡镇统计时间段(startTime = '2025-09-01', endTime = addDay(TODAY, 0), soonEndTime = addDay(TODAY, 5))
        print_县直部门待审核任务(startTime = '2025-06-01', endTime = '2099-12-31')

    if True:
        mgr = DeptTaskMgr()
        mgr.writeExcel(12)
        pass

    #-----------------------------------------------------
    if False:
        downloader.loadTasksFromRecv()
        year = TODAY.year
        month = TODAY.month
        weekStart = fmtDate(TODAY - datetime.timedelta(TODAY.weekday()))
        weekEnd = fmtDate(TODAY)
        print_市周报表数据(year, month, weekStart, weekEnd)

if __name__ == '__main__':
    main()