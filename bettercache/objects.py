"""Cache Objects represent cached data with serialized fields and queryable
keys.

This roughly follows patterns from Django's own DB models, but allows the
similar interface to access data in a cache, for adding, finding, updating,
or invalidating entries easily.
"""

import json
import collections


class CacheModel(object):

    def __init__(self, *args, **kwargs):
        items = [(k, v) for (k, v)
            in vars(type(self)).items()
            if isinstance(v, CacheField)
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
        
    def keys(self):
        keys = collections.OrderedDict()

        def order_key((k, v)):
            cache_key = getattr(type(self), k)
            return cache_key.order
        
        items = [(k, v) for (k, v)
            in vars(type(self)).items()
            if isinstance(v, CacheKey)
        ]

        for k, v in sorted(items, key=order_key):
                keys[k] = getattr(self, k)
        return keys


_next_order_value = 0
def _next_order():
    global _next_order_value
    _next_order_value += 1
    return _next_order_value

class CacheField(object):
    def __init__(self, name=None):
        self.order = _next_order()
        self.name = name

    def __get__(self, obj, cls):
        if obj is None:
            return self
        else:
            return self.cache_to_python(obj._data[self.name])

    def __set__(self, obj, value):
        obj._data[self.name] = self.python_to_cache(value)

    def python_to_cache(self, value):
        return json.dumps(value)

    def cache_to_python(self, value):
        return json.loads(value)


class CacheKey(CacheField):
    pass

