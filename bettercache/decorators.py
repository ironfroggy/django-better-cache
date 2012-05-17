import functools

from bettercache.objects import CacheModel, Key, Field


class CachedMethod(CacheModel):
    """Caches the result of a callable based on the arguments it was called with, but also on a list of attributes on the instance the method is called on.
    
    ::

        class Home(object):

            def __init__(self, address):
                self.address = address

            @CachedMethod('address')
            def geocode(self):
                return g.geocode(self.address)

    This example caches each call to ``geocode()`` uniquele for each value
    of the ``address`` attribute.

    """

    module = Key()
    classname = Key()
    method_name = Key()
    data = Key()
    args = Key()
    kwargs = Key()

    result = Field()

    @classmethod
    def cache(cls, key_attrs, expires=None):
        """Decorates a method to provide cached-memoization using a
        combination of the positional arguments, keyword argments, and
        whitelisted instance attributes.
        """

        def decorator(func):

            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                module = type(self).__module__
                classname = type(self).__name__
                method_name = func.__name__

                data = {} 
                if isinstance(key_attrs, basestring):
                    _key_attrs = key_attrs.split()
                else:
                    _key_attrs = key_attrs
                for key_attr in _key_attrs:
                    key_value = getattr(self, key_attr)
                    if isinstance(key_value, dict):
                        key_value = ('dict', sorted(key_value.items()))
                    elif isinstance(key_value, set):
                        key_value = ('set', sorted(key_value))
                    else:
                        key_value = (type(key_value).__name__, key_value)
                    data[key_attr] = key_value
                data = sorted(data.items())
                
                result_cache, new = cls.get_or_create(
                    module=module,
                    classname=classname,
                    method_name=method_name,
                    data=data,
                    args=args,
                    kwargs=sorted(kwargs.items()),
                )

                if new:
                    result_cache.result = func(self, *args, **kwargs)
                    result_cache.save(expires)

                return result_cache.result

            return wrapper

        return decorator


class CachedFormMethod(CachedMethod):
    """This specialized subclass of ``CachedMethod`` caches uniquely based
    on the result of cleaned form data. It is intended to decorate methods
    of Django ``Form`` subclasses.
    """

    @classmethod
    def cache(cls, expires=None):
        return super(CachedFormMethod, cls).cache(['cleaned_data'], expires)
