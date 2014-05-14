from sqlalchemy import (
    Column,
    Integer,
    Unicode,
)
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .defaults import default_sql_url


Base = declarative_base()

table_prefix = 'rasmusmediaweb_'


def make_session(settings=None):
    settings = dict(settings or {})
    settings.setdefault('sqlalchemy.url', default_sql_url)
    engine = engine_from_config(settings,
                                prefix='sqlalchemy.')
    session = sessionmaker(bind=engine)()
    return session


class Setting(Base):
    __tablename__ = '%ssettings' % table_prefix

    id = Column(Integer, primary_key=True)
    key = Column(Unicode(40))
    value = Column(Unicode(40))


class PathCache(Base):
    __tablename__ = '%spath_cache' % table_prefix

    id = Column(Integer, primary_key=True)
    path = Column(Unicode(255), unique=True, index=True)
    data = Column(Unicode)
