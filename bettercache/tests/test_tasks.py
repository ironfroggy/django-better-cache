import mock
from unittest2 import TestCase

from bettercache.tasks import GeneratePage

class TestGeneratePage(TestCase):
    def setUp(self):
        self.gp = GeneratePage()

    def test_should_rebuild(self):
        self.assertTrue(self.gp.should_rebuild(mock.Mock()))
