import peewee as pw
import datetime, json

db = pw.SqliteDatabase('my.db')

class Person(pw.Model):
    xz = pw.CharField(null = True)
    addr = pw.CharField(null = True)
    name = pw.CharField(null = True)
    idcard = pw.CharField(null = True)
    jtgx = pw.CharField(null = True)

    flag = pw.IntegerField(default = 0)
    suggest_1 = pw.TextField(null = True)
    suggest_2 = pw.TextField(null = True)
    suggest_3 = pw.TextField(null = True)
    suggest_4 = pw.TextField(null = True)
    suggest_5 = pw.TextField(null = True)
    info = pw.TextField(null = True)
    result = pw.TextField(null = True)

    class Meta:
        table_name = 'person'
        database = db

class Info(pw.Model):
    data = pw.TextField(null = True)

    class Meta:
        table_name = 'info'
        database = db

db.create_tables([Person, Info])


def _test():
    import persons
    rs = []
    for it in persons.personInfos:
        cols = it.split('\t')
        if len(cols) != 4:
            print('Error:', cols)
        addr, name, idcard, jtgx = cols
        rs.append(cols)
    i = 0
    while i < len(rs):
        spec = rs[i : min(i + 100, len(rs))]
        Person.insert_many(spec, ('addr', 'name', 'idcard', 'jtgx')).execute()
        i += 100

#_test()
