from builder import Builder
from method_builder import M
from fn import _
from shortcuts import C, P, val, on, _0, _1, _2, _3, _4, _5

builder = Builder()


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
