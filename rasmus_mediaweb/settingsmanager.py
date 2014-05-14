from sqlalchemy.orm.exc import NoResultFound

from .dbmodels import Setting
from .defaults import default_sql_url


def get_settings(settings=None, **kwargs):
    our_settings = {
        'default_locale_name': 'en',
        'jinja2.filters': {
            'model_url': 'pyramid_jinja2.filters:model_url_filter',
            'route_url': 'pyramid_jinja2.filters:route_url_filter',
            'static_url': 'pyramid_jinja2.filters:static_url_filter',
        },
        'sqlalchemy.url': default_sql_url,
    }
    our_settings.update(settings if settings else {})
    our_settings.update(kwargs if kwargs else {})

    return our_settings


class SettingsManager(object):
    def __init__(self, db):
        self.db = db

    def __getitem__(self, k):
        try:
            return self.db.query(Setting).filter_by(key=k).one().value
        except NoResultFound:
            return None

    def __setitem__(self, k, v):
        try:
            setting = self.db.query(Setting).filter_by(key=k).one()
        except NoResultFound:
            setting = Setting(key=k)

        setting.value = v
        self.db.add(setting)

    def keys(self):
        return [x.key for x in self.db.query(Setting)]

    def items(self):
        return [(x.key, x.value) for x in self.db.query(Setting)]

    def update_missing(self, settings):
        for setting in self.db.query(Setting).all():
            if setting.key not in settings:
                settings[setting.key] = setting.value
