import pymysql, datetime, random, time

db : pymysql.connections.Connection = None

def openDB():
    global db
    db = pymysql.connect(host='10.119.84.80', port=3306, user='root', password='Root@2020', database='ZWShare', autocommit = 1)

def closeDB():
    db.close()

def selectAll(sql):
    cc = db.cursor()
    cc.execute(sql)
    rs = cc.fetchall()
    datas = []
    for r in rs:
        datas.append(r)
    cc.close()
    print(datas)
    return datas

def main():
    today = datetime.datetime.today()
    yestoday = today - datetime.timedelta(days=1)
    cc = db.cursor()
    sql = f'select * from _user'
    print('环卫车辆日统计情况', sql)
    selectAll(sql)

openDB()
main()