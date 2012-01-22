.. Django Better Cache documentation master file, created by
   sphinx-quickstart on Mon Dec 12 23:03:03 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2

   Better cache template tag

Welcome to Django Better Cache's documentation!
===============================================

Better Cache originally provided a replacement ``{% cache %}`` tag, but as of
version 0.5 includes a Cache ORM module, as well. Overall, the aim is to
simplify and empower your use of caches with sane defaults and obvious
behaviors.


Better cache template tag
-------------------------

Better Cache provides a replacement for the default cache template tag library from Django.
It is a better version of {% cache %}

What is better about Better Cache?

 - Nested cache fragments inherit the variables their parent fragments key on
 - Parent cache fragments can be given additional keys by their child cache fragments

An example:

::

    {% cache 500 "outer" x %}
        y = {{ y }}<br />
        {% cache 500 "inner" y %}
            x = {{ x }}<br />
        {% endcache %}
    {% endcache %}

In the default {% cache %} tag from Django, the inner fragment will not be
rerendered when x changes, because only the outer fragment uses that as a key
variable. The outer fragment will not update with y changes, because only the
inner fragment uses that.

With Better Cache, x and y affect both, so fragments will be re-rendered when
any important variable changes.

Better Cache also allows a syntax of giving defaults to key variables:

::

    {% cache 500 "test" x=10 %}


Controlling inheritence
***********************

You don't always want the outer cache fragments to invalidate when variables
only important to the inner fragment changes. In some cases, the inner fragment
is allowed to get stale if it stays cached longer as part of the parent, so
we want a way to disable the inheritence of the variables.

You can do this with the `local` modifier. All modifiers after the `local` will
affect only this cache fragment, not its parent.

::

    {% cache 500 "outer" x %}
        y = {{ y }}<br />
        {% cache 500 "inner" local y %}
            x = {{ x }}<br />
        {% endcache %}
    {% endcache %}


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

