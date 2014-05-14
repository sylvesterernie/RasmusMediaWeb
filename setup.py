import os
import re
from setuptools import setup, find_packages


def get_version():
    regex = re.compile(r'__version__ *= *[\'\"]([a-zA-Z0-9.]*)[\'\"].*')
    base = os.path.dirname(__file__)
    version = None
    with open(os.path.join(base, 'rasmus_mediaweb', '__init__.py')) as f:
        for line in f:
            line = line.strip()
            match = regex.match(line)
            if match:
                version = match.group(1)
                break

    return version

setup(
    name='RasmusMediaWeb',
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        'Pyramid >= 1.5, <= 1.5.999',
        'Jinja2 >= 2.7, <= 2.7.999',
        'pyramid_jinja2 >= 2.0, <= 2.0.999',
        'Waitress >= 0.8, <= 0.8.999',
        'SQLAlchemy >= 0.9, <= 0.9.999',
        'Alembic >= 0.6, <= 0.6.999',
        'requests >= 2.2, <= 2.2.999',
        'pyramid_debugtoolbar >= 2.0, <= 2.0.999',
        'guessit >= 0.7, <= 0.7.999',
        'beautifulsoup4 >= 4.3.2, <= 4.3.999',
    ],
    entry_points={
        'console_scripts': [
            'rasmus-mediaweb-server = rasmus_mediaweb.server:main',
            'rasmus-mediaweb-manage = rasmus_mediaweb.manage:main'
        ],
        'paste.app_factory': [
            'wsgiapp = rasmus_mediaweb.wsgi:make_app',
        ],
    }
)
