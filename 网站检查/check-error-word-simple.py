import os
import requests, time
from io import StringIO
import dept

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

def skipSpace(html, idx):
    while html[idx] == ' ' or html[idx] == '\t':
        idx += 1
    return idx

def skipComment(html, tagBegin):
    idx = tagBegin
    if html[idx : idx + 4] != '<!--':
        return idx
    idx = html.find('-->', idx + 4)
    if idx < 0:
        return len(html)
    #comment = html[tagBegin : idx + 3]
    return idx + 3

def skipScriptAndStyle(html, tagBegin):
    #nowHtml = html[tagBegin : ]
    tb = tagBegin + 1  # ship char <
    tb = skipSpace(html, tb)
    isScript = html[tb: tb + 6].lower() == 'script'
    isStyle = html[tb: tb + 5].lower() == 'style'
    if isScript or isStyle:
        idx = html.find('</', tb)
        idx = html.find('>', idx)
        #nowTag = nowHtml[0 : idx - tagBegin]
        return idx + 1
    return tagBegin

# write tag content
def appendContent(html, maxLen, idx, out):
    space = (' ', '\t', '\r', '\n')
    while idx < maxLen and html[idx] != '<':
        if html[idx] not in space:
            out.write(html[idx])
        idx += 1
    return idx

def getText(url):
    rsp = requests.get(url)
    html = rsp.text
    out = StringIO()
    idx = 0
    maxLen = len(html)
    while True:
        tagBegin = html.find('<', idx)
        if tagBegin < 0:
            break
        idx = skipComment(html, tagBegin)
        if idx == tagBegin: # not comment tag
            idx = skipScriptAndStyle(html, tagBegin)
        if idx == tagBegin: # normal tag, skip tag self
            idx = html.find('>', idx)
            if idx < 0:
                break
            idx += 1
        idx = appendContent(html, maxLen, idx, out)

    text = out.getvalue()
    text = text.replace('&nbsp;', '')
    text = text.replace('&gt;', '>')
    text = text.replace('&lt;', '<')
    text = text.replace('&amp;', '<')
    return text


def parseDeptName(url, parentUrl):
    dd = '县级-'
    su = url
    if parentUrl:
        su = parentUrl
    su = su.strip()
    for n in dept.depts:
        if n['url'] in su:
            dd = n['name']
            break
    return dd

def checkFix(url, parentUrl, errWord : str, errWordCtx):
    if parentUrl:
        return 'Is-A-File'
    text = getText(url)
    errWord = errWord.replace(' ', '')
    errWord = errWord.replace('\t', '')
    errWordCtx = errWordCtx.replace(' ', '')
    errWordCtx = errWordCtx.replace('\t', '')
    
    if (errWord not in text) and (errWordCtx not in text):
        return '已改正' # 没有错词，也没有上下文
    if (errWord in text) and (errWordCtx not in text):
        return '已改正' #存在错词，但没有上下文
    # if (errWord in text) and (errWordCtx in text):
    return '未改正'
    

def find():
    f = open('error-word.txt', 'r', encoding = 'utf-8')
    rs = []
    for line in f.readlines():
        spec = line.strip().split('\t')
        # 错敏字	上下文  引用页	 附件引用页
        if len(spec) == 4:
            errWord, errWordCtx, url, parentUrl = spec
        elif len(spec) == 3:
            errWord, errWordCtx, url = spec
            parentUrl = None
        else:
            raise Exception()
        
        deptName = parseDeptName(url, parentUrl)
        fixed = checkFix(url, parentUrl, errWord, errWordCtx)
        line = deptName + '\t' + errWord + '\t' + fixed + '\n'
        time.sleep(0.2)

        rs.append(line)
        print(line)
    f.close()

    f = open('error-word_result.txt', 'w', encoding='utf-8')
    f.writelines(rs)
    f.close()

def test():
    url = 'http://www.dean.gov.cn/ztzl/jxhxjzg/kpxc2/201302/t20130222_3984808.html'
    text = getText(url)
    print(text)

if __name__ == '__main__':
    # error-word.txt 除行之外，不能有换行符
    # 仅查找所在的部门
    find()
    #test()
    pass