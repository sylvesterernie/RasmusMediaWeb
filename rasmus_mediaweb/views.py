import os
import mimetypes

from pyramid.view import view_config, view_defaults
from pyramid.view import notfound_view_config
from pyramid.exceptions import NotFound
from pyramid.response import FileResponse
import guessit

from .pathcache import PathCacheManager
from .findmedia import find_manager


@view_config(renderer='templates/dashboard.jinja2',
             route_name='dashboard')
def dashboard(request):
    return {}


@view_config(renderer='templates/find-media.jinja2',
             route_name='find_media')
def find_media(request):
    return {}


def flatten_finds(finds):
    all = []
    for k, group in finds.items():
        all += group
    return all


@view_config(renderer='json',
             route_name='api_find_media')
def api_find_media(request):
    return flatten_finds(find_manager.find(request.params['s'],
                                           request.params['t']))


@view_config(renderer='templates/transmission.jinja2',
             route_name='transmission')
def transmission(request):
    return {}


@view_config(renderer='templates/media.jinja2',
             route_name='media')
def media(request):
    return {}


def get_type(path):
    if os.path.isdir(path):
        return 'folder'
    else:
        return mimetypes.guess_type(path)[0]


@view_config(route_name='media_access',
             request_method='GET')
def media_access(request):
    basedir = request.registry.settings.get('media.dir', None)
    if not basedir:
        raise NotFound(request.path_url)

    path = request.matchdict['path']
    if '..' in path:
        raise NotFound(path)

    itempath = basedir + path

    content_type = 'application/octet-stream'
    if not request.params.get('download', False):
        content_type = mimetypes.guess_type(itempath)[0]

    return FileResponse(itempath,
                        request=request,
                        content_type=content_type)


@view_defaults(route_name='api_media',
               renderer='json')
class MediaAPI(object):
    def __init__(self, request):
        self.request = request

    @view_config(request_method='GET')
    def get(self):
        basedir = self.request.registry.settings.get('media.dir', None)
        if not basedir:
            raise NotFound(self.request.path_url)

        path = self.request.matchdict['path']
        if '..' in path:
            raise NotFound(path)

        dirpath = basedir + path
        if not os.path.isdir(dirpath):
            raise NotFound(self.request.path_url)
        items = []
        for name in os.listdir(dirpath):
            if name.startswith('.'):
                continue
            href = self.request.path_url + name
            type_ = get_type(os.path.join(dirpath, name)) or ''

            if type_ is None:
                continue
            major = type_.split('/')[0]
            if type_ != 'folder':
                if major != 'video':
                    continue

            itempath = path + name
            if itempath.startswith('//'):
                itempath = itempath[1:]
            if type_ == 'folder':
                href += '/'
                itempath += '/'

            item = {
                'name': name,
                'href': href,
                'type': type_,
                'path': itempath,
            }
            if type_ != 'folder':
                pm = PathCacheManager(self.request.db)
                data = pm.get(itempath, None)
                if data is None:
                    cached = False
                    media_info = guessit.guess_file_info(name)
                    if 'language' in media_info:
                        media_info['language'] = [x.english_name for x in
                                                  media_info['language']]
                    pm[itempath] = {'media_info': media_info}
                else:
                    cached = True
                    media_info = data['media_info']

                item.update({
                    'download_url': self.request.route_url('media_access',
                                                           path=itempath) + '?download=1',
                    'stream_url': self.request.route_url('media_access',
                                                         path=itempath),
                    'size': os.stat(os.path.join(dirpath, name)).st_size,
                    'media_info': media_info,
                })

            items.append(item)
        return {'items': items}


@notfound_view_config(renderer='json',
                      content_type='application/json')
def notfound_json(request):
    request.response.status = '404 Not Found'
    return {'error': '%s not found' % request.path, 'arguments': [request.path]}


@notfound_view_config(renderer='templates/404.jinja2')
def notfound(request):
    request.response.status = '404 Not Found'
    return {}
