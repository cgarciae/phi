from builder import Builder
from fn import underscore as us


class RecordProxy(object):
    """docstring for RecClass."""

    def __getattr__ (self, attr):
        f = lambda x: getattr(x, attr)
        return Builder(f, {})

    def __getitem__(self, item):
        f = lambda x: x[item]
        return Builder(f, {})


class ObjectProxy(us._Callable):
    """docstring for RecClass."""

    # def __getattr__ (self, attr):
    #
    #     def method_proxy(*args, **kwargs):
    #         def f(x):
    #             method = getattr(x, attr)
    #             return method(*args, **kwargs)
    #         return Builder(f)
    #
    #     return method_proxy

    def __getattr__(self, name):
        attr_name = us._random_name()

        def method_proxy(*args, **kwargs):
            def f(x):
                method = getattr(x, name)
                return method(*args, **kwargs)

            return self.__class__(
                us.F(f) << us.F(self),
                "getattr(%s, %%(%s)r)" % (self._format, attr_name),
                dict(
                    list(self._format_args.items()) + [(attr_name, name)]
                ),
                self._arity
            )

        return method_proxy



    def contains(self, *args, **kwargs):
        def f(x):
            if hasattr(x, 'contains'):
                return x.contains(*args, **kwargs)
            else:
                return x.__contains__(*args, **kwargs)

        return Builder(f, {})



######################
# Objects
######################
Rec = Builder.Rec = RecordProxy()
Obj = Builder.Obj = ObjectProxy()
