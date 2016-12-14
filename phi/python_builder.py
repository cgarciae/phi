

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
    # import ipdb
    # ipdb.set_trace()  ######### Break Point ###########

    PythonBuilder.Register2(f, "")

#custom methods
@PythonBuilder.Register("phi.python_builder.", explain=False)
def Not(x):
    """
**Not**

    Not() <=> lambda x: not x

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
    return not x

@PythonBuilder.Register("phi.python_builder.", explain=False)
def Contains(x, y): return y in x

@PythonBuilder.Register("phi.python_builder.", explain=False)
def In(x, y): return x in y

@PythonBuilder.Register("phi.python_builder.", explain=False)
def And(x, y): return x and y

@PythonBuilder.Register("phi.python_builder.", explain=False)
def Or(x, y): return x or y

@PythonBuilder.Register("phi.python_builder.", explain=False)
def First(x): return next(iter(x))

@PythonBuilder.Register("phi.python_builder.", explain=False)
def Last(x): return list(x)[-1]


__all__ = ["PythonBuilder"]
