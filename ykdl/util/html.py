#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from ykdl.compact import Request, urlopen

from .match import match1

fake_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.2.1'
}

def add_header(key, value):
    global fake_headers
    fake_headers[key] = value

def unicodize(text):
    return re.sub(r'\\u([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])', lambda x: chr(int(x.group(0)[2:], 16)), text)

def ungzip(data):
    """Decompresses data for Content-Encoding: gzip.
    """
    from io import BytesIO
    import gzip
    buffer = BytesIO(data)
    f = gzip.GzipFile(fileobj=buffer)
    return f.read()

def undeflate(data):
    """Decompresses data for Content-Encoding: deflate.
    (the zlib compression is used.)
    """
    import zlib
    decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
    return decompressobj.decompress(data)+decompressobj.flush()

def get_location(url, headers = fake_headers):
    response = urlopen(Request(url, headers = fake_headers))
    # urllib will follow redirections and it's too much code to tell urllib
    # not to do that
    return response.geturl()

def get_content(url, headers=fake_headers, data=None, charset = None):
    """Gets the content of a URL via sending a HTTP GET request.

    Args:
        url: A URL.
        headers: Request headers used by the client.
        decoded: Whether decode the response body using UTF-8 or the charset specified in Content-Type.

    Returns:
        The content as a string.
    """

    req = Request(url, headers=headers, data=data)
    #if cookies_txt:
    #    cookies_txt.add_cookie_header(req)
    #    req.headers.update(req.unredirected_hdrs)
    response = urlopen(req)
    data = response.read()

    # Handle HTTP compression for gzip and deflate (zlib)
    resheader = response.info()
    if 'Content-Encoding' in resheader:
        content_encoding = resheader['Content-Encoding']
    else:
        content_encoding = None
    if content_encoding == 'gzip':
        data = ungzip(data)
    elif content_encoding == 'deflate':
        data = undeflate(data)

    if charset == 'ignore':
        return data

    # Decode the response body
    if charset is None:
        charset = match1(resheader['Content-Type'], r'charset=([\w-]+)') or \
              match1(str(data), r'charset=\"([^\"]+)', 'charset=([^"]+)') or 'utf-8'
    try:
        data = data.decode(charset)
    except:
        from .log import w
        w("wrong charset for {}".format(url))
    return data

#DEPRECATED below, return None or 0
def url_size(url, faker = False):
    return 0

def urls_size(urls):
    return sum(map(url_size, urls))

def url_info(url, faker = False):
    return '', '', 0
