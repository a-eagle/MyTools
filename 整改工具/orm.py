
import datetime
import peewee as pw
from sqlalchemy import null
import mcore

def cur_datetime():
    t = datetime.datetime.now()
    return t.strftime('%Y-%m-%d %H:%M:%S')

class IssueModel(mcore.BaseModel):
    question = pw.TextField(null=True)
    depts = pw.TextField(null=True)
    tips = pw.TextField(null=True)
    fix = pw.IntegerField(default=0)
    create_time = pw.CharField(default=cur_datetime)
    update_time = pw.CharField(default=cur_datetime)


class AnswerModel(mcore.BaseModel):
    issue_id = pw.IntegerField(default=0)
    dept = pw.TextField(null=True)
    answer = pw.TextField(null=True)
    accept = pw.IntegerField(default=0)
    create_time = pw.CharField(default=cur_datetime)
    update_time = pw.CharField(default=cur_datetime)

def init():
    mcore.db.create_tables([IssueModel, AnswerModel])
