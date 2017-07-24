from flask import Flask
from flask_login import LoginManager


# store private information in instance
app = Flask(__name__, instance_relative_config=True, static_folder='static', template_folder='templates')


# Load default templates
app.config.from_object('app.default_config.DevelopmentConfig')


# Start the index service
if app.config['ENABLE_SEARCH']:
    from whooshalchemy import IndexService
    si = IndexService(config=app.config)


# Configure login page
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'user.login'


# Import base view
from . import view


# Blueprint views
from app.user import user_view
from app.report import report_view


# Register with any rules
app.register_blueprint(user_view.bp)
app.register_blueprint(report_view.bp)
