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
* `phi.builder.Builder.PatchAt`
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

######################
# Helpers
######################

_True = lambda x: True
_False = lambda x: False
_None = lambda x: None
_NoLeadingUnderscore = lambda name: name[0] != "_"

#######################
### Builder
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

        if dsl._CompilationContextManager.WITH_GLOBAL_CONTEXT is dsl._NO_VALUE:
            raise Exception("Cannot use 'Context' outside of a 'With' block")

        return dsl._CompilationContextManager.WITH_GLOBAL_CONTEXT

    def With(self, *args, **kwargs):
        return self.NMake(dsl.With(*args, **kwargs))
    With.__doc__ = dsl.With.__doc__


    @property
    def Ref(self):
        """
Returns an object that helps you to inmediatly create and [read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read) [references](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Ref).

**Creating Refences**

You can manually create a [Ref](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Ref) outside the DSL using `Ref` and then pass to as/to a [Read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read) or [Write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Write) expression. Here is a contrived example

    from phi import P

    r = P.Ref('r')

    assert [600, 3, 6] == P.Pipe(
        2,
        P + 1, {'a'},  # a = 2 + 1 = 3
        P * 2, {'b'},  # b = 3 * 2 = 6
        P * 100, {'c', r },  # c = r = 6 * 100 = 600
        ['c', 'a', 'b']
    )

    assert r() == 600

**Reading Refences from the Current Context**

While the expression `Read.a` with return a function that will discard its argument and return the value of the reference `x` in the current context, the expression `Ref.x` will return the value inmediatly, this is useful when using it inside pyton lambdas.

    Read.x(None) <=> Ref.x

As an example

    from phi import P, Obj, Ref

    assert {'a': 97, 'b': 98, 'c': 99} == P.Pipe(
        "a b c", Obj
        .split(' ').Write.keys  # keys = ['a', 'b', 'c']
        .map(ord),  # [ord('a'), ord('b'), ord('c')] == [97, 98, 99]
        lambda it: zip(Ref.keys, it),  # [('a', 97), ('b', 98), ('c', 99)]
        dict   # {'a': 97, 'b': 98, 'c': 99}
    )

        """
        return _RefProxyInstance

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
**Make**

    Make(code*, refs={}, flatten=False, create_ref_context=True, _return_type=None)

`Make` takes an expression from the DSL and compiles it to a function.

**Arguments**

* ***code**: any expression from the DSL.`code` is implicitly a `tuple` since that is what Python gives you when you declare a [Variadic Function](https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists), therefore, according to the rules of the DSL, all expressions inside of `code` will be composed together. See [Composition](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Composition).
* `refs = {}`: dictionary of external/default values for references passed during compilation. By default its empty, it might be useful if you want to inject values and [Read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read) without the need of an explicit [Write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Write) operation. You might also consider using `phi.builder.Builder.Val` instead of this.
* `flatten = False` : if `flatten` is True and the argument being returned by the compiled function is a `list` it will flatten the list. This is useful if you have nested branches in the last computation.
* `create_ref_context = True` : determines if a reference manager should be created on compilation. See `phi.builder.Builder.NMake` for more information on what happens when its set to `False`.
* `_return_type = None` : By default `Make` returns an object of the same class e.g. `Builder`, however you can pass in a custom class that inherits from `Builder` as the return contianer. This is useful if the custom builder has specialized methods.

While `Pipe` is might be an nicer since it makes the initial value being piped explicit, it has the overhead of having to "compile" the expression into a function every time. If you have something like

    from phi import P

    xs = []

    for i in xrange(10000000000):
        x = P.Pipe(
            i,
            some_dsl_expression
        )

        xs.append(x)

you are better of using `Make` to compile that DSL expression in advanced

    from phi import P

    xs = []
    f = P.Make(some_dsl_expression)

    for i in xrange(10000000000):
        x = f(i)
        xs.append(x)

