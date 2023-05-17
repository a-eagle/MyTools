# -*- coding: UTF-8 -*-
# 检查县级部门超时情况

import dept
from urllib import request, error
import re
import time
import sqlite3
from datetime import date
import os


#  every item is {dept:, url:, lmName?:,  partern:, maxDay: , result: , status: 'OK | Out-Time | Net-Error | Empty-LM', lastDay:'', diff: }
pagesInfo = []

# startDate is YYYY-MM-DD
def diffDay(strDate):
    now = date.today()
    orc = date(int(strDate[0:4]), int(strDate[5:7]), int(strDate[8:10]))
    diff = now - orc
    return diff.days

def loadUrl(url):
    try:
        response = request.urlopen(url)
        b = response.read()
        return b.decode('UTF-8')
    except error.HTTPError as e:
        print('Load url fail:', e.reason, url)
        return str(e.code)

def fetchPageInfo(item):
    html = loadUrl(item['url'])
    if len(html) < 20:
        item['result'] = html
        item['status'] = 'Net-Error'
        return
    days = re.finditer(item['partern'], html, re.S)
    r = ''
    for m in days:
        d = m.group(1)
        if d > r:
             r = d
    if not r:
        item['status'] = 'Empty-LM'
        return
    
    df = diffDay(r)
    item['diff'] = df
    maxDay = item.get('maxDay', 365)
    beDays = {365: 335, 30 : 30}
    be = beDays.get(maxDay, maxDay)
    if df > maxDay:
        item['status'] = '已超期'
    elif df > be:
        item['status'] = '即将超期'
    else:
        item['status'] = 'OK'
    item['lastDay'] = r

