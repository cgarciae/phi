"""
# Lambdas
Phi's `Lambda` class allows you to create quick lambdas that are much more readable and compact than Python's `lambda` keyword. You probably will not use an object of type `Lambda` directly but rather one of type `Builder` or type derived from `Builder`. These types have the following hierarchy

    Builder < Lambda < Function < Node

where `dsl.Node` is the base class for any object in the DSL and `dsl.Function` is the class that wraps functions. In this scheme `Lambda` is a class which has a very specific purpose: enable you to create quick lambdas and integrate the `Builder` class with the DSL. The main way in which you will use `Lambda`'s capabilities with be through the `phi.P` which implements the `Builder` class.

## Operations
`Lambda` overrides all operators plus the `__getitem__` and `__call__` special methods. Using operator overloading you can do things like

    form phi import P

    f = (P * 2) / (P + 1)

    assert f(1) == 1  #( 1 * 2 ) / ( 1 + 1) == 2 / 2 == 1

the previous expression for `f` is equivalent to

    f(x) = (x * 2) / (x + 1)

As you see, it creates very math-like functions that are very readable. The overloading mechanism has the following rules:

Let `g` be a Lambda, `h` a callable or Node, and `$` any python operator, then

    f = g $ h

is equivalent to

    f(x) = g(x) $ h(x)

Naturally `a $ b` returns also returns Lambda so operations can be chained. When `b` is not a callable or Node (as `1` in `P + 1`) then the expression

    a $ b

is reinterpreted as this so it does what you expect

    a $ Input(b)

where `Input` derives from `Node`. For more information see [dsl](https://cgarciae.github.io/phi/dsl.m.html). Also, reverse methods like `__radd__` (reverse for `__add__`) are also implemented so that expressions like `1 + P` -where `1` is not a Lambda- work as expected.


## __call__
Lambda implements the `__call__` special method so you can naturally use them as functions.

## __getitem__
The special method `__getitem__` is also implemented and enables you to define a lambda uses pythons access mechanism on its argument. The expression

    P[x]

is equivalent to

    lambda obj: obj[x]

### Examples
Add the first and last element of a list

    from phi import P

    f = P[0] + P[-1]

    assert f([1, 2, 3, 4]) == 5  #1 + 4 == 5

## `>>`
The special method `__rshift__` (right shift) needed to overload `>>` is implemented differently than the other methods in that

    f = g >> h

is NOT equivalent to

    f(x) = g(x) >> h(x)

Instead it represents Composition from the [dsl](https://cgarciae.github.io/phi/dsl.m.html) or function application depending on the context

### Composition
The expression

    g >> h

is equivalent to the expression

    (g, h)

which is equivalent to

    lambda x: h(g(x))

Note that atleast one of `g` or `h` has to be a `Lambda` for this operator to work. An easy way create a Lambda from any function `f` is to do

    P.Make(f)

### Application
Given `a` and `g` where

* `a` is not an instance of `dsl.Node` and is not a callable
* `g` is an instance of `Lambda`

then the expresion

    a >> g

is equivalent to

    g(a)

## <<
The special method `__lshift__` (left shift) behaves as a reversed form of `>>` in the sense that the order of operations on excecution is done backwards

### Composition Comparison

* `f >> g` is equivalent to `lambda x: g(f(x))`. `f` is executed first then `g`. Reads left to right.
* `f << g` is equivalent to `lambda x: f(g(x))`. `g` is executed first then `f`. Reads right to left.

### Application
Given `a` and `g` where

* `a` is not an instance of `dsl.Node` and is not a callable
* `g` is an instance of `Lambda`

then

    g << a

is equivalent to

    g(a)

## fn.py
The `Lambda` class takes much of its inspiration and code from [fn.py](https://github.com/fnpy/fn.py)'s '`_`' object, however it differs from it in the following aspects:

* It implements `dsl.Function` to better integrate with the DSL
* It only creates functions of arity 1 to comply with the DSL. Where in fn.py expressions like `_ + _` are equivalent to `lambda a, b: a + b`, phi's lambdas intepret `P + P` as `lambda a: a + a`. In the context of the DSL this is incredibly useful since it allows you to write expressions like `P[0] + P[1]` (equivalent to `lambda a: a[0] + a[1]`) to add the first two elements of e.g. a previous branched computation, in fn.py `_[0] + _[1]` is equivalent to `lambda a, b: a[0] + b[1]`.
* The operators `>>` and `<<` are used for function composition or application.

"""

import dsl
import utils
import operator

def _fmap(opt):
    def method(self, b):

        other = (lambda _: b) if not hasattr(b, '__call__') else b

        if not isinstance(other, Lambda):
            other = self.__class__(other)

        f = lambda x: opt( self(x), other(x) )


        return self.__unit__(f)

    return method

def _fmap_flip(opt):
    def method(self, b):

        other = (lambda _: b) if not hasattr(b, '__call__') else b

        if not isinstance(other, Lambda):
            other = self.__class__(other)

        f = lambda x: opt( other(x), self(x) )


        return self.__unit__(f)

    return method

def _unary_fmap(opt):
    def method(self):
        return self.__then__(opt)

    return method

class Lambda(dsl.Function):
    """docstring for Lambda."""

    def __init__(self, f):
        super(Lambda, self).__init__(f)
        self._f = f

    def __unit__(self, f, _return_type=None):
        "Monadic unit, also known as `return`"
        if _return_type:
            return _return_type(f)
        else:
            return self.__class__(f)

    def __then__(self, other, **kwargs):

        f = utils.forward_compose2(self, other)

        return self.__unit__(f, **kwargs)

    ## Override operators
    def __call__(self, x, flatten=False):
        y = self._f(x)
        return utils.flatten_list(y) if flatten else y


    def __getitem__(self, key):
        f = lambda x: x[key]
        return self.__then__(f)


    def __rrshift__(self, prev):

        if hasattr(prev, '__call__'):
            if not isinstance(prev, Lambda):
                prev = self.__class__(prev)

            return prev.__then__(self)
        else: #apply
            return self(prev)

    __rlshift__ = __rshift__ = __then__
    __lshift__ = __rrshift__



    __add__ = _fmap(operator.add)
    __mul__ = _fmap(operator.mul)
    __sub__ = _fmap(operator.sub)
    __mod__ = _fmap(operator.mod)
    __pow__ = _fmap(operator.pow)

    __and__ = _fmap(operator.and_)
    __or__ = _fmap(operator.or_)
    __xor__ = _fmap(operator.xor)

    __div__ = _fmap(operator.div)
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
    __rdiv__ = _fmap_flip(operator.div)
    __rdivmod__ = _fmap_flip(divmod)
    __rtruediv__ = _fmap_flip(operator.truediv)
    __rfloordiv__ = _fmap_flip(operator.floordiv)

    __rand__ = _fmap_flip(operator.and_)
    __ror__ = _fmap_flip(operator.or_)
    __rxor__ = _fmap_flip(operator.xor)

