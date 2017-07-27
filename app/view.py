from datetime import datetime
from flask import render_template, g, current_app, url_for, redirect, request, jsonify
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

    # Catch all for any add
    if session:
        session.commit()
        session.remove()


@app.teardown_appcontext
def shutdown_session(exception=None):
    # db_session.remove()
    # pg_session.remove()
    print('absolute session end', flush=True)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db_session.rollback()
    return render_template('500.html'), 500


@app.route('/_add_numbers')
def add_numbers():
    """Add two numbers server side, ridiculous but well..."""
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)
