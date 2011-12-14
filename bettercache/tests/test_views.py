from unittest2 import TestCase
import mock

from bettercache.views import BetterView

class TestView(TestCase):
    def setUp(self):
        self.view = BetterView()
        self.view.should_bypass_cache = lambda x: False
        self.view.get_cache = lambda x: (None, None, )
        self.view.set_cache = lambda x, y: True
        self.request = mock.Mock()
        self.request.build_absolute_uri = '_'

    @mock.patch('bettercache.views.proxy')
    def test_miss(self, proxy):
        ''' make sure we proxy when there is no cache '''
        proxy.return_value = {}
        self.view.get(self.request)
        self.assertTrue(proxy.called)

    @mock.patch('bettercache.views.GeneratePage')
    @mock.patch('bettercache.views.strip_wsgi')
    @mock.patch('bettercache.views.proxy')
    def test_notexpired(self, proxy, strip_wsgi, GP):
        ''' make sure we don't send off a task if it's not expired '''
        self.view.get_cache = lambda x: ('_', False, )
        self.view.get(self.request)
        self.assertFalse(GP.apply_async.called)
        self.assertFalse(proxy.called)

    @mock.patch('bettercache.views.GeneratePage')
    @mock.patch('bettercache.views.strip_wsgi')
    @mock.patch('bettercache.views.proxy')
    def test_expired(self, proxy, strip_wsgi, GP):
        ''' make sure thats when it's expired the task is sent '''
        self.view.get_cache = lambda x: ('_', True, )
        self.view.get(self.request)
        self.assertTrue(GP.apply_async.called)
        self.assertFalse(proxy.called)
