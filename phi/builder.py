import inspect
import utils
from utils import identity
import functools
import dsl
from lambdas import Lambda
from special_objects import ObjectProxy, RecordProxy

#######################
### Applicative
#######################

class Builder(Lambda):
    """
    An [Applicative](http://learnyouahaskell.com/functors-applicative-functors-and-monoids) is an object who wraps around a function and posses the means to apply it.

    The `Applicative` class contains a inner field `f` that must be a function, internal methods rely On this fact to give you the nice syntax of the DSL. The `Applicative` class is also a function, meaning it implements the `__call__` method, which very simply delegates the computation to the function it contains.

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

    # def __rrshift__(self, x):
    #     return self(x)

    @classmethod
    def Scope(cls):
        return dsl.With.GLOBAL_SCOPE

    def With(self, *args, **kwargs):
        w = dsl.With(*args, **kwargs)
        return self.__then__(w)

    def Pipe(self, x, *code, **kwargs):
        return self.Make(*code, **kwargs)(x)

    def Run(self, *code, **kwargs):
        return self.Pipe(None, *code, **kwargs)

    def Make(self, *code, **kwargs):
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

        return self.__unit__(lambda x: g(*args, **kwargs), self._refs, _return_type=_return_type)

    def _(self, g, *args, **kwargs):
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

        f = lambda x: g(x, *args, **kwargs)
        return self.__then__(f, _return_type=_return_type)

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
        return self._(lambda z: x)

    def On(self, ref):

        if type(ref) is str:
            ref = dsl.Ref(ref)

        if ref.name not in self._refs:
            refs = dict(self._refs, **{ref.name: ref})
        else:
            refs = self._refs

        return self.__unit__(utils.compose2(ref.set, self), refs)

    # def With(self, *args, **kwargs):
    #     code = (self, dsl.With(*args))
    #     f, refs = dsl.Compile(code, {})
    #     return self.__unit__(f, refs, **kwargs)

    def Ref(self, name):
        return dsl.Ref(name)

    @property
    def Obj(self):
        return ObjectProxy(self)

    @property
    def Rec(self):
        return RecordProxy(self)


    @classmethod
    def DoRegisterMethod(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity):
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

        This method accepts the same arguments as `{3}.{0}`. """ + explanation + """

        ** Documentation from `{3}.{0}`**

            {2}
        """).format(original_name, name, fn_docs, library_path)

        if name in cls.__core__:
            raise Exception("Can't add method '{0}' because its On __core__".format(name))

        fn = method_type(fn)
        setattr(cls, name, fn)

    @classmethod
    def RegisterMethod(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity):
        def register_decorator(fn):

            cls.DoRegisterMethod(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type)

            return fn
        return register_decorator


    @classmethod
    def RegisterFunction0(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
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
            return self._0(fn, *args, **kwargs)

        explanation = """However, a partial with the arguments is returned which expects any argument `x` such that

            {3}.{0}(*args, **kwargs) <==> builder.{1}(*args, **kwargs)(x)

        """ + explanation

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type)

    @classmethod
    def RegisterFunction1(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
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

        explanation = """However, the 1st argument is omitted, a partial with the rest of the arguments is returned which expects the 1st argument such that

            {3}.{0}(x1, *args, **kwargs) <==> builder.{1}(*args, **kwargs)(x1)

        """ + explanation

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type)


    @classmethod
    def RegisterFunction2(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._2(fn, *args, **kwargs)

        explanation = """However, the 2nd argument is omitted, a partial with the rest of the arguments is returned which expects the 2nd argument such that

            {3}.{0}(x1, x2, *args, **kwargs) <==> builder.{1}(x1, *args, **kwargs)(x2)
        """ + explanation

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type)

    @classmethod
    def RegisterFunction3(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._3(fn, *args, **kwargs)

        explanation = """However, the 3rd argument is omitted, a partial with the rest of the arguments is returned which expects the 3rd argument such that

            {3}.{0}(x1, x2, x3, *args, **kwargs) <==> builder.{1}(x1, x2, *args, **kwargs)(x3)
        """ + explanation

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type)

    @classmethod
    def RegisterFunction4(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._4(fn, *args, **kwargs)

        explanation = """However, the 4th argument is omitted, a partial with the rest of the arguments is returned which expects the 4th argument such that

            {3}.{0}(x1, x2, x3, x4, *args, **kwargs) <==> builder.{1}(x1, x2, x3, *args, **kwargs)(x4)
        """ + explanation

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type)

    @classmethod
    def RegisterFunction5(cls, fn, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
        """
        """
        @functools.wraps(fn)
        def method(self, *args, **kwargs):
            kwargs['_return_type'] = _return_type
            return self._5(fn, *args, **kwargs)

        explanation = """However, the 5th argument is omitted, a partial with the rest of the arguments is returned which expects the 5th argument such that

            {3}.{0}(x1, x2, x3, x4, x5, *args, **kwargs) <==> builder.{1}(x1, x2, x3, x4, *args, **kwargs)(x5)
        """ + explanation

        cls.DoRegisterMethod(method, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, _return_type=_return_type)

    @classmethod
    def Register0(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction0(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def Register1(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction1(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def Register2(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction2(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def Register3(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction3(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def Register4(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction4(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, _return_type=_return_type)
            return fn
        return register_decorator

    @classmethod
    def Register5(cls, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, _return_type=None):
        def register_decorator(fn):
            cls.RegisterFunction5(fn, library_path, alias=alias, original_name=original_name, doc=doc, wrapped=wrapped, explanation=explanation, method_type=method_type, _return_type=_return_type)
            return fn
        return register_decorator



Builder.__core__ = [ name for name, f in inspect.getmembers(Builder, inspect.ismethod) ]
