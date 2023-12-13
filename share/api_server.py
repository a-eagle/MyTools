# pip install pymysql
# pip install flask

from flask import Flask, url_for, abort, make_response, request
import pymysql
import json

app = Flask(__name__)
db : pymysql.connections.Connection = None

appKeys = ('YQCDPYY') #大屏

def isAppKeyOK(appKey):
    if not appKey:
        return False
    return appKey in appKeys

def openDB():
    global db
    if not db:
        db = pymysql.connect(host='10.119.81.253', port=3306, user='root', password='Root@2020', database='ZWShare')
    db.ping(True)
    return db

# return [{_name, _name_cn, _dept_id}, ...] 第一条是表信息，其余是列信息
def getTableColumns(tableName):
    global db
    openDB()
    sql = 'select _name, _name_cn, _dept_id from  _table_prototype where _owner  = %s '
    cc = db.cursor()
    cc.execute(sql, (tableName, ))
    rs = cc.fetchall()
    data = [ {'_name': d[0], '_name_cn': d[1], '_dept_id': d[2]} for d in rs]
    cc.close()
    return data

# return {_name, _name_cn, _dept_id}
def findColumn(cols, name):
    for c in cols:
        if c['_name'] == name:
            return c
    return None

# return [{name: value: }, ] 
def buildQueryParams(cols, params):
    newParams = []
    for k in params:
        if not findColumn(cols, k):
            return False
        if findColumn(cols, k):
            newParams.append({'name' : k, 'value': params[k]})
    return newParams

def getResultTitles(cursor, cols):
    titles = []
    for d in cursor.description:
        if (d[0] == 'id' or d[0] == '_id'):
            continue
        c = findColumn(cols, d[0])
        if c:
            titles.append(c['_name_cn'])
    return titles

def getDeptName(deptId):
    global db
    sql = f'select _name from  _department where _id = {deptId}'
    cc = db.cursor()
    cc.execute(sql)
    rs = cc.fetchall()
    names = [r[0] for r in rs]
    if len(names) != 1:
        return ''
    return names[0]

def getSelectSql(tablename, cols, params):
    sql = 'select '
    for i in range(1, len(cols)):
        sql += cols[i]['_name'] + ','
    sql = sql[0 : -1]
    sql += ' from ' + tablename
    if len(params) > 0:
        sql += ' where '
    for idx, p in enumerate(params):
        if idx != 0:
            sql += ' and '
        sql += ' ' + p['name'] + ' = %s '
    return sql

@app.route('/RestService/rest/api/<tableName>', methods = ['GET'])
def queryApi(tableName):
    global db
    print('[api-server] Request=', tableName, 'params=', request.args)
    cols = getTableColumns(tableName)
    if len(cols) == 0:
        abort(404)
    orgParams = {}
    for k in request.args:
        orgParams[k] = request.args[k]
    appKey = orgParams.get('appKey')
    if not isAppKeyOK(appKey):
        return '{"status": "Fail", "msg": "appKey错误", "code": 1 }'
    del orgParams['appKey']

    params = buildQueryParams(cols, orgParams)
    if params == False:
        return '{"status": "Fail", "msg": "请求参数错误", "code": 2 }'
    
    tableNameCN = cols[0]['_name_cn']
    isCanAll = ('开放' in tableNameCN) or ('全量' in tableNameCN) or ('公共' in tableNameCN)
    if not isCanAll:
        deptName = getDeptName(cols[0]['_dept_id'])
        isCanAll = ('开放' in deptName) or ('全量' in deptName) or ('公共' in deptName)

    if len(cols) == 1:
        return '{"status": "Fail", "msg": "需要指定查询参数", "code": 3 }'
    if (not isCanAll) and len(params) == 0:
        return '{"status": "Fail", "msg": "需要指定查询参数" , "code": 4}'
    sql = getSelectSql(tableName, cols, params)
    
    print('[api-server] query sql=', sql)
    
    cc = db.cursor()
    paramVals = [p['value'] for p in params]
    cc.execute(sql, paramVals)
    rs = cc.fetchall()
    body = [d for d in rs]
    titles = getResultTitles(cc, cols)
    if len(rs) == 0:
        data = {'status': 'Success', 'msg':'未查询到相关信息', 'code': 0, "titles": titles, 'data':None}
    else:
        data = {'status': 'Success', 'msg':'', 'code': 0, "titles": titles, "data" : body}
    cc.close()
    return json.dumps(data, ensure_ascii=False)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=8058, debug=False)