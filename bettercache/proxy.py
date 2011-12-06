# Create your views here.

import socket
import time
#import asyncore, socket

from django.http import HttpResponse
from django.conf import settings

HOST = (settings.BETTERCACHE_ORIGIN_HOST, settings.BETTERCACHE_ORIGIN_PORT)

def proxy(request):
    #print request
    if request.META['QUERY_STRING']:
        querystring = request.META['PATH_INFO'] + '?' + request.META['QUERY_STRING']
    else:
        querystring = request.META['PATH_INFO']
    server_protocol = request.META['SERVER_PROTOCOL']

    data = []
    data.append(' '.join([request.method, querystring, server_protocol]))#
    for a, b in request.environ.iteritems():
        if a.startswith('HTTP_'):
            a = header_name(a)
            data.append('%s %s'%(a,b))
    data = '\r\n'.join(data)+'\r\n\r\n'
    #print data

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(HOST)

    sock.sendall(data)
    output = []
    while True:
        #print 'doing'
        buf = sock.recv(1024)
        if buf:
            output.append(buf)
        else:
            break
    incoming = ''.join(output)
    #print incoming

    if incoming.startswith('HTTP/'):
        #print incoming[:incoming.index('\r\n')]
        status_line = incoming[:incoming.index('\r\n')].split()
        server_protocol, status_code = status_line[0],status_line[1]
        headers = incoming[incoming.index('\r\n')+2:incoming.index('\r\n\r\n')]
        content = incoming[incoming.index('\r\n\r\n')+4:]

        response = HttpResponse(content, status=int(status_code))
        for i in headers.split('\r\n'):
            print i[:i.index(':')], i[i.index(':')+2:]
            response[i[:i.index(':')]] = i[i.index(':')+2:]

        return response
    else:
        return HttpResponse2(incoming)


def header_name(name):
    """Convert header name like HTTP_XXXX_XXX to Xxxx-Xxx:"""
    words = name[5:].split('_')
    for i in range(len(words)):
        words[i] = words[i][0].upper() + words[i][1:].lower()
    result = '-'.join(words) + ':'
    return result


class HttpResponse2(object):
    status_code = 200

    def __init__(self, content=''):
        if not isinstance(content, basestring) and hasattr(content, '__iter__'):
            self._container = content
            self._is_string = False
        else:
            self._container = [content]
            self._is_string = True
        self.cookies = {}#SimpleCookie()
        self._headers = {}#{'content-type': ('Content-Type', content_type)}

    def items(self):
        return self._headers.values()

    def __iter__(self):
        self._iterator = iter(self._container)
        return self

    def next(self):
        chunk = self._iterator.next()
        if isinstance(chunk, unicode):
            chunk = chunk.encode(self._charset)
        return str(chunk)
