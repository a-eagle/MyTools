import peewee as pw
import sys, datetime, json

db_cc = pw.SqliteDatabase(f'files/cc.db')

def formatDateTime(datetime):
    return datetime.strftime('%Y-%m-%d %H:%M:%S')

class HistoryModel(pw.Model):
    history = pw.TextField(null = True)
    isDelete = pw.IntegerField(default = 0)
    createTime = pw.TextField(null = True)
    updateTime = pw.TextField(null = True)

    class Meta:
        database = db_cc

    @classmethod
    def diff(clazz, new : dict, old, updateTime):
        if not new:
            return
        NOW = formatDateTime(datetime.datetime.now())
        if not updateTime:
            updateTime = NOW
        if isinstance(updateTime, datetime.datetime):
            updateTime = formatDateTime(updateTime)
        cols = clazz._meta.columns
        skips = ('id', 'history', 'createTime', 'updateTime', 'isDelete')
        newKeys = new.keys()
        changedHistory = None
        changedCols = None
        for colName in cols:
            if colName in skips:
                continue
            if colName not in newKeys:
                continue
            newVal = new.get(colName, None)
            oldVal = getattr(old, colName) if old else None
            
            if newVal == oldVal:
                continue
            if (newVal == None or newVal == '') and (oldVal == None or oldVal == ''):
                continue # is same
            # is not same
            if changedHistory is None:
                changedHistory = []
                changedCols = []
            h = {'time': updateTime, 'col': colName, 'data': str(newVal if newVal else '')}
            changedCols.append(colName)
            changedHistory.append(h)
        return changedHistory, changedCols
    
    @classmethod
    def diffSave(clazz, src : dict):
        if not src:
            return False
        old = None
        if src and src.get('id', 0):
            old = clazz.get_or_none(int(src['id']))
        NOW = formatDateTime(datetime.datetime.now())
        hisData, modifyCols = clazz.diff(src, old, NOW)
        if not hisData:
            return True
        history = json.loads(old.history) if old and old.history else []
        history.extend(hisData)
        historyStr = json.dumps(history, ensure_ascii = False)
        if not old:
            srcData = clazz(**src)
            srcData.history = historyStr
            srcData.createTime = NOW
            srcData.save()
            return srcData
        else:
            old.history = historyStr
            old.updateTime = NOW
            for colName in modifyCols:
                setattr(old, colName, src.get(colName, None))
            old.save()
            return old

class JcbdModel(HistoryModel):
    bbnc = pw.TextField(default = '') # 报表名称
    fbcj = pw.TextField(default = '') # 发表层级
    ssbm = pw.TextField(default = '') # 所属部门
    sjx = pw.TextField(default = '') # 数据项（字段）
    sjxgs = pw.TextField(default = '') # 数据项个数
    tbcj = pw.TextField(default = '') # 填报层级
    bsfs = pw.TextField(default = '') # 报送方式
    ywxtmc = pw.TextField(default = '') # 业务系统名称
    gxpl = pw.TextField(default = '') # 更新频率
    gxsj = pw.TextField(default = '') # 更新时间
    lxr = pw.TextField(default = '') # 联系人
    jbr = pw.TextField(default = '') # 经办人
    bm = pw.TextField(default = '') # 县直部门
    ybtx_zh = pw.TextField(default = '') # 是否有一表同享账号
    ybtx_in = pw.TextField(default = '') # 是否在一表同享系统中
    ybtx_mb = pw.TextField(default = '') # 一表同享系统中模板名称
    mark = pw.TextField(default = '') # 备注
    sureTime = pw.TextField(null = True, default = '') # 确认时间

class UserModel(HistoryModel):
    name = pw.TextField()
    old = pw.TextField()


db_cc.create_tables([JcbdModel, UserModel])

if __name__ == '__main__':
    new = {'name' : 'user-2', 'old' :'old-1y', 'id': '1'} # id = 1,
    UserModel.diffSave(new)
    pass