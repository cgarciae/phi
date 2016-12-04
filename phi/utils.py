from collections import namedtuple
import functools, inspect

def identity(x):
    return x

def compose2(f, g):
    return lambda x: f(g(x))


DefaultArgSpec = namedtuple('DefaultArgSpec', 'has_default default_value')

def _get_default_arg(args, defaults, arg_index):
    """ Method that determines if an argument has default value or not,
    and if yes what is the default value for the argument

    :param args: array of arguments, eg: ['first_arg', 'second_arg', 'third_arg']
    :param defaults: array of default values, eg: (42, 'something')
    :param arg_index: index of the argument in the argument array for which,
    this function checks if a default value exists or not. And if default value
    exists it would return the default value. Example argument: 1
    :return: Tuple of whether there is a default or not, and if yes the default
    value, eg: for index 2 i.e. for "second_arg" this function returns (True, 42)
    """
    if not defaults:
        return DefaultArgSpec(False, None)

    args_with_no_defaults = len(args) - len(defaults)

    if arg_index < args_with_no_defaults:
        return DefaultArgSpec(False, None)
    else:
        value = defaults[arg_index - args_with_no_defaults]
        if (type(value) is str):
            value = '"%s"' % value
        return DefaultArgSpec(True, value)

def get_method_sig(method):
    """ Given a function, it returns a string that pretty much looks how the
    function signature_ would be written in python.

    :param method: a python method
    :return: A string similar describing the pythong method signature_.
    eg: "my_method(first_argArg, second_arg=42, third_arg='something')"
    """

    # The return value of ArgSpec is a bit weird, as the list of arguments and
    # list of defaults are returned in separate array.
    # eg: ArgSpec(args=['first_arg', 'second_arg', 'third_arg'],
    # varargs=None, keywords=None, defaults=(42, 'something'))
    argspec = inspect.getargspec(method)
    arg_index=0
    args = []

    # Use the args and defaults array returned by argspec and find out
    # which arguments has default
    for arg in argspec.args:
        default_arg = _get_default_arg(argspec.args, argspec.defaults, arg_index)
        if default_arg.has_default:
            args.append("%s=%s" % (arg, default_arg.default_value))
        else:
            args.append(arg)
        arg_index += 1
    return "%s(%s)" % (method.__name__, ", ".join(args))

def get_instance_methods(instance):
    for method_name in dir(instance):
        method = getattr(instance, method_name)
        if hasattr(method, '__call__'):
            yield method_name, method


def _flatten_list(container):
    for i in container:
        if isinstance(i, list):
            for j in flatten_list(i):
                yield j
        else:
            yield i

def flatten_list(container):
    return list(_flatten_list(container))


def _flatten(container):
    for i in container:
        if hasattr(i, '__iter__'):
            for j in _flatten(i):
                yield j
        else:
            yield i

def flatten(container):
    return list(_flatten(container))

_true = lambda x: True
_false = lambda x: False

def _get_patch_members(builder, module, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):

    if type(whitelist) is list:
        whitelist_list = whitelist
        whitelist = lambda x: x in whitelist_list

    if type(blacklist) is list:
        blacklist_list = blacklist
        blacklist = lambda x: x in blacklist_list

    return [
        (name, f) for (name, f) in inspect.getmembers(module, getmembers_predicate) if whitelist(name) and not blacklist(name)
    ]

def patch_with_members_from_0(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.RegisterFunction0(f, module_name, _return_type=_return_type)

def patch_with_members_from_1(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.RegisterFunction1(f, module_name, _return_type=_return_type)

def patch_with_members_from_2(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.RegisterFunction2(f, module_name, _return_type=_return_type)

def patch_with_members_from_3(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.RegisterFunction3(f, module_name, _return_type=_return_type)

def patch_with_members_from_4(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.RegisterFunction4(f, module_name, _return_type=_return_type)

def patch_with_members_from_5(builder, module, module_alias=None, blacklist=_false, whitelist=_true, _return_type=None, getmembers_predicate=inspect.isfunction):
    module_name = module_alias if module_alias else module.__name__
    patch_members = _get_patch_members(builder, module, blacklist=blacklist, whitelist=whitelist, getmembers_predicate=getmembers_predicate)

    for name, f in patch_members:
        builder.RegisterFunction5(f, module_name, _return_type=_return_type)
