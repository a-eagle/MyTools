import peewee as pw
import datetime, json

db = pw.SqliteDatabase('my.db')

class User(pw.Model):
    name = pw.CharField()
    password = pw.CharField(null = True)
    dept = pw.CharField(null = True)

    class Meta:
        table_name = 'users'
        database = db

class History(pw.Model):
    refTable = pw.CharField(column_name = 'ref_table')
    refId = pw.IntegerField(column_name = 'ref_id', null = True)
    info = pw.TextField(null = True)
    operatorName = pw.CharField(column_name = 'operator_name', null = True)
    createTime = pw.DateTimeField(column_name = 'create_time', formats='%Y-%m-%d %H:%M:%S', default = datetime.datetime.now)

    class Meta:
        table_name = 'history'
        database = db

    # beforeModel: is Model object
    # afterVal: is dict object
    # return a History object, Note: need update 'operatorName'
    @staticmethod
    def diffUpdateByModel(beforeModel, afterVal):
        if not afterVal or not beforeModel:
            return
        changed = {}
        clazz = beforeModel.__class__
        for k in afterVal:
            if getattr(beforeModel, k, None) != afterVal[k]:
                field = getattr(clazz, k)
                changed[field.column_name] = afterVal[k]
        meta = beforeModel.__class__._meta
        info = json.dumps(changed, ensure_ascii = False)
        h = History(refTable = meta.table_name, refId = beforeModel.id, info = info)
        return h
    
    # afterVal: is dict object
    # return a History object, Note: need update 'operatorName'
    @staticmethod
    def diffUpdateById(modelClass, refId, afterVal):
        obj = modelClass.get_or_none(refId)
        if not obj:
            return None
        return History.diffUpdateByModel(obj, afterVal)
    
db.create_tables([User, History])
#User.create(name = 'GY', password = 'kdk')

u = User.get_or_none(6)
h = History.diffUpdateByModel(u, {'name': 'G"Yxx是这x', 'password': 'kdk'})
h.operatorName = 'Six'
h.save()
