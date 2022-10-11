import os
import requests, time
from io import StringIO
import dept
import xlrd
import peewee as pw

dept.depts.append({"url": 'http://www.dean.gov.cn/sfxzbzhgfhzl/', "name": '吴山镇'})
dept.depts.append({"url": 'http://www.dean.gov.cn/ztzl/zwgkzl/wszzt/', "name": '吴山镇'})

dept.depts.append({"url": 'http://www.dean.gov.cn/zjda/', "name": '县级-走进德安'})
dept.depts.append({"url": 'http://www.dean.gov.cn/xwzx/', "name": '县级-新闻中心'})
dept.depts.append({"url": 'http://www.dean.gov.cn/sjkf', "name": '县级-数据开放'})
dept.depts.append({"url": 'http://www.dean.gov.cn/tzly/', "name": '县级-投资旅游'})
dept.depts.append({"url": 'http://www.dean.gov.cn/zmhd/', "name": '县级-政民互动'})
dept.depts.append({"url": 'http://www.dean.gov.cn/ztzl/', "name": '县级-专题专栏'})
dept.depts.append({"url": 'http://www.dean.gov.cn/zw/02/', "name": '县级-重点领域'})
dept.depts.append({"url": 'http://www.dean.gov.cn/zw/zwwgk/', "name": '县级-政务五公开'})

db = pw.SqliteDatabase('db/error-word.db')

class Info(pw.Model):
    id = pw.PrimaryKeyField(column_name='_id')
    # [部门] 错敏词	推荐修改	所在上下文	所在文章链接	内容类型	父页面地址 [结果]

    deptName = pw.CharField(column_name='_dept_name')
    errWord = pw.CharField(column_name='_err_word')
    suggestWord = pw.CharField(column_name='_suggest_word')
    ctx = pw.CharField(column_name='_ctx')
    suggestCtx = pw.CharField(column_name='_suggest_ctx')
    fileType = pw.CharField(column_name='_file_type')
    url = pw.CharField(column_name='_url')
    parentUrl = pw.CharField(column_name='_parent_url')

    hasCtx = pw.CharField(column_name='_has_ctx')
    hasSuggestCtx = pw.CharField(column_name='_has_suggest_ctx')
    result = pw.CharField(column_name='_result')

    class Meta:
        database = db
        table_name = '_info_20220815'

def getText(url):
    rsp = requests.get(url)
    html = rsp.text
    out = StringIO()
    idx = 0
    maxLen = len(html)
    space = (' ', '\t', '\r', '\n')
    while True:
        idx = html.find('>', idx)
        if idx < 0:
            break
        idx += 1
        if idx >= maxLen:
            break
        while html[idx] != '<' and idx < maxLen:
            if html[idx]  not in space:
                out.write(html[idx])
            idx += 1
    return out.getvalue().replace('&nbsp;', '')

def getTextInXlsx(url):
    rsp = requests.get(url)
    if rsp.status_code != 200:
        return '' # str(rsp.status_code)

    cnt = rsp.content
    fileName = os.path.basename(url)
    f = open(fileName, 'wb')
    f.write(cnt)
    f.close()
    wb = xlrd.open_workbook(fileName)
    out = StringIO()
    for sh in wb.sheets():
        for r in range(sh.nrows):
            out.write(';'.join((str(c) for c in sh.row_values(r))))
    os.remove(fileName)
    return out.getvalue()

def parseDeptName(url, parentUrl, fileType):
    dd = '县级-'
    su = url
    if fileType != '文章':
        su = parentUrl
    for n in dept.depts:
        if n['url'] in su:
            dd = n['name']
            break
    return dd

# return (hasCtx, hasSuggestCtx, result)
def parseFile(url, errWord, ctx, suggestCtx, fileType):
    if fileType == '文章':
        txt = getText(url)
    elif fileType == 'excel':
        txt = getTextInXlsx(url)
    elif fileType == 'word':
        return ('Unknow', 'Unknow', 'Unknow')
    elif fileType == 'pdf':
        return ('Unknow', 'Unknow', 'Unknow')
    else:
        return ('Unknow', 'Unknow', 'Unknow')
    hasCtx = ctx in txt
    hasSuggestCtx = suggestCtx in txt
    result = 'Unknow'
    if hasSuggestCtx and (not hasCtx):
        result = 'Yes'
    if hasCtx and (not hasSuggestCtx):
        result = 'No'
    hasCtx = 'Yes' if hasCtx else 'No'
    hasSuggestCtx = 'Yes' if hasSuggestCtx else 'No'
    return (hasCtx, hasSuggestCtx, result)

def init():
    Info.drop_table()
    db.create_tables([Info])
    f = open('error-word.txt', 'r', encoding = 'utf-8')
    rs = []
    for line in f.readlines():
        spec = line.strip().split('\t')
        if len(spec) < 6:
            break
        # 错敏词	推荐修改	所在上下文	所在文章链接	内容类型	父页面地址
        errWord, suggestWord, ctx, url, fileType, parentUrl = spec
        if suggestWord == '-':
            suggestWord = ''
        suggestCtx = ctx.replace(errWord, suggestWord, 1)
        deptName = parseDeptName(url, parentUrl, fileType)
        hasCtx, hasSuggestCtx, result = parseFile(url, errWord, ctx, suggestCtx, fileType)
        line = deptName + '\t' + line.strip() + '\t' + hasCtx + '\t' + hasSuggestCtx + '\t' + result + '\n'
        rs.append(line)
        Info.create(deptName = deptName, errWord = errWord, suggestWord = suggestWord, ctx = ctx, fileType = fileType,
            suggestCtx = suggestCtx, url = url, parentUrl = parentUrl, result = result, hasCtx = hasCtx, hasSuggestCtx = hasSuggestCtx)
        print(line)
        time.sleep(0.2)
    f.close()

    f = open('error-word_result.txt', 'w', encoding='utf-8')
    f.writelines(rs)
    f.close()

def recheck(deptName = None):
    exp = Info.result != 'Yes'
    if deptName is not None:
        exp = exp and Info.deptName == deptName
    ls = Info.select().where(exp)
    for line in ls:
        hasCtx, hasSuggestCtx, result = parseFile(line.url, line.errWord, line.ctx, line.suggestCtx, line.fileType)
        line.hasCtx = hasCtx
        line.hasSuggestCtx = hasSuggestCtx
        line.result = result
        line.save()
        print(line.id, line.deptName, line.errWord, line.suggestWord, line.ctx, line.fileType, line.url, line.hasCtx, line.hasSuggestCtx, line.result, sep = '\t')
        time.sleep(0.2)

if __name__ == '__main__':
    # error-word.txt 除行之外，不能有换行符
    # 第一次生成结果文件，只生成一次
    # init()

    # 重复检查整改情况
    recheck('蒲亭镇')
    pass