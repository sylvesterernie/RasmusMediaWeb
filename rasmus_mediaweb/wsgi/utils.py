import logging
import pprint

import requests


logger = logging.getLogger('rasmus_mediaweb')


class Proxy(object):
    def __init__(self, base_url, chop=''):
        self.base_url = base_url
        self.chop = chop

    def __call__(self, environ, start_response):
        method = environ['REQUEST_METHOD'].lower()
        path_info = environ['PATH_INFO']
        script = environ['SCRIPT_NAME']

        callback = getattr(requests, method)

        proxied_headers = {}
        for k, v in environ.items():
            if k.startswith('HTTP_X_'):
                proxied_headers[k[5:].replace('_', '-')] = v

        for k in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            if k in environ:
                proxied_headers[k.replace('_', '-')] = environ[k]

        proxied_data = environ['wsgi.input'].read()

        url = self.base_url
        if self.chop and path_info.startswith(self.chop):
            path_info = path_info[len(self.chop):]

        if url.endswith('/') and path_info.startswith('/'):
            url += path_info[1:]
        else:
            url += path_info

        kwargs = {'headers': proxied_headers}
        if len(proxied_data) > 0:
            kwargs['data'] = proxied_data

        logger.debug('Proxying request 1: ' + pprint.pformat(dict(
            url=url,
            headers_sent_to_source=proxied_headers,
            data_sent_to_source=proxied_data,
        )))

        res = callback(url, **kwargs)

        # we have made the request to the actual source, now it's
        # time to return that result back to the caller

        headers = dict(res.headers.items())
        if 'content-encoding' in headers:
            del headers['content-encoding']
        start_response('%s' % res.status_code, headers.items())
        data = b''
        count = 0
        for x in res.iter_content():
            count += len(x)
            data += x

        headers['content-length'] = '%i' % len(data)

        logger.debug('Proxying request 2: ' + pprint.pformat(dict(
            headers_returned=headers,
            data_returned=data,
        )))

        return [data]
