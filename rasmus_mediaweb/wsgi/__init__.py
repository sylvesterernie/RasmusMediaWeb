from ..config import (get_config, get_settings)

from .gzipper import make_gzip_middleware


def make_pyramid_app(settings=None, **kwargs):
    config = get_config(settings, **kwargs)

    return config.make_wsgi_app()


def make_app(settings=None, **kwargs):
    app = make_pyramid_app(settings, **kwargs)
    settings = get_settings(settings, **kwargs)
    if settings.get('middleware.gzip', True):
        app = make_gzip_middleware(app, settings, compress_level=6)
    return app
