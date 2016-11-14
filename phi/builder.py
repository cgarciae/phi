import inspect
import utils
from utils import identity
import functools
import dsl

#######################
### Applicative
#######################

class Builder(dsl.Function):
    """
    An [Applicative](http://learnyouahaskell.com/functors-applicative-functors-and-monoids) is an object who wraps around a function and posses the means to apply it.

    The `Applicative` class contains a inner field `f` that must be a function, internal methods rely on this fact to give you the nice syntax of the DSL. The `Applicative` class is also a function, meaning it implements the `__call__` method, which very simply delegates the computation to the function it contains.

    > **Note:** The `tb` object with is contains the whole TensorBuilder API is an Applicative itself, it contians the identity function.

    **DSL**

    Check out the description of the DSL [here](https://cgarciae.gitbooks.io/phi/content/dsl/).

    **Properties**

    Many methods registered/patched by TensorBuilder onto `Applicative` actually use `phi.core.applicative.Applicative.compose` internally, therefore, an expression of the DSL like this

        (tb.softmax(),
        tb.dropout(keep_prob),
        tb.relu_layer(10)) # Notice the begging and ending '()' tuple parenthesis

    is equivalent to this

        tb.softmax()
        .dropout(keep_prob),
        .relu_layer(10)


    """

    def __init__(self, f=identity, refs={}):
        super(Builder, self).__init__(f)
        self.f = f
        self.refs = refs


    def _unit(self, f, refs, _return_type=None):
        "Monadic unit, also known as `return`"
        if _return_type:
            return _return_type(f, refs)
        else:
            return self.__class__(f, refs)

    def __call__(self, x):
        return self.f(x)

    @classmethod
    def Scope(cls):
        return dsl.Scope.GLOBAL_SCOPE

    def _0(self, g, *args, **kwargs):
        """
        Takes in a function `g` and composes it with `phi.core.Applicative.f` as `g o f`. All \*args and \*\* are forwarded to g. This is an essential method since most registered methods use this.

        **Arguments**

        * `g`: A function
        * All \*args and \*\* are forwarded to `g`

        **Return**

        Applicative

        **Examples**

            import tensorflow as tf
            from phi import tb


        """
        _return_type = None

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']

        return self._unit(lambda x: g(*args, **kwargs), self.refs, _return_type=_return_type)

    def _(self, *code, **kwargs):
        _return_type = None

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']

        g, refs = dsl.Compile(code, self.refs)
        h = utils.compose2(g, self)

        return self._unit(h, refs, _return_type=_return_type)

    def _1(self, g, *args, **kwargs):
        """
        Takes in a function `g` and composes it with `phi.core.Applicative.f` as `g o f`. All \*args and \*\* are forwarded to g. This is an essential method since most registered methods use this.

        **Arguments**

        * `g`: A function
        * All \*args and \*\* are forwarded to `g`

        **Return**

        Applicative

        **Examples**

            import tensorflow as tf
            from phi import tb


        """
        _return_type = None

        if '_return_type' in kwargs:
            _return_type = kwargs['_return_type']
            del kwargs['_return_type']

        return self._unit(lambda x: g(self(x), *args, **kwargs), self.refs, _return_type=_return_type)

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

        return self._unit(_lambda, self.refs, _return_type=_return_type)

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

        return self._unit(_lambda, self.refs, _return_type=_return_type)

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

        return self._unit(_lambda, self.refs, _return_type=_return_type)

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

        return self._unit(_lambda, self.refs, _return_type=_return_type)


    def val(self, x):
        """
        """
        return self._1(lambda _: x)

    def run(self):
        return self(None)

    def on(self, ref):

        if type(ref) is str:
            ref = dsl.Ref(ref)

        if ref.name not in self.refs:
            refs = dict(self.refs, **{ref.name: ref})
        else:
            refs = self.refs

        return self._unit(utils.compose2(ref.set, self), refs)

    def ref(self, name):
        return dsl.Ref(name)

    def identity(self, x):
        return x

    def __rrshift__(self, x):
        return self(x)

    @classmethod
    def pipe(cls, x, *code, **kwargs):
        """
        `pipe` takes in a `builder` of type `Builder`, `BuilderTree` or `Object` preferably and an object `code` which must be part of the domain of the DSL, and compiles `code` to a function of type `Builder -> Builder` and applies it to the input `builder`. All \*args after `builder` are taken as a tuple, therefore, it makes it easier to define an initial tuple `()` element to define a sequential operation.

        **Arguments**

        * `builder`: a `Builder`, `BuilderTree` or `Object` preferably.
        * `*code`: a sequence of elements of the DSL.

        **Return**

        An object with the result of the computation, probable types: `Object | Builder | BuilderTree | list(Object) |  `

        **Examples**

            import tensorflow as tf
            from phi import tb

            x = placeholder(tf.float32, shape=[None, 10])

            h = tb.pipe(
                x,
                [
                    { tf.device("/gpu:0"):
                        tb.relu_layer(20)
                    }
                ,
                    { tf.device("/gpu:1"):
                        tb.sigmoid_layer(20)
                    }
                ,
                    { tf.device("/cpu:0"):
                        tb.tanh_layer(20)
                    }
                ],
                tb.relu_layer(10)
                .object()
            )
        """

        builder = cls.compile(*code, **kwargs)

        return builder(x)

    @classmethod
    def compile(cls, *code, **kwargs):
        """
        `compile` an object `code` which must be part of the domain of the DSL and returns function. It applies the rules of the DSL to create an actual Python function that does what you intend. Normally you will just use pipe, which not only compiles the DSL it actually performs the computation to a given Object/Builder, however, it you are building and API this might be useful since you can create a function from an AST which can itself be used as an element of another AST since final elements of the DSL are functions.

        **Arguments**

        * `*code`: a sequence of elements of the DSL.

        **Return**

        A function

        **Examples**

            import tensorflow as tf
            from phi import tb

            x = placeholder(tf.float32, shape=[None, 10])

            f = tb.compile(
                tb.build, #accept a Object as a parameter and create a builder so you can use the rest of the methods
                [
                    { tf.device("/gpu:0"):
                        tb.relu_layer(20)
                    }
                ,
                    { tf.device("/gpu:1"):
                        tb.sigmoid_layer(20)
                    }
                ,
                    { tf.device("/cpu:0"):
                        tb.tanh_layer(20)
                    }
                ],
                tb.relu_layer(10)
                .object()
            )

            h = f(x)

        """
        return cls()._(*code, **kwargs)


    @classmethod
    def register_as_method(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation=""):
        """
        This method enables you to register any function `fn` that takes an Applicative as its first argument as a method of the Builder class.

        **Arguments**

        * `fn`: a function that atleast takes an Applicative as its first argument.
        * `library_path`: the route of the librar from which this function was taken, used for documentation purposes.
        * `alias`: allows you to specify the name of the method, it will take the name of the function if its `None`.
        * `doc`: the documentation for the method, if `None` a predefied documentation will be generated based on the documentation of `fn`.

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

        This method accepts the same arguments as `{3}.{0}`. """ + explanation + """

        ** Documentation from `{3}.{0}`**

            {2}
        """).format(original_name, name, fn_docs, library_path)

        if name in cls.__core__:
            raise Exception("Can't add method '{0}' because its on __core__".format(name))

        setattr(cls, name, fn)

    @classmethod
    def register_method(self, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation=""):
        def register_decorator(fn):

            self.register_as_method(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation)

            return fn
        return register_decorator


    @classmethod
    def register_function0(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        """
        This method enables you to register any function `fn` that takes an object as its first argument as a method of the Builder and Applicative class.

        **Arguments**

        * `fn`: a function that atleast takes an Object as its first argument.
        * `library_path`: the route of the librar from which this function was taken, used for documentation purposes.
        * `alias`: allows you to specify the name of the method, it will take the name of the function if its `None`.
        * `doc`: the documentation for the method, if `None` a predefied documentation will be generated based on the documentation of `fn`.

        **Return**

        `None`

        **Examples**

        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._0(fn, *args, **kwargs)

        explanation = """However, a partial with the arguments is returned which expects any argument `x` such that

            {3}.{0}(*args, **kwargs) <==> builder.{1}(*args, **kwargs)(x)

        """ + explanation

        cls.register_as_method(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation)

    @classmethod
    def register_function_1(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        """
        This method enables you to register any function `fn` that takes an object as its first argument as a method of the Builder and Applicative class.

        **Arguments**

        * `fn`: a function that atleast takes an Object as its first argument.
        * `library_path`: the route of the librar from which this function was taken, used for documentation purposes.
        * `alias`: allows you to specify the name of the method, it will take the name of the function if its `None`.
        * `doc`: the documentation for the method, if `None` a predefied documentation will be generated based on the documentation of `fn`.

        **Return**

        `None`

        **Examples**

        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._1(fn, *args, **kwargs)

        explanation = """However, the 1st argument is omitted, a partial with the rest of the arguments is returned which expects the 1st argument such that

            {3}.{0}(x1, *args, **kwargs) <==> builder.{1}(*args, **kwargs)(x1)

        """ + explanation

        cls.register_as_method(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation)


    @classmethod
    def register_function_2(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._2(fn, *args, **kwargs)

        explanation = """However, the 2nd argument is omitted, a partial with the rest of the arguments is returned which expects the 2nd argument such that

            {3}.{0}(x1, x2, *args, **kwargs) <==> builder.{1}(x1, *args, **kwargs)(x2)
        """ + explanation

        cls.register_as_method(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation)

    @classmethod
    def register_function_3(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._3(fn, *args, **kwargs)

        explanation = """However, the 3rd argument is omitted, a partial with the rest of the arguments is returned which expects the 3rd argument such that

            {3}.{0}(x1, x2, x3, *args, **kwargs) <==> builder.{1}(x1, x2, *args, **kwargs)(x3)
        """ + explanation

        cls.register_as_method(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation)

    @classmethod
    def register_function_4(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._4(fn, *args, **kwargs)

        explanation = """However, the 4th argument is omitted, a partial with the rest of the arguments is returned which expects the 4th argument such that

            {3}.{0}(x1, x2, x3, x4, *args, **kwargs) <==> builder.{1}(x1, x2, x3, *args, **kwargs)(x4)
        """ + explanation

        cls.register_as_method(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation)

    @classmethod
    def register_function_5(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._5(fn, *args, **kwargs)

        explanation = """However, the 5th argument is omitted, a partial with the rest of the arguments is returned which expects the 5th argument such that

            {3}.{0}(x1, x2, x3, x4, x5, *args, **kwargs) <==> builder.{1}(x1, x2, x3, x4, *args, **kwargs)(x5)
        """ + explanation

        cls.register_as_method(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, _return_type=_return_type)

    @classmethod
    def register_1(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        def register_decorator(fn):
            cls.register_function_1(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def register_2(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        def register_decorator(fn):
            cls.register_function_2(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def register_3(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        def register_decorator(fn):
            cls.register_function_3(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def register_4(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        def register_decorator(fn):
            cls.register_function_4(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def register_5(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", _return_type=None):
        def register_decorator(fn):
            cls.register_function_5(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, _return_type=_return_type)
            return fn
        return register_decorator



Builder.__core__ = [ name for name, f in inspect.getmembers(Builder, inspect.ismethod) ]
