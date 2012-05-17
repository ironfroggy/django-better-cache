"""Cache Objects represent cached data with serialized fields and queryable
keys.

This roughly follows patterns from Django's own DB models, but allows the
similar interface to access data in a cache, for adding, finding, updating,
or invalidating entries easily.
"""

import json
import cPickle as pickle
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
import urllib

from django.core.cache import cache as _cache


class CacheModel(object):
    """Defines a structured class of cache entry, in the same way a DB
    defines tables or other schema. The structure is a series of fields
    and keys, and instances of ``CacheModel`` can be saved to the cache
    and fetched back if you know the keys.
    
    You do not need to construct key strings by hand.
    """

    expires = None

    class Missing(Exception):
        """Raised when fetching with keys that are not found."""

    def __init__(self, *args, **kwargs):
        items = self._get_fields()
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

    @classmethod
    def _get_fields(cls):
        for k in dir(cls):
            v = getattr(cls, k)
            if isinstance(v, Field):
                yield (k, v)

    def _all_keys(self):
        keys = self.keys()
        keys['$MODULE'] = type(self).__module__
        keys['$CLASS'] = type(self).__name__
        return keys
        
    def keys(self):
        """Create an ordered dict of the names and values of key fields."""

        keys = OrderedDict()

        def order_key((k, v)):
            cache_key = getattr(type(self), k)
            return cache_key.order
        
        items = [(k, getattr(type(self), k)) for k
            in dir(type(self))
        ]
        items = [(k, v) for (k, v)
            in items
            if isinstance(v, Key)
        ]

        for k, v in sorted(items, key=order_key):
            keys[k] = getattr(self, k)
        return keys

    @classmethod
    def _key_quote(cls, unquoted):
        return unquoted.replace('_', '__').replace(' ', '_')

    @classmethod
    def _key(cls, keys):
        def sk(k, v):
            try:
                field = getattr(cls, k)
            except AttributeError:
                return v
            return '='.join((k, field.python_to_cache(v)))
        return cls._key_quote('/'.join(sk(k, v) for (k, v) in keys.items()))

    def key(self):
        """Produce a unique key-string based on the Key fields defined by the class."""

        return self._key(self._all_keys())

    def serialize(self):
        """Serialize all the fields into one string."""

        keys = self._all_keys()
        serdata = {}
        for fieldname, value in self._data.items():
            serdata[fieldname] = getattr(type(self), fieldname).python_to_cache(value)
        return json.dumps(serdata)

    @classmethod
    def deserialize(cls, string):
        """Reconstruct a previously serialized string back into an instance of a ``CacheModel``."""

        data = json.loads(string)
        for fieldname, value in data.items():
            data[fieldname] = getattr(cls, fieldname).cache_to_python(value)
        return cls(**data)

    def save(self, expires=None):
        """Save a copy of the object into the cache."""

        if expires is None:
            expires = self.expires
        s = self.serialize()
        key = self._key(self._all_keys())
        _cache.set(key, s, expires)

    @classmethod
    def _get(cls, **kwargs):
        k = cls(**kwargs).key()
        data = _cache.get(k)
        return data

    @classmethod
    def get(cls, **kwargs):
        """Get a copy of the type from the cache and reconstruct it."""

        data = cls._get(**kwargs)
        if data is None:
            new = cls()
            new.from_miss(**kwargs)
            return new
        return cls.deserialize(data)

    @classmethod
    def get_or_create(cls, **kwargs):
        """Get a copy of the type from the cache, or create a new one."""

        data = cls._get(**kwargs)
        if data is None:
            return cls(**kwargs), True
        return cls.deserialize(data), False

    def from_miss(self, **kwargs):
        """Called to initialize an instance when it is not found in the cache.
        
        For example, if your CacheModel should pull data from the database to
        populate the cache,

            ...

            def from_miss(self, username):
                user = User.objects.get(username=username)
                self.email = user.email
                self.full_name = user.get_full_name()
        """
    
        raise type(self).Missing(type(self)(**kwargs).key())

    def delete(self):
        """Deleting any existing copy of this object from the cache."""

        key = self._key(self._all_keys())
        _cache.delete(key)


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

class PickleField(Field):
    """Alternative serialization using Pickle format."""

    def python_to_cache(self, value):
        return pickle.dumps(value)

    def cache_to_python(self, value):
        return pickle.loads(value.encode('ascii'))


class Key(Field):
    pass

