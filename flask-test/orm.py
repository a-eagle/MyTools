import peewee as pw
import mcore

class User(mcore.BaseModel):
    name = pw.CharField()
    

class Dept(mcore.BaseModel):
    name = pw.CharField()
    

def init():
    mcore.db.create_tables([User, Dept])
