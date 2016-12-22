class Expression(Lambda):
    """
All basic/terminal elements of this language are callables (implement `__call__`) of arity 1.

### Examples
Compiling a function just returns back the function

Seq(f) == f

and piping through a function is just the same a applying the function

P.Pipe(x, f) == f(x)
    """

def Branch(self, *branches, **kwargs):
    """
While `Seq` is sequential, `Branch` allows you to split the computation and get back a list with the result of each path. While the list literal should be the most incarnation of this expresion, it can actually be any iterable (implements `__iter__`) that is not a tuple and yields a valid expresion.

After compilation the expresion:

k = [f, g]

is equivalent to

k(x) = [ f(x), g(x) ]


In general, the following rules apply after compilation:

**General Branching**

let fs = <some iterable of valid expressions>

is equivalent to

k(x) = [ f(x) for f in fs ]


**Composing & Branching**

A more common scenario however is to see how braching interacts with composing. The expression

k = (f, [g, h])

is *almost* equivalent to

k = [ (f, g), (f, h) ]

As you see its as if `f` where distributed over the list. We say *almost* because what really happens is that the iterable is first compiled to a function and the whole sequence is then composed

 z(x) = [ g(x), h(x) ]
 k(x) = (f, z)(x) = z(f(x))

As you see `f` is only excecuted once.

### Examples

form phi import P

avg_word_length = P.Pipe(
    "1 22 333",
    lambda s: s.split(' '), # ['1', '22', '333']
    lambda l: map(len, l), # [1, 2, 3]
    [
        sum # 1 + 2 + 3 == 6
    ,
        len # len([1, 2, 3]) == 3
    ],
    lambda l: l[0] / l[1] # sum / len == 6 / 3 == 2
)

assert avg_word_length == 2

The previous could also be done more briefly like this

form phi import P, Obj

avg_word_length = P.Pipe(
    "1 22 333",
    Obj.split(' '), # ['1', '22', '333']
    P.map(len), # [1, 2, 3]
    [
        sum # sum([1, 2, 3]) == 6
    ,
        len # len([1, 2, 3]) == 3
    ],
    P[0] / P[1] # 6 / 3 == 2
)

assert avg_word_length == 2

In the example above the last expression

P[0] / P[1]

works for a couple of reasons

1. The previous expression returns a list
2. In general the expression `P[x]` compiles to a function with the form `lambda obj: obj[x]`
3. The class `Lambda` (the class from which the object `P` inherits) overrides most operators to create functions easily. For example, the expression

(P * 2) / (P + 1)

compile to a function of the form

f(x) = (x * 2) / (x + 1)

Check out the documentatio for Phi [lambdas](https://cgarciae.github.io/phi/lambdas.m.html).

    """

def Seq(self, *sequence, **kwargs):
    """
In this language tuples are used to express function composition. After compilation, the expression

k = (f, g)

be equivalent to

k(x) = g(f(x))

As you see, its a little different from the mathematical definition. Excecution order flow from left to right, and this makes reading and reasoning about code structured in the way more easy. This bahaviour is based upon the `|>` (pipe) operator found in languages like F#, Elixir and Elm. You can pack as many expressions as you like and they will be applied in order to the data that is passed through them when compiled an excecuted.

In general, the following rules apply after compilation:

**General Sequence**

k = (f0, f1, ..., fn-1, fn)

is equivalent to

k(x) = fn(fn-1(...(f1(f0(x)))))

**Single Function**

k = (f)

is equivalent to

k = f

**Identity**

The empty tuple

k = ()

is equivalent to

k(x) = x

### Examples

from phi import P

f = Seq(
    lambda x: x * 2,
    lambda x: x + 1,
    lambda x: x ** 2
)

assert f(1) == 9 # ((1 * 2) + 1) ** 2

As you see, `Seq`s `*args` are interpreted as a tuple which means all expressions contained are composed. The previous example using `P.Pipe`

from phi import P

assert 9 == P.Pipe(
    1,
    lambda x: x * 2,
    lambda x: x + 1,
    lambda x: x ** 2
)

Again, `Pipe`'s signature is `Pipe(x, *args)` and `*args` is interpreted as a tuple which means all expressions contained are composed.

    """

@property
def Rec(self):
    """
List or iterables in general provide you a way to branch your computation in the DSL, but access to the values of each branch are then done by index, this might be a little inconvenient because it reduces readability. Record branches provide a way to create named branches via a dictionary object where the keys are the names of the branches and the values are valid expressions representing the computation of that branch.

A special object is returned by this expression when excecuted, this object derives from `dict` and fully emulates it so you can treat it as such, however it also implements the `__getattr__` method, this lets you access a value as if it where a field if its key is a of type string.

### Examples

from phi import P

stats = P.Pipe(
    [1,2,3],
    dict(
        sum = sum
    ,
        len = len
    )
)

assert stats.sum == 6
assert stats.len == 3

assert stats['sum'] == 6
assert stats['len'] == 3

Now lets image that we want to find the average value of the list, we could calculate it outside of the pipe doing something like `avg = stats.sum / stats.len`, however we could also do it inside the pipe using `P.Rec` or `phi.Rec` like this

from phi import P, Rec

avg = P.Pipe(
    [1,2,3],
    dict(
        sum = sum
    ,
        len = len
    ),
    Rec.sum / Rec.len
)
    """

