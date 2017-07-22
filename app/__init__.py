from flask import Flask, Blueprint, url_for, redirect
from flask_restful import Api

# store private information in instance
app = Flask(__name__, instance_relative_config=True, static_folder='static', template_folder='templates')

# Load default templates
app.config.from_object('app.default_config.DevelopmentConfig')

# Start the index service
if app.config['ENABLE_SEARCH']:
    from whooshalchemy import IndexService
    si = IndexService(config=app.config)


@app.route('/')
def catch_all():
    return redirect(
        url_for('index')
    )


# Avoid favicon 404
@app.route("/favicon.ico", methods=['GET'])
def favicon():
    return url_for('static', filename='favicon.ico')


# Create api and register views
# api = Api(app=app)
# api_bp = Blueprint('api', __name__)

from . import view
from app.user import user_view
from app.report import report_view

app.register_blueprint(user_view.bp)
app.register_blueprint(report_view.bp)

# from .resources import GalleryView
# Add api resources
# api.add_resource(GalleryView, '/gallery')

# Register the API to the app
# app.register_blueprint(api_bp)
