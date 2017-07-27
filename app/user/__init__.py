from . import views as user_view
from .model import User
from app import lm


@lm.user_loader
def load_user(uid):
    return User.get(id=int(uid))
