API Documentation
=================


``decorators``
--------------

.. autoclass:: bettercache.decorators.CachedMethod
    :members:

.. autoclass:: bettercache.decorators.CachedFormMethod

``handlers``
-------------

.. autoclass:: bettercache.handlers.AsyncHandler

``middleware``
---------------

.. autoclass:: bettercache.middleware.BetterCacheMiddleware
    :members:
    :undoc-members:

``objects``
------------

.. autoclass:: bettercache.objects.CacheModel
    :members: Missing, get, get_or_create, deserialize, delete, from_miss, key, keys, save, serialize
    :undoc-members:

``proxy``
----------

.. automodule:: bettercache.proxy
    :members:
    :undoc-members:

``tasks``
----------

.. autoclass:: bettercache.tasks.GeneratePage
    :members: queue
    :undoc-members: 

``utils``
----------

.. automodule:: bettercache.utils
    :members:
    :undoc-members:

``views``
----------

.. automodule:: bettercache.views

    ``cache_view``
    
        Callable version of the ``BetterView``

    .. autoclass:: BetterView
