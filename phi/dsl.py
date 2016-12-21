"""
The Phi DSL is all about combining functions in useful ways, enabling a declarative approach that can improve clarity, readability and lead to shorter code. All valid expression of the DSL can be compiled to a function using `P.Make` or applied to a value using `P.Pipe`.

Phi offers the following constructs/expressions, **try to read their documentation in order**:

* **`phi.dsl.Function`**: any function of arity 1 is an element of the language
* **`phi.dsl.Seq`**: allows to sequentially compose functions
* **`phi.dsl.Branch`**: lets to create a branched computation that returns a list with the results of each branch
* **`phi.dsl.Val`**: allows you to specify an input value, compiles to a (constant) function that returns the same value no matter the input
* **`phi.dsl.With`**: lets you to specify a context manager for the expresion (uses the `with` statemente)
* **`phi.dsl.Record`**: lets to create a branched computation with named branches that returns a record-like structure with the results of each branch
* **`phi.dsl.Read` & `phi.dsl.Write`**: allow you to create a reference to the value at some point and read it latter on.
* **`phi.dsl.If`**: allows you to create conditional computation

Any expresion can appear inside any other expresion in a nested fasion. They correct way to think about this is that each sub-expression will be compiled to a function of arity 1, therefore from the parent expresion's point of view all of its elements are just functions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .utils import identity
from . import utils
from abc import ABCMeta, abstractmethod
from inspect import isclass
import functools
from .lambdas import Lambda


###############################
# Helpers
###############################
class _ReadProxy(object):
    """docstring for _ReadProxy."""

    def __init__(self, __builder__):
        self.__builder__ = __builder__

    def __getitem__(self, name):
        return self.__do__(name)

    def __getattr__(self, name):
        return self.__do__(name)

    def __call__ (self, name):
        return self.__do__(name)

    def __do__(self, name):
        if type(name) is Ref:
            name = name.name

        g = lambda z: _CompilationContextManager.get_ref(name).value

        return self.__builder__.__then__(g)


class _WriteProxy(object):
    """docstring for _WriteProxy."""

    def __init__(self, __builder__):
        self.__builder__ = __builder__

    def __getitem__(self, ref):
        return self.__do__([ref])

    def __getattr__ (self, ref):
        return self.__do__([ref])

    def __call__ (self, *refs):
        return self.__do__(refs)

    def __do__(self, refs):
        refs = [ Ref(ref) if type(ref) is str else ref for ref in refs ]

        def g(x):
            for ref in refs:
                ref.set(x)
                _CompilationContextManager.set_ref(ref)

            return x

        return self.__builder__.__then__(g)

class _ObjectProxy(object):
    """docstring for Underscore."""

    def __init__(self, __builder__):
        self.__builder__ = __builder__

    def __getattr__(self, name):

        def method_proxy(*args, **kwargs):
            f = lambda x: getattr(x, name)(*args, **kwargs)
            return self.__builder__.__then__(f)

        return method_proxy

class _RefProxy(object):
    """docstring for _ReadProxy."""

    def __getitem__(self, name):
        return _CompilationContextManager.get_ref(name).value

    def __getattr__(self, name):
        return _CompilationContextManager.get_ref(name).value

    def __call__(self, *args, **kwargs):
        return Ref(*args, **kwargs)

_RefProxyInstance = _RefProxy()

class _RecordProxy(object):
    """docstring for _RecordProxy."""

    def __init__(self, __builder__):
        self.__builder__ = __builder__

    def __call__(self, **branches):
        gs = { key : _parse(value)._f for key, value in branches.items() }

        def h(x):
            return _RecordObject(**{key: g(x) for key, g in gs.items() })

        return self.__builder__.__then__(h)

    def __getattr__ (self, attr):
        f = lambda x: getattr(x, attr)
        return self.__builder__.__then__(f)

    def __getitem__(self, key):
        f = lambda x: x[key]
        return self.__builder__.__then__(f)


class Ref(object):
    """
This class manages references inside the DSL, these are created, written, and read from during the `phi.dsl.Read` and `phi.dsl.Write` operations.
    """
    def __init__(self, name, value=utils.NO_VALUE):
        super(Ref, self).__init__()
        self.name = name
        """
The reference name. Can be though a key in a dictionary.
        """
        self.value = value
        """
The value of the reference. Can be though a value in a dictionary.
        """

    def __call__(self, *optional):
        """
Returns the value of the reference. Any number of arguments can be passed, they will all be ignored.
        """
        if self.value is utils.NO_VALUE:
            raise Exception("Trying to read Ref('{0}') before assignment".format(self.name))

        return self.value

    def set(self, x):
        """
