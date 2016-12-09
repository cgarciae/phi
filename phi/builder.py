"""
The `phi.builder.Builder` class exposes most of the API, you will normally use the `phi.P` object instance (or any equivalent object provided by a Phi-based library) to do most of the work. This module 4 main goals:

1. Exposing a public API for the [dsl](https://cgarciae.github.io/phi/dsl.m.html). See methods like `phi.builder.Builder.Make` and `phi.builder.Builder.Pipe`.
2. Exposing the [lambdas](https://cgarciae.github.io/phi/lambdas.m.html) capabilities.
3. Helping you integrate existing code into the DSL.
4. Let you write [fluent](https://en.wikipedia.org/wiki/Fluent_interface) code in Python.

To integrate existing code, the `phi.builder.Builder` class offers the following functionalities:

* Create *special* partials useful for the DSL. See the `phi.builder.Builder._` [underscore] method.
* Register functions as methods of the `phi.builder.Builder` class. See the `*Register*` method family e.g. `phi.builder.Builder.Register1`.
* Create functions that proxy methods from an object. See `phi.builder.Builder.Obj`.
* Create functions that proxy fields from an object. See `phi.builder.Builder.Rec`.

If you want to create a library based on Phi, integrate an existing library, or create some Phi-based helpers for your project, instead of using the `*Register*` methods on the `Builder` class, you should consider doing the following:

1. Create a custom class that inherits from `Builder`.
1. Use the `*Register*` methods or decorators of your custom class to give it your desired functionalities.
1. Instantiate a global object of this class. Preferably choose a single capital letter for its name (phi uses `P`).
"""

import inspect
import utils
from utils import identity
import functools
import dsl
from lambdas import Lambda

#######################
### Applicative
#######################

