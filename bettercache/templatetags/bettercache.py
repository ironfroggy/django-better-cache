import itertools

from django import template
from django.core.cache import cache
from django.utils.hashcompat import md5_constructor    
from django.utils.encoding import force_unicode
from django.utils.http import urlquote


register = template.Library()


def do_cache(parser, token):
    nodelist = parser.parse(('endcache',))
    parser.delete_first_token()
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise template.TemplateSyntaxError("'%s' tag requires at least 2 arguments." % tokens[0])
    return CacheNode(nodelist, tokens[1], tokens[2], tokens[3:])


class CacheNode(template.Node):
    
    key_stack = []
    fragment_stack = {}
    
    def __init__(self, nodelist, expire_time_var, fragment_name, vary_on):
        self.nodelist = nodelist
        self.expire_time_var = template.Variable(expire_time_var)
        self.fragment_name = fragment_name
        self.vary_on = vary_on

    def push_keys(self, keys):
        self.key_stack.append(keys)

    def pop_keys(self):
        return self.key_stack.pop()

    def make_cache_key(self, context):
        all_stack_vary_on = itertools.chain(*self.key_stack)
        vary_values = []

        for vary_var in all_stack_vary_on:
            try:
                vary_var, default = vary_var.split(':')
            except ValueError:
                pass
            try:
                vary_values.append(template.resolve_variable(vary_var, context))
            except template.VariableDoesNotExist, e:
                try:
                    vary_values.append(default)
                except NameError:
                    raise e

        args = md5_constructor(u':'.join([urlquote(value) for value in vary_values]))

        self.fragment_stack[self.fragment_name] = self
        try:
            fragment_name = ":".join(self.fragment_stack)
        finally:
            del self.fragment_stack[self.fragment_name]

        cache_key = 'bettercache.%s.%s' % (fragment_name, args.hexdigest())

        return cache_key

    def render(self, context):
        expire_time = int(self.expire_time_var.resolve(context))

        self.key_stack.append(self.vary_on)
        try:
            cache_key = self.make_cache_key(context)
            value = cache.get(cache_key)
            if value is None:
                value = self.nodelist.render(context)
                cache.set(cache_key, value, expire_time)

            return value
        finally:
            self.key_stack.pop()


register.tag('cache', do_cache)
