import peewee as pw, json, requests, datetime, time, urllib.parse, os, sys, re

sys.path.append(__file__[0 : __file__.upper().index('任务管理')])

db = pw.SqliteDatabase('任务管理/tasks.db')

class LocalTemplateModel(pw.Model):
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

class TaskModel(pw.Model):
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
class RecvTaskModel(pw.Model):
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

class DelTaskModel(pw.Model):
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

class UserModel(pw.Model):
    userId = pw.CharField()
    username = pw.CharField(null = True) # phone number
    nickname = pw.CharField(null = True) #创建者
    email = pw.CharField(null = True)
    phonenumber = pw.CharField(null = True)
    status = pw.CharField(null = True)
    roles =  pw.CharField(null = True) # json data
    depts =  pw.CharField(null = True) # json data
    userPosition = pw.CharField(null = True)

    class Meta:
        database = db

class DeptModel(pw.Model):
    deptId = pw.CharField() # 480845479616935
    parentId = pw.CharField(null = True)
    deptName = pw.CharField(null = True) # 大坂村委会
    businessType = pw.CharField(null = True)
    regionCode = pw.CharField(null = True) # 360426103203
    levelNum = pw.CharField(null = True)
    ancestors =  pw.CharField(null = True) #  480845479616935,486770361569304,486770361569336,486842392252788,486840248607527
    ancestorsName =  pw.CharField(null = True) # 江西省>九江市>德安县>德安县丰林镇>大坂村委会
    status = pw.CharField(null = True)
    regionCodeLabel = pw.CharField(null = True) # 江西省>九江市>德安县>丰林镇>大坂村委会

    class Meta:
        database = db

db.create_tables([TaskModel, LocalTemplateModel, DelTaskModel, RecvTaskModel, UserModel, DeptModel])
