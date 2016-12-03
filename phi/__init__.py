from builder import Builder
import utils
import dsl
from dsl import With

#patches
import functions_patch

P = Builder(utils.identity, {})

# shortcuts
Map0 = P.Map0
Map = P.Map
Map2 = P.Map2
Map3 = P.Map3
Map4 = P.Map4
Map5 = P.Map5
On = P.On
Val = P.Val
# P = Pipe = P
C = Compile = P.Compile
Obj = P.Obj
Rec = P.Rec

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
