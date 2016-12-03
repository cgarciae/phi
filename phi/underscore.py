import dsl
import utils
import operator

def fMap(opt):
    def method(self, b):
        return self.__then__(lambda a: opt(a, b))

    return method

def fMap_flip(opt):
    def method(self, b):
        return self.__then__(lambda a: opt(b, a))

    return method

def unary_fMap(opt):
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

    def __then__(self, other):
        code = (self, other)
        f, refs = dsl.Compile(code, {})

        return self.__unit__(f, refs)

    def __rrshift__(self, x):
        print ""
        if type(x) is dsl.Node or hasattr(x, '__call__'):
            print x, "RRSHIFT COMPOSE"
            return self.__then__(x)
        else: #apply
            print x, "RRSHIFT APPLY"
            return self(x)

    __rshift__ = __then__
    __getitem__ = fMap(operator.itemgetter)
    __add__ = fMap(operator.add)
    __mul__ = fMap(operator.mul)
    __sub__ = fMap(operator.sub)
    __mod__ = fMap(operator.mod)
    __pow__ = fMap(operator.pow)

    __and__ = fMap(operator.and_)
    __or__ = fMap(operator.or_)
    __xor__ = fMap(operator.xor)

    __div__ = fMap(operator.div)
    __divmod__ = fMap(divmod)
    __floordiv__ = fMap(operator.floordiv)
    __truediv__ = fMap(operator.truediv)

    __contains__ = fMap(operator.contains)

    # __lshift__ = fMap(operator.lshift)
    # __rshift__ = fMap(operator.rshift)

    __lt__ = fMap(operator.lt)
    __le__ = fMap(operator.le)
    __gt__ = fMap(operator.gt)
    __ge__ = fMap(operator.ge)
    __eq__ = fMap(operator.eq)
    __ne__ = fMap(operator.ne)

    __neg__ = unary_fMap(operator.neg)
    __pos__ = unary_fMap(operator.pos)
    __invert__ = unary_fMap(operator.invert)

    __radd__ = fMap_flip(operator.add)
    __rmul__ = fMap_flip(operator.mul)
    __rsub__ = fMap_flip(operator.sub)
    __rmod__ = fMap_flip(operator.mod)
    __rpow__ = fMap_flip(operator.pow)
    __rdiv__ = fMap_flip(operator.div)
    __rdivmod__ = fMap_flip(divmod)
    __rtruediv__ = fMap_flip(operator.truediv)
    __rfloordiv__ = fMap_flip(operator.floordiv)

    # __rlshift__ = fMap_flip(operator.lshift)
    # __rrshift__ = fMap_flip(operator.rshift)

    __rand__ = fMap_flip(operator.and_)
    __ror__ = fMap_flip(operator.or_)
    __rxor__ = fMap_flip(operator.xor)


class Underscore(Lambda):
    """docstring for Underscore."""

    def __getattr__(self, name):

        def method_proxy(*args, **kwargs):
            def f(x):
                method = getattr(x, name)
                return method(*args, **kwargs)

            return self.__then__(f)

        return method_proxy



underscore = Underscore(utils.identity, {})
