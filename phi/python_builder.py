"""
`PythonBuilder` helps you integrate Python's built-in functions and keywords into the DSL and it also includes a bunch of useful helpers for common stuff. `phi`'s global `P` object is an instance of this class.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from .builder import Builder
from . import utils
import inspect

class PythonBuilder(Builder):
    """
This class has two types of methods:

1. Methods that start with a lowercase letter are core python functions automatically registered as methods (e.g. `phi.python_builder.PythonBuilder.map` or `phi.python_builder.PythonBuilder.sum`).
2. Methods that start with a capytal letter like `phi.python_builder.PythonBuilder.And`, `phi.python_builder.PythonBuilder.Not`, `phi.python_builder.PythonBuilder.Contains`, this is done because some mimimic keywords (`and`, `or`, `not`, etc) and its ilegal to give them these lowercase names, however, methods like `phi.python_builder.PythonBuilder.Contains` that could use lowercase are left capitalized to maintain uniformity.
    """

P = PythonBuilder()

# built in functions
_function_2_names = ["map", "filter", "reduce"]
_functions_2 = [ (_name, f) for _name, f in __builtins__.items() if _name in _function_2_names ]

for _name, f in __builtins__.items():
    try:
        if hasattr(f, "__name__") and _name[0] is not "_" and not _name[0].isupper() and _name not in _function_2_names:
            PythonBuilder.Register(f, "", alias=_name)
    except Exception as e:
        print(e)

for _name, f in _functions_2:
    PythonBuilder.Register2(f, "")

#custom methods
@PythonBuilder.Register("phi.python_builder.", explain=False)
def Not(a):
    """
**Not**

    Not() <=> lambda a: not a

Returns a function that negates the input argument.

** Examples **

    from phi import P

    assert True == P.Pipe(
        1,
        P + 1,  # 1 + 1 == 2
        P > 5,  # 2 > 5 == False
        P.Not() # not False == True
    )

or shorter

    from phi import P

    assert True == P.Pipe(
        1,
        (P + 1 > 5).Not()  # not 1 + 1 > 5 == not 2 > 5 == not False == True
    )

or just

    from phi import P

    f = (P + 1 > 5).Not()

    assert f(1) == True
    """
    return not a

@PythonBuilder.Register("phi.python_builder.", explain=False)
def Contains(a, b):
    """
**Contains**

    Contains(b) <=> lambda a: b in a

Returns a partial function which when executed determines whether the argument partially applied is contained in the value being passed down.

** Examples **

    from phi import P

    assert False == P.Pipe(
        [1,2,3,4], P
        .filter(P % 2 != 0)   #[1, 3], keeps odds
        .Contains(4)   #4 in [1, 3] == False
    )
    """
    return b in a

@PythonBuilder.Register("phi.python_builder.", explain=False)
def In(a, b):
    """
**In**

    In(b) <=> lambda a: a in b

Returns a partial function which when executed determines whether the argument partially applied contains the value being passed down.

** Examples **

    from phi import P

    assert False == P.Pipe(
        3,
        P * 2,   #3 * 2 == 6
        P.In([1,2,3,4])   #6 in [1,2,3,4] == False
    )
    """
    return a in b

@PythonBuilder.Register("phi.python_builder.", explain=False)
def First(a):
    """
**First**

    First() <=> lambda a: a[0]

Returns a function which when executed returns the first element of the iterable being passed.

** Examples **

    from phi import P

    assert 3 == P.Pipe(
        range(1, 10), P  #[1, 2, ..., 8, 9]
        .filter(P % 3 == 0)   #[3, 6, 9]
        .First()   # [3, 6, 9][0] == 3
    )
    """
    return next(iter(a))

@PythonBuilder.Register("phi.python_builder.", explain=False)
def Last(a):
    """
**Last**

    Last() <=> lambda a: a[-1]

Returns a function which when executed returns the last element of the iterable being passed.

** Examples **

    from phi import P

    assert 3 == P.Pipe(
        range(1, 10), P  #[1, 2, ..., 8, 9]
        .filter(P % 3 == 0)   #[3, 6, 9]
        .Last()   # [3, 6, 9][-1] == 9
    )
    """
    return list(a)[-1]

@PythonBuilder.Register("phi.python_builder.", explain=False)
def Flatten(a):
    return utils.flatten(a)



__all__ = ["PythonBuilder"]
