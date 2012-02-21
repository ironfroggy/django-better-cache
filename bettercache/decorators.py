import functools

from bettercache.objects import CacheModel, Key, Field


class CachedFormMethod(CacheModel):
    module = Key()
    classname = Key()
    method_name = Key()
    data = Key()
    args = Key()
    kwargs = Key()

    result = Field()

    @classmethod
    def cache(cls, expires=None):

        def decorator(func):

            @functools.wraps(func)
            def wrapper(form, *args, **kwargs):
                assert form.is_valid(), "Can only call cached methods on clean forms."

                module = type(form).__module__
                classname = type(form).__name__
                method_name = func.__name__
                data = sorted(form.data.items())

                result_cache, new = cls.get_or_create(
                    module=module,
                    classname=classname,
                    method_name=method_name,
                    data=data,
                    args=args,
                    kwargs=sorted(kwargs.items()),
                )

                if new:
                    result_cache.result = func(form, *args, **kwargs)
                    result_cache.save(expires)

                return result_cache.result

            return wrapper

        return decorator
