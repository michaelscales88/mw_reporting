from datetime import datetime
from flask import render_template, g, current_app, url_for, redirect
from flask_login import current_user

from app import app
from app.database import db_session


@app.route('/')
def catch_all():
    return redirect(
        url_for('index')
    )


# Avoid favicon 404
@app.route("/favicon.ico", methods=['GET'])
def favicon():
    return url_for('static', filename='favicon.ico')


@app.route('/index', methods=['GET', 'POST'])
def index():
    print('base index')
    # User module is accessed through the navigation bar
    loaded_modules = [name for name in current_app.blueprints.keys() if name != 'user']
    print(loaded_modules)
    return render_template(
        'index.html',
        title='Index',
        blueprints=loaded_modules
    )


@app.before_request
def before_request():
    print('setup')
    g.user = current_user
    g.session = db_session
    g.search_enabled = current_app.config['ENABLE_SEARCH']
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
    # if g.search_enabled:
    #     si.register_class(User)  # update whoosh


@app.teardown_request
def teardown(error):
    print('teardown')
    session = getattr(g, 'session', None)
    # Only commit if we get this far
    if session:
        session.commit()


@app.teardown_appcontext
def shutdown_session(exception=None):
    print('absolute session end')
    db_session.remove()     # Be certain than the session closes


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db_session.rollback()
    return render_template('500.html'), 500
