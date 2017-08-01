from flask_login import LoginManager
from flask_moment import Moment

from app.util.flask_extended import Flask

# store private information in instance
app = Flask(__name__, instance_relative_config=True, static_folder='static', template_folder='templates')


# Load default templates
app.config.from_object('app.default_config.DevelopmentConfig')
app.config.from_yaml('clients.yml', silent=True)
app.config.from_yaml('secret_stuff.yml', silent=True)


# Start the index service
if app.config['ENABLE_SEARCH']:
    from whooshalchemy import IndexService
    si = IndexService(config=app.config)


# Configure login page
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'user.login'


# Render UTC dates based on browser settings
moment = Moment(app)    # Also nice jquery and moment import


# Import base view
from . import view


# Blueprint views
from app.user import user_view
from app.report import report_view


# Register with any rules
app.register_blueprint(user_view.bp)
app.register_blueprint(report_view.bp)
