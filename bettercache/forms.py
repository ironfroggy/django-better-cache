import functools

from bettercache.objects import CacheModel, Key, Field


class CachedFormMethod(CacheModel):
    module = Key()
    classname = Key()
    method_name = Key()
    data = Key()

    result = Field()

    def __call__(self, func):

        @functools.wraps(func)
        def wrapper(form, *args, **kwargs):
            assert form.is_valid(), "Can only call cached methods on clean forms."

            module = type(form).__module__
            classname = type(form).__name__
            method_name = func.__name__
            data = sorted(form.data.items())
            
            result_cache, new = CachedFormMethod.get_or_create(
                module=module,
                classname=classname,
                method_name=method_name,
                data=data)

            if new:
                result_cache.result = func(form, *args, **kwargs)
                result_cache.save()

            return result_cache.result

        return wrapper
