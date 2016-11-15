from utils import identity
import utils
import pprint
from abc import ABCMeta, abstractmethod
from inspect import isclass


###############################
# Ref
###############################

NO_VALUE = object()

class Ref(object):
    """docstring for Ref."""
    def __init__(self, name, value=NO_VALUE):
        super(Ref, self).__init__()
        self.name = name
        self.value = None if value is NO_VALUE else value
        self.assigned = value is not NO_VALUE

    def __call__(self, *optional):
        if not self.assigned:
            raise Exception("Trying to read Ref('{0}') before assignment".format(self.name))

        return self.value

    def set(self, x):
        self.value = x

        if not self.assigned:
            self.assigned = True

        return x

###############################
# DSL Elements
###############################

class Node(object):
    """docstring for Node."""

    __metaclass__ = ABCMeta

    @abstractmethod
    def __compile__(self, refs):
        pass

class Function(Node):
    """docstring for Function."""
    def __init__(self, f):
        super(Function, self).__init__()
        self._f= f
        self._refs = {}

    def __iter__(self):
        yield self

    def __compile__(self, refs):
        refs = dict(refs, **self._refs)
        return self._f, refs

    def __str__(self):
        return "Fun({0})".format(self._f)


Identity = Function(identity)


class Tree(Node):
    """docstring for Tree."""

    def __init__(self, branches):
        self.branches = list(branches)

    def __compile__(self, refs):
        fs = []

        for node in self.branches:
            node_fs, refs = node.__compile__(refs)

            if type(node_fs) is list:
                fs += node_fs
            else:
                fs.append(node_fs)

        return fs, refs

    def __str__(self):
        return pprint.pformat(self.branches)


class Sequence(Node):
    """docstring for Sequence."""
    def __init__(self, left, right):
        super(Sequence, self).__init__()
        self.left = left
        self.right = right

    def __compile__(self, refs):
        f_left, refs = self.left.__compile__(refs)

        f_left = to_fn(f_left)

        f_right, refs = self.right.__compile__(refs)

        f_right = compose(f_right, f_left)

        return f_right, refs

    def __str__(self):
        return "Seq({0}, {1})".format(self.left, self.right)


class Scope(Node):
    """docstring for Dict."""

    GLOBAL_SCOPE = None

    def __init__(self, scope, body):
        super(Scope, self).__init__()
        self.scope = scope
        self.body = body

    def __compile__(self, refs):
        scope_f, refs = self.scope.__compile__(refs)
        body_fs, refs = self.body.__compile__(refs)

        def scope_function(x):
            with scope_f(x) as scope:
                with self.set_scope(scope):
                    return body_fs(x)

        return scope_function, refs

    def set_scope(self, new_scope):
        self.new_scope = new_scope
        self.old_scope = Scope.GLOBAL_SCOPE

        return self

    def __enter__(self):
        Scope.GLOBAL_SCOPE = self.new_scope

    def __exit__(self, *args):
        Scope.GLOBAL_SCOPE = self.old_scope

    def __str__(self):
        return "\{ {0}: {1}\}".format(pprint.pformat(self.scope), pprint.pformat(self.body))

class Read(Node):
    """docstring for Read."""
    def __init__(self, name):
        super(Read, self).__init__()
        self.name = name

    def __compile__(self, refs):
        ref = refs[self.name]
        f = ref #ref is callable with an argument
        return f, refs


class Write(Node):
    """docstring for Read."""
    def __init__(self, ref):
        super(Write, self).__init__()
        self.ref = ref

    def __compile__(self, refs):

        if type(self.ref) is str:
            name = self.ref

            if name in refs:
                self.ref = refs[name]
            else:
                refs = refs.copy()
                refs[name] = self.ref = Ref(self.ref)

        elif self.ref.name not in refs:
            refs = refs.copy()
            refs[self.ref.name] = self.ref

        return self.ref.set, refs


class Input(Node):
    """docstring for Input."""
    def __init__(self, value):
        super(Input, self).__init__()
        self.value = value

    def __compile__(self, refs):
        f = lambda x: self.value
        return f, refs


class Apply(Node):
    """docstring for Read."""
    def __init__(self):
        super(Write, self).__init__()



#######################
### FUNCTIONS
#######################

def Compile(code, refs):
    ast = parse(code)
    fs, refs = ast.__compile__(refs)

    fs = to_fn(fs)

    return fs, refs


def compose(fs, g):
    if type(fs) is list:
        return [ utils.compose2(f, g) for f in fs ]
    else:
        return utils.compose2(fs, g)


def to_fn(fs):
    if type(fs) is list:
        return lambda x: [ f(x) for f in fs ]
    else:
        return fs

def is_iter_instance(x):
    return hasattr(x, '__iter__') and not isclass(x)

def parse(code):
    #if type(code) is tuple:
    if isinstance(code, Node):
        return code
    elif hasattr(code, '__call__') or isclass(code):
        return Function(code)
    elif type(code) is str:
        return Read(code)
    elif type(code) is set:
        return parse_set(code)
    elif type(code) is tuple:
        return parse_tuple(code)
    elif type(code) is dict:
        return parse_dictionary(code)
    elif is_iter_instance(code): #leave last
        return parse_iterable(code) #its iterable
    else:
        raise Exception("Parse Error: Element not part of the DSL. Got:\n{0} of type {1}".format(code, type(code)))

def parse_set(code):
    if len(code) == 0:
        return Identity

    for ref in code:
        if not isinstance(ref, (str, Ref)):
            raise Exception("Parse Error: Sets can only contain strings or Refs, get {0}".format(code))

    writes = tuple([ Write(ref) for ref in code ])
    return parse(writes)

def build_sequence(right, *prevs):
    left = prevs[0] if len(prevs) == 1 else build_sequence(*prevs)
    return Sequence(left, right)

def parse_tuple(tuple_code):
    nodes = [ parse(code) for code in tuple_code ]

    if len(nodes) == 0:
        return Identity

    if len(nodes) == 1:
        return nodes[0]

    nodes.reverse()

    return build_sequence(*nodes)


def parse_iterable(iterable_code):
    nodes = [ parse(code) for code in iterable_code ]

    if len(nodes) == 1:
        return nodes[0]

    return Tree(nodes)

def parse_dictionary(dict_code):

    if len(dict_code) != 1:
        raise Exception("Parse Error: dict object has to have exactly 1 element. Got {0}".format(dict_code))

    scope_code, body_code = list(dict_code.items())[0]
    body = parse(body_code)

    if not hasattr(scope_code, '__call__'):
        scope = Input(scope_code)
    else:
        scope = parse(scope_code)

    return Scope(scope, body)
