import dsl
import utils
import operator

def fmap(opt):
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

def fmap_flip(opt):
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

def unary_fmap(opt):
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



    __add__ = fmap(operator.add)
    __mul__ = fmap(operator.mul)
    __sub__ = fmap(operator.sub)
    __mod__ = fmap(operator.mod)
    __pow__ = fmap(operator.pow)

    __and__ = fmap(operator.and_)
    __or__ = fmap(operator.or_)
    __xor__ = fmap(operator.xor)

    __div__ = fmap(operator.div)
    __divmod__ = fmap(divmod)
    __floordiv__ = fmap(operator.floordiv)
    __truediv__ = fmap(operator.truediv)

    __contains__ = fmap(operator.contains)

    # __lshift__ = fmap(operator.lshift)
    # __rshift__ = fmap(operator.rshift)

    __lt__ = fmap(operator.lt)
    __le__ = fmap(operator.le)
    __gt__ = fmap(operator.gt)
    __ge__ = fmap(operator.ge)
    __eq__ = fmap(operator.eq)
    __ne__ = fmap(operator.ne)

    __neg__ = unary_fmap(operator.neg)
    __pos__ = unary_fmap(operator.pos)
    __invert__ = unary_fmap(operator.invert)

    __radd__ = fmap_flip(operator.add)
    __rmul__ = fmap_flip(operator.mul)
    __rsub__ = fmap_flip(operator.sub)
    __rmod__ = fmap_flip(operator.mod)
    __rpow__ = fmap_flip(operator.pow)
    __rdiv__ = fmap_flip(operator.div)
    __rdivmod__ = fmap_flip(divmod)
    __rtruediv__ = fmap_flip(operator.truediv)
    __rfloordiv__ = fmap_flip(operator.floordiv)

    # __rlshift__ = fmap_flip(operator.lshift)
    # __rrshift__ = fmap_flip(operator.rshift)

    __rand__ = fmap_flip(operator.and_)
    __ror__ = fmap_flip(operator.or_)
    __rxor__ = fmap_flip(operator.xor)
