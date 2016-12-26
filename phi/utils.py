"""
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple
import inspect

def identity(x):
    return x

def state_identity(x, state):
    return x, state

def compose2(f, g):
    return lambda x: f(g(x))

def forward_compose2(f, g):
    return lambda x: g(f(x))

def merge(dict_a, dict_b):
    return dict(dict_a, **dict_b)

def lift(f):
    return lambda x, state: (f(x), state)


class _NoValue(object):
    def __repr__(self):
        return "NoValue"

NO_VALUE = _NoValue()

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
