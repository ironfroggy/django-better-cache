.. Django Better Cache documentation master file, created by
   sphinx-quickstart on Mon Dec 12 23:03:03 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


Welcome to Django Better Cache's documentation!
===============================================

Better Cache originally provided a replacement ``{% cache %}`` tag, but as of
version 0.5 includes a Cache ORM module, as well. Overall, the aim is to
simplify and empower your use of caches with sane defaults and obvious
behaviors.

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   templatetags
   cachemodel
   roadmap


CacheModel
----------

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


Contributing
------------

Fork and send pull requests, please!

http://github.com/ironfroggy/django-better-cache/


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

