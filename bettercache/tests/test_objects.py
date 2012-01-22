from bettercache.objects import CacheModel, Field, Key
import unittest


class A(CacheModel):
    a = Key()
    b = Key()

class B(CacheModel):
    x = Field(name='y')

class C(CacheModel):
    name = Key()
    value = Field()

class D(CacheModel):
    a = Key()
    b = Key()


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

    def test_non_string_key(self):
        a = A(a='foo', b=42)
        b = A(a='foo', b='42')
        a.key()

    def test_save_and_get(self):
        c = C(name='T', value=42)
        c.save()
        c2 = C.get(name='T')
        self.assertEqual(c2.value, 42)
        self.assertEqual(c2.name, 'T')

    def test_same_keys(self):
        a = A(a=1, b=2)
        d = D(a=1, b=2)

        self.assertEqual(a.keys(), d.keys())
        self.assertNotEqual(a._all_keys(), d._all_keys())

