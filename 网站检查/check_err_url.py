# -*- coding: UTF-8 -*-

# 检查错链、 身份证、手机号、银行卡脱敏处理

from email.policy import default
import pymysql
import dept
from urllib.parse import urljoin
import requests
import re
import time
import peewee
from datetime import date
import os
import pyquery

db = peewee.SqliteDatabase('db/check_url.db')
ss = requests.Session()

class Link(peewee.Model):
    title = peewee.TextField(null = True)
    url = peewee.TextField(null = True, unique = True)
    parent_url = peewee.TextField(null = True)
    status_code = peewee.CharField(null = True)
    is_loaded = peewee.BooleanField(null = True, default = False)
    content_type = peewee.CharField(null = True, max_length = 64)
    content = peewee.TextField(null = True)
    sec_err = peewee.TextField(null = True)
    net_err = peewee.TextField(null = True)

    class Meta:
        database = db
        db_table = '_link'


def getTitle(cnt):
    cnt = pyquery.PyQuery(cnt)
    t = cnt.find('title')
    s = t.text()
    return s.replace('\n', '')

def getUrls(cnts, curUrl):
    if not cnts:
        return []

    cc = re.finditer(r'<meta\s+http-equiv="refresh"\s+content=["\'](.*?)["\']', cnts, re.S | re.I)
    meta = None
    for c in cc:
        meta = c.group(1)[6:]
        meta = urljoin(curUrl, meta)
        hs = Link.get_or_none(Link.url == meta)
        if hs is None:
            v = Link( url = meta, parent_url = curUrl)
            return [v]
        return []

    cnt = pyquery.PyQuery(cnts)
    a = cnt.find('a').items()
    data = []
    pageUrls = {}
    for it in a:
        stitle = it.attr('title')
        if not stitle:
            stitle = it.text()
        surl = it.attr('href')
        if (not surl) or surl.startswith('javascript:'):
            continue
        surl = urljoin(curUrl, surl)
        if surl in pageUrls:
            d = pageUrls[surl]
            if not d.title:
                d.title = stitle
            continue
        hs = Link.get_or_none(Link.url == surl)
        if hs is None:
            v = Link(title = stitle, url = surl, parent_url = curUrl)
            data.append(v)
            pageUrls[surl] = v
    return data


def loadLink(link):
    link.is_loaded = True
    try:
        rs = ss.get(link.url)
    except Exception as e:
        link.net_err = str(e.args)
        print(e.args, link.url)
        return
    link.status_code = rs.status_code
    link.content_type = rs.headers['Content-Type']
    if (rs.status_code == 200) and ('www.dean.gov.cn' in link.url):
        if 'text/html' in link.content_type:
            link.content = rs.text
            if not link.title:
                link.title = getTitle(link.content)

def checkSecError(link):
    if not link.content:
        return
    if 'text/html' in link.content_type:
        sec = []
        # check sheng fen zheng card
        r = re.finditer(r'(?<!\d)360426\d{11}[xX0-9](?!\d)', link.content, re.S)
        for m in r:
            sec.append(m.group(0))
        # check ying hang card
        r = re.finditer(r'(?<!\d)\d{16-19}(?!\d)', link.content, re.S)
        for m in r:
            sec.append(m.group(0))
        # check shou ji hao ma
        r = re.finditer(r'(?<!\d)\d{11}(?!\d)', link.content, re.S)
        for m in r:
            sec.append(m.group(0))
        link.sec_err = ','.join(sec)

def loadOne(link):
    loadLink(link)
    subLinks = getUrls(link.content, link.url)
    checkSecError(link)
    link.content = ''
    link.save()
    Link.bulk_create(subLinks)

if __name__ == '__main__':
    # Link.drop_table()
    Link.create_table()
    # Link.delete().execute()
    # Link.create(url = 'http://www.dean.gov.cn/')
    while True:
        one = Link.get_or_none(Link.is_loaded == False)
        if not one:
            break
        loadOne(one)
        time.sleep(1.5)
        break