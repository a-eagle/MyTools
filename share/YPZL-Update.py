import pymysql, datetime, random, time

db : pymysql.connections.Connection = None

def openDB():
    global db
    db = pymysql.connect(host='10.119.81.253', port=3306, user='root', password='Root@2020', database='ZWShare', autocommit = 1)

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
    return datas

def 环卫车辆日统计情况():
    today = datetime.datetime.today()
    yestoday = today - datetime.timedelta(days=1)
    cc = db.cursor()
    sql = f'update efa921c1731b4f1a50bb3fd02e6fe1385 set _c04 = "{yestoday.strftime("%Y.%m.%d")}", _c03 = "{random.randint(0, 2)}"'
    print('环卫车辆日统计情况', sql)
    cc.execute(sql)
    cc.close()

def 环卫作业量情况():
    cc = db.cursor()
    today = datetime.datetime.today()
    yestoday = today - datetime.timedelta(days=1)
    data = selectAll('select _c01, _c02, _c03 from ef4c4e9222fa50b2caa443029cb8b599f')[0] # 年份  月份  作业量
    print('环卫作业量情况', data)
    if int(data[0]) == yestoday.year and int(data[1]) == yestoday.month:
        zyl = int(float(data[2])) + random.randint(2904 - 100, 2904 + 100)
        sql = f'update ef4c4e9222fa50b2caa443029cb8b599f set _c03 = "{zyl}"'
    else:
        zyl = random.randint(2904 - 100, 2904 + 100)
        sql = f'update ef4c4e9222fa50b2caa443029cb8b599f set _c01 ="{yestoday.year}", _c02="{yestoday.month}", _c03 = "{zyl}"'
    print('环卫作业量情况 sql=', sql)
    cc.execute(sql)
    cc.close()

def 环卫整体统计情况():
    cc = db.cursor()
    today = datetime.datetime.today()
    yestoday = today - datetime.timedelta(days=1)
    yestoday = yestoday.strftime('%Y-%m-%d')
    sql = f'update e913885429c257812fb25ad8914f46b58 set _c13 = "{yestoday}" ,_c11 = "{random.randint(10, 35)}", _c12="{random.randint(10, 20)}"'  # 日期(昨日), 今日车务提醒次数, 今日异常报警次数
    cc.execute(sql)
    print('环卫整体统计情况 sql = ', sql)
    cc.close()

def 环卫垃圾数月统计情况():
    cc = db.cursor()
    today = datetime.datetime.today()
    yestoday = today - datetime.timedelta(days=1)
    data = selectAll('select _c05, _c04 from e01a96701575b38c594fe681dc24af1ef')[0] # 年月(yyyy.mm)  垃圾处理量
    ym = yestoday.strftime('%Y.%m')
    if data[0] == ym:
        cll = int(data[1]) + random.randint(125, 135)
    else:
        cll = random.randint(125, 135)
    sql = f'update e01a96701575b38c594fe681dc24af1ef set _c05 = "{ym}", _c04 = "{cll}" '
    print('环卫垃圾数月统计情况 sql=', sql)
    cc.execute(sql)
    cc.close()

def 市民热线12345工作情况():
    cc = db.cursor()
    data = selectAll('select _c01, _c02 from ec4fd304eab4c9fd7e936b149f0a4853b')[0]
    qz, ts = int(data[0][0:-1]), int(data[1][0:-1])
    qz += random.randint(8, 15)
    ts += random.randint(3, 7)
    sql = f'update ec4fd304eab4c9fd7e936b149f0a4853b set _c01="{qz}件", _c02="{ts}件" '
    print('市民热线12345工作情况 sql=', sql)
    cc.execute(sql)
    cc.close()

def updateOneDay():
    try:
        openDB()
        环卫车辆日统计情况()
        环卫作业量情况()
        环卫整体统计情况()
        环卫垃圾数月统计情况()
        #市民热线12345工作情况()
        closeDB()
    except Exception as e:
        print('Exception:', e)

if __name__ == '__main__':
    lastDay = '2024-01-02'
    while True:
        today = datetime.datetime.today()
        sd = today.strftime('%Y-%m-%d')
        if sd == lastDay:
            time.sleep(600)
            continue
        lastDay = sd
        updateOneDay()
        pass