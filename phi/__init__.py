from builder import Builder
import utils
import dsl
from dsl import With
from special_objects import Obj, Rec
from underscore import underscore as _

#patches
import functions_patch

ph = Builder(utils.identity, {})

# shortcuts
_0 = ph._0
Map = ph.Map
Map2 = ph.Map2
Map3 = ph.Map3
Map4 = ph.Map4
Map5 = ph.Map5
on = ph.on
Val = ph.Val
Pipe = ph.Pipe
Compile = ph.Compile

########################
# Documentation
########################
import os
import sys

#pdoc
__all__ = ["tensordata", "dsl", "builder"]

#set documentation
def _read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

module = sys.modules[__name__]
raw_docs = _read("README-template.md")
__version__ = _read("version.txt")
module.__doc__ = raw_docs.format(__version__)
