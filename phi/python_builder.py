from builder import Builder
import utils
import inspect

class PythonBuilder(Builder):
    """
Methods that start with a lowercase letter are most probably core python functions automatically as methods (e.g. `phi.builder.Builder.map` or `phi.builder.Builder.sum`). There is a third batch of methods that like `phi.builder.Builder.And`, `phi.builder.Builder.Not`, `phi.builder.Builder.Contains`, etc, that are not considered core `Builder` methods but are packaged with this class for conveniece, initially they where capitalized because they mimimic keywords (`and`, `or`, `not`, etc) and its ilegal to give them these lowercase names, however, methods like `phi.builder.Builder.Contains` that could use lowercase are left capitalized to maintain uniformity.
    """


# built in functions
function_2_names = ["map", "filter", "reduce"]
functions_2 = [ (name, f) for name, f in __builtins__.items() if name in function_2_names ]

for name, f in __builtins__.items():
    try:
        if hasattr(f, "__name__") and name[0] is not "_" and not name[0].isupper() and name not in function_2_names:
            PythonBuilder.RegisterFunction1(f, "python", alias=name)
    except Exception as e:
        print(e)

for name, f in functions_2:
    PythonBuilder.RegisterFunction2(f, "python")

#custom methods
@PythonBuilder.Register1("python", explain=False)
def Not(x): return not x

@PythonBuilder.Register1("python")
def Contains(x, y): return y in x

@PythonBuilder.Register1("python")
def In(x, y): return x in y

@PythonBuilder.Register1("python", explain=False)
def And(x, y): return x and y

@PythonBuilder.Register1("python")
def Or(x, y): return x or y

@PythonBuilder.Register1("python")
def First(x): next(iter(x))

@PythonBuilder.Register1("python")
def Last(x): list(x)[-1]


# __all__ = ["PythonBuilder"]
