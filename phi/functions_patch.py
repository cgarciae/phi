from builder import Builder
import utils
import inspect


# built in functions
function_2_names = ["map", "filter", "reduce"]
functions_2 = [ (name, f) for name, f in __builtins__.items() if name in function_2_names ]

for name, f in __builtins__.items():
    try:
        if hasattr(f, "__name__") and name[0] is not "_" and name not in function_2_names:
            Builder.register_function_1(f, "python", alias=name)
    except Exception as e:
        print(e)

for name, f in functions_2:
    Builder.register_function_2(f, "python")


#custom methods
@Builder.register_1("python")
def Not(x): return not x

@Builder.register_1("python")
def And(x, y): return x and y

@Builder.register_1("python")
def Or(x, y): return x or y

@Builder.register_1("python")
def In(x, y): return x in y
