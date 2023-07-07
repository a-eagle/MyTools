import requests, time, peewee as pw, requests
from io import StringIO
import dept

dept.depts.append({"url": 'http://www.dean.gov.cn/ztzl/', "name": '县级'})
dept.depts.append({"url": 'http://www.dean.gov.cn/xwzx/', "name": '县级'})
dept.depts.append({"url": 'http://www.dean.gov.cn/zw/zwwgk/', "name": '县级'})
dept.depts.append({"url": 'http://www.dean.gov.cn/sfxzbzhgfhzl/', "name": '吴山镇（示范专栏）'})

db = pw.SqliteDatabase('error-word.db')

class ErrorWord(pw.Model):
    uid = pw.CharField(unique = True) # 标记唯一码 fileName#no
    no = pw.CharField(null=True)
    deptName = pw.CharField()
    errWord = pw.CharField()
    suggest = pw.CharField(null=True)
    question = pw.CharField()
    linkUrl = pw.CharField()
    quikUrl = pw.CharField()
    refUrl = pw.CharField(null=True)
    ctx = pw.CharField(null=True)
    isErrWordInCtx = pw.BooleanField() # ctx has error word
    isCtxInHtml = pw.CharField() # ctx in html source: 'Yes' 'No' 'Unknow' 'NoCheck'

    fixedError = pw.BooleanField(default=False)
    class Meta:
        database = db

ErrorWord.create_table()

def genUID(fileName, no):
    return fileName + '#' + str(no)

# 删除<tag>，只保留文本内容
def htmlToText(html):
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
        while idx < maxLen and html[idx] != '<':
            if html[idx]  not in space:
                out.write(html[idx])
            idx += 1
    return out.getvalue().replace('&nbsp;', '')

# info is a dict
def checkCtxInHtml(info):
    url : str = info['linkUrl']
    if not url.endswith('.html'):
        info['isCtxInHtml'] = 'Unknow'
    resp = requests.get(url)
    html = resp.text
    text = htmlToText(html)
    isIn = info['ctx'] in text
    info['isCtxInHtml'] = 'Yes' if isIn else 'No'

def checkDeptByUrl(info):
    url : str = info['linkUrl']
    for d in dept.depts:
        if d['url'] in url:
            info['deptName'] = d['name']
            return
    info['deptName'] = '--'

def load_file(fileName):
    datas = []
    f = open(fileName, 'r', encoding='utf-8')
    lines = f.readlines()
    START_NO = 1
    lineNo = -1
    idx = -1
    LEN = len(lines)
    while idx < len(lines):
        # 1 line
        idx += 1
        lineNo += 1
        no = lineNo + START_NO
        if idx >= len(lines):
            break

        line = lines[idx].strip().replace(' ', '')
        pos = line.index('.')
        nowNo = int(line[0 : pos])
        if no != nowNo:
            print('No Error: ', no, nowNo)
            raise Exception()
        question = line[pos + 1 : ]
        pos = line.index('：“') + 2
        epos = line.index('”,', pos + 1)
        errWord = line[pos : epos]

        pos = line.find('建议修改为:“', epos)
        if pos >= 0:
            pos += 7
            # check last is "
            if line[(len(line)) - 1] != '”':
                print('Tag Error: line last char is not ”')
                raise Exception()
            suggest = line[pos : -1]
        else:
            suggest = None

        # 2 line
        line = lines[idx + 1].strip().replace(' ', '')
        if line == '由于网络原因无法确认此错误是否已修复':
            idx += 1 # skip this line

        rowInfo = {'uid': genUID(fileName, no), 'no': no, 'errWord' : errWord, 'suggest': suggest, 'question': question, 'isCtxInHtml': 'NoCheck'}
        while idx < len(lines) - 1:
            idx += 1
            line = lines[idx].strip().replace(' ', '')
            if line == '链接地址:':
                idx += 1
                linkUrl = lines[idx].strip().replace(' ', '')
                rowInfo['linkUrl'] = linkUrl
            elif line == '快照地址:':
                idx += 1
                quikUrl = lines[idx].strip().replace(' ', '')
                rowInfo['quikUrl'] = quikUrl
            elif line == '引用地址:':
                idx += 1
                refUrl = lines[idx].strip().replace(' ', '')
                rowInfo['refUrl'] = refUrl
            elif line == '': # is space line
                break
            else:
                ctx = line.replace(' ', '')
                rowInfo['ctx'] = ctx
                rowInfo['isErrWordInCtx'] = rowInfo['errWord'] in ctx

        #checkCtxInHtml(rowInfo)
        checkDeptByUrl(rowInfo)
        print(rowInfo['uid'], rowInfo['deptName'], rowInfo['question'], rowInfo['isErrWordInCtx'], rowInfo.get('isCtxInHtml'), '\n')
        saveOne(rowInfo)
        datas.append(rowInfo)
    return datas

def saveOne(data):
    obj = ErrorWord.get_or_none(ErrorWord.uid == data['uid'])
    if not obj:
        # only insert
        ErrorWord.create(**data)

def saveAll(datas):
    for d in datas:
        ErrorWord.create(**d)

def writeToFile():
    f = open('error-word-rs.txt', 'w')
    f.write('部门\t问题\t链接地址\t引用地址\t所在上下文\n')
    for row in ErrorWord.select():
        refUrl = row.refUrl if row.refUrl else '-'
        deptName = row.deptName if row.deptName != '县级' else '--'
        s = deptName + '\t' + row.question + '\t' + row.linkUrl + '\t' + refUrl + '\t' + row.ctx + '\n'
        f.write(s)
    f.close()

if __name__ == '__main__':
    #datas = load_file('error-word-1.txt')
    #datas = load_file('error-word-1_1.txt')
    #datas = load_file('error-word-2.txt')
    #datas = load_file('error-word-2_1.txt')
    writeToFile()
