from unittest2 import TestCase

import mock

from django.conf import settings

from bettercache.proxy import proxy, header_name

class TestHeaderName(TestCase):

    def testheadername(self):
        self.assertEqual(header_name('HTTP_CACHE_CONTROL'), 'Cache-Control')
