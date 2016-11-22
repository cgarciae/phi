from builder import Builder
from fn import _
import utils
import dsl
from dsl import With
from special_objects import Obj, Rec

#patches
import functions_patch

ph = Builder()

# shortcuts
_0 = ph._0
_1 = ph._1
_2 = ph._2
_3 = ph._3
_4 = ph._4
_5 = ph._5
on = ph.on
val = ph.val
Pipe = ph.Pipe
Compile = ph.Compile

########################
# Documentation
########################
import os
import sys

#pdoc
__all__ = ["tensordata", "patches", "builder"]

#set documentation
def _read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

module = sys.modules[__name__]
raw_docs = _read("README-template.md")
__version__ = _read("version.txt")
module.__doc__ = raw_docs.format(__version__)
