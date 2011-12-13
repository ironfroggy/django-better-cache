"""Cache Objects represent cached data with serialized fields and queryable
keys.

This roughly follows patterns from Django's own DB models, but allows the
similar interface to access data in a cache, for adding, finding, updating,
or invalidating entries easily.
"""

import json
import collections

from django.core.cache import cache as _cache


class CacheModel(object):

    def __init__(self, *args, **kwargs):
        items = [(k, v) for (k, v)
            in vars(type(self)).items()
            if isinstance(v, Field)
        ]
        known_fields = set()
        for name, field in items:
            if field.name is None:
                field.name = name
            known_fields.add(field.name)

        self._data = {}
        
        for name, value in kwargs.items():
            if name in known_fields:
                setattr(self, name, value)
            else:
                raise AttributeError("Unknown field '{0}' given.".format(name))

    def _all_keys(self):
        keys = self.keys()
        keys['$MODULE'] = type(self).__module__
        keys['$CLASS'] = type(self).__name__
        return keys
        
    def keys(self):
        keys = collections.OrderedDict()

        def order_key((k, v)):
            cache_key = getattr(type(self), k)
            return cache_key.order
        
        items = [(k, v) for (k, v)
            in vars(type(self)).items()
            if isinstance(v, Key)
        ]

        for k, v in sorted(items, key=order_key):
            keys[k] = getattr(self, k)
        return keys

    @classmethod
    def _key(self, keys):
        return '/'.join('='.join((k, v)) for (k, v) in keys.items())

    def key(self):
        return self._key(self._all_keys())

    def serialize(self):
        keys = self._all_keys()
        serdata = {}
        for fieldname, value in self._data.items():
            serdata[fieldname] = getattr(type(self), fieldname).python_to_cache(value)
        return json.dumps(serdata)

    @classmethod
    def deserialize(cls, string):
        data = json.loads(string)
        for fieldname, value in data.items():
            data[fieldname] = getattr(cls, fieldname).cache_to_python(value)
        return cls(**data)

    def save(self):
        s = self.serialize()
        key = self._key(self._all_keys())
        _cache.set(key, s)

    @classmethod
    def get(cls, **kwargs):
        k = cls(**kwargs).key()
        data = _cache.get(k)
        return cls.deserialize(data)


_next_order_value = 0
def _next_order():
    global _next_order_value
    _next_order_value += 1
    return _next_order_value

class Field(object):
    def __init__(self, name=None):
        self.order = _next_order()
        self.name = name

    def __get__(self, obj, cls):
        if obj is None:
            return self
        else:
            return obj._data[self.name]

    def __set__(self, obj, value):
        obj._data[self.name] = value

    def python_to_cache(self, value):
        return json.dumps(value)

    def cache_to_python(self, value):
        return json.loads(value)


class Key(Field):
    pass
