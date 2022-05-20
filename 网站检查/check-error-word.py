import requests, time
from io import StringIO
import dept

dept.depts.append({"url": 'http://www.dean.gov.cn/ztzl/', "name": '专题专栏'})
dept.depts.append({"url": 'http://www.dean.gov.cn/xwzx/', "name": '新闻中心'})
dept.depts.append({"url": 'http://www.dean.gov.cn/zw/zwwgk/', "name": '政务五公开'})
dept.depts.append({"url": 'http://www.dean.gov.cn/sfxzbzhgfhzl/', "name": '吴山镇（示范专栏）'})


def getCtx(txt, idx, tagLen):
    # check left
    left = idx - 1
    leftTxt = ''
    MAX_CTX_LEN = 20
    while len(leftTxt) < MAX_CTX_LEN and left > 0:
        while left > 0 and txt[left] != '>' and len(leftTxt) < MAX_CTX_LEN:
            if txt[left] not in (' ', '\t', '\r', '\n'):
                leftTxt = txt[left] + leftTxt
            left -= 1
        while left > 0 and txt[left] != '<' and len(leftTxt) < MAX_CTX_LEN:
            left -= 1
        if left > 0 and txt[left] == '<':
            left -= 1
    # check right
    right = idx
    rightTxt = ''
    maxLen = len(txt)
    MAX_CTX_LEN += tagLen
    while len(rightTxt) < MAX_CTX_LEN and right < maxLen:
        while right < maxLen and txt[right] != '<' and len(rightTxt) < MAX_CTX_LEN:
            if txt[right] not in (' ', '\t', '\r', '\n'):
                rightTxt += txt[right]
            right += 1
        while right < maxLen and txt[right] != '>' and len(rightTxt) < MAX_CTX_LEN:
            right += 1
        if right < maxLen and txt[right] == '>':
            right += 1
    return leftTxt + rightTxt

def findCtx(txt, tag):
    idx = 0
    rs = []
    while True:
        idx = txt.find(tag, idx)
        if idx < 0:
            break
        rs.append(getCtx(txt, idx, len(tag)))
        idx += len(tag)
    return '|+|'.join(rs)

def getText(html):
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

def parseText(url, tag, ctxText, type):
    dd = '?'
    for n in dept.depts:
        if n['url'] in url:
            dd = n['name']
            break

    if type != '文章':
        return ('NoCheck', dd)

    rsp = requests.get(url)
    t = getText(rsp.text)
    newCtx = findCtx(t, tag)
    
    if ctxText in newCtx:
        return ('No', dd)
    return ("Yes", dd)

def checkFile():
    f = open('error-word.txt', 'r', encoding = 'utf-8')
    rs = []
    for line in f.readlines():
        spec = line.strip().split('\t')
        if len(spec) < 6:
            break
        # 错敏词	推荐修改	修改说明	所在上下文	所在文章链接	所在文章标题	快照	网站名称	网站标识码	发布时间	问题类型	问题级别	内容类型	父页面地址
        tag, suggestTag, _, ctxText, url, *_, docType, _ = spec
        result, deptName = parseText(url, tag, ctxText, docType)
        line = deptName + '\t' + line.strip() + '\t' + result + '\n'
        rs.append(line)
        print(line)
        time.sleep(0.5)
    f.close()

    f = open('error-word_check.txt', 'w', encoding='utf-8')
    f.writelines(rs)
    f.close()

if __name__ == '__main__':
    # error-word.txt 除行之外，不能有换行符
    checkFile()

    # test one line
    # line = ''
    # spec = line.split('\t')
    # tag, suggestTag, _, ctxText, url, *_, docType, _ = spec
    # v = parseText(url, tag, ctxText, docType)
    # line = line.strip() + '\t' + v + '\n'