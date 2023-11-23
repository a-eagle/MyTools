import requests, time, datetime, random, math, json, os, re
from datetime import datetime
from urllib.parse import urlencode
from urllib.parse import quote

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',

    'Cookie': 'easyuiThemeName=2; JSESSIONID=7A31AF8F300AC12785D9735FAE3C72E2' # 需要设置
}

def seq(data):
    rs = '['
    lv = []
    for d in data:
        item = '{'
        for k, v in d.items():
            if type(v) == str:
                item += f'"{k}":"{str(v)}",'
            elif type(v) == bool:
                item += f'"{k}":' + ('true' if v else 'false') + ','
            elif type(v) == int:
                item += f'"{k}":{str(v)},'
            else:
                raise Exception('[seq] error type')
        item = item[0 : -1] + '}'
        lv.append(item)
    xn = ','.join(lv)
    rs += xn + ']'
    return rs

def getResDirInfoForNew(resName):
    # 取得最近的目录类型，名称
    #url = 'http://10.97.10.42:8082/govportal/myRes/catalogRegistration!getLatestVo.action'
    #resp = requests.post(url, headers = headers)
    #js = json.loads(resp.text)
    #resTypeVal, baseTypes = js['resTypeVal'], js['resFormat']
    resTypeVal = 'bf854296bc494d38a86fbdd455fa8e60'
    baseTypes = '市县目录-九江市-德安县-德安县信息办-业务类-公共服务类'

    # 取得resCode
    url = 'http://10.97.10.42:8082/govportal/myRes/resRegister!genResCode.action'
    params = {'resTypeId' : resTypeVal}
    params = urlencode(params)
    resp = requests.post(url, data = params, headers = headers)
    js = json.loads(resp.text)
    if js['flag'] != 1:
        raise Exception('[createResDir] genResCode fail. ' + js)
    resCode = js['msg']

    # 检查infoName
    url = 'http://10.97.10.42:8082/govportal/myRes/resRegister!checkInfoName.action'
    params = {'infoName': resName, 'oldInfoName': '', 'resTypeVal': resTypeVal, 'resTypeValOld': ''}
    params = urlencode(params)
    resp = requests.post(url, data = params, headers = headers)
    if resp.text != 'true':
        raise Exception('[createResDir] 资源名称非法：' + resp.text + ', resName=' + resName)
    return resTypeVal, baseTypes, resCode

def getColArr(cols):
    if type(cols) == str:
        cols = re.split('\s+|、', cols)
    elif type(cols) == list:
        pass
    else:
        raise Exception('[createResDir] 参数cols类型错误' + cols)
    colArr = []
    for c in cols:
        colArr.append({'resourceName': c, "fieldType":"1","fieldLength":"100","description":"","fieldPrec":"","dateType":"","fieldOpen":"0","publishTime":""})
    return colArr

# param cols: (1)str类型，自动根据\s+|、来分割  (2).字符数组 list
def createResDir(resName, cols):
    resName = resName.strip()
    print('[createResDir]' ,resName)
    if not resName:
        return
    colArr = getColArr(cols)
    resTypeVal, baseTypes, resCode = getResDirInfoForNew(resName)
    
    regData = {
        'rdId' : '',  'baseTypes' : baseTypes, 'relationTypes':'', 'rdCodeOld': '', 'orgSocialCode': '', 'oldInfoName': '', 'internalDep':'', 'customFormat': '',
        'resTypeValOld':'', 'relationTypeVal': '',
        'selfLable' : resName, 'infoName': resName, 'description': resName, 'createunitsName': '德安县信息办',
        'shareClassId': '402882a75885fd150158860e3d170006', 'shareCondition': '依申请', 'shareDuty' : '', 'isShareDuty' : '0', 
        'shareTypeName': '4028829d44f8223f0144f87555540001', 'security' : '0', 'resTypeVal': resTypeVal, 'resFormatTypes': 'xlsx', 'resFormatType': 'xlsx',
        'rdCode': resCode, 'openType': '0', 'newnewnewRdCode': resCode, 'resFormat': '2', 'systemId': '0', 'upFre': '5', # upFre更新周期每年:5， 实时:1
        'state': '1', 'resOpenScore': '1'   # state=1 保存   resOpenScore资源公开类型
    }
    regData['colArr'] = seq(colArr)
    regData = urlencode(regData)
    #print('[createResDir] colArr=', colArr)
    #print('[createResDir] regData=', regData)

    url = 'http://10.97.10.42:8082/govportal/myRes/catalogRegistration!saveDirectoryRegistered.action'
    resp = requests.post(url, data=regData, headers = headers)
    js = json.loads(resp.text)
    print('[createResDir] result =', js)
    if js['code'] != '1':
        raise Exception('[createResDir] 注册失败')
    time.sleep(3)

if __name__ == '__main__':
    headers['Cookie'] = 'easyuiThemeName=2; JSESSIONID=2901D5569ECDFE93B7A066688B2AE5DA'
    
    # 注册目录
    # createResDir('个体户异常名录', '名称	统一社会信用代码	注册号	经营者	异常状态	标记异常日期	标记异常原因 联系电话	管辖工商所	经营场所')
    # createResDir('个体注销明细', '名称	统一社会信用代码	经营者	经营状态	经营场所	成立日期	经营范围	资金数额(万元)	登记机关')
    #createResDir('企业年报名单', '企业名称	统一社会信用代码	法定代表人	成立日期	年报年度	报送状态	企业类型	登记机关	管辖机关	企业住所	年报时间')
    #createResDir('企业异常名录', '列入原因	列入文号	异常状态	法定代表人	注册资本(万元)	登记机关	住所')
    #createResDir('食品经营许可证', '单位名称	社会信用代码	法定代表人（负责人）	住所	经营场所	主体业态	经营项目	行政许可申请受理通知书文号	行政许可决定文书号	证书编号	发证日期	有效日期	发证机关')
    #createResDir('预包装食品销售备案', '食品经营者名称	统一社会信用代码	法定代表人（负责人）	联系人	申请类型	申请人姓名	经营场所地址	有无外设仓库	是否含冷藏冷冻食品	是否含特殊食品	具体特殊食品	备案编号	备案机关	备案时间')
    
    #createResDir('纺织服装产业规上名单', '组织机构代码、单位详细名称、营业收入（千元）、利润总额（千元）')
    #createResDir('德安县纺织服装企业信息表', '企业名称、法人代表、注册时间、地址、占地面积（亩）、主要产品')
    #createResDir('德安县纺织服装产业重点项目', '项目名称、建设规模、总投资、项目资金来源')
    #createResDir('德安县现代轻纺产业规上企业信息', '企业名称、投资人、投资来源、面积㎡、员工数、主要产品、关联产品 主要设备、主要工艺')
    #createResDir('德安县质量管理体系认证获证企业名单', '认证项目、证书编号、获证组织名称、获证组织统一社会信用代码、法定代表人')