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
    beDays = {365: 335}
    be = beDays.get(maxDay, maxDay)
    if df > maxDay:
        item['status'] = '已超期'
    elif df > be:
        item['status'] = '即将超期'
    else:
        item['status'] = 'OK'
    item['lastDay'] = r


def fetchSubUrl(url, partern):    
    pass

def init():
    # 专题专栏
    partern = r"<span[^>]*>\s*(\d{4}-\d{2}-\d{2})\s*</span>"
    pagesInfo.append({'dept':'吴山镇', 'lmName': '示范乡镇标准化规范化专栏', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '走进吴山', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zjws/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '政策解读', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zcjd_201718/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '吴山镇行政权力清单', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/wszqlqd/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '三农', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zc/sn/',  'partern': partern, 'maxDay': 120})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '社会保障', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zc/shbz_201711/',  'partern': partern, 'maxDay': 120})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '住房', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zc/zf_201712/',  'partern': partern, 'maxDay': 120})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '就业', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zc/jy_201713/',  'partern': partern, 'maxDay': 120})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '教育', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zc/jy_201714/',  'partern': partern, 'maxDay': 120})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '民政', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zc/mz/',  'partern': partern, 'maxDay': 120})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '卫健', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zc/wj/',  'partern': partern, 'maxDay': 120})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '税务', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zc/sw/',  'partern': partern, 'maxDay': 120})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '重大项目建设', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/zdxmjs/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '社会救助', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/shjz_201735/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '养老服务', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/ylfw_201736/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '公共法律服务', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/ggflfw/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '就业创业', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/jycy_201738/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '生态环境', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/sthj_201739/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '农村危房改造', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/ncwfgz_201740/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '涉农补贴', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/snbt/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '公共文化服务', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/ggwhfw/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '卫生健康', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/wsjk/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '安全生产', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/aqsc_201744/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '食品药品监管', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/spypjg_201745/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '扶贫', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/fp_201746/',  'partern': partern})
    pagesInfo.append({'dept':'吴山镇', 'lmName': '社会保险', 'url' : 'http://www.dean.gov.cn/sfxzbzhgfhzl/zdly_201722/shbxly/',  'partern': partern})

    pagesInfo.append({ 'lmName': '德安县政府部门行政权力清单', 'url' : 'http://www.dean.gov.cn/ztzl/xzspggzl/daxzfbmxzqlqd/',  'partern': partern})
    pagesInfo.append({ 'lmName': '德安县“一次不跑”清单', 'url' : 'http://www.dean.gov.cn/ztzl/xzspggzl/daxycbpqd/',  'partern': partern})
    pagesInfo.append({ 'lmName': '德安县行政事业性收费', 'url' : 'http://www.dean.gov.cn/ztzl/xzspggzl/daxxzsyxsf/',  'partern': partern})
    pagesInfo.append({ 'lmName': '奋斗百年路 启航新征程', 'url' : 'http://www.dean.gov.cn/ztzl/fdbnl/index.html',  'partern': partern})
    pagesInfo.append({ 'lmName': '防控疫情', 'url' : 'http://www.dean.gov.cn/ztzl/fkyq/',  'partern': partern})
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

if __name__ == '__main__':
    init()
    for it in pagesInfo:
        fetchPageInfo(it)
        #print(it)
        if it['status'] == 'OK':
            #print(it['lmName'], it.get('status'), it.get('result'), it.get('lastDay'), it['url'], sep = '\t')
            pass
    #print('----------------------------------------------')
    for it in pagesInfo:
        if it['status'] != 'OK':
            print(it.get('dept', '县级'), it['lmName'], it.get('lastDay'), it.get('status'), it.get('diff'), it['url'], sep = '\t')
            
    input('END')