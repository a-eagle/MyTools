from flask import Flask, url_for, views, abort, g, jsonify, request, session, redirect
import flask
import mviews, orm
import depts


#------------------------------------------------
app = Flask(__name__, static_folder='ui/static', template_folder='ui/templates')

@app.route('/')
def root():
    return redirect('/issue/list.html')
    
#"""
@app.before_request
def _open_db(*args):
    #if mcore.db.is_closed():
    #    mcore.db.connect(reuse_if_open=True)
    g.depts = depts.depts
    g.depts_bm = depts.depts_bm
    g.depts_xz = depts.depts_xz
    g.depts_xzzf = depts.depts_xzzf
    if 'username' in session:
        g.isAdmin = session['username'] == 'admin'
    
@app.teardown_request
def _close_db(*args):
    #if not mcore.db.is_closed():
    #    mcore.db.close()
    pass

#"""

orm.init()
mviews.init(app)


#----------------admin--------------------------------
@app.route('/admin')
def admin():
    session['username'] = 'admin'
    return 'admin ok' 


app.run(host = '0.0.0.0', port=5050, debug=True)