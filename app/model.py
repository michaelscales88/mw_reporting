from sqlalchemy_utils import generic_repr
from sqlalchemy.ext.declarative import declared_attr, declarative_base


@generic_repr
class _Base(object):

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


Base = declarative_base(cls=_Base)
