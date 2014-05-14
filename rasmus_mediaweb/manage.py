import argparse

from .dbmodels import make_session
from .settingsmanager import SettingsManager

db_setting_opts = {
    'transmission.url': {
        'title': 'Transmission URL',
        'help': 'URL to transmission rpc service (typically http://somehost.com/transmission/rpc)'
    },

    'media.dir': {
        'title': 'Media Directory',
        'help': 'Path of a directory containing media files (or sub-directories)'
    },
}


def print_settings(sm):
    for key, value in sm.items():
        info = db_setting_opts.get(key, {})
        print()
        print('  %s: %s\n    %s' % (key, value, info.get('help', ''),))


def settings(args):
    to_set = getattr(args, 'settings', None) or []

    session = make_session()
    try:
        sm = SettingsManager(session)
        if not args.quiet:
            print()
            if len(to_set) > 0:
                print('Original Settings:')
            else:
                print('Settings:')
            print_settings(sm)

        if len(to_set) > 0:
            for keyvalue in to_set:
                key, value = keyvalue.split('=', 1)
                key = key.strip().lower()
                value = value.strip()
                sm[key] = value

            session.commit()

            if not args.quiet:
                print()
                print('New Settings:')
                print_settings(sm)
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(
        description='Command-line interface for managing RasmusMediaWeb',
    )
    subparsers = parser.add_subparsers(
        title='subcommands',
    )
    settings_parser = subparsers.add_parser(
        'settings',
        help='Manage/Retrieve settings'
    )
    settings_parser.set_defaults(callback=settings)
    settings_parser.add_argument(
        '-s', '--set',
        dest='settings',
        metavar='name=value',
        nargs='+',
    )
    settings_parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        default=False,
    )

    args = parser.parse_args()

    if getattr(args, 'callback', None) is None:
        parser.print_help()
    else:
        args.callback(args)
