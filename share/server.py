# pip install pymysql
# pip install flask

from flask import Flask, url_for, abort, make_response, request
import pymysql
import json

app = Flask(__name__)
db : pymysql.connections.Connection = None

def openDB():
    global db
    if not db:
        db = pymysql.connect(host='10.119.81.253', port=3306, user='root', password='Root@2020', database='ZWShare')
    db.ping(True)
    return db

# return [{_name, _name_cn, _dept_id}, ...]
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
        newParams.append({'name' : k, 'value': params[k]})
    return newParams

def getResultTitles(cursor, cols):
    titles = []
    for d in cursor.description:
        if (d[0] == 'id' or d[0] == '_id'):
            continue
        c = findColumn(cols, d[0])
        titles.append(c['_name_cn'])
    return titles

@app.route('/RestService/rest/api/<tableName>', methods = ['GET'])
def queryApi(tableName):
    global db
    print(tableName, request.args)
    cols = getTableColumns(tableName)
    if len(cols) == 0:
        abort(404)

    params = buildQueryParams(cols, request.args)
    if params == False:
        return '{"status": "Fail", "msg": "请求参数错误" }'
    
    tableNameCN = cols[0]['_name_cn']
    isPublic = cols[0]['_dept_id'] == 34
    isCanAll = ('开放' in tableNameCN) or ('全量' in tableNameCN) or isPublic

    if len(cols) == 1:
        return '{"status": "Fail", "msg": "需要指定查询参数" }'
    if (not isCanAll) and len(params) == 0:
        return '{"status": "Fail", "msg": "需要指定查询参数" }'

    sql = 'select * from  ' + tableName + ' '
    if len(params) > 0:
        sql += 'where '
    for idx, p in enumerate(params):
        if idx != 0:
            sql += ' and '
        sql += ' ' + p['name'] + ' = %s '
    print(sql)
    
    cc = db.cursor()
    paramVals = [p['value'] for p in params]
    cc.execute(sql, paramVals)
    rs = cc.fetchall()
    body = [d[1 : ] for d in rs] # skip id column
    titles = getResultTitles(cc, cols)
    if len(rs) == 0:
        data = {'status': 'Fail', 'msg':'未查询到相关信息'}
    else:
        data = {'status': 'Success', 'msg':'', "titles": titles, "data" : body}

    return json.dumps(data, ensure_ascii=False)


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=8058, debug=False)