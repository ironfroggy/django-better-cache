from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock

from bettercache.tasks import GeneratePage

#class TestGeneratePage(TestCase):
#    def setUp(self):
#        self.gp = GeneratePage()