This reduces the overhead of parsing the expressions and creating the function.


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

    def ThenAt(self, n, f, *args, **kwargs):
        """
`ThenAt` enables you to create a partially apply many arguments to a function, the returned partial expects a single arguments which will be applied at the `n`th position of the original function.

**Arguments**

* **n**: position at which the created partial will apply its awaited argument on the original function.
* **f**: function which the partial will be created.
* **args & kwargs**: all `*args` and `**kwargs` will be passed to the function `f`.
* `_return_type = None`: type of the returned `builder`, if `None` it will return the same type of the current `builder`. This special kwarg will NOT be passed to `f`.

You can think of `n` as the position that the value being piped down will pass through the `f`. Say you have the following expression

    D == fun(A, B, C)

all the following are equivalent

    from phi import P, Pipe, ThenAt

    D == Pipe(A, ThenAt(1, fun, B, C))
    D == Pipe(B, ThenAt(2, fun, A, C))
    D == Pipe(C, ThenAt(3, fun, A, B))

you could also use the shortcuts `Then`, `Then2`,..., `Then5`, which are more readable

    from phi import P, Pipe

    D == Pipe(A, P.Then(fun, B, C))
    D == Pipe(B, P.Then2(fun, A, C))
    D == Pipe(C, P.Then3(fun, A, B))

There is a special case not discussed above: `n = 0`. When this happens only the arguments given will be applied to `f`, this method it will return a partial that expects a single argument but completely ignores it

    from phi import P

    D == Pipe(None, P.ThenAt(0, fun, A, B, C))
    D == Pipe(None, P.Then0(fun, A, B, C))

**Examples**

Max of 6 and the argument:

    from phi import P

    assert 6 == P.Pipe(
        2,
        P.Then(max, 6)
    )

Previous is equivalent to

    assert 6 == max(2, 6)

Open a file in read mode (`'r'`)

    from phi import P

    f = P.Pipe(
        "file.txt",
        P.Then(open, 'r')
    )

Previous is equivalent to

    f = open("file.txt", 'r')

Split a string by whitespace and then get the length of each word

    from phi import P

    assert [5, 5, 5] == P.Pipe(
        "Again hello world",
        P.Then(str.split, ' ')
        .Then2(map, len)
    )

Previous is equivalent to

    x = "Again hello world"

    x = str.split(x, ' ')
    x = map(len, x)

    assert [5, 5, 5] == x

As you see, `Then2` was very useful because `map` accepts and `iterable` as its `2nd` parameter. You can rewrite the previous using the [PythonBuilder](https://cgarciae.github.io/phi/python_builder.m.html) and the `phi.builder.Builder.Obj` object

    from phi import P, Obj

    assert [5, 5, 5] == P.Pipe(
        "Again hello world",
        Obj.split(' '),
        P.map(len)
    )

**Also see**

* `phi.builder.Builder.Obj`
* [PythonBuilder](https://cgarciae.github.io/phi/python_builder.m.html)
* `phi.builder.Builder.RegisterAt`
        """
        _return_type = None
        n -= 1

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']

        def _lambda(x):
            x = self(x)
            new_args = args[0:n] + (x,) + args[n:] if n >= 0 else args
            return f(*new_args, **kwargs)

        return self.__unit__(_lambda, _return_type=_return_type)

    def Then0(self, f, *args, **kwargs):
        """
`Then0(f, ...)` is equivalent to `ThenAt(0, f, ...)`. Checkout `phi.builder.Builder.ThenAt` for more information.
        """
        return self.ThenAt(0, f, *args, **kwargs)

    def Then(self, f, *args, **kwargs):
        """
`Then(f, ...)` is equivalent to `ThenAt(1, f, ...)`. Checkout `phi.builder.Builder.ThenAt` for more information.
        """
        return self.ThenAt(1, f, *args, **kwargs)

    Then1 = Then

    def Then2(self, f, arg1, *args, **kwargs):
        """
`Then2(f, ...)` is equivalent to `ThenAt(2, f, ...)`. Checkout `phi.builder.Builder.ThenAt` for more information.
        """
        args = (arg1,) + args
        return self.ThenAt(2, f, *args, **kwargs)

    def Then3(self, f, arg1, arg2, *args, **kwargs):
        """
`Then3(f, ...)` is equivalent to `ThenAt(3, f, ...)`. Checkout `phi.builder.Builder.ThenAt` for more information.
        """
        args = (arg1, arg2) + args
        return self.ThenAt(3, f, *args, **kwargs)

    def Then4(self, f, arg1, arg2, arg3, *args, **kwargs):
        """
`Then4(f, ...)` is equivalent to `ThenAt(4, f, ...)`. Checkout `phi.builder.Builder.ThenAt` for more information.
        """
        args = (arg1, arg2, arg3) + args
        return self.ThenAt(4, f, *args, **kwargs)

    def Then5(self, f, arg1, arg2, arg3, arg4, *args, **kwargs):
        """
`Then5(f, ...)` is equivalent to `ThenAt(5, f, ...)`. Checkout `phi.builder.Builder.ThenAt` for more information.
        """
        args = (arg1, arg2, arg3, arg4) + args
        return self.ThenAt(5, f, *args, **kwargs)


    def Val(self, x):
        return self.__then__(lambda z: x)
    Val.__doc__ = dsl.Input.__doc__

    @property
    def Write(self):
        """
`Write` is a `property` that returns an object that defines the `__call__`, `__getattr__` and `__getitem__` methods which you can use to define a [Write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Write) expression. The following DSL expression

    {`my_ref`}

is equivalent to any of these

    Write.my_ref
    Write['my_ref']
    Write('my_ref')

**Also see**

* [dsl.Write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Write)
* [dsl.Read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read)
* `phi.builder.Builder.Read`

        """
        return _WriteProxy(self)


    @property
    def Read(self):
        """
`Read` is a `property` that returns an object that defines the `__call__`, `__getattr__` and `__getitem__` methods which you can use to define a [Read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read) expression. The following DSL expression

    `my_ref`

is equivalent to any of these

    Read.my_ref
    Read['my_ref']
    Read('my_ref')

**Also see**

* [dsl.Read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read)
* [dsl.Write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Write)
* `phi.builder.Builder.Write`
* `phi.builder.Builder.Obj`
* `phi.builder.Builder.Rec`

        """
        return _ReadProxy(self)

    @property
    def Obj(self):
        """
`Obj` is a `property` that returns an object that defines the `__getattr__` method which when called helps you create a partial that emulates a method call. The following expression

    Obj.some_method(x1, x2, ...)

is equivalent to

    lambda obj: obj.some_method(x1, x2, ...)

**Examples**

    from phi import P, Obj

    assert "hello world" == P.Pipe(
        "  HELLO HELLO {0}     ",
        Obj.format("WORLD"),  # "   HELLO HELLO WORLD     "
        Obj.strip(),          # "HELLO HELLO WORLD"
        Obj.lower()           # "hello hello world"
        Obj.split(' ')        # ["hello", "hello", "world"]
        Obj.count("hello")    # 2
    )

**Also see**

* `phi.builder.Builder.Rec`
* [dsl.Write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Write)
* `phi.builder.Builder.Write`
        """
        return _ObjectProxy(self)

    @property
    def Rec(self):
        """
`Rec` is a `property` that returns an object that defines the `__getattr__` and `__getitem__` methods which when called help you create a partial that emulates a field access. The following expression

    Rec.some_field

is equivalent to

    lambda rec: rec.some_field

**Examples**

    from phi import P, Obj, Rec

    class Point(object):

        def __init__(self, x, y):
            self.x = x
            self.y = y

        def flip_cords(self):
            y = self.y
            self.y = self.x
            self.x = y

    assert 4 == P.Pipe(
        Point(1, 2),         # point(x=1, y=2)
        Obj.flip_cords(),    # point(x=2, y=1)
        Rec.x,               # point.x = 2
        P * 2                # 2 * 2 = 4
    )

**Also see**

* `phi.builder.Builder.Obj`
* `phi.builder.Builder.Read`
* `phi.builder.Builder.Write`
        """
        return _RecordProxy(self)

    @classmethod
    def _RegisterMethod(cls, f, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True):
        if wrapped:
            f = functools.wraps(wrapped)(f)

        fn_signature = utils.get_method_sig(f)
        fn_docs = inspect.getdoc(f)
        name = alias if alias else f.__name__
        original_name = f.__name__ if wrapped else original_name if original_name else name

        f.__name__ = name
        f.__doc__ = doc if doc else ("""
THIS METHOD IS AUTOMATICALLY GENERATED

    {builder_class}.{name}(*args, **kwargs)

It accepts the same arguments as `{library_path}{original_name}`. """ + explanation + """

**{library_path}{original_name}**

    {fn_docs}

        """).format(original_name=original_name, name=name, fn_docs=fn_docs, library_path=library_path, builder_class=cls.__name__) if explain else fn_docs

        if name in cls.__core__:
            raise Exception("Can't add method '{0}' because its on __core__".format(name))

        f = method_type(f)
        setattr(cls, name, f)


    @classmethod
    def RegisterMethod(cls, *args, **kwargs):
        """
**RegisterMethod**

    RegisterMethod(f, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True)

`classmethod` for registering functions as methods of this class.

**Arguments**

* **f** : the particular function being registered as a method
* **library_path** : library from where `f` comes from, unless you pass an empty string, put a period `"."` at the end of the library name.
* `alias=None` : alias for the name/method being registered
* `original_name=None` : name of the original function, used for documentation purposes.
* `doc=None` : complete documentation of the method being registered
* `wrapped=None` : if you are registering a function which wraps around another function, pass this other function through `wrapped` to get better documentation, this is specially useful is you register a bunch of functions in a for loop. Please include an `explanation` to tell how the actual function differs from the wrapped one.
* `explanation=""` : especify any additional information for the documentation of the method being registered, you can use any of the following format tags within this string and they will be replace latter on: `{original_name}`, `{name}`, `{fn_docs}`, `{library_path}`, `{builder_class}`.
* `method_type=identity` : by default its applied but does nothing, you might also want to register functions as `property`, `classmethod`, `staticmethod`
* `explain=True` : decide whether or not to show any kind of explanation, its useful to set it to `False` if you are using a `Register*` decorator and will only use the function as a registered method.

A main feature of `phi` is that it enables you to integrate your library or even an existing library with the DSL. You can achieve three levels of integration

1. Passing your functions to the DSL. This a very general machanism -since you could actually do everything with python lamdas- but in practice functions often receive multiple parameters.
2. Creating partials with the `Then*` method family. Using this you could integrate any function, but it will add a lot of noise if you use heavily on it.
3. Registering functions as methods of a `Builder` derived class. This produces the most readable code and its the approach you should take if you want to create a Phi-based library or a helper class.

While point 3 is the most desirable it has a cost: you need to create your own `phi.builder.Builder`-derived class. This is because SHOULD NOT register functions to existing builders e.g. the `phi.builder.Builder` or [PythonBuilder](https://cgarciae.github.io/phi/builder.m.html#phi.python_builder.PythonBuilder) provided by phi because that would pollute the `P` object. Instead you should create a custom class that derives from `phi.builder.Builder`,  [PythonBuilder](https://cgarciae.github.io/phi/builder.m.html#phi.python_builder.PythonBuilder) or another custom builder depending on your needs and register your functions to that class.

**Examples**

Say you have a function on a library called `"my_lib"`

    def some_fun(obj, arg1, arg2):
        # code

You could use it with the dsl like this

    from phi import P, Then

    P.Pipe(
        input,
        ...
        Then(some_fun, arg1, arg2)
        ...
    )

assuming the first parameter `obj` is being piped down. However if you do this very often or you are creating a library, you are better off creating a custom class derived from `Builder` or `PythonBuilder`

    from phi import Builder #or PythonBuilder

    class MyBuilder(Builder): # or PythonBuilder
        pass

and registering your function as a method. The first way you could do this is by creating a wrapper function for `some_fun` and registering it as a method

    def some_fun_wrapper(self, arg1, arg2):
        return self.Then(some_fun, arg1, arg2)

    MyBuilder.RegisterMethod(some_fun_wrapper, "my_lib.", wrapped=some_fun)

Here we basically created a shortcut for the original expression `Then(some_fun, arg1, arg2)`. You could also do this using a decorator

    @MyBuilder.RegisterMethod("my_lib.", wrapped=some_fun)
    def some_fun_wrapper(self, arg1, arg2):
        return self.Then(some_fun, arg1, arg2)

However, this is such a common task that we've created the method `Register` to avoid you from having to create the wrapper. With it you could register the function `some_fun` directly as a method like this

    MyBuilder.Register(some_fun, "my_lib.")

or by using a decorator over the original function definition

    @MyBuilder.Register("my_lib.")
    def some_fun(obj, arg1, arg2):
        # code

Once done you've done any of the previous approaches you can create a custom global object e.g. `M` and use it instead of/along with `P`

    M = MyBuilder(lambda x: x)

    M.Pipe(
        input,
        ...
        M.some_fun(arg1, args)
        ...
    )

**Argument position**

`phi.builder.Builder.Register` internally uses `phi.builder.Builder.Then`, this is only useful if the object being piped is intended to be passed as the first argument of the function being registered, if this is not the case you could use `phi.builder.Builder.Register2`, `phi.builder.Builder.Register3`, ..., `phi.builder.Builder.Register5` or `phi.builder.Builder.RegisterAt` to set an arbitrary position, these functions will internally use `phi.builder.Builder.Then2`, `phi.builder.Builder.Then3`, ..., `phi.builder.Builder.Then5` or `phi.builder.Builder.ThenAt` respectively.

**Wrapping functions**

Sometimes you have an existing function that you would like to modify slightly so it plays nicely with the DSL, what you normally do is create a function that wraps around it and passes the arguments to it in a way that is convenient

    import some_lib

    @MyBuilder.Register("some_lib.")
    def some_fun(a, n):
        return some_lib.some_fun(a, n - 1) # forward the args, n slightly modified

When you do this -as a side effect- you loose the original documentation, to avoid this you can use the Registers `wrapped` argument along with the `explanation` argument to clarity the situation

    import some_lib

    some_fun_explanation = "However, it differs in that `n` is automatically subtracted `1`"

    @MyBuilder.Register("some_lib.", wrapped=some_lib.some_fun, explanation=some_fun_explanation)
    def some_fun(a, n):
        return some_lib.some_fun(a, n - 1) # forward the args, n slightly modified

Now the documentation for `MyBuilder.some_fun` will be a little bit nicer since it includes the original documentation from `some_lib.some_fun`. This behaviour is specially useful if you are wrapping an entire 3rd party library, you usually automate the process iterating over all the funcitions in a for loop. The `phi.builder.Builder.PatchAt` method lets you register and entire module using a few lines of code, however, something you have to do thing more manually and do the iteration yourself.

**See Also**

* `phi.builder.Builder.PatchAt`
* `phi.builder.Builder.RegisterAt`
        """
        unpack_error = True

        try:
            f, library_path = args
            unpack_error = False
            cls._RegisterMethod(f, library_path, **kwargs)

        except:
            if not unpack_error:
                raise

            def register_decorator(f):
                library_path, = args
                cls._RegisterMethod(f, library_path, **kwargs)

                return f
            return register_decorator


    @classmethod
    def _RegisterAt(cls, n, f, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None):

        _wrapped = wrapped if wrapped else f

        @functools.wraps(f)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self.ThenAt(n, f, *args, **kwargs)

        all_args, previous_args, last_arg = _make_args_strs(n)

        explanation = """
However, the 1st argument is omitted, a partial with the rest of the arguments is returned which expects the 1st argument such that

    {library_path}{original_name}("""+ all_args +"""*args, **kwargs)

is equivalent to

    {builder_class}.{name}("""+ previous_args +"""*args, **kwargs)("""+ last_arg +""")

        """ + explanation  if explain else ""

        cls.RegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, explain=explain)

    @classmethod
    def RegisterAt(cls, *args, **kwargs):
        """
**RegisterAt**

    RegisterAt(n, f, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True, _return_type=None)

Most of the time you don't want to register an method as such, that is, you don't care about the `self` builder object, instead you want to register a function that transforms the value being piped down the DSL. For this you can use `RegisterAt` so e.g.

    def some_fun(obj, arg1, arg2):
        # code

    @MyBuilder.RegisterMethod("my_lib.")
    def some_fun_wrapper(self, arg1, arg2):
        return self.ThenAt(1, some_fun, arg1, arg2)

can be written directly as

    @MyBuilder.RegisterAt(1, "my_lib.")
    def some_fun(obj, arg1, arg2):
        # code

For this case you can just use `Register` which is a shortcut for `RegisterAt(1, ...)`

    @MyBuilder.Register("my_lib.")
    def some_fun(obj, arg1, arg2):
        # code

**Also See**

* `phi.builder.Builder.RegisterMethod`
        """
        unpack_error = True

        try:
            n, f, library_path = args
            unpack_error = False
            cls._RegisterAt(n, f, library_path, **kwargs)

        except:
            if not unpack_error:
                raise

            def register_decorator(f):
                n, library_path = args
                cls._RegisterAt(n, f, library_path, **kwargs)

                return f
            return register_decorator

    @classmethod
    def Register0(cls, *args, **kwargs):
        """
`Register0(...)` is a shortcut for `RegisterAt(0, ...)`

**Also See**

* `phi.builder.Builder.RegisterAt`
* `phi.builder.Builder.RegisterMethod`
        """
        return cls.RegisterAt(0, *args, **kwargs)

    @classmethod
    def Register(cls, *args, **kwargs):
        """
`Register(...)` is a shortcut for `RegisterAt(1, ...)`

**Also See**

* `phi.builder.Builder.RegisterAt`
* `phi.builder.Builder.RegisterMethod`
        """
        return cls.RegisterAt(1, *args, **kwargs)

    @classmethod
    def Register2(cls, *args, **kwargs):
        """
`Register2(...)` is a shortcut for `RegisterAt(2, ...)`

**Also See**

* `phi.builder.Builder.RegisterAt`
* `phi.builder.Builder.RegisterMethod`
        """
        return cls.RegisterAt(2, *args, **kwargs)

    @classmethod
    def Register3(cls, *args, **kwargs):
        """
`Register3(...)` is a shortcut for `RegisterAt(3, ...)`

**Also See**

* `phi.builder.Builder.RegisterAt`
* `phi.builder.Builder.RegisterMethod`
        """
        return cls.RegisterAt(3, *args, **kwargs)

    @classmethod
    def Register4(cls, *args, **kwargs):
        """
`Register4(...)` is a shortcut for `RegisterAt(4, ...)`

**Also See**

* `phi.builder.Builder.RegisterAt`
* `phi.builder.Builder.RegisterMethod`
        """
        return cls.RegisterAt(4, *args, **kwargs)

    @classmethod
    def Register5(cls, *args, **kwargs):
        """
`Register5(...)` is a shortcut for `RegisterAt(5, ...)`

**Also See**

* `phi.builder.Builder.RegisterAt`
* `phi.builder.Builder.RegisterMethod`
        """
        return cls.RegisterAt(5, *args, **kwargs)

    @classmethod
    def PatchAt(cls, n, module, module_alias=None, method_name_modifier=_None, blacklist_predicate=_False, whitelist_predicate=_True, return_type_predicate=_None, getmembers_predicate=inspect.isfunction):
        """
This classmethod lets you easily patch all of functions/callables from a module or class as methods a Builder class.

**Arguments**

* **n** : the position the the object being piped will take in the arguments when the function being patched is applied. See `RegisterMethod` and `ThenAt`.
* **module** : a module or class from which the functions/methods/callables will be taken.
* `module_alias = None` : an optional alias for the module used for documentation purposes.
* `method_name_modifier = lambda f_name: None` : a function that can modify the name of the method will take. If `None` the name of the function will be used.
* `blacklist_predicate = lambda f_name: name[0] != "_"` : A predicate that determines which functions are banned given their name. By default it excludes all function whose name start with `'_'`. `blacklist_predicate` can also be of type list, in which case all names contained in this list will be banned.
* `whitelist_predicate = lambda f_name: True` : A predicate that determines which functions are admitted given their name. By default it include any function. `whitelist_predicate` can also be of type list, in which case only names contained in this list will be admitted. You can use both `blacklist_predicate` and `whitelist_predicate` at the same time.
* `return_type_predicate = lambda f_name: None` : a predicate that determines the `_return_type` of the Builder. By default it will always return `None`. See `phi.builder.Builder.ThenAt`.
* `getmembers_predicate = inspect.isfunction` : a predicate that determines what type of elements/members will be fetched by the `inspect` module, defaults to [inspect.isfunction](https://docs.python.org/2/library/inspect.html#inspect.isfunction). See [getmembers](https://docs.python.org/2/library/inspect.html#inspect.getmembers).

**Examples**

Lets patch ALL the main functions from numpy into a custom builder!

    from phi import PythonBuilder #or Builder
    import numpy as np

    class NumpyBuilder(PythonBuilder): #or Builder
        "A Builder for numpy functions!"
        pass

    NumpyBuilder.PatchAt(1, np)

    N = NumpyBuilder(lambda x: x)

Thats it! Although a serious patch would involve filtering out functions that don't take arrays. Another common task would be to use `NumpyBuilder.PatchAt(2, ...)` (`PatchAt(n, ..)` in general) when convenient to send the object being pipe to the relevant argument of the function. The previous is usually done with and a combination of `whitelist_predicate`s and `blacklist_predicate`s on `PatchAt(1, ...)` and `PatchAt(2, ...)` to filter or include the approriate functions on each kind of patch. Given the previous code we could now do

    import numpy as np

    x = np.array([[1,2],[3,4]])
    y = np.array([[5,6],[7,8]])

    z = N.Pipe(
        x, N
        .dot(y)
        .add(x)
        .transpose()
        .sum(axis=1)
    )

Which is strictly equivalent to

    import numpy as np

    x = np.array([[1,2],[3,4]])
    y = np.array([[5,6],[7,8]])

    z = np.dot(x, y)
    z = np.add(z, x)
    z = np.transpose(z)
    z = np.sum(z, axis=1)

The thing to notice is that with the `NumpyBuilder` we avoid the repetitive and needless passing and reassigment of the `z` variable, this removes a lot of noise from our code.
        """
        module_name = module_alias if module_alias else module.__name__ + '.'
        patch_members = _get_patch_members(builder, module, blacklist_predicate=blacklist_predicate, whitelist_predicate=whitelist_predicate, getmembers_predicate=getmembers_predicate)

        for name, f in patch_members:
            cls.RegisterAt(n, f, module_name, _return_type=return_type_predicate(f.__name__), alias=method_name_modifier(f.__name__))


