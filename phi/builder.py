"""
The `phi.builder.Builder` class exposes most of the API, you will normally use the `phi.P` object instance (or any equivalent object provided by a Phi-based library) to do most of the work. This module 4 main goals:

1. Exposing a public API for the [dsl](https://cgarciae.github.io/phi/dsl.m.html). See methods like `phi.builder.Builder.Make` and `phi.builder.Builder.Pipe`.
2. Exposing the [lambdas](https://cgarciae.github.io/phi/lambdas.m.html) capabilities.
3. Helping you integrate existing code into the DSL.
4. Let you write [fluent](https://en.wikipedia.org/wiki/Fluent_interface) code in Python.

To integrate existing code, the `phi.builder.Builder` class offers the following functionalities:

* Create *special* partials useful for the DSL. See the `phi.builder.Builder.Then` method.
* Register functions as methods of the `phi.builder.Builder` class. See the `*Register*` method family e.g. `phi.builder.Builder.Register`.
* Create functions that proxy methods from an object. See `phi.builder.Builder.Obj`.
* Create functions that proxy fields from an object. See `phi.builder.Builder.Rec`.

If you want to create a library based on Phi, integrate an existing library, or create some Phi-based helpers for your project, instead of using the `*Register*` methods on the `Builder` class, you should consider doing the following:

1. Create a custom class that inherits from `Builder`.
1. Use the `*Register*` methods or decorators of your custom class to give it your desired functionalities.
1. Instantiate a global object of this class. Preferably choose a single capital letter for its name (phi uses `P`).

**Also see**

* [python_builder](https://cgarciae.github.io/phi/python_builder.m.html)
* [dsl](https://cgarciae.github.io/phi/dsl.m.html)
* [lambdas](https://cgarciae.github.io/phi/lambdas.m.html)
* [patch](https://cgarciae.github.io/phi/patch.m.html)
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import inspect
from . import utils
from .utils import identity
import functools
from . import dsl
from .lambdas import Lambda

#######################
### Applicative
#######################

class Builder(Lambda):
    """
    All the core methods of the `Builder` class start with a capital letter (e.g. `phi.builder.Builder.Pipe` or `phi.builder.Builder.Make`) on purpose to avoid name chashes with methods that libraries might register."""

    @classmethod
    def Context(cls, *args):
        """
**Builder Core**. Also available as a global function as `phi.Context`.

Returns the context object of the current `dsl.With` statemente.

**Arguments**

* ***args**: By design `Context` accepts any number of arguments and completely ignores them.

This is a classmethod and it doesnt return a `Builder`/`Lambda` by design so it can be called directly:

    from phi import P, Context, Obj

    def read_file(z):
        f = Context()
        return f.read()

    lines = P.Pipe(
        "text.txt",
        P.With( open,
            read_file,
            Obj.split("\\n")
        )
    )

Here we called `Context` with no arguments to get the context back, however, since you can also give this function an argument (which it will ignore) it can be passed to the DSL so we can rewrite the previous as:

    from phi import P, Context, Obj

    lines = P.Pipe(
        "text.txt",
        P.With( open,
            Context, # f
            Obj.read()
            Obj.split("\\n")
        )
    )

`Context` yields an exception when used outside of a `With` block.

**Also see**

