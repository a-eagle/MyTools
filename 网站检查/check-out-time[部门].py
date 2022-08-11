# -*- coding: UTF-8 -*-

# from tkinter.tix import Tree
# from sqlalchemy import column, null, table
import dept
from urllib import request, error
from urllib.parse import urljoin
import re
import time
import sqlite3
from datetime import date
import os, peewee as pw
from bs4 import BeautifulSoup

db = pw.SqliteDatabase('db/dept-out-time.db')


class LMInfo(pw.Model):
    id = pw.PrimaryKeyField(column_name='_id')
    deptName = pw.CharField(column_name='_dept_name')
    lmName = pw.CharField(column_name='_lm_name')
    lastDate = pw.CharField(column_name='_last_date')
    url = pw.CharField(column_name='_url')

    class Meta:
        database = db
        table_name = '_lm_info'

db.create_tables([LMInfo])


def saveLMInfo(deptName, lmName, lastDate, url):
    info = LMInfo.get_or_none(deptName = deptName, lmName = lmName)
    if not info:
        info = LMInfo.create(deptName = deptName, lmName = lmName, lastDate=lastDate, url=url)
    else:
        info.lastDate = lastDate
        info.url = url
    info.save()
    return info

def loadUrl(url):
    try:
        response = request.urlopen(url)
        b = response.read()
        return b.decode('UTF-8')
    except error.HTTPError as e:
        #print(e.reason)
        return 'HttpError: ' + str(e.code)

def loadDeptHomePage_Links(url):
    text = loadUrl(url)
    idx = text.find('<!-- 信息公开树 开始 -->')
    if idx < 0:
        print('Not find tag <!-- 信息公开树 开始 -->')
        return False
    endIdx = text.find('<!-- 信息公开树 结束 -->', idx)
    text = text[idx : endIdx]
    # pattern = re.compile(r'<a\s+href\s*=\s*"(http[^"]+)"[^>]*>([^<]+)</a>', re.M)
    it = re.finditer(r'<a\s+href\s*=\s*"(http[^"]+)"[^>]*>([^<]+)</a>', text, re.M | re.I)
    d = []
    for m in it:
        url = m.group(1)
        name = m.group(2)
        d.append({'name': name, 'url': url})
    return d

def loadContentPage_LastDate(url):
    if not 'http://www.dean.gov.cn/' in url:
        return 'Not-Dean-Domain'
        
    text = loadUrl(url)
    idx = text.find('<ul class="info-list"')
    if idx < 0:
        # print('Not find tag info-list')
        idx = text.find('http-equiv="refresh"')
        if idx > 0:
            # 是一个父栏目
            return 'IS-PA'
        print('Not find last date in: ', url)
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
        time.sleep(0.5)
        date = loadContentPage_LastDate(a['url'])
        print('Load ',deptName, ' ', a['name'], ' -> ', date[0: 30])
        saveLMInfo(deptName, a['name'], date, a['url'])

def loadAllDepts():
    y = True
    for d in dept.depts:
        print('-------', d['name'], '-------------')
        loadOneDept(d['name'], d['url'])

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

    dp = [('修改失效文件', 365), ('动态', 10), ('文件', 120), ('人事信息', 365), \
            ('财政预算', 365), ('财政决算', 365), ('财政绩效评价', 365), \
            ('重点工作分解及进展', 180), ('重点工作完成情况', 180), ('工作报告', 180), ('政策解读', 180), \
            ('统计年报', 365), ('据统计与分析', 180), ('履职依据', 365), ('行政权力运行', 365), ('政务清单', 365), ('年度', 365), ('新闻发言人', 365), \
            ('投资政策', 120), ('公告', 180), ('.*', 365)]
            
    yj = {365: 335, 180: 160}
    for name, day in dp:
        if re.search(name, lmName):
            if diff >= day:
                return ('OUT-TIME', diff)
            if (day in yj) and (diff >= yj[day]):
                return ('BE-OUT-TIME', diff)
            return ('OK', diff)
    return ('Match-Error', diff)
    

