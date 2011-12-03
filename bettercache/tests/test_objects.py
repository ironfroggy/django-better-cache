from bettercache.objects import CacheModel, CacheField, CacheKey
import unittest


class A(CacheModel):
    a = CacheKey()
    b = CacheKey()

class B(CacheModel):
    x = CacheField(name='y')

class C(CacheModel):
    name = CacheKey()
    value = CacheField()


class ModelTest(unittest.TestCase):

    def test_key_order(self):
        keys = A(a=1, b=2).keys().items()
        self.assertEqual(keys[0], ('a', 1))
        self.assertEqual(keys[1], ('b', 2))

    def test_name_override(self):
        self.assertEqual(B(y=10).y, 10)

    def test_unknown_field(self):
        self.assertRaises(AttributeError, B, z=1)

    def test_keys(self):
        keys = C(name='T', value=42).keys()
        self.assertEqual(dict(keys), {'name': 'T'})

    def test_serialize(self):
        c = C(name='T', value=42)
        s = c.serialize()
        c2 = C.deserialize(s)

    def test_save_and_get(self):
        c = C(name='T', value=42)
        c.save()
        c2 = C.get(name='T')
        self.assertEqual(c2.value, 42)
        self.assertEqual(c2.name, 'T')

