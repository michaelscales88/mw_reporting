from . import views as user_view
from .model import User
from flask_login import LoginManager
from app import app


# Configure login page
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'user.login'


@lm.user_loader
def load_user(id):
    return User.get(id=int(id))
