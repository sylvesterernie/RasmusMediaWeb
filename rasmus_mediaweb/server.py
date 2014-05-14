import argparse

from waitress import serve

from .wsgi import make_app


def main():
    parser = argparse.ArgumentParser(
        description=('Command-line interface for running the '
                     'RasmusMediaWeb server'),
    )
    parser.add_argument(
        '-p', '--port',
        default='8888',
        help='Port to listen on (default: 8888)',
    )
    parser.add_argument(
        '-i', '--interface',
        default='0.0.0.0',
        help='Interface to listen on (default: 0.0.0.0)',
    )
    parser.add_argument(
        '--prefix',
        help='Serve app at a prefixed url',
    )
    args = parser.parse_args()

    kwargs = {
        'host': args.interface,
        'port': args.port,
    }
    if args.prefix:
        kwargs['url_prefix'] = args.prefix

    serve(make_app(), **kwargs)
