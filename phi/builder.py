"""
The `phi.builder.Builder` extends the [Expression](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Expression) class and adds methods that enable you to register external functions as methods. You should NOT register functions on the `Builder` or [PythonBuilder](https://cgarciae.github.io/phi/python_builder.m.html) classes, instead you should create a class of your own that extends these and register your functions there. The benefit of having this registration mechanism, instead of just implementing the methods yourself is that you can automate the process to register a collection of existing functions or methods.

**See**

* `phi.builder.Builder.RegisterMethod`
* `phi.builder.Builder.RegisterAt`
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

class Builder(dsl.Expression):
    """
    All the public methods of the `Builder`, `Expression` and `Expression` classes start with a capital letter on purpose to avoid name chashes with methods that you might register."""

    @classmethod
    def _RegisterMethod(cls, f, library_path, alias=None, original_name=None, doc=None, wrapped=None, explanation="", method_type=utils.identity, explain=True):
        if wrapped:
            f = functools.wraps(wrapped)(f)

        fn_signature = utils.get_method_sig(f)
        fn_docs = inspect.getdoc(f)
        name = alias if alias else f.__name__
        original_name = f.__name__ if wrapped else original_name if original_name else name

        f.__name__ = str(name)
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

        try:
            @functools.wraps(f)
            def method(self, *args, **kwargs):
                kwargs['_return_type'] = _return_type
                return self.ThenAt(n, f, *args, **kwargs)
        except:
            import ipdb
            ipdb.set_trace()

            _1 = 1
            
            raise

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
    def PatchAt(cls, n, module, module_alias=None, method_name_modifier=_None, blacklist_predicate=_False, whitelist_predicate=_True, return_type_predicate=_None, getmembers_predicate=inspect.isfunction, admit_private=False):
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
        patch_members = _get_patch_members(module, blacklist_predicate=blacklist_predicate, whitelist_predicate=whitelist_predicate, getmembers_predicate=getmembers_predicate, admit_private=admit_private)

        for name, f in patch_members:
            cls.RegisterAt(n, f, module_name, _return_type=return_type_predicate(f.__name__), alias=method_name_modifier(f.__name__))


Builder.__core__ = [ name for name, f in inspect.getmembers(Builder, inspect.ismethod) ]



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

def _get_patch_members(module, blacklist_predicate=_NoLeadingUnderscore, whitelist_predicate=_True, _return_type=None, getmembers_predicate=inspect.isfunction, admit_private=False):

    if type(whitelist_predicate) is list:
        whitelist = whitelist_predicate
        whitelist_predicate = lambda x: x in whitelist

    if type(blacklist_predicate) is list:
        blacklist = blacklist_predicate
        blacklist_predicate = lambda x: x in blacklist or '_' == x[0] if not admit_private else False

    return [
        (name, f) for (name, f) in inspect.getmembers(module, getmembers_predicate) if whitelist_predicate(name) and not blacklist_predicate(name)
    ]
