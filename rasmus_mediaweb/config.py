import logging
import os

from pyramid.config import Configurator
from pyramid.wsgi import wsgiapp
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker

from .settingsmanager import SettingsManager
from .wsgi.utils import Proxy
from .settingsmanager import get_settings
from .defaults import default_sql_url, etcdir


def db_from_registry(registry):
    maker = registry.dbmaker
    session = maker()

    return session


def request_db(request):
    session = db_from_registry(request.registry)

    def cleanup(request):
        if request.exception is not None:
            session.rollback()
        else:
            session.commit()
        session.close()

    request.add_finished_callback(cleanup)

    return session


class ConfigError(Exception):
    pass


class MissingSettingError(ConfigError):
    def __init__(self, setting):
        self.setting = setting
        super(MissingSettingError, self).__init__(
            'Missing configuration setting: "%s"' % setting)


def make_bool(v):
    if isinstance(v, (int, bool)):
        return bool(v)
    v = str(v).lower()
    return True if v in ('1', 'true', 't') else False


def get_config(settings=None, **kwargs):
    settings = get_settings(settings, **kwargs)
    if (settings['sqlalchemy.url'] == default_sql_url
        and not os.path.exists(etcdir)):
        os.makedirs(etcdir)
    engine = engine_from_config(settings,
                                prefix='sqlalchemy.')
    db = sessionmaker(bind=engine)()
    try:
        sm = SettingsManager(db)
        sm.update_missing(settings)
    finally:
        db.close()

    if 'rasmus.debug.javascript' in settings:
        settings['rasmus.debug.javascript'] = make_bool(settings['rasmus.debug.javascript'])
    else:
        settings['rasmus.debug.javascript'] = False

    config = Configurator(settings=settings)
    config.registry.dbmaker = sessionmaker(bind=engine)
    config.add_request_method(request_db, reify=True)
    logger = logging.getLogger('rasmus_mediaweb')
    logger.info('Using configuration:')
    logger.info('  %s = %s'
                % ('sqlalchemy.url', settings['sqlalchemy.url']))
    if not settings.get('transmission.url', None):
        raise MissingSettingError('tranmission.url')
    for k, v in sm.items():
        logger.info('  %s = %s' % (k, v))
    config.include('pyramid_jinja2')
    if settings.get('debug_toolbar', False):
        config.include('pyramid_debugtoolbar')

    config.add_static_view(name='static', path='rasmus_mediaweb:static')


    def check_content_type_factory(val, config):
        def check(context, request):
            from pprint import pprint

            pprint({'content_type': request.content_type, 'checking': val})
            return request.content_type == val

        check.text = check.phash = lambda: 'content type = %s' % val
        return check

    config.add_view_predicate('content_type', check_content_type_factory)

    config.scan('rasmus_mediaweb')

    config.add_route('dashboard', '/')
    config.add_route('index', '/')
    config.add_route('find_media', '/find-media/')
    config.add_route('api_find_media', '/api/v1/media-search/')
    config.add_route('media', '/media/')
    config.add_route('transmission', '/transmission/')
    config.add_view(
        wsgiapp(Proxy(
            settings['transmission.url'], chop='/transmission/proxy')),
        route_name='transmission_proxy')
    config.add_route('transmission_proxy', '/transmission/proxy{remaining:.*}')
    config.add_route('api_media', '/api/v1/media{path:.*}')
    config.add_route('media_access', '/media-access{path:.*}')
    return config
