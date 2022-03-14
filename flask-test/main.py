from flask import Flask, url_for, views, abort
import flask
import mviews, orm

app = Flask(__name__, static_folder='ui/static', template_folder='ui/templates')

@app.route('/')
def root():
    return flask.render_template('index.html')
    
"""
@app.before_request
def _open_db(*args):
    if mcore.db.is_closed():
        mcore.db.connect(reuse_if_open=True)
    
@app.teardown_request
def _close_db(*args):
    if not mcore.db.is_closed():
        mcore.db.close()
"""

mviews.init(app)
orm.init()

app.run(host = '0.0.0.0', port=5050, debug=True)