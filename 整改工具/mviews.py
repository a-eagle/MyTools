from flask import Flask, request, Blueprint, jsonify, render_template, url_for, g
import json
import orm, mcore

#-----------------------------------------------------
class IssueView(mcore.BaseView):
    _modelCls = orm.IssueModel


bp_issue = Blueprint('issue', __name__, url_prefix='/issue')
IssueView.initRoute(bp_issue)


#-----------------------------------------------------
class AnswerView(mcore.BaseView):
    _modelCls = orm.AnswerModel

    def get_by_issue_id(self, *args, **kwargs):
        id = kwargs['id']
        objs = orm.AnswerModel.select().where(orm.AnswerModel.issue_id == id).execute()
        d = [u.__data__ for u in objs]
        return self.success(d)

bp_answer = Blueprint('answer', __name__, url_prefix='/answer')
AnswerView.initRoute(bp_answer)
AnswerView.addUrlRule(bp_answer, '/issue_id/<int:id>', 'get_by_issue_id')

#-----------------------------------------------------------
class StatsView(mcore.BaseView):
    def info(self, *args, **kwargs):
        g.iuuses = [u.__data__ for u in orm.IssueModel.select( orm.IssueModel.id, orm.IssueModel.fix, orm.IssueModel.depts).execute()]
        g.answers = [u.__data__ for u in orm.AnswerModel.select(orm.AnswerModel.accept, orm.AnswerModel.dept, orm.AnswerModel.issue_id).execute()]
        return render_template('/stats/info.html')

bp_stats = Blueprint('stats', __name__, url_prefix='/stats')
StatsView.initRoute(bp_stats)
StatsView.addUrlRule(bp_stats, '/info.html', 'info')


def init(app : Flask):
    app.register_blueprint(bp_issue)
    app.register_blueprint(bp_answer)
    app.register_blueprint(bp_stats)
