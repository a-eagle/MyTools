# -*- coding: UTF-8 -*-

import dept
from urllib import request, error
import re
import time
import sqlite3
from datetime import date
import os

conn = sqlite3.connect('db/dept-out-time.db')
cur = conn.cursor()

def initDB():
    cur.execute("""
        CREATE TABLE _lm_info (
            _id INTEGER  PRIMARY KEY AUTOINCREMENT,
            _dept_name VARCHAR(120),
            _lm_name VARCHAR(120),
            _last_date VARCHAR(12),
            _url text
        )
     """)
    conn.commit()

def saveLMInfo(deptName, lmName, lastDate, url):
    sql = 'select _id from _lm_info where _dept_name = ? and _lm_name = ? '
    rs = cur.execute(sql, (deptName, lmName))
    for row in rs:
        sql = 'update _lm_info set _url = ? , _last_date = ? where _id = ? '
        cur.execute(sql, (url, lastDate, row[0]))
        return
    sql = 'insert into _lm_info (_dept_name, _lm_name, _last_date, _url) values (?, ?, ?, ?) '
    cur.execute(sql, (deptName, lmName, lastDate, url))

def loadUrl(url):
    try:
        response = request.urlopen(url)
        b = response.read()
        return b.decode('UTF-8')
    except error.HTTPError as e:
        #print(e.reason)
        return str(e.code)

def loadDeptHomePage_Links(url):
    text = loadUrl(url)
    idx = text.find('<!-- 信息公开树 开始 -->')
    if idx < 0:
        print('Not find tag <!-- 信息公开树 开始 -->')
        return False
    endIdx = text.find('<!-- 信息公开树 结束 -->', idx)
    text = text[idx : endIdx]
    # pattern = re.compile(r'<a\s+href\s*=\s*"(http[^"]+)"[^>]*>([^<]+)</a>', re.M)
    it = re.finditer(r'<a\s+href\s*=\s*"(http[^"]+)"[^>]*>([^<]+)</a>', text, re.M)
    d = []
    for m in it:
        url = m.group(1)
        name = m.group(2)
        d.append({'name': name, 'url': url})
    return d

def loadContentPage_LastDate(url):
    text = loadUrl(url)
    idx = text.find('<ul class="info-list">')
    if idx < 0:
        # print('Not find tag info-list')
        idx = text.find('http-equiv="refresh"')
        if idx > 0:
            # 是一个父栏目
            return 'IS-PA'
        print('occour unkow error, pause: ', url)
        return text

    # pattern = re.compile(r'<span>(\d{4}-{\d}2-\d{2})</span>', re.M)
    text = text[idx : ]
    it = re.finditer(r'<span>(\d{4}-\d{2}-\d{2})</span>', text, re.M)
    rs = ''
    for m in it:
        d = m.group(1)
        if rs < d:
            rs = d
    if rs == '':
        rs = 'IS-Empty'
    return rs

def loadOneDept(deptName, url):
    links = loadDeptHomePage_Links(url)
    for a in links:
        date = loadContentPage_LastDate(a['url'])
        print('Load ',deptName, ' ', a['name'], ' -> ', date[0: 30])
        saveLMInfo(deptName, a['name'], date, a['url'])
        time.sleep(1.5)
    conn.commit()

def loadAllDepts():
    y = True
    for d in dept.depts:
        print('-------', d['name'], '-------------')
        #if d['name'] == '塘山乡':
        #    y = True
        if not y:
            continue
        loadOneDept(d['name'], d['url'])

#initDB()

# startDate is YYYY-MM-DD
def diffDay(strDate):
    now = date.today()
    orc = date(int(strDate[0:4]), int(strDate[5:7]), int(strDate[8:10]))
    diff = now - orc
    return diff.days

def checkTime(lmName, lastDate):
    if len(lastDate) != 10:
        return ('No Check', 0)
    diff = diffDay(lastDate)
    if diff <= 10:
        return ('OK', diff)

    dp = [('修改失效文件', 335), ('动态', 10), ('文件', 120), ('人事信息', 335), \
            ('财政预算', 335), ('财政决算', 335), ('财政绩效评价', 335), \
            ('重点工作分解及进展', 180), ('重点工作完成情况', 180), ('工作报告', 180), ('政策解读', 180), \
            ('统计年报', 335), ('据统计与分析', 180), ('履职依据', 335), ('行政权力运行', 335), ('政务清单', 335), ('年度', 335), ('新闻发言人', 335), \
            ('投资政策', 120), ('公告', 180)]
    for it in dp:
        if lmName.find(it[0]) >= 0:
            return ('OK', diff) if diff <= it[1] else ('OUT-TIME', diff)

    return ('OK', diff) if diff <= 335 else ('OUT-TIME', diff)

# outForReload : bool
def checkAllTime(outForReload):
    if os.path.exists("result.js"):
        os.remove("result.js")
    sql = 'select _id, _dept_name, _lm_name, _last_date, _url from _lm_info where length(_last_date) == 10'
    rs = cur.execute(sql)
    rows = []
    for row in rs:
        et = checkTime(row[2], row[3])
        if et[0] is not 'OK':
            rows.append(row)
    for row in rows:
        et = None
        if outForReload:
            time.sleep(1.5)
            ld = loadContentPage_LastDate(row[4])
            if ld != row[3]:
                saveLMInfo(row[1], row[2], ld, row[4])
                conn.commit()
            et = checkTime(row[2], ld)
        else:
            et = checkTime(row[2], row[3])
        if et[0] is not 'OK':
            print(row[1], row[2], row[3], et, row[4])
    
if __name__ == '__main__':
    startTicks = time.time()
    #initDB()
    loadAllDepts()
    checkAllTime(True)
    endTicks = time.time()
    m = int(int(endTicks - startTicks) / 60)
    print('Use time: %d minutes' % (m))