from builder import Builder

#############################
## Shortcuts
#############################
def val(x):
    return Builder().val(x)

def on(ref):
    return Builder().on(ref)

def C(*args, **kwargs):
    return Builder().C(*args, **kwargs)

def _0(*args, **kwargs):
    return Builder()._0(*args, **kwargs)

def _1(*args, **kwargs):
    return Builder()._1(*args, **kwargs)

def _2(*args, **kwargs):
    return Builder()._2(*args, **kwargs)

def _3(*args, **kwargs):
    return Builder()._3(*args, **kwargs)

def _4(*args, **kwargs):
    return Builder()._4(*args, **kwargs)

def _5(*args, **kwargs):
    return Builder()._5(*args, **kwargs)