class Builder(Lambda):
    """
    All the core methods of the `Builder` class start with a capital letter (e.g. `phi.builder.Builder.Pipe` or `phi.builder.Builder.Make`) on purpose to avoid name chashes with functions that libraries might register. Methods that start with a lowercase letter are most probably core python functions automatically as methods (e.g. `phi.builder.Builder.map` or `phi.builder.Builder.sum`). There is a third batch of methods that like `phi.builder.Builder.And`, `phi.builder.Builder.Not`, `phi.builder.Builder.Contains`, etc, that are not considered core `Builder` methods but are packaged with this class for conveniece, initially they where capitalized because they mimimic keywords (`and`, `or`, `not`, etc) and its ilegal to give them these lowercase names, however, methods like `phi.builder.Builder.Contains` that could use lowercase are left capitalized to maintain uniformity."""

    @classmethod
    def Context(cls, *args):
        """
**Builder Core**. Also available as a global function as `phi.Context`.

Returns the context object of the current `dsl.With` statemente.

**Arguments**

* ***args**: By design `Context` accepts any number of arguments and completely ignores them.

This is a classmethod and it doesnt return a `Builder`/`Lambda` by design so it can be called directly:

    from phi import P, Context, Obj

    def read_file(_):
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

**More info**

* `phi.builder.Builder.Obj`
* [dsl](https://cgarciae.github.io/phi/dsl.m.html)
        """

        if dsl.With.GLOBAL_CONTEXT is dsl._NO_VALUE:
            raise Exception("Cannot use 'Context' outside of a 'With' block")

        return dsl.With.GLOBAL_CONTEXT

    With = dsl.With
    Ref = dsl.Ref

    def Pipe(self, x, *code, **kwargs):
        """
`Pipe` is method that takes an input argument plus an expression from the DSL, it compiles the expression and applies the resulting function to the input. Its highly inspired by Elixir's [|> (pipe)](https://hexdocs.pm/elixir/Kernel.html#%7C%3E/2) operator.

**Arguments**

* **x**: any input object
* ***code**: any expression from the DSL.`code` is implicitly a `tuple` since that is what Python gives you when you declare a [Variadic Function](https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists), therefore, according to the rules of the DSL, all expressions inside of `code` will be composed together. See [Composition](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Composition).

**Examples**

    from phi import P

    def add1(x): return x + 1
    def mul3(x): return x * 3

    x = P.Pipe(
        1,
        add1,
        mul3
    )

    assert x == 6

The previous using [lambdas](https://cgarciae.github.io/phi/lambdas.m.html)

    from phi import P

    x = P.Pipe(
        1,
        P + 1,
        P * 3
    )

    assert x == 6

Create a branched computation instead

    from phi import P

    [x, y] = P.Pipe(
        1,
        [
            P + 1  #1 + 1 == 2
        ,
            P * 3  #1 * 3 == 3
        ]
    )

    assert x == 2
    assert y == 3

Compose it with a multiplication by 2

    from phi import P

    [x, y] = P.Pipe(
        1,
        P * 2,  #1 * 2 == 2
        [
            P + 1  #2 + 1 == 3
        ,
            P * 3  #2 * 3 == 6
        ]
    )

    assert x == 3
    assert y == 6

Give names to the branches

    from phi import P

    result = P.Pipe(
        1,
        P * 2,  #1 * 2 == 2
        dict(
            x = P + 1  #2 + 1 == 3
        ,
            y = P * 3  #2 * 3 == 6
        )
    )

    assert result.x == 3
    assert result.y == 6

Divide the `x` by the `y`.


    from phi import P, Rec

    result = P.Pipe(
        1,
        P * 2,  #1 * 2 == 2
        dict(
            x = P + 1  #2 + 1 == 3
        ,
            y = P * 3  #2 * 3 == 6
        ),
        Rec.x / Rec.y  #3 / 6 == 0.5
    )

    assert result == 0.5

Save the value from the `P * 2` computation as `s` and retrieve it at the end in a branch

    from phi import P, Rec

    [result, s] = P.Pipe(
        1,
        P * 2, {'s'}  #1 * 2 == 2
        dict(
            x = P + 1  #2 + 1 == 3
        ,
            y = P * 3  #2 * 3 == 6
        ),
        [
            Rec.x / Rec.y  #3 / 6 == 0.5
        ,
            's'
        ]
    )

    assert result == 0.5
    assert s == 2

Add an input `Val` of 9 on a branch and add to it 1 just for the sake of it

    from phi import P, Rec, Val

    [result, s, val] = P.Pipe(
        1,
        P * 2, {'s'}  #2 * 1 == 2
        dict(
            x = P + 1  #2 + 1 == 3
        ,
            y = P * 3  #2 * 3 == 6
        ),
        [
            Rec.x / Rec.y  #3 / 6 == 0.5
        ,
            's'  #2
        ,
            Val(9) + 1  #10
        ]
    )

    assert result == 0.5
    assert s == 2
    assert val == 10

        """
        return self.Make(*code, **kwargs)(x)

    def Run(self, *code, **kwargs):
        """
        """
        return self.Pipe(None, *code, **kwargs)

    def Make(self, *code, **kwargs):
        """
        """

        _return_type = None
        flatten = None

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']

        if 'flatten' in kwargs:
            flatten = kwargs['flatten']
            del kwargs['flatten']

        g, refs = dsl.Compile(code, self._refs)
        f = utils.compose2(g, self)
        flatten_f = lambda x: utils.flatten_list(x) if type(x) is list else x

        if flatten:
            f = utils.compose2(flatten_f, f)

        return self.__unit__(f, refs, _return_type=_return_type)

    M = Make

    def _0(self, g, *args, **kwargs):
        """
        """
        _return_type = None

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']

        return self.__unit__(lambda x: g(*args, **kwargs), self._refs, _return_type=_return_type)

    def _(self, g, *args, **kwargs):
        """
        """
        _return_type = None

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']

        f = lambda x: g(x, *args, **kwargs)
        return self.__then__(f, _return_type=_return_type)

    _1 = _

    def _2(self, g, arg1, *args, **kwargs):
        """
        """
        _return_type = None

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']


        def _lambda(x):
            arg2 = self(x)
            new_args = tuple([arg1, arg2] + list(args))
            return g(*new_args, **kwargs)

        return self.__unit__(_lambda, self._refs, _return_type=_return_type)

    def _3(self, g, arg1, arg2, *args, **kwargs):
        """
        """
        _return_type = None

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']


        def _lambda(x):
            arg3 = self(x)
            new_args = tuple([arg1, arg2, arg3] + list(args))
            return g(*new_args, **kwargs)

        return self.__unit__(_lambda, self._refs, _return_type=_return_type)

    def _4(self, g, arg1, arg2, arg3, *args, **kwargs):
        """
        """
        _return_type = None

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']

        def _lambda(x):
            arg4 = self(x)
            new_args = tuple([arg1, arg2, arg3, arg4] + list(args))
            return g(*new_args, **kwargs)

        return self.__unit__(_lambda, self._refs, _return_type=_return_type)

    def _5(self, g, arg1, arg2, arg3, arg4, *args, **kwargs):
        """
        """
        _return_type = None

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']

        def _lambda(x):
            arg5 = self(x)
            new_args = tuple([arg1, arg2, arg3, arg4, arg5] + list(args))
            return g(*new_args, **kwargs)

        return self.__unit__(_lambda, self._refs, _return_type=_return_type)


    def Val(self, x):
        """
        """
        return self.__then__(lambda _: x)

    def On(self, ref):
        """
        """
        if type(ref) is str:
            ref = dsl.Ref(ref)

        if ref.name not in self._refs:
            refs = dict(self._refs, **{ref.name: ref})
        else:
            refs = self._refs

        return self.__unit__(utils.compose2(ref.set, self), refs)



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
    def DoRegisterMethod(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True):
        """
        This method enables you to register any function `fn` that takes an Applicative as its first argument as a method of the Builder class.

        **Arguments**

        * `fn`: a function that atleast takes an Applicative as its first argument.
        * `library_path`: the route of the librar from which this function was taken, used for documentation purposes.
        * `alias`: allows you to specify the name of the method, it will take the name of the function if its `None`.
        * `doc`: the documentation for the method, if `None` a predefied documentation will be generated based On the documentation of `fn`.

        **Return**

        `None`

        **Examples**

        """

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
            raise Exception("Can't add method '{0}' because its On __core__".format(name))

        fn = method_type(fn)
        setattr(cls, name, fn)

    @classmethod
    def RegisterMethod(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True):
        def register_decorator(fn):

            cls.DoRegisterMethod(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain)

            return fn
        return register_decorator


    @classmethod
    def RegisterFunction0(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._0(fn, *args, **kwargs)

        explanation = """
However, a partial with the arguments is returned which expects any argument `x` and complete ignores it, such that

    {3}.{0}(*args, **kwargs)

is equivalent to

    builder.{1}(*args, **kwargs)(x)

        """ + explanation if explain else ""

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain)

    @classmethod
    def RegisterFunction1(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        """
        This method enables you to register any function `fn` that takes an object as its first argument as a method of the Builder and Applicative class.

        **Arguments**

        * `fn`: a function that atleast takes an Object as its first argument.
        * `library_path`: the route of the librar from which this function was taken, used for documentation purposes.
        * `alias`: allows you to specify the name of the method, it will take the name of the function if its `None`.
        * `doc`: the documentation for the method, if `None` a predefied documentation will be generated based On the documentation of `fn`.

        **Return**

        `None`

        **Examples**

        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._(fn, *args, **kwargs)

        explanation = """
However, the 1st argument is omitted, a partial with the rest of the arguments is returned which expects the 1st argument such that

    {3}.{0}(x1, *args, **kwargs)

is equivalent to

    builder.{1}(*args, **kwargs)(x1)

        """ + explanation  if explain else ""

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain)


    @classmethod
    def RegisterFunction2(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._2(fn, *args, **kwargs)

        explanation = """
However, the 2nd argument is omitted, a partial with the rest of the arguments is returned which expects the 2nd argument such that

    {3}.{0}(x1, x2, *args, **kwargs)

is equivalent to

    builder.{1}(x1, *args, **kwargs)(x2)
        """ + explanation if explain else ""

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain)

    @classmethod
    def RegisterFunction3(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._3(fn, *args, **kwargs)

        explanation = """
However, the 3rd argument is omitted, a partial with the rest of the arguments is returned which expects the 3rd argument such that

    {3}.{0}(x1, x2, x3, *args, **kwargs)

is equivalent to

    builder.{1}(x1, x2, *args, **kwargs)(x3)
        """ + explanation if explain else ""

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain)

    @classmethod
    def RegisterFunction4(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._4(fn, *args, **kwargs)

        explanation = """
However, the 4th argument is omitted, a partial with the rest of the arguments is returned which expects the 4th argument such that

    {3}.{0}(x1, x2, x3, x4, *args, **kwargs)

is equivalent to

    builder.{1}(x1, x2, x3, *args, **kwargs)(x4)

        """ + explanation if explain else ""

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain)

    @classmethod
    def RegisterFunction5(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._5(fn, *args, **kwargs)

        explanation = """
However, the 5th argument is omitted, a partial with the rest of the arguments is returned which expects the 5th argument such that

    {3}.{0}(x1, x2, x3, x4, x5, *args, **kwargs)

is equivalent to

    builder.{1}(x1, x2, x3, x4, *args, **kwargs)(x5)
        """ + explanation if explain else ""

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain, _return_type=_return_type)

    @classmethod
    def Register0(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction0(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def Register1(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        def register_decorator(fn):
            _wrapped = wrapped if wrapped else fn
            cls.RegisterFunction1(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=_wrapped, explanation=explanation, method_type=method_type, explain=explain, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def Register2(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction2(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def Register3(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction3(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def Register4(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction4(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def Register5(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction5(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain, _return_type=_return_type)
            return fn
        return register_decorator


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