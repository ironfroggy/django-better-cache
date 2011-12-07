# Create your views here.
from httplib2 import Http

from django.http import HttpResponse
from django.conf import settings
from django.core.servers.basehttp import is_hop_by_hop

HOST = (settings.BETTERCACHE_ORIGIN_HOST, settings.BETTERCACHE_ORIGIN_PORT)


def clean_local(hostname):
    return hostname.replace('local.www','www.test').replace(':8000','')


def proxy(request):

    uri = request.build_absolute_uri()
    uri = clean_local(uri)

    headers = {}
    for name, val in request.environ.iteritems():
        if name.startswith('HTTP_'):
            name = header_name(name)
            if name == "Host":
                val = clean_local(val)
            headers[name] = val

    # TODO: try/except
    print uri
    print headers
    info, content = Http().request(uri, 'GET', headers=headers)
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
