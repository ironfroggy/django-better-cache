CacheModel
==========

To make the management of cached data easier, ``bettercache`` provides a
structured model for data caching, without the developer constantly
building up ad-hoc key strings. This should be a familiar interface,
fashioned after Django's own database models.

::

    class User(CacheModel):
        username = Key()
        email = Field()
        full_name = Field()

    user = User(
        username = 'bob',
        email = 'bob@hotmail.com',
        full_name = 'Bob T Fredrick',
    )
    user.save()
    
    ...

    user = User.get(username='bob')
    user.email == 'bob@hotmail.com'
    user.full_name == 'Bob T Fredrick'

``CacheModel`` subclasses are a collection of ``Key`` and ``Field``
properties to
populate with data to be stored in the cache. The creation of keys are
automatic, based on the ``CacheModel`` class and the values given for all
the ``Key`` fields for an instance.

The cache objects can save any fields with JSON-serializable values.

API Reference
-------------

``CacheModel``
    A base class you can inherit and define structures to store in the cache,
    much like a Django Model storing data in the database.

``CacheModel.Missing``
    An exception raised when an object cannot be found in the cache.

``CacheModel.save()``
    Sends the serialized object to the cache for storage.

``CacheModel.get(key1=x, key2=y)``
    Looks for an instance of the cache model to load and return, by
    the keys given. All keys defined in the model without defaults
    must be given.

``CacheModel.from_miss(**kwargs)``
    When you define a ``CacheModel`` subclass, you can opt to implement
    the ``from_miss()`` method, which will be called on an instance of
    your class with the keys which couldn't be found in the database.

    Your ``from_miss()`` method should initialize the instance, after
    which the object will be saved to the cache and returned back from
    the original ``get()`` call in the first place.

``Field``
    In your ``CacheModel``, you should define one or more ``Field``
    properties. The values of these properties in your instance will
    all be serialized and sent to the cache when the object is saved.

``Key``
    At least one of your fields must be defined as a ``Key``, which
    will be combined with the class information to generate a unique
    key to identify the object in the cache.
