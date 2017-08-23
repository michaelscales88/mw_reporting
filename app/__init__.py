from __future__ import absolute_import
from flask_login import LoginManager
from platform import system
from app.util import Flask, make_celery, AlchemyEncoder


# Need to make some decisions based on the file system
deployed = system() == 'Linux'


# store private information in instance
app = Flask(
    __name__,
    instance_relative_config=True,
    instance_path='/var/www/tmp/' if deployed else None,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static'
)


# Set the json encoder
app.json_encoder = AlchemyEncoder


# Get app settings
app.config.from_object(
    'app.default_config.ProductionConfig'
) if deployed else app.config.from_object(
    'app.default_config.DevelopmentConfig'
)

app.config.from_yaml('clients.yml', silent=True)
app.config.from_yaml('secret_stuff.yml', silent=True)


# Init task queue
celery = make_celery(app)


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
