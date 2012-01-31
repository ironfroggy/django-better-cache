bettercache template tags
=========================

Currently, the only tag provided is a replacement for Django's builtin
``{% cache %}`` tag, which makes it easier to work with nested blocks.

cache
-----

Better Cache provides a replacement for the default cache template tag library
from Django. It is a better version of ``{% cache %}``.

What is better about Better Cache's version of the cache tag?

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

Default Keys
************

Better Cache also allows a syntax of giving defaults to key variables:

::

    {% cache 500 "test" x=10 %}
        ...
    {% endcache %}

This allows the block to be rendered as if ``x`` had the value ``10``, caching
the result and reusing if later if ``x`` really does exist and have that value
later.

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