Sets the value of the reference equal to the input argument `x`. Its also an identity function since it returns `x`.
        """
        self.value = x

        return x


class _CompilationContextManager(object):

    COMPILATION_GLOBAL_REFS = None
    WITH_GLOBAL_CONTEXT = utils.NO_VALUE

    def __init__(self, next_refs, next_with_global_context):
        self.previous_refs = _CompilationContextManager.COMPILATION_GLOBAL_REFS
        self.next_refs = next_refs

        self.previous_with_global_context = _CompilationContextManager.WITH_GLOBAL_CONTEXT
        self.next_with_global_context = next_with_global_context

    def __enter__(self):
        _CompilationContextManager.COMPILATION_GLOBAL_REFS = self.next_refs
        _CompilationContextManager.WITH_GLOBAL_CONTEXT = self.next_with_global_context

    def __exit__(self, *args):
        _CompilationContextManager.COMPILATION_GLOBAL_REFS = self.previous_refs
        _CompilationContextManager.WITH_GLOBAL_CONTEXT = self.previous_with_global_context

    @classmethod
    def set_ref(cls, ref):
        #Copy to avoid stateful behaviour
        cls.COMPILATION_GLOBAL_REFS = cls.COMPILATION_GLOBAL_REFS.copy()

        if ref.name in cls.COMPILATION_GLOBAL_REFS:
            other_ref = cls.COMPILATION_GLOBAL_REFS[ref.name]
            # merge state: borg pattern
            other_ref.__dict__.update(ref.__dict__)
        else:
            cls.COMPILATION_GLOBAL_REFS[ref.name] = ref

    @classmethod
    def get_ref(cls, name):
        return cls.COMPILATION_GLOBAL_REFS[name]



class _RecordObject(dict):
    """docstring for DictObject."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getattr__ (self, attr):
        return self[attr]

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

class _WithContextManager(object):

    def __init__(self, new_scope):
        self.new_scope = new_scope
        self.old_scope = _CompilationContextManager.WITH_GLOBAL_CONTEXT

    def __enter__(self):
        _CompilationContextManager.WITH_GLOBAL_CONTEXT = self.new_scope

    def __exit__(self, *args):
        _CompilationContextManager.WITH_GLOBAL_CONTEXT = self.old_scope
###############################
# DSL Elements
###############################



class Expression(Lambda):


    def Branch(self, *branches, **kwargs):
        gs = [ _parse(code)._f for code in branches ]

        def h(x):
            return [ g(x) for g in gs ]

        return self.__then__(h, **kwargs)


    def Seq(self, *sequence, **kwargs):
        fs = [ _parse(elem)._f for elem in sequence ]

        def g(x):
            return functools.reduce(lambda x, f: f(x), fs, x)

        return self.__then__(g, **kwargs)

    @property
    def Rec(self):
        return _RecordProxy(self)

    def With(self, context_manager, *body, **kwargs):
        context_f = _parse(context_manager, else_input=True)._f
        body_f = _parse(body)._f

        def g(x):
            with context_f(x) as scope:
                with _WithContextManager(scope):
                    return body_f(x)

        return self.__then__(g, **kwargs)


    @property
    def Read(self):
        return _ReadProxy(self)

    @property
    def Write(self):
        return _WriteProxy(self)
    #Write.__doc__ = Read.__doc__

    @property
    def Rec(self):
        return _RecordProxy(self)

    @property
    def Obj(self):
        return _ObjectProxy(self)

    @property
    def Ref(self):
        return _RefProxyInstance


    def Val(self, val, **kwargs):
        f = lambda z: val

        return self.__then__(f, **kwargs)


    def If(self, condition, *then, **kwargs):
        cond_f = _parse(condition)._f
        then_f = _parse(then)._f
        else_f = _parse(kwargs.pop("Else", utils.identity))._f

        g = lambda x: then_f(x) if cond_f(x) else else_f(x)

        expr = self.__then__(g, **kwargs)
        expr._cond_f = cond_f
        expr._then_f = then_f
        expr._previous_f = self._f

        return expr

    def Else(self, Else, **kwargs):
        kwargs["Else"] = Else

        expr = self.__unit__(self._previous_f).If(self._cond_f, self._then_f, **kwargs)
        del expr._cond_f
        del expr._then_f
        del expr._previous_f

        return expr

    def ElseIf(self, condition, *then, **kwargs):
        kwargs["Else"] = self.__class__().If(condition, *then)
        return self.__unit__(self._previous_f).If(self._cond_f, self._then_f, **kwargs)



    @staticmethod
    def Context(*args):
        if _CompilationContextManager.WITH_GLOBAL_CONTEXT is utils.NO_VALUE:
            raise Exception("Cannot use 'Context' outside of a 'With' block")

        return _CompilationContextManager.WITH_GLOBAL_CONTEXT


#######################
### FUNCTIONS
#######################

def Compile(code, refs, create_ref_context=True):
    """
Publically exposed as [Builder.Make](https://cgarciae.github.io/phi/builder.m.html#phi.builder.Builder.Make).
    """
    f = _parse(code)._f

    refs = { name: value if type(value) is Ref else Ref(name, value) for name, value in refs.items() }

    def g(x):
        with _CompilationContextManager(refs, utils.NO_VALUE):
            return f(x)

    return g if create_ref_context else f


def _parse(code, else_input=False):
    #if type(code) is tuple:
    if isinstance(code, Expression):
        return code
    elif hasattr(code, '__call__') or isclass(code):
        return Expression(code)
    elif type(code) is str or type(code) is Ref:
        return Expression().Read(code)
    elif type(code) is set:
        return Expression().Write(*code)
    elif type(code) is tuple:
        return Expression().Seq(*code)
    elif type(code) is dict:
        return Expression().Rec(**code)
    elif hasattr(code, '__iter__') and not isclass(code): #leave last
        return Expression().Branch(*list(code)) #its iterable
    elif else_input:
        return Expression().Val(code)
    else:
        raise Exception("Parse Error: Element not part of the DSL. Got: {0} of type {1}".format(code, type(code)))
