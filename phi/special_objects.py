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