* `phi.builder.Builder.Obj`
* [dsl](https://cgarciae.github.io/phi/dsl.m.html)
        """

        if dsl.CompilationContextManager.WITH_GLOBAL_CONTEXT is dsl._NO_VALUE:
            raise Exception("Cannot use 'Context' outside of a 'With' block")

        return dsl.CompilationContextManager.WITH_GLOBAL_CONTEXT

    def With(self, *args, **kwargs):
        return self.NMake(dsl.With(*args, **kwargs))
    With.__doc__ = dsl.With.__doc__


    Ref = dsl.Ref

    def If(self, *args, **kwargs):
        return self.NMake(dsl.If(*args, **kwargs))
    If.__doc__ = dsl.If.__doc__

    def Pipe(self, x, *code, **kwargs):
        """
`Pipe` is method that takes an input argument plus an expression from the DSL, it compiles the expression and applies the resulting function to the input. Its highly inspired by Elixir's [|> (pipe)](https://hexdocs.pm/elixir/Kernel.html#%7C%3E/2) operator.

**Arguments**

* **x**: any input object
* ***code**: any expression from the DSL.`code` is implicitly a `tuple` since that is what Python gives you when you declare a [Variadic Function](https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists), therefore, according to the rules of the DSL, all expressions inside of `code` will be composed together. See [Composition](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Composition).
* ****kwargs**: `Pipe` forwards all `kwargs` to `phi.builder.Builder.Make`, visit its documentation for more info.

**Examples**

    from phi import P

    def add1(x): return x + 1
    def mul3(x): return x * 3

    x = P.Pipe(
        1,     #input
        add1,  #1 + 1 == 2
        mul3   #2 * 3 == 6
    )

    assert x == 6

The previous using [lambdas](https://cgarciae.github.io/phi/lambdas.m.html) to create the functions

    from phi import P

    x = P.Pipe(
        1,      #input
        P + 1,  #1 + 1 == 2
        P * 3   #2 * 3 == 6
    )

    assert x == 6

**Also see**

* `phi.builder.Builder.Make`
* `phi.builder.Builder.Run`
* [dsl](https://cgarciae.github.io/phi/dsl.m.html)
* [Compile](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Compile)
* [lambdas](https://cgarciae.github.io/phi/lambdas.m.html)
        """
        return self.Make(*code, **kwargs)(x)

    def NPipe(self, x, *code, **kwargs):
        """
`NPipe` is shortcut for `Pipe(..., create_ref_context=False)`, its full name should be *NoCreateRefContextPipe* but its impractically long. Normally methods that [compile](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Compile) DSL expressions like `phi.builder.Builder.Make` or `phi.builder.Builder.Pipe` create a reference context unless especified, these contexts encapsulate references (see [read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read) or [write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Write)) and prevent them from leaking, which is good. There are times however when you consciously want a sub-Make or sub-Pipe expression to read or write references from the main Make or Pipe expression, for this you need to set `create_ref_context` to `False`.

**Arguments**

* Same arguments as `phi.builder.Builder.Pipe` but...
* **create_ref_context** is hardcoded to `False`

**Examples**

If you compile a sub expression as a function for another expression e.g.

    from phi import P

    assert 1 == P.Pipe(
        1, {'s'}, # write s == 1, outer context
        lambda x: P.Pipe(
            x,
            P + 1, {'s'} # write s == 2, inner context
        ),
        's'  # read s == 1, outer context
    )

you find that references are not shared. However if you avoid the creation of a new reference context via a keyword arguments

    from phi import P

    assert 2 == P.Pipe(
        1, {'s'},   #write s == 1, same context
        lambda x: P.Pipe(
            x,
            P + 1, {'s'},   #write s == 2, same context
            create_ref_context=False
        ),
        's'   # read s == 2, same context
    )

you can achieve what you want. Yet writting `create_ref_context=False` is a little cumbersome, so to make things nicer we just use a shortcut by appending an `N` at the beggining of the `NPipe` method

    from phi import P

    assert 2 == P.Pipe(
        1, {'s'},   #write s == 1, same context
        lambda x: P.NPipe(
            x,
            P + 1, {'s'}   #write s == 2, same context
        ),
        's'   # read s == 2, same context
    )

**Also see**

* `phi.builder.Builder.Pipe`
* `phi.builder.Builder.NMake`
* `phi.builder.Builder.NRun`
* [dsl](https://cgarciae.github.io/phi/dsl.m.html)
* [Compile](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Compile)
        """
        return self.NMake(*code, **kwargs)(x)

    def Run(self, *code, **kwargs):
        """
`Run(*code, **kwargs)` is equivalent to `Pipe(None, *code, **kwargs)`, that is, it compiles the code and applies in a `None` value.

**Arguments**

* Same as `phi.builder.Builder.Make`.

**Examples**

You might create code that totally ignores its input argument e.g.

    from phi import P

    result = P.Pipe(
        None,
        dict(
            x = (
                Val(10),
                P + 1
            ),
            y = (
                Val(5),
                P * 5
            )
        )
    )

    assert result.x == 9
    assert result.y == 25

Here the `Val` statemente drops the `None` and introduces its own constants. Given this its more suitable to use `Run`

    from phi import P

    result = P.Run(
        dict(
            x = (
                Val(10),
                P + 1
            ),
            y = (
                Val(5),
                P * 5
            )
        )
    )

    assert result.x == 9
    assert result.y == 25

**Also see**

* `phi.builder.Builder.Make`
* `phi.builder.Builder.Pipe`
* [dsl](https://cgarciae.github.io/phi/dsl.m.html)
* [Compile](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Compile)
        """
        return self.Pipe(None, *code, **kwargs)

    def NRun(self, *code, **kwargs):
        """
`NRun` is shortcut for `Run(..., create_ref_context=False)`, its full name should be *NoCreateRefContextRun* but its impractically long.

**Also see**

* `phi.builder.Builder.Run`
* `phi.builder.Builder.NMake`
* `phi.builder.Builder.NPipe`
* [dsl](https://cgarciae.github.io/phi/dsl.m.html)
* [Compile](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Compile)
        """
        return self.NPipe(None, *code, **kwargs)

    def Make(self, *code, **kwargs):
        """
The `Make` method takes an expression from the DSL and compiles it to a function.

**Arguments**

* ***code**: any expression from the DSL.`code` is implicitly a `tuple` since that is what Python gives you when you declare a [Variadic Function](https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists), therefore, according to the rules of the DSL, all expressions inside of `code` will be composed together. See [Composition](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Composition).
* *flatten = False*: if `flatten` is True and the argument being returned by the compiled function is a `list` it will instead return a flattened list.
* *_return_type = None*: By default `Make` returns an object of the same class e.g. `Builder`, however you can pass in a custom class that inherits from `Builder` as the returned contianer. This is useful if the custom builder has specialized methods.
* *create_ref_context = True*: determines if a reference manager should be created on compilation. See [Compile](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Compile).
* *refs = True*: external/default values for references passed during compilation. See [Compile](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Compile).

**Examples**

    from phi import P

    def add1(x): return x + 1
    def mul3(x): return x * 3

    f = P.Make(
        add1,
        mul3
    )

    assert f(1) == 6

Here `f` is equivalent to

def f(x):
    x = add1(x)
    x = mul3(x)
    return x

The previous example using [lambdas](https://cgarciae.github.io/phi/lambdas.m.html) to create the functions

    from phi import P

    f = P.Make(
        P + 1,
        P * 3
    )

    assert f(1) == 6

**Also see**

* [dsl](https://cgarciae.github.io/phi/dsl.m.html)
* [Compile](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Compile)
* [lambdas](https://cgarciae.github.io/phi/lambdas.m.html)
**
        """

        _return_type = kwargs.get('_return_type', None)
        flatten = kwargs.get('flatten', False)
        refs = kwargs.get('refs', {})
        create_ref_context = kwargs.get('create_ref_context', True)

        # code = (self, code)

        if flatten:
            code = (code, lambda x: utils.flatten_list(x) if type(x) is list else x)

        f = dsl.Compile(code, refs, create_ref_context=create_ref_context)

        return self.__then__(f, _return_type=_return_type)

    def NMake(self, *args, **kwargs):
        """
`NMake` is shortcut for `Make(..., create_ref_context=False)`, its full name should be *NoCreateRefContextMake* but its impractically long. Normally methods that [compile](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Compile) DSL expressions like `phi.builder.Builder.Make` or `phi.builder.Builder.Pipe` create a reference context unless especified, these contexts encapsulate references (see [read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read) or [write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Write)) and prevent them from leaking, which is good. There are times however when you consciously want a sub-Make or sub-Pipe expression to read or write references from the main Make or Pipe expression, for this you need to set `create_ref_context` to `False`.

**Arguments**

* Same arguments as `phi.builder.Builder.Make` but...
* **create_ref_context** is hardcoded to `False`

**Examples**

If you compile a sub expression as a function for another expression e.g.

    from phi import P

    assert 1 == P.Pipe(
        1, {'s'}, # write s == 1, outer context
        P.Make(
            P + 1, {'s'} # write s == 2, inner context
        ),
        's'  # read s == 1, outer context
    )

you find that references are not shared. However if you avoid the creation of a new reference context via a keyword arguments

    from phi import P

    assert 2 == P.Pipe(
        1, {'s'},   #write s == 1, same context
        P.Make(
            P + 1, {'s'},   #write s == 2, same context
            create_ref_context=False
        ),
        's'   # read s == 2, same context
    )

you can achieve what you want. Yet writting `create_ref_context=False` is a little cumbersome, so to make things nicer we just use a shortcut by appending an `N` at the beggining of the `NMake` method

    from phi import P

    assert 2 == P.Pipe(
        1, {'s'},   #write s == 1, same context
        P.NMake(
            P + 1, {'s'}   #write s == 2, same context
        ),
        's'   # read s == 2, same context
    )

**Also see**

* `phi.builder.Builder.Make`
* `phi.builder.Builder.NPipe`
* `phi.builder.Builder.NRun`
* [dsl](https://cgarciae.github.io/phi/dsl.m.html)
* [Compile](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Compile)
        """
        kwargs['create_ref_context'] = False
        return self.Make(*args, **kwargs)

    def ThenAt(self, n, expr, *args, **kwargs):
        _return_type = None
        n -= 1

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']

        def _lambda(x):
            x = self(x)
            new_args = args[0:n] + (x,) + args[n:] if n >= 0 else args
            return expr(*new_args, **kwargs)

        return self.__unit__(_lambda, _return_type=_return_type)

    def Then0(self, expr, *args, **kwargs):
        """
        """
        return self.ThenAt(0, expr, *args, **kwargs)

    def Then(self, expr, *args, **kwargs):
        """
        """
        return self.ThenAt(1, expr, *args, **kwargs)

    Then1 = Then

    def Then2(self, expr, arg1, *args, **kwargs):
        """
        """
        args = (arg1,) + args
        return self.ThenAt(2, expr, *args, **kwargs)

    def Then3(self, expr, arg1, arg2, *args, **kwargs):
        """
        """
        args = (arg1, arg2) + args
        return self.ThenAt(3, expr, *args, **kwargs)

    def Then4(self, expr, arg1, arg2, arg3, *args, **kwargs):
        """
        """
        args = (arg1, arg2, arg3) + args
        return self.ThenAt(4, expr, *args, **kwargs)

    def Then5(self, expr, arg1, arg2, arg3, arg4, *args, **kwargs):
        """
        """
        args = (arg1, arg2, arg3, arg4) + args
        return self.ThenAt(5, expr, *args, **kwargs)


    def Val(self, x):
        """
        """
        return self.__then__(lambda z: x)

    @property
    def Write(self):
        """
        """
        return WriteProxy(self)


    @property
    def Read(self):

        return ReadProxy(self)

    @property
    def Obj(self):
        """
        """
        return ObjectProxy(self)

    @property
    def Rec(self):
        """
        """
        return RecordProxy(self)


    @classmethod
    def _RegisterMethod(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True):
        if wrapped:
            fn = functools.wraps(wrapped)(fn)

        fn_signature = utils.get_method_sig(fn)
        fn_docs = inspect.getdoc(fn)
        name = alias if alias else fn.__name__
        original_name = fn.__name__ if wrapped else original_name if original_name else name

        fn.__name__ = name
        fn.__doc__ = doc if doc else ("""
THIS METHOD IS AUTOMATICALLY GENERATED

    builder.{1}(*args, **kwargs)

It accepts the same arguments as `{3}.{0}`. """ + explanation + """

**{3}.{0}**

    {2}

        """).format(original_name, name, fn_docs, library_path) if explain else fn_docs

        if name in cls.__core__:
            raise Exception("Can't add method '{0}' because its on __core__".format(name))

        fn = method_type(fn)
        setattr(cls, name, fn)


    @classmethod
    def RegisterMethod(cls, *args, **kwargs):
        try:
            fn, library_path = args
            cls._RegisterMethod(fn, library_path, **kwargs)

        except:
            def register_decorator(fn):
                library_path, = args
                cls._RegisterMethod(fn, library_path, **kwargs)

                return fn
            return register_decorator


    @classmethod
    def _RegisterAt(cls, n, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):

        _wrapped = wrapped if wrapped else fn

        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self.ThenAt(n, fn, *args, **kwargs)

        all_args, previous_args, last_arg = _make_args_strs(n)

        explanation = """
However, the 1st argument is omitted, a partial with the rest of the arguments is returned which expects the 1st argument such that

    {3}.{0}("""+ all_args +"""*args, **kwargs)

is equivalent to

    builder.{1}("""+ previous_args +"""*args, **kwargs)("""+ last_arg +""")

        """ + explanation  if explain else ""

        cls.RegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain)

    @classmethod
    def RegisterAt(cls, *args, **kwargs):
        try:
            n, fn, library_path = args
            cls._RegisterAt(n, fn, library_path, **kwargs)

        except:
            def register_decorator(fn):
                n, library_path = args
                cls._RegisterAt(n, fn, library_path, **kwargs)

                return fn
            return register_decorator

    @classmethod
    def Register0(cls, *args, **kwargs):
        return cls.RegisterAt(0, *args, **kwargs)

    @classmethod
    def Register(cls, *args, **kwargs):
        return cls.RegisterAt(1, *args, **kwargs)

    @classmethod
    def Register2(cls, *args, **kwargs):
        return cls.RegisterAt(2, *args, **kwargs)

    @classmethod
    def Register3(cls, *args, **kwargs):
        return cls.RegisterAt(3, *args, **kwargs)

    @classmethod
    def Register4(cls, *args, **kwargs):
        return cls.RegisterAt(4, *args, **kwargs)

    @classmethod
    def Register5(cls, *args, **kwargs):
        return cls.RegisterAt(5, *args, **kwargs)


Builder.__core__ = [ name for name, f in inspect.getmembers(Builder, inspect.ismethod) ]


class ObjectProxy(object):
    """docstring for Underscore."""

    def __init__(self, __builder__):
        self.__builder__ = __builder__

    def __getattr__(self, name):

        def method_proxy(*args, **kwargs):
            f = lambda x: getattr(x, name)(*args, **kwargs)
            return self.__builder__.__then__(f)

        return method_proxy


class ReadProxy(object):
    """docstring for Underscore."""

    def __init__(self, __builder__):
        self.__builder__ = __builder__

    def __getitem__(self, name):
        return self.__builder__.NMake(name)

    def __getattr__(self, name):
        return self.__builder__.NMake(name)

    def __call__ (self, ref):
        return self.__builder__.NMake(ref)


class WriteProxy(object):
    """docstring for Underscore."""

    def __init__(self, __builder__):
        self.__builder__ = __builder__

    def __getitem__(self, ref):
        return self.__builder__.NMake({ref})

    def __getattr__ (self, ref):
        return self.__builder__.NMake({ref})

    def __call__ (self, ref):
        return self.__builder__.NMake({ref})



class RecordProxy(object):
    """docstring for RecClass."""

    def __init__(self, __builder__):
        self.__builder__ = __builder__

    def __getattr__ (self, attr):
        f = lambda x: getattr(x, attr)
        return self.__builder__.__then__(f)

    def __getitem__(self, key):
        f = lambda x: x[key]
        return self.__builder__.__then__(f)


#######################
# Helper functions
#######################

def _make_args_strs(n):

    if n == 0:
        return "", "", "x"

    n += 1
    all_args = [ 'x' + str(i) for i in range(1, n) ]
    last = all_args[n-2]
    previous = all_args[:n-2]

    return ", ".join(all_args + [""]), ", ".join(previous + [""]), last

_make_args_strs(2)