# outForReload : bool
def checkAllTime(outForReload):
    file = open('out-time.txt', 'w')
    print('单位', '栏目', '最后更新日期', '超期', '地址', sep='\t', file = file)
    rs = LMInfo.select().where(pw.SQL('length(_last_date) == 10'))
    print(rs)
    infos = []
    for info in rs:
        et = checkTime(info.lmName, info.lastDate)
        if et[0] is not 'OK':
            infos.append(info)
    for info in infos:
        et = None
        if outForReload:
            time.sleep(1)
            ld = loadContentPage_LastDate(info.url)
            if ld != info.lastDate:
                info.lastDate = ld
                info.save()
        et = checkTime(info.lmName, info.lastDate)
        if et[0] is 'OK':
            continue
        tag = {'OUT-TIME': '已超期', 'BE-OUT-TIME': '即将超期'}
        print(info.deptName, info.lmName, info.lastDate, tag.get(et[0], et[0]), info.url, sep = '\t', file = file)
        print(info.deptName, info.lmName, info.lastDate, et, info.url)
    file.close()
    
def reloadError():
    infos = LMInfo.select().where(pw.SQL("_last_date == 'IS-Empty'"))
    for info in infos:
        date = loadContentPage_LastDate(info.url)
        print('Reload ',info.deptName, info.lmName, ' -> ', date[0: 30])
        if date != info.lastDate:
            info.lastDate = date
            info.save()

# ----------基层两化专题专区--------------
def loadAllZhuanQu():
    url = 'http://www.dean.gov.cn/ztzl/jczwgklh/index.html'
    text = loadUrl(url)
    # 吴山镇
    loadOneZhuanQu('吴山镇[专区]', 'http://www.dean.gov.cn/ztzl/zwgkzl/wszzt/')
    
def loadOneZhuanQu(deptName, url):
    text = loadUrl(url)
    soup = BeautifulSoup(text,'lxml')
    node = soup.find(text = '公开领域').parent
    gkly_url = urljoin(url, node.attrs['href'])
    nodes = soup.select('ul.row')
    ul = nodes[len(nodes) - 1]
    a = ul.select('a')
    cunInfos = []
    for m in a:
        cun = {}
        cun['name'] = m.text
        cun['url'] = urljoin(url, m.attrs['href'])
        cunInfos.append(cun)
        
    loadZhuanQuLinks(deptName, '', gkly_url)
    for m in cunInfos:
        loadZhuanQuLinks(deptName, m['name'], m['url'])

def directUrl(url):
    text = loadUrl(url)
    idx = text.find('http-equiv="refresh"')
    if idx < 0:
        return text
    idx = text.find('URL=')
    text = text[idx + 4 : ]
    idx = text.find("'")
    durl = text[0 : idx].strip()
    url = urljoin(url, durl)
    return directUrl(url)

def loadZhuanQuLinks(deptName, cun, url):
    print('loadZhuanQuLinks', deptName, cun, url)
    text = directUrl(url)
    soup = BeautifulSoup(text,'lxml')
    ula = soup.select('ul.info-tree a')
    for a in ula:
        lmName = a.text
        lmUrl = a.attrs['href']
        date = loadZhuanQu_LastDate(lmUrl)
        print('Load ',deptName, ' ', lmName, ' -> ', date[0: 30], lmUrl)
        saveLMInfo(deptName, lmName, date, lmUrl)

def loadZhuanQu_LastDate(url):
    if not 'http://www.dean.gov.cn/' in url:
        return 'Not-Dean-Domain'
        
    text = loadUrl(url)
    idx = text.find('<ul class="info-tree">')
    if idx < 0:
        # print('Not find tag info-list')
        idx = text.find('http-equiv="refresh"')
        if idx > 0:
            # 是一个父栏目
            return 'IS-PA'
        print('Not find last date in: ', url)
        return text

    # pattern = re.compile(r'<span>(\d{4}-{\d}2-\d{2})</span>', re.M)
    text = text[idx : ]
    it = re.finditer(r'<span\s+class="date">\s*(\d{4}-\d{2}-\d{2})\s*</span>', text, re.M)
    rs = ''
    for m in it:
        d = m.group(1)
        if rs < d:
            rs = d
    if rs == '':
        rs = 'IS-Empty'
    return rs

if __name__ == '__main__':
    #reloadError()
    
    startTicks = time.time()
    #loadAllDepts()
    #loadAllZhuanQu()
    checkAllTime(True)
    endTicks = time.time()
    m = int(int(endTicks - startTicks) / 60)
    print('Use time: %d minutes' % (m))
    
    
    