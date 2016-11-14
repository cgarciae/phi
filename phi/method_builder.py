from builder import Builder
import utils
import inspect


#########################
# Classes
#########################
class MethodBuilder(Builder):
    """docstring for MethodBuilder."""

    def method(self, name, *args, **kwargs):
        if not hasattr(self, name):
            register_proxy_method(name)
        return self._unit(lambda x: getattr(x, name)(*args, **kwargs), self._refs)


Builder.M = property(lambda self: MethodBuilder(self._f))
M = MethodBuilder()

#########################
# Registrations
#########################
def register_proxy_method(method_name, alias=None):
    def proxy_method(self, *args, **kwargs):
        return getattr(self, method_name)(*args, **kwargs)

    alias = alias if alias else method_name
    MethodBuilder.register_function_1(proxy_method, "any", alias=alias, _return_type=Builder)

# helpers
_is_viable_method = lambda m: inspect.isroutine(m) and m.__name__[0] is not '_'
_get_members = lambda x: inspect.getmembers(x, _is_viable_method)

# get method list
classes = [str, int, list, tuple, dict, float, bool]
method_info_list = map(_get_members, classes)
method_info_list = utils.flatten_list(method_info_list)

# register proxy methods
for name, f in method_info_list:
    register_proxy_method(name)

# alias methods: aliases for some other "obscure" method name
special_methods = {'__contains__': 'contains' }

# register alias methods
for method_name, alias in special_methods.items():
    register_proxy_method(method_name, alias)
