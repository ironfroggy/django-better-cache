"""Fulfills a request by passing it along to another server, if this one
cannot fulfill it.

This is used in configurations where bettercache runs on its own, acting
solely as a caching layer, and deferring requests it does not have in the
cache. 
"""

from httplib2 import Http
import logging

from django.http import HttpResponse
from django.conf import settings

try:
    from django.core.servers.basehttp import is_hop_by_hop
except ImportError:
    # Removed in Django 1.4
    _hop_headers = {
        'connection':1, 'keep-alive':1, 'proxy-authenticate':1,
        'proxy-authorization':1, 'te':1, 'trailers':1, 'transfer-encoding':1,
        'upgrade':1
    }

    def is_hop_by_hop(header_name):
        """Return true if 'header_name' is an HTTP/1.1 "Hop-by-Hop" header"""
        return header_name.lower() in _hop_headers

HOST = getattr(settings, 'BETTERCACHE_ORIGIN_HOST', 'localhost')
logger = logging.getLogger(__name__)

if getattr(settings, 'BETTERCACHE_ORIGIN_PORT', None):
    HOST += ":" + str(settings.BETTERCACHE_ORIGIN_PORT)


def proxy(request):
    """Pass an HTTP request on to another server."""

    # TODO: don't hardcode http
    uri = "http://" + HOST + request.META['PATH_INFO']
    if request.META['QUERY_STRING']:
        uri += '?' + request.META['QUERY_STRING']

    headers = {}
    for name, val in request.environ.iteritems():
        if name.startswith('HTTP_'):
            name = header_name(name)
            headers[name] = val

    # TODO: try/except
    http = Http()
    http.follow_redirects = False
    logger.debug("GET for: %s" % uri)
    info, content = http.request(uri, 'GET', headers=headers)
    response = HttpResponse(content, status=info.pop('status'))

    for name, val in info.items():
        if not is_hop_by_hop(name):
            response[name] = val
    logger.info("PROXY to: %s" % uri)
    return response


def header_name(name):
    """Convert header name like HTTP_XXXX_XXX to Xxxx-Xxx:"""
    
    words = name[5:].split('_')
    for i in range(len(words)):
        words[i] = words[i][0].upper() + words[i][1:].lower()
    result = '-'.join(words)
    return result
