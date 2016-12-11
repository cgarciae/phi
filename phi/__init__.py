
import builder
import utils
import dsl
import lambdas
import patch

from dsl import With
from builder import Builder

#patches
import functions_patch

P = Builder(utils.identity)

# shortcuts
Then0 = P.Then0
Then = P.Then
Then1 = P.Then1
Then3 = P.Then3
Then4 = P.Then4
Then5 = P.Then5
Read = P.Read
Write = P.Write
Val = P.Val
Pipe = P.Pipe
Make = P.Make
Obj = P.Obj
Rec = P.Rec
Context = P.Context

M = Make
"""
Abreviation for `P.Make` or the module function `phi.Make`.
"""

########################
# Documentation
########################
import os

#pdoc
__all__ = ["dsl", "builder", "lambdas", "patch"]

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

raw_docs = _read("README-template.md")
__version__ = _read("version.txt")
__doc__ = _to_pdoc_markdown(raw_docs.format(__version__))
