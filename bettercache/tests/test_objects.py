from bettercache.objects import CacheModel, CacheField, CacheKey
import unittest


class A(CacheModel):
    a = CacheKey()
    b = CacheKey()

class B(CacheModel):
    x = CacheField(name='y')


class ModelTest(unittest.TestCase):

    def test_key_order(self):
        keys = A(a=1, b=2).keys().items()
        self.assertEqual(keys[0], ('a', 1))
        self.assertEqual(keys[1], ('b', 2))

    def test_name_override(self):
        self.assertEqual(B(y=10).y, 10)

    def test_unknown_field(self):
        self.assertRaises(AttributeError, B, z=1)