def With(Node):
    """
**With**

    def With(context_manager, *body):

**Arguments**

* **context_manager**: a [context manager](https://docs.python.org/2/reference/datamodel.html#context-managers) object or valid expression from the DSL that returns a context manager.
* ***body**: any valid expression of the DSL to be evaluated inside the context. `*body` is interpreted as a tuple so all expression contained are composed.

As with normal python programs you sometimes might want to create a context for a block of code. You normally give a [context manager](https://docs.python.org/2/reference/datamodel.html#context-managers) to the [with](https://docs.python.org/2/reference/compound_stmts.html#the-with-statement) statemente, in Phi you use `P.With` or `phi.With`

**Context**

Python's `with` statemente returns a context object through `as` keyword, in the DSL this object can be obtained using the `P.Context` method or the `phi.Context` function.

### Examples

    from phi import P, Obj, Context, With, Pipe

    text = Pipe(
        "text.txt",
        With( open, Context,
            Obj.read()
        )
    )

The previous is equivalent to

    with open("text.txt") as f:
        text = f.read()

    """

def Read(Node):
    """
Giving names and saving parts of your computation to use then latter is useful to say the least. In the DSL the expression

    {'x'}

behaves like just like the indentity except that as a side effect it creates a reference to that value which you can call latter. Here `{..}` is python's sytax for a set literal and `x` is a string with the name of the reference. To read the previous you would use the expression

    'x'

This is equivalent to a sort of function like this

    lambda z: read('x')

where the input is totally ignored and a hypothetical `read` function is given the reference name and it should return its stored value (internally its not implemented like this). As you see strings in the DSL mean read from a reference and a set with a string means write to a reference.

### Example
Lets see a common situation where you would use this

    from phi import P

    P.Pipe(
        input,
        fun_1, {'fun_1_val'}
        fun_2,
        [
            fun_4
        ,
        (
            'fun_1_val',
            fun_5
        )
        ]
    )

Here you *save* the value outputed by `fun_1` and the load it as the initial value of the second branch. In normal python the previous would be *almost* equivalent to this

    x = fun_1(input)
    fun_1_val = x
    x = fun_2(x)
    x = [
        fun_4(x)
    ,
        fun_5(fun_1_val)
    ]

    return x

### Write special case
When composing its aesthetically better to put writes in the same line as the function whos value its storing to make the intent a bit more clear:

    (
        f, {'a'},
        g
    )

Here we store the value of `f` in `'a'`, however, when you are inside a branch you will be tempted to do the following to get the same result:

    [
        f, {'a'}
    ,
        g
    ]

However, if you flatten the text you realize you actually have 3 branches instead of 2

    [ f, {'a'}, g ]

and that wont save the value of `f` in `'a'` as you intended. To avoid this possible error, the DSL rewrites the expression during parsing to

    [ ( f, {'a'} ), g ]

every time there is a write expression inside a branch expression.

    """

def Val(Node):
    """
Sometimes you might need to branch the computation but start one of the branches with a values different than the one being passed down, you could always solve it like this

    P.Pipe(
        ...,
        [
            lambda z: my_value
        ,
            ...
        ]
    )

Here we just made a lamda that took in the argument `z` but it was completely ignored and it always returns `my_value`, this is called a constant function. You could also do the same with `P.Val` or the top level function `phi.Val`

    from phi import P, Val

    P.Pipe(
        ...,
        [
            Val(my_value)
        ,
            ...
        ]
    )
    """

def If(Node):
    """
**If**

    If(Predicate, *Then, Else=())

Having conditionals expressions a necesity in every language, Phi includes the `If` expression for such a purpose.

**Arguments**

* **Predicate** : a predicate expression uses to determine if the `Then` or `Else` branches should be used.
* ***Then** : an expression to be excecuted if the `Predicate` yields `True`, since this parameter is variadic you can stack expression and they will be interpreted as a tuple `phi.dsl.Seq`.
* `Else = ()` : the expression to be excecuted if the `Predicate` yields `False`, its the identity `()` by default, since this is NOT a variadic parameter make sure to include the tuple parenthesis `(...)` if you want to create a `phi.dsl.Seq`.

This object includes the `Else` method which makes things more readable, however, as a special case `phi.If` and `P.If` dont have the same behaviour in that `P.If` doesn't have the `Else` method. With `P.If` you can write

    from phi import P, Val

    assert "Less or equal to 10" == P.Pipe(
        5,
        P.If(P > 10,
            Val("Greater than 10"),
        Else = (
            Val("Less or equal to 10")
        ))
    )

however with `phi.If` its a little nicer

    from phi import P, Val, If

    assert "Less or equal to 10" == P.Pipe(
        5,
        If(P > 10,
            Val("Greater than 10")
        )
        .Else(
            Val("Less or equal to 10")
        )
    )
    """

