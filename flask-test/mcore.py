from email.policy import default
from flask import request, jsonify, Blueprint
from flask.views import MethodView
import peewee as pw

db = pw.SqliteDatabase('ui/memory.db')
# proxy = pw.DatabaseProxy()
# proxy.initialize(db)

class BaseView(MethodView):
    _ormCls = None

    @classmethod
    def initRoute(cls, bp : Blueprint):
        viewFunc = cls.as_view(bp.name)
        bp.add_url_rule('/', defaults={'id': None}, view_func=viewFunc,  methods=['GET',])
        bp.add_url_rule('/', view_func=viewFunc, methods=['POST',])
        bp.add_url_rule('/<int:id>', view_func=viewFunc, methods=['GET', 'PUT', 'DELETE'])

    @property
    def orm(self) -> pw.Model:
        return self.__class__._ormCls

    def success(self, data):
        if isinstance(data, list):
            for d in data:
                if '_del_tag' in d:
                    del d['_del_tag']
        if isinstance(data, dict):
            if '_del_tag' in data:
                del data['_del_tag']
        return jsonify(status='OK', msg=None, data=data)
    def fail(self, msg, data = None):
        return jsonify(status='Fail', msg=msg, data=data)

    def get(self, id = None):
        if id is None:
            params = request.get_json(force=True, silent=True)
            pageIdx = 0
            pageSize = 20
            if params and 'pageIdx' in params:
                pageIdx = params.pageIdx
            if params and 'pageSize' in params:
                pageSize = params.pageSize
            sl = self.orm.select().where(self.orm._del_tag == False).paginate(pageIdx + 1, pageSize)
            #print(sl.sql())
            val = [u.__data__  for u in sl.execute()]
            return self.success(val)
        else:
            u = self.orm.get_or_none(self.orm.id == id, self.orm._del_tag == False)
            if u is not None:
                return self.success(u.__data__)
            return self.fail(f'Not found by ID of {id}')

    def post(self):
        params = request.get_json(force=True, silent=True)
        if isinstance(params, list):
            r = []
            for p in params:
                u = self.orm.create(**p)
                r.append({"id": u.id})
            return self.success(r)
        elif isinstance(params, dict):
            u = self.orm.create(**params)
            return self.success({"id": u.id})
        return self.fail('post need valid json')

    def put(self, id):
        u = self.orm.get_or_none(self.orm.id == id)
        params = request.get_json(force=True, silent=True)
        if u is None:
            return self.fail( msg = f'Not found by ID of {id}')
        for k in params:
            if hasattr(u, k):
                setattr(u, k, params[k])
        u.save()
        return self.success(None)

    def delete(self, id):
        self.orm.update(_del_tag = True).where(self.orm.id == id).execute()
        return self.success(None)

class BaseModel(pw.Model):
    _del_tag = pw.BooleanField(default=False)
    class Meta:
        database = db