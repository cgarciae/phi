from builder import Builder
from fn import _
import utils
import dsl
from dsl import With
from special_objects import Obj, Rec

#patches
import functions_patch

ph = Builder()


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
