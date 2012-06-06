from unittest import TestCase

import mock

from django.conf import settings

from bettercache.proxy import proxy, header_name

class TestHeaderName(TestCase):

    def testheadername(self):
        self.assertEqual(header_name('HTTP_CACHE_CONTROL'), 'Cache-Control')

class TestProxy(TestCase):

    @mock.patch('bettercache.proxy.Http')
    def testproxy(self, Http):
        req = mock.Mock()
        req.environ = dict( HTTP_CACHE_CONTROL='cache-headers',
                        HTTP_X_FOO='foobar',
                        PATH_INFO='/foo/bar',
                        QUERY_STRING='foo=bar&bar=foo',
                        HTTP_HOST='example.com',
                        )
        req.META = req.environ
        mockhttp = mock.Mock()
        mockhttp.request.return_value = ({'status':'200','Cache-Control':'no-cache', 'Keep-Alive': '10', },'bar')
        Http.return_value = mockhttp
        resp = proxy(req)
        req_args, req_kwargs =  mockhttp.request.call_args
        self.assertTrue('foo/bar?foo=bar&bar=foo' in req_args[0])
        self.assertEqual(req_args[1], 'GET')
        headers = {'Host': 'example.com', 'X-Foo': 'foobar', 'Cache-Control': 'cache-headers'}
        self.assertEqual(req_kwargs['headers'], headers)
        self.assertEqual(resp['Cache-Control'], 'no-cache')
        self.assertEqual(resp.content, 'bar')
        self.assertFalse(hasattr(resp, 'Keep-Alive'))
