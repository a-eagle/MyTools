import threading, sys, traceback, datetime, json, logging, copy, base64, urllib3, urllib.parse
import flask, flask_cors, requests
from flask import render_template
import  peewee as pw
import orm, utils
# pip3 install openpyxl

class Server:
    def __init__(self) -> None:
        self.app = flask.Flask(__name__, static_folder = 'dist/assets',  static_url_path = '/assets',
                               template_folder = 'dist/html')
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
        # log.disabled = True
        flask_cors.CORS(self.app)

    def start(self):
        #th = threading.Thread(target = self.runner, daemon = True)
        #th.start()
        self.runner()

    def runner(self):
        self.app.add_url_rule('/', view_func = self.home, methods = ['GET'])
        self.app.add_url_rule('/api/list/<className>', view_func = self.listData, methods = ['GET', 'POST'])
        self.app.add_url_rule('/api/get/<className>/<id>', view_func = self.getData, methods = ['GET', 'POST'])
        self.app.add_url_rule('/api/save/<className>', view_func = self.saveData, methods = ['POST'])
        self.app.add_url_rule('/api/del/<className>/<ids>', view_func = self.delData, methods = ['GET', 'POST'])
        self.app.add_url_rule('/api/markdel/<className>/<ids>', view_func = self.markDelete, methods = ['GET', 'POST'])
        self.app.add_url_rule('/api/update-sure-time/<ids>', view_func = self.updateSureTime, methods = ['GET', 'POST'])
        self.app.run('0.0.0.0', 8010, use_reloader = False, debug = True)

    def home(self):
        return render_template('index.html')

    def getHexArg(self, args, name):
        vals = args.get(name, '')
        if not vals:
            return ''
        svals = utils.HexUtils.strFromHex(vals)
        return svals

    def listData(self, className):
        args = flask.request.args
        return self._listData(className, args)

    def formatData(self, data):
        for k in data:
            it = data[k]
            if type(it) == datetime.date:
                data[k] = it.strftime('%Y-%m-%d')
            elif type(it) == datetime.datetime:
                data[k] = it.strftime('%Y-%m-%d %H:%M:%S')
        return data

    """
    args = {'page': 2, 'pageSize': 5,
                'cols': utils.HexUtils.strToHex('title,cnt'),
                # 'filters': utils.HexUtils.strToHex('[{"col":"title", "op":"<=", "val": "title-2"}]')
                }
    """
    def _listData(self, className, args):
        u = utils.OrmUtils()
        model = u.findOrmClass(className)
        page = int(args.get('page', 0))
        pageSize = int(args.get('pageSize', 0))
        filters = u.getCondition(model, self.getHexArg(args, 'filters'))
        cols = u.getCols(model, self.getHexArg(args, 'cols'))
        if cols:
            qr = model.select(*cols)
        else:
            qr = model.select()
        if filters:
            qr = qr.where(*filters)
        if page and pageSize > 0:
            qr = qr.paginate(page, pageSize)
        rs = [self.formatData(d.__data__) for d in qr]
        return rs
    
    def getData(self, className, id):
        u = utils.OrmUtils()
        model = u.findOrmClass(className)
        obj = model.get_or_none(id)
        if not obj:
            return model().__data__
        return self.formatData(obj.__data__)

    def saveData(self, className):
        u = utils.OrmUtils()
        model = u.findOrmClass(className)
        data = flask.request.get_json()
        model.diffSave(data)
        return {'code': 0, 'msg': 'Sucess'}

    def delData(self, className, ids):
        if not ids:
            return
        u = utils.OrmUtils()
        model = u.findOrmClass(className)
        ids = ids.split(',')
        ids = [int(i.strip()) for i in ids]
        i = 0
        while i < len(ids):
            s = i
            e = min(len(ids), i + 200)
            sp = ids[s : e]
            qr = model.delete().where(model.id.in_(sp))
            # print(qr)
            qr.execute()
            i = e
        return {'code': 0, 'msg': 'Sucess'}

    def markDelete(self, className, ids):
        if not ids:
            return {'code': 1, 'msg': 'Fail, no id'}
        u = utils.OrmUtils()
        model = u.findOrmClass(className)
        ids = ids.split(',')
        ids = [int(i.strip()) for i in ids]
        i = 0
        while i < len(ids):
            s = i
            e = min(len(ids), i + 200)
            sp = ids[s : e]
            qr = model.update(isDelete = 1).where(model.id.in_(sp))
            # print(qr)
            qr.execute()
            i = e
        return {'code': 0, 'msg': 'Sucess'}
    
    def download(self):
        headers = {
            'content-type': 'application/octet-stream'
        }
        bs = ''
        response = flask.make_response(bs, 200)
        response.headers = headers
        return response

    def updateSureTime(self, ids):
        if not ids:
            return {'code': 1, 'msg': 'Fail, no id'}
        ids = ids.split(',')
        ids = [int(i.strip()) for i in ids]
        i = 0
        st = orm.formatDateTime(datetime.datetime.now())
        while i < len(ids):
            s = i
            e = min(len(ids), i + 200)
            sp = ids[s : e]
            qr = orm.JcbdModel.update(sureTime = st).where(orm.JcbdModel.id.in_(sp))
            qr.execute()
            i = e
        return {'code': 0, 'msg': 'Sucess'}
    
if __name__ == '__main__':
    svr = Server()
    svr.start()
    
    args = {'page': 2, 'pageSize': 5,
                'cols': utils.HexUtils.strToHex('bbnc,sjx,tbcj'),
                # 'filters': utils.HexUtils.strToHex('[{"col":"title", "op":"<=", "val": "title-2"}]')
                }
    svr._listData('JcbdModel', args)