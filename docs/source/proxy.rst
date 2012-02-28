.. Bettercache proxy documentation
Bettercache Proxy Server
======================================

The Bettercache proxy server is intended to work with a slower django application that's using the
bettercache middleware. It is threadsafe so many proxy requests can be served without loading the
application that is actually generating the pages. It will take care of serving pages from a cache
populated by the bettercache middleware/celery task and sending tasks to celery to regenerate those
pages when necessary.

Settings required for proxy server
___________________________________
In addition to the normal settings for the bettercache middleware, celery and django the following
setting is also required for the proxy server.
* BETTERCACHE_ORIGIN_HOST - The server which proxy traffic should be directed at. The host name from the
  original request will be passed on.
