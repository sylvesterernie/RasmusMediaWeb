# This is a direct copy of Paste's gzipper.py module with minor updates to support
# Python 3 and live standalone outside of Paste

# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

"""
WSGI middleware

Gzip-encodes the response.
"""

import gzip

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import BytesIO as StringIO


def header_value(headers, name):
    """
    Returns the header's value, or None if no such header.  If a
    header appears more than once, all the values of the headers
    are joined with ','.   Note that this is consistent /w RFC 2616
    section 4.2 which states:

        It MUST be possible to combine the multiple header fields
        into one "field-name: field-value" pair, without changing
        the semantics of the message, by appending each subsequent
        field-value to the first, each separated by a comma.

    However, note that the original netscape usage of 'Set-Cookie',
    especially in MSIE which contains an 'expires' date will is not
    compatible with this particular concatination method.
    """
    name = name.lower()
    result = [value for header, value in headers
              if header.lower() == name]
    if result:
        return ','.join(result)
    else:
        return None


def remove_header(headers, name):
    """
    Removes the named header from the list of headers.  Returns the
    value of that header, or None if no header found.  If multiple
    headers are found, only the last one is returned.
    """
    name = name.lower()
    i = 0
    result = None
    while i < len(headers):
        if headers[i][0].lower() == name:
            result = headers[i][1]
            del headers[i]
            continue
        i += 1
    return result


class GzipOutput(object):
    pass


class middleware(object):
    def __init__(self, application, compress_level=6):
        self.application = application
        self.compress_level = int(compress_level)

    def __call__(self, environ, start_response):
        if 'gzip' not in environ.get('HTTP_ACCEPT_ENCODING', ''):
            # nothing for us to do, so this middleware will
            # be a no-op:
            return self.application(environ, start_response)
        response = GzipResponse(start_response, self.compress_level)
        app_iter = self.application(environ,
                                    response.gzip_start_response)
        if app_iter is not None:
            response.finish_response(app_iter)

        return response.write()


class GzipResponse(object):
    def __init__(self, start_response, compress_level):
        self.start_response = start_response
        self.compress_level = compress_level
        self.buffer = StringIO()
        self.compressible = False
        self.content_length = None

    def gzip_start_response(self, status, headers, exc_info=None):
        self.headers = headers
        ct = header_value(headers, 'content-type')
        ce = header_value(headers, 'content-encoding')
        self.compressible = False
        if ct and (ct.startswith(
                'text/') or ct == 'application/json' or ct.startswith(
                'application/json;')) \
                and 'zip' not in ct:
            self.compressible = True
        if ce:
            self.compressible = False
        if self.compressible:
            headers.append(('content-encoding', 'gzip'))
        remove_header(headers, 'content-length')
        self.headers = headers
        self.status = status
        return self.buffer.write

    def write(self):
        out = self.buffer
        out.seek(0)
        s = out.getvalue()
        out.close()
        return [s]

    def finish_response(self, app_iter):
        output = None

        try:
            for s in app_iter:
                if not output:
                    if self.compressible:
                        output = gzip.GzipFile(mode='wb',
                                               compresslevel=self.compress_level,
                                               fileobj=self.buffer)
                    else:
                        output = self.buffer
                output.write(s)
            if output and self.compressible:
                output.close()
        finally:
            if hasattr(app_iter, 'close'):
                app_iter.close()
        content_length = self.buffer.tell()
        remove_header(self.headers, 'content-length')
        self.headers.append(('Content-Length', '%i' % content_length))
        self.start_response(self.status, self.headers)


def filter_factory(application, **conf):
    import warnings

    warnings.warn(
        'This function is deprecated; use make_gzip_middleware instead',
        DeprecationWarning, 2)

    def filter(application):
        return middleware(application)

    return filter


def make_gzip_middleware(app, global_conf, compress_level=6):
    """
    Wrap the middleware, so that it applies gzipping to a response
    when it is supported by the browser and the content is of
    type ``text/*`` or ``application/*``
    """
    compress_level = int(compress_level)
    return middleware(app, compress_level=compress_level)
