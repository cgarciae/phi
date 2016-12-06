"""
# Lambdas
The `phi.P` global object is of type `Builder` which follows the following class hierarchy

    Builder < Lambda < Function < Node

where `dsl.Node` is the base class for any object in the DSL and `dsl.Function` is the class that wraps functions, which are the leaf/terminal elements that actually excecute the user's functions. In this scheme `Lambda` is a class which has a very specific purpose: enable you to create quick lambdas. `Lambda` takes code from [fn.py](https://github.com/fnpy/fn.py)'s `_` (underscore)
"""

import dsl
import utils
import operator

def _fmap(opt):
    def method(self, b):
        if type(b) is not dsl.Node and not hasattr(b, '__call__'):
            b = dsl.Input(b)

        code = (
            [ self, b ],
            lambda args: opt(*args)
        )

        f, refs = dsl.Compile(code, {})

        return self.__unit__(f, refs)

    return method

def _fmap_flip(opt):
    def method(self, b):
        if type(b) is not dsl.Node and not hasattr(b, '__call__'):
            b = dsl.Input(b)

        code = (
            [ b, self ],
            lambda args: opt(*args)
        )

        f, refs = dsl.Compile(code, {})

        return self.__unit__(f, refs)

    return method

def _unary_fmap(opt):
    def method(self):
        return self.__then__(opt)

    return method

class Lambda(dsl.Function):
    """docstring for Lambda."""

    def __init__(self, f, refs):
        super(Lambda, self).__init__(f)
        self._f = f
        self._refs = refs

    def __unit__(self, f, refs, _return_type=None):
        "Monadic unit, also known as `return`"
        if _return_type:
            return _return_type(f, refs)
        else:
            return self.__class__(f, refs)

    def __call__(self, x, flatten=False):
        y = self._f(x)
        return utils.flatten_list(y) if flatten else y

    def __then__(self, other, **kwargs):
        code = (self, other)
        f, refs = dsl.Compile(code, {})

        return self.__unit__(f, refs, **kwargs)


    def __getitem__(self, key):
        f = lambda x: x[key]
        return self.__then__(f)


    def __rrshift__(self, prev):

        if type(prev) is dsl.Node or hasattr(prev, '__call__'):
            code = (prev, self)
            f, refs = dsl.Compile(code, {})
            return self.__unit__(f, refs)
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

    # __lshift__ = _fmap(operator.lshift)
    # __rshift__ = _fmap(operator.rshift)

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

    # __rlshift__ = _fmap_flip(operator.lshift)
    # __rrshift__ = _fmap_flip(operator.rshift)

    __rand__ = _fmap_flip(operator.and_)
    __ror__ = _fmap_flip(operator.or_)
    __rxor__ = _fmap_flip(operator.xor)


__all__ = []