@property
def Obj(self):
    """
`Obj` is a `property` that returns an object that defines the `__getattr__` method which when called helps you create a partial that emulates a method call. The following expression

Obj.some_method(x1, x2, ...)

is equivalent to

lambda obj: obj.some_method(x1, x2, ...)

**Examples**

from phi import P, Obj

assert "hello world" == P.Pipe(
    "  HELLO HELLO {0}     ",
    Obj.format("WORLD"),  # "   HELLO HELLO WORLD     "
    Obj.strip(),          # "HELLO HELLO WORLD"
    Obj.lower()           # "hello hello world"
    Obj.split(' ')        # ["hello", "hello", "world"]
    Obj.count("hello")    # 2
)

**Also see**

* `phi.builder.Builder.Rec`
* [dsl.Write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Write)
* `phi.builder.Builder.Write`
    """

@property
def Rec(self):
    """
`Rec` is a `property` that returns an object that defines the `__getattr__` and `__getitem__` methods which when called help you create a partial that emulates a field access. The following expression

Rec.some_field

is equivalent to

lambda rec: rec.some_field

**Examples**

from phi import P, Obj, Rec

class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def flip_cords(self):
        y = self.y
        self.y = self.x
        self.x = y

assert 4 == P.Pipe(
    Point(1, 2),         # point(x=1, y=2)
    Obj.flip_cords(),    # point(x=2, y=1)
    Rec.x,               # point.x = 2
    P * 2                # 2 * 2 = 4
)

**Also see**

* `phi.builder.Builder.Obj`
* `phi.builder.Builder.Read`
* `phi.builder.Builder.Write`
    """
    return _RecordProxy(self)


@property
def Ref(self):
    """
Returns an object that helps you to inmediatly create and [read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read) [references](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Ref).

**Creating Refences**

You can manually create a [Ref](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Ref) outside the DSL using `Ref` and then pass to as/to a [Read](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Read) or [Write](https://cgarciae.github.io/phi/dsl.m.html#phi.dsl.Write) expression. Here is a contrived example

from phi import P

r = P.Ref('r')

assert [600, 3, 6] == P.Pipe(
    2,
    P + 1, {'a'},  # a = 2 + 1 = 3
    P * 2, {'b'},  # b = 3 * 2 = 6
    P * 100, {'c', r },  # c = r = 6 * 100 = 600
    ['c', 'a', 'b']
)

assert r() == 600

**Reading Refences from the Current Context**

While the expression `Read.a` with return a function that will discard its argument and return the value of the reference `x` in the current context, the expression `Ref.x` will return the value inmediatly, this is useful when using it inside pyton lambdas.

Read.x(None) <=> Ref.x

As an example

from phi import P, Obj, Ref

assert {'a': 97, 'b': 98, 'c': 99} == P.Pipe(
    "a b c", Obj
    .split(' ').Write.keys  # keys = ['a', 'b', 'c']
    .map(ord),  # [ord('a'), ord('b'), ord('c')] == [97, 98, 99]
    lambda it: zip(Ref.keys, it),  # [('a', 97), ('b', 98), ('c', 99)]
    dict   # {'a': 97, 'b': 98, 'c': 99}
)

    """
    return _RefProxyInstance


@classmethod
def Context(cls, *args):
    """
**Builder Core**. Also available as a global function as `phi.Context`.

Returns the context object of the current `dsl.With` statemente.

**Arguments**

* ***args**: By design `Context` accepts any number of arguments and completely ignores them.

This is a classmethod and it doesnt return a `Builder`/`Lambda` by design so it can be called directly:

from phi import P, Context, Obj

def read_file(z):
    f = Context()
    return f.read()

lines = P.Pipe(
    "text.txt",
    P.With( open,
        read_file,
        Obj.split("\\n")
    )
)

Here we called `Context` with no arguments to get the context back, however, since you can also give this function an argument (which it will ignore) it can be passed to the DSL so we can rewrite the previous as:

from phi import P, Context, Obj

lines = P.Pipe(
    "text.txt",
    P.With( open,
        Context, # f
        Obj.read()
        Obj.split("\\n")
    )
)

`Context` yields an exception when used outside of a `With` block.

**Also see**

* `phi.builder.Builder.Obj`
* [dsl](https://cgarciae.github.io/phi/dsl.m.html)
    """
