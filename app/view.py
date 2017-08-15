from datetime import datetime
from flask import render_template, g, current_app, url_for, redirect
from flask_login import current_user
from flask_restful.reqparse import RequestParser

from app import app
from app.database import db_session


@app.route('/')
def catch_all():
    return redirect(
        url_for('index')
    )


@app.route('/index', methods=['GET', 'POST'])
def index():
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
    g.user = current_user
    g.session = db_session
    g.parser = RequestParser()
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()


@app.teardown_request
def teardown(error):
    session = getattr(g, 'session', None)

    # Catch all for any add
    if session:
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            session.flush()
            print(e)
            print('rollback and flush')
            # raise
        finally:
            session.remove()
            print('removed')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    print('found the 500 error')
    db_session.rollback()
    return render_template('500.html'), 500
