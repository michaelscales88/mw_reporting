from sqlalchemy import Column, Text, DateTime, Integer
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash
from app.database import Base


class User(Base):
    __searchable__ = ['alias', 'about_me']

    id = Column(Integer, primary_key=True)
    alias = Column(Text, index=True, unique=True)
    email = Column(Text, unique=True)
    avatar = Column(Text, unique=True)
    first_name = Column(Text)
    last_name = Column(Text)
    password_hash = Column(Text)
    about_me = Column(Text)
    last_seen = Column(DateTime)

    clients = relationship(
        'ClientTable',
        secondary='manager_client_link'
    )

    def __json__(self):
        return list(self.__mapper__.columns.keys())

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    @classmethod
    def get(cls, id):
        try:
            return cls.query.get(id)
        except KeyError:
            return None

    @staticmethod
    def make_unique_display_name(nickname):
        if User.query.filter_by(alias=nickname).first() is None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(alias=new_nickname).first() is None:
                break
            version += 1
        return new_nickname

    def add_client(self, client):
        if not self.tracked(client, self.clients):
            self.clients.append(client)
            return self

    def remove_client(self, client):
        if self.tracked(client, self.clients):
            self.clients.append(client)
            return self

    @staticmethod
    def tracked(obj, collection):
        return obj in collection
