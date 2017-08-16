from flask_login import LoginManager
from platform import system

from app.util.flask_extended import Flask


# Need to make some decisions based on the file system
deployed = system() == 'Linux'


# store private information in instance
app = Flask(
    __name__,
    instance_relative_config=True,
    instance_path='/tmp/' if deployed else None,
    static_folder='static',
    template_folder='templates'
)


# Get app settings
app.config.from_object(
    'app.default_config.DevelopmentConfig'
)


app.config.from_yaml('clients.yml', silent=True)
app.config.from_yaml('secret_stuff.yml', silent=True)


# Configure login page
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'user.login'


# Import base views
from . import view


# Blueprint views
from app.user import user_view
from app.report import report_view


# Register with any rules
app.register_blueprint(user_view.bp)
app.register_blueprint(report_view.bp)
