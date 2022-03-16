# -*- coding: UTF-8 -*-

# 检查错链、 身份证、手机号、银行卡脱敏处理

import dept
from urllib import request, error
from urllib.parse import urljoin
import re
import time
import sqlite3
from datetime import date
import os
import random


conn = sqlite3.connect('db/check-url.db')
cur = conn.cursor()

def initDB():
    # status: 200, 404 
    # is_loaded: yes, no 是否加载网页
    # content_type: text/html ....
    cur.execute("""
        CREATE TABLE _urls_info (
            _id INTEGER  PRIMARY KEY AUTOINCREMENT,
            title text,
            url text,
            parent_url text,
            status varchar(24),
            is_loaded varchar(8),
            content_type varchar(64),
            content text,
            sec_err text
        )
     """)
    conn.commit()

def getTitle(cnt):
    if type(cnt) != str:
        return ''
    it = re.finditer(r'<title\s*?>(.*?)</title\s*?>', cnt, re.I | re.S)
    for m in it:
        return m.group(1).replace('\n', '')
    return ''


# @return {status: 200, content:'', ...}
def loadUrl(url):
    r = {'status': 0, 'title': '', 'content': '', 'is_loaded': 'yes', 'content_type': ''}
    try:
        response = request.urlopen(url)
        r['status'] = response.status
        if response.status == 200:
            if 'www.dean.gov.cn' in url:
                r['content_type'] = response.getheader('Content-Type')
                b = response.read()
                r['content'] = b.decode('UTF-8')
                r['title'] = getTitle(r['content'])
    except error.HTTPError as e:
        r['content'] = e.reason
        r['status'] = e.code
    except Exception as e:
        print(e.args, url)
        r['content'] = str(e.args)
        pass
    return r

# return [{'url': url, 'title': title}, ..]
def getUrls(cnt, curUrl):
    r = []
    if type(cnt) != str:
        return r
    it = re.finditer(r'<a\s+.*?href\s*=\s*["\']([^"\']+)', cnt, re.S | re.I)
    idx = 0
    for m in it:
        url = m.group(1)
        url = url.replace('"', "")
        url = url.replace("'", "")
        if (url.startswith('javascript')):
            continue
        url = urljoin(curUrl, url)
        r.append({'url': url, 'title': None})
        idx += 1
        # print(idx, url)
    return r

def queryUrlInfo(url):
    rs = cur.execute('select * from _urls_info where url = ?', [url])
    for row in rs:
        return  {'_id': row[0], 'title':row[1], 'url':row[2] , 'parent_url':row[3],  'status':row[4] , 'is_loaded': row[5], 'content_type': row[6], 'content': row[7], 'sec_err': row[8]}
    return None

def insertUrlInfo(info):
    if not info:
        return False
    if hasattr(info, '_id'):
        return False
    sql = r'insert into _urls_info (title, url, parent_url, status, is_loaded, content_type, content, sec_err) values (?, ?, ?, ?, ?, ?, ?, ?)'
    cur.execute(sql, (info['title'], info['url'], info['parent_url'], info['status'], info['is_loaded'], info['content_type'], '', info['sec_err']))
    conn.commit()
    return True

# info is {_id ?, 'title':, 'url': , 'parent_url':,  'status': , 'cnt': '', 'is_loaded': 'yes', 'content_type': ''}
def updateUrlInfo(info):
    if not info:
        return False
    if not info['_id']:
        return False
    sql = 'update _urls_info set title = ?, status = ?, is_loaded = ?, content_type = ?, content = ?, sec_err = ? where _id = ?'
    cur.execute(sql, (info['title'], info['status'], info['is_loaded'], info['content_type'], info['content'], info['sec_err'], info['_id']))
    conn.commit()
    return True

def trySaveNew(info):
    nn = queryUrlInfo(info['url'])
    if nn is not None:
        return False
    sql = r'insert into _urls_info (title, url, parent_url, status, is_loaded, content_type, content) values (?, ?, ?, ?, ?, ?, ?)'
    cur.execute(sql, (info['title'], info['url'], info['parent_url'], 0, 'no', '', ''))
    conn.commit()
    return True

def checkSecError(info):
    #  and ( 'text' in info['content_type'])
    if not( info['content'] ):
        return
    sec = []
    # check sheng fen zheng card
    r = re.finditer(r'(?<!\d)360426\d{11}[xX0-9](?!\d)', info['content'], re.S)
    for m in r:
        sec.append(m.group(0))
    # check ying hang card
    r = re.finditer(r'(?<!\d)\d{16-19}(?!\d)', info['content'], re.S)
    for m in r:
        sec.append(m.group(0))
    # check shou ji hao ma
    r = re.finditer(r'(?<!\d)\d{11}(?!\d)', info['content'], re.S)
    for m in r:
        sec.append(m.group(0))
    info['sec_err'] = ','.join(sec)

def loadOne(info):
    if info and info['is_loaded'] == 'yes':
        return
    r = loadUrl(info['url'])
    info['status'] = r['status']
    info['content'] = r['content']
    info['is_loaded'] = r['is_loaded']
    info['content_type'] = r['content_type']
    if not info['title']:
        info['title'] = r['title']

    if r['content']:
        subUrls = getUrls(r['content'], info['url'])
        for s in subUrls:
            v = {'title': s['title'], 'url' : s['url'], 'parent_url': info['url']}
            sx = trySaveNew(v)
            if sx:
                v['content'] = ''
                # print('get sub -> ', v)
        checkSecError(info)
    if (info['status'] == 200):
        info['content'] = ''
    updateUrlInfo(info)
    conn.commit()
    

def fetchOne():
    # sql = 'select * from _urls_info where _id = 9365 LIMIT 1'
    sql = 'select * from _urls_info where is_loaded = "no" LIMIT 1'
    rs = cur.execute(sql)
    for row in rs:
        v = {'_id': row[0], 'title': row[1], 'url' : row[2], 'parent_url': row[3], 'status': row[4], 'is_loaded': row[5], 'content_type':row[6], 'content':row[7], 'sec_err': row[8]}
        return v
    return None

def sleep():
    s = 2 # random.uniform(3.8, 8.8)
    time.sleep(s)

if __name__ == '__main__':
    # initDB()
    # v = {'title':'', 'status':0, 'url': 'http://www.dean.gov.cn', 'parent_url':'', 'is_loaded': 'no', 'content_type':'', 'content':'', 'sec_err':''}
    # insertUrlInfo(v)

    # cur.execute('update  _urls_info set title = replace(title, "\n", "") ')
    # conn.commit()
    
    while True:
        v = fetchOne()
        if not v:
            break
        loadOne(v)
        time.sleep(1.5)
        