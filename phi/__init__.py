from builder import Builder
from method_builder import MethodBuilder
from fn import _

#############################
## Shortcuts
#############################
def val(x):
    return Builder().val(x)

def on(ref):
    return Builder().on(ref)

def C(*args, **kwargs):
    return Builder().compile(*args, **kwargs)

def P(*args, **kwargs):
    return Builder.pipe(*args, **kwargs)

M = MethodBuilder()

def _0(*args, **kwargs):
    return Builder()._0(*args, **kwargs)

def _1(*args, **kwargs):
    return Builder()._1(*args, **kwargs)

def _2(*args, **kwargs):
    return Builder()._2(*args, **kwargs)

def _3(*args, **kwargs):
    return Builder()._3(*args, **kwargs)
