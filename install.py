#!/usr/bin/env python

import argparse
import os
import subprocess
import zipfile


def extract(subdir, name):
    for x in os.listdir(subdir):
        full = os.path.join(subdir, x)
        if x.startswith(name + '-') and os.path.isfile(full):
            targetdir = os.path.join(subdir, x.rsplit('.', 1)[0])
            with zipfile.ZipFile(full) as zf:
                zf.extractall(targetdir)
            return targetdir


def main():
    parser = argparse.ArgumentParser(
        'Build and install the application'
    )
    parser.add_argument(
        'installdir',
        help='Directory to install application',
    )
    args = parser.parse_args()

    installer_dir = os.path.join('build', 'installer')
    downloads_dir = os.path.join(installer_dir, 'downloads')
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
    subprocess.call(['pip', 'install', 'virtualenv', '-d', downloads_dir])
    venv_dir = extract(downloads_dir, 'virtualenv')
    subprocess.call(['python', os.path.join(venv_dir, 'virtualenv.py'), args.installdir])
    #subprocess.call(['python', os.path.join(venv_dir, 'virtualenv.py'), '--relocatable', args.installdir])

    pip = os.path.join(args.installdir, 'bin', 'pip')
    subprocess.call([pip, 'install', '--upgrade', '.'])

    alembic = os.path.join(args.installdir, 'bin', 'alembic')
    subprocess.call([alembic, 'upgrade', 'head'])

    print()
    print('Installation complete!')
    print()
    print('Now you must configure rasmus-mediaweb:')
    print('  %s settings -s transmission.url=http://localhost:8181/transmission/rpc'
          % os.path.join(args.installdir, 'bin', 'rasmus-mediaweb-manage'))
    print()
    print('You can now run rasmusmediaweb with: ' + os.path.join(args.installdir, 'bin', 'rasmus-mediaweb-server'))
    print()


if __name__ == '__main__':
    main()
