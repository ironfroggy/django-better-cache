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
    fragment_stack = []
    
    def __init__(self, nodelist, expire_time_var, fragment_name, vary_on):
        self.nodelist = nodelist
        self.expire_time_var = template.Variable(expire_time_var)
        self.fragment_name = fragment_name
        self.vary_on = vary_on

        self.additional_keys = []

    def add_keys(self, keys):
        leaking_keys = []
        for key in keys:
            if key == 'local':
                break
            else:
                leaking_keys.append(key)
        self.additional_keys.extend(leaking_keys)

    def push_keys(self, keys):
        self.key_stack.append(keys)

    def pop_keys(self):
        return self.key_stack.pop()
    
    def get_fragment_by_name(self, name):
        for fragmentname, node in self.fragment_stack:
            if name == fragmentname:
                return node
        raise KeyError

    def get_parent(self):
        try:
            parent_name, parent = self.fragment_stack[-2]
            return parent
        except IndexError:
            raise ValueError

    def make_cache_key(self, context, extra_args=()):
        args = list(self.key_stack) + [list(extra_args)]
        all_stack_vary_on = itertools.chain(*args)
        vary_values = []
        defaults = {}

        for vary_var in all_stack_vary_on:
            try:
                vary_var, default = vary_var.split('=')
                defaults[vary_var] = default
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

        fragment_name = ":".join(name for (name, node) in self.fragment_stack)

        cache_key = 'bettercache.%s.%s' % (fragment_name, args.hexdigest())

        return cache_key, defaults

    def render(self, context):
        expire_time = int(self.expire_time_var.resolve(context))

        self.key_stack.append(self.vary_on)
        self.fragment_stack.append((self.fragment_name, self))
        try:
            cache_key, defaults = self.make_cache_key(context)
            
            extra_keys = cache.get(cache_key + '::extra_keys')
            if extra_keys is not None:
                cache_key, defaults = self.make_cache_key(context, extra_keys)

            value = cache.get(cache_key)

            if value is None:
                context.push()
                try:
                    for def_name, def_value in defaults.items():
                        if def_name not in context:
                            context[def_name] = template.Variable(def_value).resolve(context)
                    value = self.nodelist.render(context)
                finally:
                    context.pop()
                cache.set(cache_key, value, expire_time)

                # Did we get new keys from any child caches?
                # We put the new keys, unresolved, in {{key}}::extra_keys
                if self.additional_keys:
                    cache.set(cache_key + '::extra_keys', self.additional_keys, expire_time)

                # Push our keys into our parent
                # Unless they are local
                try:
                    parent = self.get_parent()
                except ValueError:
                    pass
                else:
                    parent.add_keys(self.vary_on)
                    if self.additional_keys:
                        parent.add_keys(self.additional_keys)

            return value
        finally:
            self.key_stack.pop()
            self.fragment_stack.pop()


register.tag('cache', do_cache)
