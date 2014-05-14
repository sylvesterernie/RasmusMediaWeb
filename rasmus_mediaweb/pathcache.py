import json

from sqlalchemy.orm.exc import NoResultFound

from .dbmodels import PathCache

_marker = object()


class PathCacheManager(object):
    def __init__(self, db):
        self.db = db

    def __getitem__(self, k):
        return self.get(k)

    def get(self, k, default=_marker):
        try:
            entry = self.db.query(PathCache).filter_by(path=k).one()
            return json.loads(entry.data)
        except NoResultFound:
            if default == _marker:
                raise KeyError(k)
        return default

    def __setitem__(self, k, v):
        try:
            entry = self.db.query(PathCache).filter_by(path=k).one()
        except NoResultFound:
            entry = PathCache(path=k)
        entry.data = json.dumps(v)
        self.db.add(entry)
