"""
Test
"""

from utils import identity
import utils
import pprint
from abc import ABCMeta, abstractmethod
from inspect import isclass


###############################
# Helpers
###############################

_NO_VALUE = object()

class Ref(object):
    """docstring for Ref."""
    def __init__(self, name, value=_NO_VALUE):
        super(Ref, self).__init__()
        self.name = name
        self.value = None if value is _NO_VALUE else value
        self.assigned = value is not _NO_VALUE

    def __call__(self, *optional):
        if not self.assigned:
            raise Exception("Trying to read Ref('{0}') before assignment".format(self.name))

        return self.value

    def set(self, x):
        self.value = x

        if not self.assigned:
            self.assigned = True

        return x

class RecordObject(dict):
    """docstring for DictObject."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def clear(self):
        return self.__dict__.clear()

    def copy(self):
        return self.__dict__.copy()

    def has_key(self, k):
        return self.__dict__.has_key(k)

    def pop(self, k, d=None):
        return self.__dict__.pop(k, d)

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return self.__dict__.keys()

    def values(self):
        return self.__dict__.values()

    def items(self):
        return self.__dict__.items()

    def pop(self, *args):
        return self.__dict__.pop(*args)

    def __cmp__(self, dict):
        return cmp(self.__dict__, dict)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __unicode__(self):
        return unicode(repr(self.__dict__))

###############################
# DSL Elements
###############################

class Node(object):
    """docstring for Node."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def __compile__(self, refs):
        pass

class Function(Node):
    """
    Functions are the most basic element of the DSL, 
    """
    def __init__(self, _f):
        super(Function, self).__init__()
        self._f= _f
        self._refs = {}

    def __iter__(self):
        yield self

    def __compile__(self, refs):
        refs = dict(refs, **self._refs)
        return self._f, refs

    def __str__(self):
        return "Fun({0})".format(self._f)


_Identity = Function(identity)


class Tree(Node):
    """docstring for Tree."""

    def __init__(self, iterable_code):
        self.branches = [ _parse(code) for code in iterable_code ]

    @staticmethod
    def __parse__(iterable_code):
        iterable_code = utils.flatten_list(iterable_code)

        if len(iterable_code) == 1:
            return _parse(iterable_code[0])

        return Tree(iterable_code)

    def __compile__(self, refs):
        fs = []

        for node in self.branches:
            node_f, refs = node.__compile__(refs)
            fs.append(node_f)

        def function(x):
            return [ f(x) for f in fs ]

        return function, refs

    def __str__(self):
        return pprint.pformat(self.branches)


class Sequence(Node):
    """docstring for Sequence."""
    def __init__(self, left_code, right_code):
        super(Sequence, self).__init__()
        self.left = _parse(left_code)
        self.right = _parse(right_code)

    @staticmethod
    def __build__(right, *prevs):
        left = prevs[0] if len(prevs) == 1 else Sequence.__build__(*prevs)
        return Sequence(left, right)

    @staticmethod
    def __parse__(tuple_code):
        tuple_code = list(tuple_code)

        if len(tuple_code) == 0:
            return _Identity

        if len(tuple_code) == 1:
            return _parse(tuple_code[0])

        tuple_code.reverse()

        return Sequence.__build__(*tuple_code)

    def __compile__(self, refs):
        f_left, refs = self.left.__compile__(refs)

        f_right, refs = self.right.__compile__(refs)

        f = utils.compose2(f_right, f_left)

        return f, refs

    def __str__(self):
        return "Seq({0}, {1})".format(self.left, self.right)

class Record(Node):
    """docstring for Record."""
    def __init__(self, dict_code):
        super(Record, self).__init__()
        self.nodes_dict = { key: _parse(code) for key, code in dict_code.iteritems() }

    @staticmethod
    def __parse__(dict_code):
        return Record(dict_code)

    def __compile__(self, refs):
        funs_dict = {}
        out_refs = refs.copy()

        for key, node in self.nodes_dict.iteritems():
            f, next_refs = node.__compile__(refs)

            out_refs.update(next_refs)
            funs_dict[key] = f

        def function(x):
            return RecordObject(**{key: f(x) for key, f in funs_dict.iteritems() })

        return function, out_refs



class With(Node):
    """docstring for Record."""

    GLOBAL_SCOPE = None

    def __init__(self, scope_code, *body_code):
        super(With, self).__init__()
        self.scope = _parse(scope_code, else_input=True)
        self.body = _parse(body_code)

    def __compile__(self, refs):
        scope_f, refs = self.scope.__compile__(refs)
        body_fs, refs = self.body.__compile__(refs)

        def function(x):
            with scope_f(x) as scope:
                with self.set_scope(scope):
                    return body_fs(x)

        return function, refs

    def set_scope(self, new_scope):
        self.new_scope = new_scope
        self.old_scope = With.GLOBAL_SCOPE

        return self

    def __enter__(self):
        With.GLOBAL_SCOPE = self.new_scope

    def __exit__(self, *args):
        With.GLOBAL_SCOPE = self.old_scope


class Read(Node):
    """docstring for Read."""
    def __init__(self, name):
        super(Read, self).__init__()
        self.name = name

    def __compile__(self, refs):
        ref = refs[self.name]
        f = ref #ref is callable with an argument
        return f, refs


class Write(Node):
    """docstring for Read."""
    def __init__(self, ref):
        super(Write, self).__init__()
        self.ref = ref

    @staticmethod
    def __parse__(code):
        if len(code) == 0:
            return _Identity

        for ref in code:
            if not isinstance(ref, (str, Ref)):
                raise Exception("Parse Error: Sets can only contain strings or Refs, get {0}".format(code))

        writes = tuple([ Write(ref) for ref in code ])
        return _parse(writes)

    def __compile__(self, refs):

        if type(self.ref) is str:
            name = self.ref

            if name in refs:
                self.ref = refs[name]
            else:
                refs = refs.copy()
                refs[name] = self.ref = Ref(self.ref)

        elif self.ref.name not in refs:
            refs = refs.copy()
            refs[self.ref.name] = self.ref

        return self.ref.set, refs


class Input(Node):
    """docstring for Input."""
    def __init__(self, value):
        super(Input, self).__init__()
        self.value = value

    def __compile__(self, refs):
        f = lambda x: self.value
        return f, refs




#######################
### FUNCTIONS
#######################

def Compile(code, refs):
    ast = _parse(code)
    f, refs = ast.__compile__(refs)

    return f, refs


def _parse(code, else_input=False):
    #if type(code) is tuple:
    if isinstance(code, Node):
        return code
    elif hasattr(code, '__call__') or isclass(code):
        return Function(code)
    elif type(code) is str:
        return Read(code)
    elif type(code) is set:
        return Write.__parse__(code)
    elif type(code) is tuple:
        return Sequence.__parse__(code)
    elif type(code) is dict:
        return Record.__parse__(code)
    elif hasattr(code, '__iter__') and not isclass(code): #leave last
        return Tree.__parse__(code) #its iterable
    elif else_input:
        return Input(code)
    else:
        raise Exception("Parse Error: Element not part of the DSL. Got:\n{0} of type {1}".format(code, type(code)))
