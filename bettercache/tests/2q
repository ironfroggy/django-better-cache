from unittest2 import TestCase

from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_cache_control

from bettercache.utils import get_cc_dict, set_post_pre_check_headers

class TestCCDict(TestCase):
    def test_get_cc_dict(self):
        resp = HttpResponse()
        resp['Cache-Control'] = 'x=1, y'
        expected = dict(x='1', y=True)
        actual = get_cc_dict(resp)
        for k in expected:
            self.assertEqual(expected[k], actual[k])

class TestPostPre(TestCase):
    def setUp(self):
        self.resp = HttpResponse()
        if hasattr(settings, 'CACHE_POST_CHECK_RATIO'):
            self.real_post_ratio = settings.CACHE_POST_CHECK_RATIO
        settings.CACHE_POST_CHECK_RATIO = 0.5

    def tearDown(self):
        if hasattr(self, 'real_post_ratio'):
            settings.CACHE_POST_CHECK_RATIO = self.real_post_ratio
        else:
            del settings.CACHE_POST_CHECK_RATIO

    def do_cc(self, response):
        set_post_pre_check_headers(response)
        return get_cc_dict(response)


    def test_simple(self):
        """ make sure the headers get computed and added correctly """
        self.resp['Cache-Control'] = "max-age=100"
        ccd = self.do_cc(self.resp)
        self.assertEqual(ccd['pre-check'], '100')
        self.assertEqual(ccd['post-check'], '50')

    def test_no_max_age(self):
        """ make sure no headers get added if there is no max-age """
        ccd = self.do_cc(self.resp)
        self.assertFalse('pre-check' in ccd)
        self.assertFalse('post-check' in ccd)

    def test_no_overwrite(self):
        self.resp['Cache-Control'] = "max-age=100"
        patch_cache_control(self.resp, **{'pre-check' : 10, 'post-check' : 1,})
        ccd = self.do_cc(self.resp)
        self.assertEqual(ccd['pre-check'], '10')
        self.assertEqual(ccd['post-check'], '1')
