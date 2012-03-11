import functools

from bettercache.objects import CacheModel, Key, Field


class CachedMethod(CacheModel):
    module = Key()
    classname = Key()
    method_name = Key()
    data = Key()
    args = Key()
    kwargs = Key()

    result = Field()

    @classmethod
    def cache(cls, key_attrs, expires=None):

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
                
                result_cache, new = CachedFormMethod.get_or_create(
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

    @classmethod
    def cache(cls, expires=None):
        return super(CachedFormMethod, cls).cache(['cleaned_data'], expires)
