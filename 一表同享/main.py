import flask
import orm
from werkzeug.routing import BaseConverter           

app = flask.Flask(__name__, instance_relative_config = True, static_folder='ui/static', template_folder='ui/templates')
app.config.from_mapping(
    SECRET_KEY = 'xielaic4cE@xef*',
)
#os.makedirs(app.instance_path)

# @app.before_request
def _open_db(*args):
    if orm.db.is_closed():
        orm.db.connect(reuse_if_open = True)

# @app.teardown_request
def _close_db(*args):
    if not orm.db.is_closed():
        orm.db.close()

@app.before_request
def __before_request():
    path : str = flask.request.path
    print('req:', path)
    if path.startswith('/static/') or  ('/login' == path):
        return
    # check is html page
    if path.endswith('.html') or path.endswith('.htm'):
        return flask.render_template(path[1 :]) # strip '/'
    # check user login
    #if 'user' not in flask.session:
    #    return flask.redirect('/login.html') # flask.url_for('loginPage')


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5050, debug = True)