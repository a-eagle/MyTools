import traceback, json, copy
from flask import Flask, request, jsonify
import orm, peewee as pw
from flask_cors import CORS   # pip install -U flask-cors 


app = Flask(__name__, instance_relative_config = True) # , static_folder='ui/static', template_folder='ui/templates'
cors = CORS(app)

app.config.from_mapping(
    SECRET_KEY = 'xielaic4cE@xef*',
)

@app.before_request
def _open_db(*args):
    if orm.db.is_closed():
        orm.db.connect(reuse_if_open = True)

@app.teardown_request
def _close_db(*args):
    if not orm.db.is_closed():
        orm.db.close()

logFile = open('log.txt', 'a+')

@app.route("/save-data", methods=['POST'])
def saveData():
    try:
        if not request.data:
            return '{"code": 1, "msg": "No data"}'
        data = request.data.decode('utf-8')
        print('Save:', data)
        data = json.loads(data)
        p = orm.Person.get_or_none(orm.Person.id == data['id'])
        if not p:
            print(f', Not find this id\n')
            return '{"code": 3, "msg": "Not find person by id: ' + str(data['id']) + '"}'
        p.suggest_5 = data.get('suggest_5', None)
        p.info = data.get('info', None)
        p.save()
        print(f', Success\n')
        return '{"code": 0, "msg": "Success"}'
    except Exception as e:
        traceback.print_exc()
        return '{"code": 2, "msg": "' + str(e) + '"}'

lastId = 0
@app.route("/get-next-1", methods=['GET'])
def getNext_1():
    global lastId
    try:
        MAX_ID = 8276
        if lastId > 8276:
            return {"code": 2, "msg": "END"}
        data = None
        while lastId <= MAX_ID:
            q = orm.Person.get_or_none(orm.Person.id == lastId)
            lastId += 1
            if q and q.suggest_2:
                data = q.__data__
                break
        if data:
            return {"code": 0, "msg": "Success", "data": data}
        return {"code": 2, "msg": "END"}
    except Exception as e:
        traceback.print_exc()
        return '{"code": 3, "msg": "' + str(e) + '"}'


lastId_2 = 0
@app.route("/get-next", methods=['GET'])
def getNext_2():
    try:
        global lastId_2
        MAX_ID = 8276
        data = None
        if lastId_2 <= MAX_ID:
            q = orm.Person.select().where(orm.Person.id > lastId_2, 
                                        orm.Person.suggest_2.is_null(False) & (orm.Person.suggest_2 != ''),
                                        orm.Person.info.is_null(True) | (orm.Person.info == '')
                                        )
            for it in q:
                data = it.__data__
                lastId_2 = it.id
                break
        if data:
            return {"code": 0, "msg": "Success", "data": data}
        return {"code": 2, "msg": "END"}
    except Exception as e:
        traceback.print_exc()
        return '{"code": 3, "msg": "' + str(e) + '"}'    


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5050, debug = True)
