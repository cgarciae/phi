
import builder
import utils
import dsl
import lambdas

from dsl import With
from builder import Builder

#patches
import functions_patch

P = Builder(utils.identity, {})

# shortcuts
_0 = P._0
_1 = P._
_2 = P._2
_3 = P._3
_4 = P._4
_5 = P._5
On = P.On
Val = P.Val
Pipe = P.Pipe
M = Make = P.Make
Obj = P.Obj
Rec = P.Rec

########################
# Documentation
########################
import os
import sys

#pdoc
__all__ = ["dsl", "builder", "lambdas"]

#set documentation
def _read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

module = sys.modules[__name__]
raw_docs = _read("README-template.md")
__version__ = _read("version.txt")
module.__doc__ = raw_docs.format(__version__)