Builder.__core__ = [ name for name, f in inspect.getmembers(Builder, inspect.ismethod) ]


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
        return dsl._CompilationContextManager.get_ref(name).value

    def __getattr__(self, name):
        return dsl._CompilationContextManager.get_ref(name).value

    def __call__(self, *args, **kwargs):
        return dsl.Ref(*args, **kwargs)

_RefProxyInstance = _RefProxy()

class _ReadProxy(object):
    """docstring for _ReadProxy."""

    def __init__(self, __builder__):
        self.__builder__ = __builder__

    def __getitem__(self, name):
        return self.__builder__.NMake(name)

    def __getattr__(self, name):
        return self.__builder__.NMake(name)

    def __call__ (self, ref):
        return self.__builder__.NMake(ref)


class _WriteProxy(object):
    """docstring for _WriteProxy."""

    def __init__(self, __builder__):
        self.__builder__ = __builder__

    def __getitem__(self, ref):
        return self.__builder__.NMake({ref})

    def __getattr__ (self, ref):
        return self.__builder__.NMake({ref})

    def __call__ (self, ref):
        return self.__builder__.NMake({ref})



class _RecordProxy(object):
    """docstring for _RecordProxy."""

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

def _get_patch_members(builder, module, blacklist_predicate=_NoLeadingUnderscore, whitelist_predicate=_True, _return_type=None, getmembers_predicate=inspect.isfunction):

    if type(whitelist_predicate) is list:
        whitelist = whitelist_predicate
        whitelist_predicate = lambda x: x in whitelist

    if type(blacklist_predicate) is list:
        blacklist = blacklist_predicate
        blacklist_predicate = lambda x: x in blacklist

    return [
        (name, f) for (name, f) in inspect.getmembers(module, getmembers_predicate) if whitelist_predicate(name) and not blacklist_predicate(name)
    ]


