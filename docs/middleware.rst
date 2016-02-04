.. Bettercache middleware documentation

Bettercache Middleware and Celery Task
======================================

The bettercache middleware is intended as a replacement for django's caching middleware that does offline page updateing via celery.

Bettercache Regeneration Strategy
____________________________________
Bettercache has two cache timeouts a postcheck and precheck. The postcheck time should be
shorter then the precheck. If it isn't celery will never be used to regenerate pages.
* Before the postcheck time the page is simply served from cache.
* Betwen the postcheck and the precheck times Bettercache will serve the cached page. Then it will queue a celery task to regenerate the page and recache the page to reset both postcheck and precheck timeouts.
* After the precheck time a new page will be regenerated and served.

When will bettercache cache a page?
_______________________________________
Bettercache will cache a page under the following conditions

* request._cache_update_cache is not `True`.
* The status code is 200, 203, 300, 301, 404, or 410.
* The setting `BETTERCACHE_ANONYMOUS_ONLY` is not `True` or the session hasn't been
  accessed.
* The request does not have any uncacheable headers. To change this override
  `has_uncacheable_headers`.

See the :ref:`task API docs <api-tasks>` for more information.

Bettercache header manipulation
________________________________
The bettercache middleware will change some of the request headers before it caches a page for the first time.

* If `BETTERCACHE_ANONYMOUS_ONLY` is not `True` bettercache will remove `Vary: Cookie` headers.
* The `Cache-Control` headers are modified so that
  - `max-age` and `pre-check` set to `BETTERCACHE_CACHE_MAXAGE` unless the request already had a `max-age` header in which case that will be honored.
  - `post-check` is set to `BETTERCACHE_EDGE_POSTCECK_RATIO` * the `max-age`.
* The `Edge-Control` header is set with `cache-maxage` to `BETTERCACHE_EDGE_MAXAGE`.

.. _intro-to-middleware:

Bettercache middleware settings
________________________________
The following settings are currently aspirational but the changes should be coming soon.

* BETTERCACHE_EXTERNAL_MAXAGE - the default external the Cache-Control max-age/pre-check headers to
* BETTERCACHE_EXTERNAL_POSTCHECK_RATIO - the ratio of max_age to set the Cache-Control post-check header to
* BETTERCACHE_LOCAL_MAXAGE - the number of seconds to cache pages for locally
* BETTERCACHE_LOCAL_POSTCHECK - the number of seconds after which to attempt to regenerate a page locally

See the :ref:`middleware API docs <api-middleware>` for more information.

Betterache middleware TODO list
________________________________
* Remove akamai headers and create hooks for additional header manipulation
* Allow views to set non-default cache local_maxage/postchecks?
* Switch to better settings module
* Switch to not caching django request objects but json body/header/additional info objects
