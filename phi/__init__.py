from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


from . import utils
from . import builder
from . import dsl

from .utils import identity

from . import python_builder
from .builder import Builder
from .python_builder import PythonBuilder

from .api import *

########################
# Documentation
########################
import os

#set documentation

def _to_pdoc_markdown(doc):
    indent = False
    lines = []

    for line in doc.split('\n'):
        if "```" in line:
            indent = not indent
            line = line.replace("```python", '')
            line = line.replace("```", '')

        if indent:
            line = "    " + line

        lines.append(line)

    return '\n'.join(lines)

def _read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

_raw_docs = _read("README-template.md")
__version__ = _read("version.txt")
__doc__ = _to_pdoc_markdown(_raw_docs.format(__version__))
