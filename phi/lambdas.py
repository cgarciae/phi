"""
Phi's `Lambda` class allows you to create quick lambdas that are much more readable and compact than Python's `lambda` keyword. The `P` object

** Operations **
`Lambda` overrides all operators plus the `__getitem__` and `__call__` special methods. Using operator overloading you can do things like

    form phi import P

    f = (P * 2) / (P + 1)

    assert f(1) == 1  #( 1 * 2 ) / ( 1 + 1) == 2 / 2 == 1

the previous expression for `f` is equivalent to

    lambda x: (x * 2) / (x + 1)

As you see, it creates very math-like functions that are very readable. The overloading mechanism has the following rules:

Let `g` be a Lambda, `h` a callable or Lambda, and `$` any python operator, then

    f = g $ h

is equivalent to

    lambda x: g(x) $ h(x)

Naturally `a $ b` returns also returns Lambda so operations can be chained. When `b` is not a callable or Node (as `1` in `P + 1`) then the expression

    a $ b

is reinterpreted as this so it does what you expect

    a $ Val(b)

For more information see [Val](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Expression.Val). Also, reverse methods like `__radd__` (reverse for `__add__`) are also implemented so that expressions like `1 + P` work as expected.

** State **
You might see function like [Read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Expression.Read) and [Write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Expression.Write) that make the look as if you are doing stateful voodoo behind the scenes, dont worry, internally Internally `Lambda` is implemented using a pattern that passes state from lambda to lambda in a functional manner. All normal functions of the form

    y = f(x)

are lifted to

    (y, new_state) = f(x, state)

where state is a `dict`. This way [Read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Expression.Read) and [Write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Expression.Write) can be implemented in such a way that they can read/write from/to the state `dict` being passed around, Write returns a new `dict` with the updated values, all operations are immutable. Since internally Lambdas return a tuple with a value and a dict, you might wonder why you only get the value when you call a Lambda, see `__call__` next.

** __call__ **

    def __call__(self, x, *return_state, **state)

* Arguments *

* `x` : a value to apply the computation
* `*return_state` : an optional boolean to determine whether the resulting internal state should be returned, defaults to `False`
* `**state` : all keyword argument are interpreted as initial values from the state `dict` that will be passed through the computation, defaults to `{}`.

Normally you call a `Lambda` only passing the value

    f = P + 1
    f(1) == 2

however if you pass an extra argument with `True` you can get the state back

    f = P + 1
    f(1, True) == (2, {})

and if you pass keyword arguments you will se that the returned state includes them

    f = P + 1
    f(1, True, a=0) == (2, {"a": 0})

Naturally this behaviour is only useful if you include expression that do something with the state, so lets do that

    from phi import P, Read, Write, Seq

    f = Seq(Read("a"), P + 5, Write("a"))
    f(None, True, a=0) == (5, {"a": 5})

Here we pass `None` to `f` but also set `a = 0` internally and then

1. `Read("a")` dicards `None` and sets the value to `0` which is the current value of `a`
2. `P + 5` adds `5` to `0`
3. `Write("a")` sets the value `a` of the state to `5`

The previous can also be written more compactly as

    f = Read("a") + 5 >> Write("a")
    f(None, True, a=0) == (5, {"a": 5})

or even

    f = Read.a + 5 >> Write.a
    assert f(None, True, a=0) == (5, {"a": 5})

** __getitem__ **
The special method `__getitem__` is also implemented and enables you to define a lambda uses pythons access mechanism on its argument. The expression

    P[x]

is equivalent to

    lambda obj: obj[x]

** Examples **
Add the first and last element of a list

    from phi import P

    f = P[0] + P[-1]

    assert f([1, 2, 3, 4]) == 5  #1 + 4 == 5

** `>>` **
The special method `__rshift__` (right shift) needed to overload `>>` is implemented differently than the other methods in that

    f = g >> h

is NOT equivalent to

    f(x) = g(x) >> h(x)

Instead it represents function composition or function application depending on the context.

* Composition *

The expression

    g >> h

is equivalent to the expression

    Seq(g, h)

which is equivalent to

    lambda x: h(g(x))

See [Seq](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Expression.Seq). Note that atleast one of `g` or `h` has to be a `Lambda` for this operator to work. An easy way create a Lambda from any function `f` is to do

    P.Seq(f)

* Application *

Given `a` and `g` where

* `a` is not an instance of `Lambda` and its not a callable
* `g` is an instance of `Lambda`

then the expresion

    a >> g

is equivalent to

    g(a)

** << **
The special method `__lshift__` (left shift) behaves as a reversed form of `>>` in the sense that the order of operations on excecution is done backwards

* Composition Comparison *

* `f >> g` is equivalent to `lambda x: g(f(x))`. `f` is executed first then `g`. Reads left to right.
* `f << g` is equivalent to `lambda x: f(g(x))`. `g` is executed first then `f`. Reads right to left.

* Application *

Given `a` and `g` where

* `a` is not an instance of `dsl.Node` and is not a callable
* `g` is an instance of `Lambda`

then

    g << a

is equivalent to

    g(a)

** fn.py **

The `Lambda` class takes much of its inspiration and code from [fn.py](https://github.com/fnpy/fn.py)'s '`_`' object, however it differs from it in the following aspects:

* It only creates functions of arity 1 to comply with the DSL. Where in fn.py expressions like `_ + _` are equivalent to `lambda a, b: a + b`, phi's lambdas intepret `P + P` as `lambda a: a + a`. In the context of the DSL this is incredibly useful since it allows you to write expressions like `P[0] + P[1]` (equivalent to `lambda a: a[0] + a[1]`) to add the first two elements of e.g. a previous branched computation, in fn.py `_[0] + _[1]` is equivalent to `lambda a, b: a[0] + b[1]`.
* The operators `>>` and `<<` are used for function composition or application.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division


from . import utils
import operator

def _fmap(opt):
    def method(self, b):

        other = (lambda z: b) if not hasattr(b, '__call__') else b

        if not isinstance(other, Lambda):
            other = utils.lift(other)
            other = self.__class__(other)

        f = self._f
        g = other._f

        def h(x, state):
            y1, state1 = f(x, state)
            y2, state2 = g(x, state)

            y_out = opt(y1, y2)
            state_out = utils.merge(state1, state2)

            return y_out, state_out


        return self.__unit__(h)

    return method

def _fmap_flip(opt):
    def method(self, b):

        other = (lambda z: b) if not hasattr(b, '__call__') else b

        if not isinstance(other, Lambda):
            other = utils.lift(other)
            other = self.__class__(other)

        f = self._f
        g = other._f

        def h(x, state):
            y2, state = g(x, state)
            y1, state = f(x, state)

            y_out = opt(y2, y1)

            return y_out, state


        return self.__unit__(h)

    return method

def _unary_fmap(opt):
    def method(self):
        return self.__then__(utils.lift(opt))

    return method

class Lambda(object):
    """docstring for Lambda."""

    def __init__(self, f=lambda x, state: (x, state)):
        self._f = f

    def __unit__(self, f, _return_type=None):
        "Monadic unit, also known as `return`"
        if _return_type:
            return _return_type(f)
        else:
            return self.__class__(f)

    def __then__(self, other, **kwargs):
        f = self._f
        g = other

        h = lambda x, state: g(*f(x, state))

        return self.__unit__(h, **kwargs)

    ## Override operators
    def __call__(self, __x__, *__return_state__, **state):
        x = __x__
        return_state = __return_state__

        if len(return_state) == 1 and type(return_state[0]) is not bool:
            raise Exception("Invalid return state condition, got {return_state}".format(return_state=return_state))

        with _StateContextManager(state):
            y, next_state = self._f(x, state)

        return (y, next_state) if len(return_state) >= 1 and return_state[0] else y




    def __getitem__(self, key):
        f = utils.lift(lambda x: x[key])
        return self.__then__(f)


    def __rrshift__(self, prev):

        if hasattr(prev, '__call__'):
            if not isinstance(prev, Lambda):
                prev = self.__class__(utils.lift(prev))

            return prev.__then__(self._f)
        else: #apply
            return self(prev)

    def __rshift__(self, other):
        if hasattr(other, '__call__'):
            if not isinstance(other, Lambda):
                other = self.__class__(utils.lift(other))

            return self.__then__(other._f)
        else: #apply
            return self(other)

    __rlshift__ = __rshift__
    __lshift__ = __rrshift__



    __add__ = _fmap(operator.add)
    __mul__ = _fmap(operator.mul)
    __sub__ = _fmap(operator.sub)
    __mod__ = _fmap(operator.mod)
    __pow__ = _fmap(operator.pow)

    __and__ = _fmap(operator.and_)
    __or__ = _fmap(operator.or_)
    __xor__ = _fmap(operator.xor)

    __div__ = _fmap(operator.truediv)
    __divmod__ = _fmap(divmod)
    __floordiv__ = _fmap(operator.floordiv)
    __truediv__ = _fmap(operator.truediv)

    __contains__ = _fmap(operator.contains)

    __lt__ = _fmap(operator.lt)
    __le__ = _fmap(operator.le)
    __gt__ = _fmap(operator.gt)
    __ge__ = _fmap(operator.ge)
    __eq__ = _fmap(operator.eq)
    __ne__ = _fmap(operator.ne)

    __neg__ = _unary_fmap(operator.neg)
    __pos__ = _unary_fmap(operator.pos)
    __invert__ = _unary_fmap(operator.invert)

    __radd__ = _fmap_flip(operator.add)
    __rmul__ = _fmap_flip(operator.mul)
    __rsub__ = _fmap_flip(operator.sub)
    __rmod__ = _fmap_flip(operator.mod)
    __rpow__ = _fmap_flip(operator.pow)
    __rdiv__ = _fmap_flip(operator.truediv)
    __rdivmod__ = _fmap_flip(divmod)
    __rtruediv__ = _fmap_flip(operator.truediv)
    __rfloordiv__ = _fmap_flip(operator.floordiv)

    __rand__ = _fmap_flip(operator.and_)
    __ror__ = _fmap_flip(operator.or_)
    __rxor__ = _fmap_flip(operator.xor)

CALL_COUNT = 0


###############################

class _RefProxy(object):
    """docstring for _ReadProxy."""

    def __getattr__(self, name):
        return _StateContextManager.REFS[name]

    def __getitem__(self, name):
        return _StateContextManager.REFS[name]

    def __call__(self, *args, **kwargs):
        return Ref(*args, **kwargs)

_RefProxyInstance = _RefProxy()

class _StateContextManager(object):

    REFS = None

    def __init__(self, next_refs):
        self.previous_refs = _StateContextManager.REFS
        self.next_refs = next_refs

    def __enter__(self):
        _StateContextManager.REFS = self.next_refs

    def __exit__(self, *args):
        _StateContextManager.REFS = self.previous_refs


class Ref(object):
    """
Returns an object that helps you to inmediatly create and [read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read) [references](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Ref).

**Creating Refences**

You can manually create a [Ref](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Ref) outside the DSL using `Ref` and then pass to as/to a `phi.dsl.Expression.Read` or `phi.dsl.Expression.Write` expression. Here is a contrived example

from phi import P, Ref

r = Ref('r')

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

    def write(self, x):
        """
Sets the value of the reference equal to the input argument `x`. Its also an identity function since it returns `x`.
        """
        self.value = x

        return x
