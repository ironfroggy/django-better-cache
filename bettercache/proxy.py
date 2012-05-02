# Create your views here.
from httplib2 import Http

from django.http import HttpResponse
from django.conf import settings
from django.core.servers.basehttp import is_hop_by_hop

HOST = getattr(settings, 'BETTERCACHE_ORIGIN_HOST', 'localhost')

if getattr(settings, 'BETTERCACHE_ORIGIN_PORT', None):
    HOST += ":" + str(settings.BETTERCACHE_ORIGIN_PORT)


def proxy(request):

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
    info, content = http.request(uri, 'GET', headers=headers)
    response = HttpResponse(content, status=info.pop('status'))

    for name, val in info.items():
        if not is_hop_by_hop(name):
            response[name] = val

    return response


def header_name(name):
    """Convert header name like HTTP_XXXX_XXX to Xxxx-Xxx:"""
    words = name[5:].split('_')
    for i in range(len(words)):
        words[i] = words[i][0].upper() + words[i][1:].lower()
    result = '-'.join(words)
    return result