def init():
    # 专题专栏
    partern = r"<span[^>]*>\s*(\d{4}-\d{2}-\d{2})\s*</span>"
    
    pagesInfo.append({ 'lmName': '德安县政府部门行政权力清单', 'url' : 'http://www.dean.gov.cn/ztzl/xzspggzl/daxzfbmxzqlqd/',  'partern': partern})
    pagesInfo.append({ 'lmName': '德安县“一次不跑”清单', 'url' : 'http://www.dean.gov.cn/ztzl/xzspggzl/daxycbpqd/',  'partern': partern})
    pagesInfo.append({ 'lmName': '德安县行政事业性收费', 'url' : 'http://www.dean.gov.cn/ztzl/xzspggzl/daxxzsyxsf/',  'partern': partern})
    pagesInfo.append({ 'lmName': '奋斗百年路 启航新征程', 'url' : 'http://www.dean.gov.cn/ztzl/fdbnl/index.html',  'partern': partern})
    # pagesInfo.append({ 'lmName': '防控疫情', 'url' : 'http://www.dean.gov.cn/ztzl/fkyq/',  'partern': partern})
    pagesInfo.append({ 'lmName': '重要政策', 'url' : 'http://www.dean.gov.cn/ztzl/czzjzdjc/zyzc/',  'partern': partern})
    pagesInfo.append({ 'lmName': '工作进程及总结', 'url' : 'http://www.dean.gov.cn/ztzl/czzjzdjc/gzjcjzj/',  'partern': partern})
    pagesInfo.append({ 'lmName': '新春走基层', 'url' : 'http://www.dean.gov.cn/ztzl/xczjc/',  'partern': partern})
    pagesInfo.append({ 'lmName': '做好“六稳”工作 落实“六保”任务', 'url' : 'http://www.dean.gov.cn/ztzl/lwlb/',  'partern': partern})
    pagesInfo.append({ 'lmName': '践行核心价值观', 'url' : 'http://www.dean.gov.cn/ztzl/jxhxjzg/',  'partern': partern})
    pagesInfo.append({ 'lmName': '公益广告', 'url' : 'http://www.dean.gov.cn/ztzl/jxhxjzg/gygg/',  'partern': partern})
    pagesInfo.append({ 'lmName': '文明礼仪', 'url' : 'http://www.dean.gov.cn/ztzl/jxhxjzg/wmly2/',  'partern': partern})
    pagesInfo.append({ 'lmName': '科普宣传', 'url' : 'http://www.dean.gov.cn/ztzl/jxhxjzg/kpxc2/',  'partern': partern})
    pagesInfo.append({ 'lmName': '“五型”政府', 'url' : 'http://www.dean.gov.cn/ztzl/wxzf/',  'partern': partern})
    pagesInfo.append({ 'lmName': '专题报道', 'url' : 'http://www.dean.gov.cn/ztzl/wxzf/gzyw/',  'partern': partern})
    pagesInfo.append({ 'lmName': '政策文件', 'url' : 'http://www.dean.gov.cn/ztzl/wxzf/zcwj/',  'partern': partern})
    pagesInfo.append({ 'lmName': '卫生和健康教育', 'url' : 'http://www.dean.gov.cn/ztzl/wshjkjy/',  'partern': partern})
    pagesInfo.append({ 'lmName': '信息化建设', 'url' : 'http://www.dean.gov.cn/ztzl/xxhjs/',  'partern': partern})
    pagesInfo.append({ 'lmName': '专题报道', 'url' : 'http://www.dean.gov.cn/ztzl/xxhjs/gzyw_157153/',  'partern': partern})
    pagesInfo.append({ 'lmName': '政策文件', 'url' : 'http://www.dean.gov.cn/ztzl/xxhjs/zcwj_157154/',  'partern': partern})
    pagesInfo.append({ 'lmName': '工作推进', 'url' : 'http://www.dean.gov.cn/ztzl/jczwgklh/gztj/',  'partern': partern})
    pagesInfo.append({ 'lmName': '政策指导', 'url' : 'http://www.dean.gov.cn/ztzl/jczwgklh/zczd/',  'partern': partern})
    pagesInfo.append({ 'lmName': '标准目录', 'url' : 'http://www.dean.gov.cn/ztzl/jczwgklh/bzml/',  'partern': partern})
    pagesInfo.append({ 'lmName': '禁毒专栏', 'url' : 'http://www.dean.gov.cn/ztzl/jdzl/',  'partern': partern})
    pagesInfo.append({ 'lmName': '资源信息共享目录', 'url' : 'http://www.dean.gov.cn/ztzl/zyxxgxml/',  'partern': partern})
    pagesInfo.append({ 'lmName': '身边好人榜', 'url' : 'http://www.dean.gov.cn/ztzl/sbhrb/',  'partern': partern})
    # pagesInfo.append({ 'lmName': '', 'url' : '',  'partern': partern})

    #走进德安
    partern2 = r"发布日期：\s*(\d{4}-\d{2}-\d{2})"
    pagesInfo.append({ 'lmName': '历史沿革', 'url' : 'http://www.dean.gov.cn/zjda/lsyg/202006/t20200609_3957066.html',  'partern': partern2})
    pagesInfo.append({ 'lmName': '人口民族', 'url' : 'http://www.dean.gov.cn/zjda/rkmz/202006/t20200609_3957178.html',  'partern': partern2})
    pagesInfo.append({ 'lmName': '行政区划', 'url' : 'http://www.dean.gov.cn/zjda/xzqh/202006/t20200615_4032428.html',  'partern': partern2})
    pagesInfo.append({ 'lmName': '地理气候', 'url' : 'http://www.dean.gov.cn/zjda/dlqh/202006/t20200615_4032431.html',  'partern': partern2})
    pagesInfo.append({ 'lmName': '自然资源', 'url' : 'http://www.dean.gov.cn/zjda/zrzy/202006/t20200615_4032445.html',  'partern': partern2})
    pagesInfo.append({ 'lmName': '城镇建设', 'url' : 'http://www.dean.gov.cn/zjda/czjs/202006/t20200615_4032449.html',  'partern': partern2})
    pagesInfo.append({ 'lmName': '经济状况', 'url' : 'http://www.dean.gov.cn/zjda/jjzk/202006/t20200615_4032451.html',  'partern': partern2})
    pagesInfo.append({ 'lmName': '产业结构', 'url' : 'http://www.dean.gov.cn/zjda/cyjg/202006/t20200615_4032455.html',  'partern': partern2})
    pagesInfo.append({ 'lmName': '社会事业', 'url' : 'http://www.dean.gov.cn/zjda/shsy/202006/t20200615_4032461.html',  'partern': partern2})
    pagesInfo.append({ 'lmName': '交通邮电', 'url' : 'http://www.dean.gov.cn/zjda/jtyd/202006/t20200615_4032465.html',  'partern': partern2})

    #投资旅游
    pagesInfo.append({ 'lmName': '招商信息', 'url' : 'http://www.dean.gov.cn/tzly/zsxx/',  'partern': partern})
    pagesInfo.append({ 'lmName': '投资指南', 'url' : 'http://www.dean.gov.cn/tzly/tzzn/',  'partern': partern})
    pagesInfo.append({ 'lmName': '投资政策', 'url' : 'http://www.dean.gov.cn/tzly/tzzc/',  'partern': partern})
    pagesInfo.append({ 'lmName': '投资环境', 'url' : 'http://www.dean.gov.cn/tzly/tzhj/',  'partern': partern})
    pagesInfo.append({ 'lmName': '园区企业', 'url' : 'http://www.dean.gov.cn/tzly/yqqy/',  'partern': partern})
    pagesInfo.append({ 'lmName': '招商项目', 'url' : 'http://www.dean.gov.cn/tzly/zsxm/',  'partern': partern})
    pagesInfo.append({ 'lmName': '就业创业', 'url' : 'http://www.dean.gov.cn/tzly/jycy/',  'partern': partern})
    #pagesInfo.append({ 'lmName': '农业类', 'url' : 'http://www.dean.gov.cn/tzly/zsxm/nyl/',  'partern': partern})
    #pagesInfo.append({ 'lmName': '工业类', 'url' : 'http://www.dean.gov.cn/tzly/zsxm/gyl/',  'partern': partern})
    #pagesInfo.append({ 'lmName': '旅游类', 'url' : 'http://www.dean.gov.cn/tzly/zsxm/lyl/',  'partern': partern})
    pagesInfo.append({ 'lmName': '企业招聘', 'url' : 'http://www.dean.gov.cn/tzly/jycy/qyzp/',  'partern': partern})
    pagesInfo.append({ 'lmName': '个人求职', 'url' : 'http://www.dean.gov.cn/tzly/jycy/grqz/',  'partern': partern})
    pagesInfo.append({ 'lmName': '政策法规', 'url' : 'http://www.dean.gov.cn/tzly/jycy/zcfg_157134/',  'partern': partern})

    pagesInfo.append({ 'lmName': '县委领导', 'url' : 'http://www.dean.gov.cn/zw/zwwgk/03/02/001/sj/zslsj/grj_zsl/202108/t20210810_5061330.html',  'partern': partern, 'maxDay' : 30})
    pagesInfo.append({ 'lmName': '县委领导', 'url' : 'http://www.dean.gov.cn/zw/zwwgk/03/02/001/fsj/af/grjl_af/202103/t20210311_4929752.html',  'partern': partern, 'maxDay' : 30})
    pagesInfo.append({ 'lmName': '县政府领导', 'url' : 'http://www.dean.gov.cn/zw/zwwgk/03/02/003/xz/xz_af/grjl_af2/202108/t20210810_5061337.html',  'partern': partern, 'maxDay' : 30})

if __name__ == '__main__':
    init()
    for it in pagesInfo:
        fetchPageInfo(it)
        #print(it)
        if it['status'] != 'OK':
            pass
    #print('----------------------------------------------')
    file = open('out-time.txt', 'a')
    for it in pagesInfo:
        if it['status'] != 'OK':
            print(it.get('dept', '县级'), it['lmName'], it.get('lastDay'), it.get('status'), it['url'], sep = '\t', file = file)
            print(it.get('dept', '县级'), it['lmName'], it.get('lastDay'), it.get('status'), it['url'])
    file.close()       