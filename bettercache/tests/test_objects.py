from bettercache.objects import CacheModel, Field, Key, PickleField
import unittest


class A(CacheModel):
    a = Key()
    b = Key()

class B(CacheModel):
    x = Field(name='y')

class C(CacheModel):
    name = Key()
    value = Field()

class C2(C):
    pass

class D(CacheModel):
    a = Key()
    b = Key()

class E(CacheModel):
    a = Key()
    b = Field()

    def from_miss(self, a):
        self.b = a + 1

class F(CacheModel):
    a = Key()
    b = Field()

class P(CacheModel):
    k = Key()
    p = PickleField()


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
        self.assertNotEqual(a.key(), b.key())

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

    def test_missing(self):
        def get():
            C.get(name='missing')

        self.assertRaises(CacheModel.Missing, get)

    def test_from_miss(self):
        e = E.get(a=1)

        self.assertEqual(e.b, 2)

    def test_empty_subclass(self):
        a = C(name='foo', value=10)
        b = C2(name='foo', value=20)
        a.save()
        b.save()

        self.assertEqual(a.keys(), b.keys())

        self.assertEqual(10, C.get(name='foo').value)
        self.assertEqual(20, C2.get(name='foo').value)

    def test_pickle_field(self):
        s = set((1, 2, 3))
        p = P(k=1, p=s)
        p.save()

        self.assertEqual(s, P.get(k=1).p)

