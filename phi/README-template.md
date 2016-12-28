# Phi
Phi library for functional programming in Python that intends to remove as much of the pain as possible from your functional programming experience in Python.

## Import
For demonstration purposes we will import right now everything we will need for the rest of the exercises like this
```python
from phi.api import *
```
but you can also import just what you need from the `phi` module.

## Math-like Lambdas

#### Operators

Using the `P` object you can create quick lambdas using any operator. You can write things like

```python
f = (P * 6) / (P + 2)  #lambda x: (x * 6) / (x + 2)

assert f(2) == 3  # (2 * 6) / (2 + 2) == 12 / 4 == 3
```

where the expression for `f` is equivalent to

```python
f = lambda x: (x * 6) / (x + 2)
```

#### getitem
You can also use the `P` object to create lambdas that access the items of a collection
```python
f = P[0] + P[-1]  #lambda x: x[0] + x[-1]

assert f([1,2,3,4]) == 5   #1 + 4 == 5
```

#### field access
If you want create lambdas that access the field of some entity you can use the `Rec` (for Record) object an call that field on it
```python
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])

f = Rec.x + Rec.y  #lambda p: p.x + p.y

assert f(Point(3, 4)) == 7   #point.x + point.y == 3 + 4 == 7
```
#### method calling
If you want to create a lambda that calls the method of an object you use the `Obj` object and call that method on it with the parameters
```python
f = Obj.upper() + ", " + Obj.lower()  #lambda s: s.upper() + ", " + s.lower()

assert f("HEllo") == "HELLO, hello"   # "HEllo".upper() + ", " + "HEllo".lower() == "HELLO" + ", " + "hello" == "HELLO, hello"
```
Here no parameters were needed but in general
```python
f = Obj.some_method(arg1, arg2, ...) #lambda obj: obj.some_method(arg1, arg2, ...)
```
is equivalent to
```python
f = lambda obj: obj.some_method(arg1, arg2, ...)
```
## Composition
#### >> and <<
You can use the `>>` operator to *forward* compose expressions

```python
f = P + 7 >> math.sqrt  #executes left to right

assert f(2) == 3  # math.sqrt(2 + 7) == math.sqrt(9) == 3
```
This is preferred because it is more readable, but you can use the `<<` to compose them *backwards* just like the mathematical definition of function composition

```python
f =  math.sqrt << P + 7 #executes right to left

assert f(2) == 3  # math.sqrt(2 + 7) == math.sqrt(9) == 3
```

#### Seq and Pipe
If you need to do a long or complex composition you can use `Seq` (for 'Sequence') instead of many chained `>>`

```python
f = Seq(
  str,
  P + "00",
  int,
  math.sqrt
)

assert f(1) == 10  # sqrt(int("1" + "00")) == sqrt(100) == 10
```
If you want to create a composition and directly apply it to an initial value you can use `Pipe`

```python
assert 10 == Pipe(
  1,  #input
  str,  # "1"
  P + "00",  # "1" + "00" == "100"
  int,  # 100
  math.sqrt  #sqrt(100) == 10
)
```

## Combinators
#### List, Tuple, Set, Dict
There are a couple of combinators like `List`, `Tuple`, `Set`, `Dict` that help you create compound functions that return the container types `list`, `tuple`, `set` and `dict` respectively. For example, you can pass `List` a couple of expressions to get a function that returns a list with the values of these functions

```python
f = List( P + 1, P * 10 )  #lambda x: [ x +1, x * 10 ]

assert f(3) == [ 4, 30 ]  # [ 3 + 1, 3 * 10 ] == [ 4, 30 ]
```
The same logic applies for `Tuple` and `Set`. With `Dict` you have to use keyword arguments

```python
f = Dict( x = P + 1, y = P * 10 )  #lambda x: [ x +1, x * 10 ]

d = f(3)

assert d == {{ 'x': 4, 'y': 30 }}  # {{ 'x': 3 + 1, 'y': 3 * 10 }} == {{ 'x': 4, 'y': 30 }}
assert d.x == 4   #access d['x'] via field access as d.x
assert d.y == 30  #access d['y'] via field access as d.y
```
As you see, `Dict` returns a custom `dict` that also allows *field access*, this is useful because you can use it in combination with `Rec`.

#### State: Read and Write
Internally all these expressions are implemented in such a way that they not only pass their computed values but also pass a **state** dictionary between them in a functional manner. By reading from and writing to this state dictionary the `Read` and `Write` combinators can help you "save" the state of intermediate computations to read them later

```python
assert [70, 30] == Pipe(
  3,
  Write(s = P * 10),  #s = 3 * 10 == 30
  P + 5,  #30 + 5 == 35
  List(
    P * 2  # 35 * 2 == 70
  ,
    Read('s')  #s == 30
  )
)
```
If you need to perform many reads inside a list -usually for output- you can use `ReadList` instead
```python
assert [2, 4, 22] == Pipe(
    1,
    Write(a = P + 1),  #a = 1 + 1 == 2
    Write(b = P * 2),  #b = 2 * 2 == 4
    P * 5,   # 4 * 5 == 20
    ReadList('a', 'b', P + 2)  # [a, b, 20 + 2] == [2, 4, 22]
)
```
`ReadList` interprets string elements as `Read`s, so the previous is translated to
```python
List(Read('a'), Read('b'), P + 2)
```

#### Then, Then2, ..., Then5, ThenAt
To create a partial expression from a function e.g.
```python
def repeat_word(word, times, upper=False):
  if upper:
    word = word.upper()

  return [ word ] * times
```
use the `Then` combinator which accepts a function plus all but the *1st* of its `*args` + `**kwargs`
```python
f = P[::-1] >> Then(repeat_word, 3)
g = P[::-1] >> Then(repeat_word, 3, upper=True)

assert f("ward") == ["draw", "draw", "draw"]
assert g("ward") == ["DRAW", "DRAW", "DRAW"]
```
and assumes that the *1st* argument of the function will be applied last, e.g. `word` in the case of `repeat_word`. If you need the *2nd* argument to be applied last use `Then2`, and so on. In general you can use `ThenAt(n, f, *args, **kwargs)` where `n` is the position of the argument that will be applied last. Example
```python
# since map and filter receive the iterable on their second argument, you have to use `Then2`
f = Then2(filter, P % 2 == 0) >> Then2(map, P**2) >> list  #lambda x: map(lambda z: z**2, filter(lambda z: z % 2 == 0, x))

assert f([1,2,3,4,5]) == [4, 16]  #[2**2, 4**2] == [4, 16]
```
Be aware that `P` already has the `map` and `filter` methods so you can write the previous more easily as
```python
f = P.filter(P % 2 == 0) >> P.map(P**2) >> list  #lambda x: map(lambda z: z**2, filter(lambda z: z % 2 == 0, x))

assert f([1,2,3,4,5]) == [4, 16]  #[2**2, 4**2] == [4, 16]
```

#### Val
If you need to create a constant function with a given value use `Val`
```python
f = Val(42)  #lambda x: 42

assert f("whatever") == 42
```

#### Others
Check out the `With`, `If` and more, combinators on the documentation. The `P` object also offers some useful combinators as methods such as `Not`, `First`, `Last` plus **almost all** python built in functions as methods:

```python
f = Obj.split(' ') >> P.map(len) >> sum >> If( (P < 15).Not(), "Great! Got {{0}} letters!".format).Else("Too short, need at-least 15 letters")

assert f("short frase") == "Too short, need at-least 15 letters"
assert f("some longer frase") == "Great! Got 15 letters!"
```

## The DSL
Phi has a small omnipresent DSL that has these simple rules:

1. Any element of the class `Expression` is an element of the DSL. `P` and all the combinators are of the `Expression` class.
2. Any callable of arity 1 is an element of the DSL.
3. The container types `list`, `tuple`, `set`, and `dict` are elements of the DSL. They are translated to their counterparts `List`, `Tuple`, `Set` and `Dict`, their internal elements are forwarded.
4. Any value `x` that does not comply with any of the previous rules is also an element of the DSL and is translated to `Val(x)`.

Using the DSL, the expression

```python
f = P**2 >> List( P, Val(3), Val(4) )  #lambda x: [ x**2]

assert f(10) == [ 100, 3, 4 ]  # [ 10**2, 3, 4 ]  == [ 100, 3, 4 ]
```
can be rewritten as
```python
f = P**2 >> [ P, 3, 4 ]

assert f(10) == [ 100, 3, 4 ]  # [ 10 ** 2, 3, 4 ]  == [ 100, 3, 4 ]
```
Here the values `3` and `4` are translated to `Val(3)` and `Val(4)` thanks to the *4th* rule, and `[...]` is translated to `List(...)` thanks to the *3rd* rule. Since the DSL is omnipresent you can use it inside any core function, so the previous can be rewritten using `Pipe` as
```python
assert [ 100, 3, 4 ] == Pipe(
  10,
  P**2,  # 10**2 == 100
  [ P, 3, 4 ]  #[ 100, 3, 4 ]
)
```

#### F
You can *compile* any element to an `Expression` using `F`
```python
f = F((P + "!!!", 42, Obj.upper()))  #Tuple(P + "!!!", Val(42), Obj.upper())

assert f("some tuple") == ("some tuple!!!", 42, "SOME TUPLE")
```
Other example
```python
f = F([ P + n for n in range(5) ])  >> [ len, sum ]  # lambda x: [ len([ x, x+1, x+2, x+3, x+4]), sum([ x, x+1, x+2, x+3, x+4]) ]

assert f(10) == [ 5, 60 ]  # [ len([10, 11, 12, 13, 14]), sum([10, 11, 12, 13, 14])] == [ 5, (50 + 0 + 1 + 2 + 3 + 4) ] == [ 5, 60 ]
```

## Fluent Programming
All the functions you've seen are ultimately methods of the `PythonBuilder` class which inherits from the `Expression`, therefore you can also [fluently](https://en.wikipedia.org/wiki/Fluent_interface) chain methods instead of using the `>>` operator. For example

```python
f = Dict(
  x = 2 * P,
  y = P + 1
).Tuple(
  Rec.x + Rec.y,
  Rec.y / Rec.x
)

assert f(1) == (4, 1)  # ( x + y, y / x) == ( 2 + 2, 2 / 2) == ( 4, 1 )
```
This more complicated previous example
```python
f = Obj.split(' ') >> P.map(len) >> sum >> If( (P < 15).Not(), "Great! Got {{0}} letters!".format).Else("Too short, need at-least 15 letters")

assert f("short frase") == "Too short, need at-least 15 letters"
assert f("some longer frase") == "Great! Got 15 letters!"
```
can be be rewritten as
```python
f = (
  Obj.split(' ')
  .map(len)
  .sum()
  .If( (P < 15).Not(),
    "Great! Got {{0}} letters!".format
  ).Else(
    "Too short, need at-least 15 letters"
  )
)

assert f("short frase") == "Too short, need at-least 15 letters"
assert f("some longer frase") == "Great! Got 15 letters!"
```

## Integrability
#### Register, Register2, ..., Register5, RegistarAt
If you want to have custom expressions to deal with certain data types, you can create a custom class that inherits from `Builder` or `PythonBuilder`
```python
from phi import PythonBuilder

class MyBuilder(PythonBuilder):
  pass

M = MyBuilder()
```
and register your function in it using the `Register` class method

```python
def remove_longer_than(some_list, n):
  return [ elem from elem in some_list if len(elem) <= n ]

MyBuilder.Register(remove_longer_than, "my.lib.")
```
Or better even use `Register` as a decorator
```python
@MyBuilder.Register("my.lib.")
def remove_longer_than(some_list, n):
  return [ elem for elem in some_list if len(elem) <= n ]
```

Now the method `MyBuilder.remove_longer_than` exists on this class. You can then use it like this
```python
f = Obj.lower() >> Obj.split(' ') >> M.remove_longer_than(6)

assert f("SoMe aRe LONGGGGGGGGG") == ["some", "are"]
```
As you see the argument `n = 6` was partially applied to `remove_longer_than`, an expression which waits for the `some_list` argument to be returned. Internally the `Registar*` method family uses the `Then*` method family.

#### PatchAt
If you want to register a batch of functions from a module or class automatically you can use the `PatchAt` class method. It's an easy way to integrate an entire module to Phi's DSL. See `PatchAt`.

#### Libraries
Phi currently powers the following libraries that integrate with its DSL:

* [PythonBuilder](https://cgarciae.github.io/phi/python_builder.m.html) : helps you integrate Python's built-in functions and keywords into the phi DSL and it also includes a bunch of useful helpers for common stuff. `phi`'s global `P` object is an instance of this class. [Shipped with Phi]
* [TensorBuilder](https://github.com/cgarciae/tensorbuilder): a TensorFlow library enables you to easily create complex deep neural networks by leveraging the phi DSL to help define their structure.
* NumpyBuilder: Comming soon!

## Documentation
Check out the [complete documentation](https://cgarciae.github.io/phi/).

## More Examples
The global `phi.P` object exposes most of the API and preferably should be imported directly. The most simple thing the DSL does is function composition:

```python
from phi.api import *

def add1(x): return x + 1
def mul3(x): return x * 3

x = Pipe(
    1.0,     #input 1
    add1,  #1 + 1 == 2
    mul3   #2 * 3 == 6
)

assert x == 6
```

Use phi [lambdas](https://cgarciae.github.io/phi/lambdas.m.html) to create the functions

```python
from phi.api import *

x = Pipe(
    1.0,      #input 1
    P + 1,  #1 + 1 == 2
    P * 3   #2 * 3 == 6
)

assert x == 6
```

Create a branched computation instead

```python
from phi.api import *

[x, y] = Pipe(
    1.0,  #input 1
    [
        P + 1  #1 + 1 == 2
    ,
        P * 3  #1 * 3 == 3
    ]
)

assert x == 2
assert y == 3
```

Compose it with a function equivalent to `f(x) = (x + 3) / (x + 1)`

```python
from phi.api import *

[x, y] = Pipe(
    1.0,  #input 1
    (P + 3) / (P + 1),  #(1 + 3) / (1 + 1) == 4 / 2 == 2
    [
        P + 1  #2 + 1 == 3
    ,
        P * 3  #2 * 3 == 6
    ]
)

assert x == 3
assert y == 6
```

Give names to the branches

```python
from phi.api import *

result = Pipe(
    1.0,  #input 1
    (P + 3) / (P + 1),  #(1 + 3) / (1 + 1) == 4 / 2 == 2
    dict(
        x = P + 1  #2 + 1 == 3
    ,
        y = P * 3  #2 * 3 == 6
    )
)

assert result.x == 3
assert result.y == 6
```

Divide `x` by `y`.

```python
from phi.api import *

result = Pipe(
    1.0,  #input 1
    (P + 3) / (P + 1),  #(1 + 3) / (1 + 1) == 4 / 2 == 2
    dict(
        x = P + 1  #2 + 1 == 3
    ,
        y = P * 3  #2 * 3 == 6
    ),
    Rec.x / Rec.y  #3 / 6 == 0.5
)

assert result == 0.5
```

Save the value from the `(P + 3) / (P + 1)` computation as `s` and load it at the end in a branch

```python
from phi.api import *

[result, s] = Pipe(
    1.0,  #input 1
    Write(s = (P + 3) / (P + 1)), #s = 4 / 2 == 2
    dict(
        x = P + 1  #2 + 1 == 3
    ,
        y = P * 3  #2 * 3 == 6
    ),
    [
        Rec.x / Rec.y  #3 / 6 == 0.5
    ,
        Read('s')  #s == 2
    ]
)

assert result == 0.5
assert s == 2
```

Add 3 to the loaded `s` for fun and profit

```python
from phi.api import *

[result, s] = Pipe(
    1.0,  #input 1
    Write(s = (P + 3) / (P + 1)), #s = 4 / 2 == 2
    dict(
        x = P + 1  #2 + 1 == 3
    ,
        y = P * 3  #2 * 3 == 6
    ),
    [
        Rec.x / Rec.y  #3 / 6 == 0.5
    ,
        Read('s') + 3  # 2 + 3 == 5
    ]
)

assert result == 0.5
assert s == 5
```

Use the `Read` and `Write` field access lambda style just because

```python
from phi.api import *

[result, s] = Pipe(
    1.0,  #input 1
    (P + 3) / (P + 1), #4 / 2 == 2
    Write.s,  #s = 2
    dict(
        x = P + 1  #2 + 1 == 3
    ,
        y = P * 3  #2 * 3 == 6
    ),
    [
        Rec.x / Rec.y  #3 / 6 == 0.5
    ,
        Read.s + 3  # 2 + 3 == 5
    ]
)

assert result == 0.5
assert s == 5
```

Add an input `Val` of 9 on a branch and add to it 1 just for the sake of it

```python
from phi.api import *

[result, s, val] = Pipe(
    1.0,  #input 1
    (P + 3) / (P + 1), Write.s,  #4 / 2 == 2, saved as 's'
    dict(
        x = P + 1  #2 + 1 == 3
    ,
        y = P * 3  #2 * 3 == 6
    ),
    [
        Rec.x / Rec.y  #3 / 6 == 0.5
    ,
        Read.s + 3  # 2 + 3 == 5
    ,
        Val(9) + 1  #input 9 and add 1, gives 10
    ]
)

assert result == 0.5
assert s == 5
assert val == 10
```

Do the previous only if `y > 7` else return `"Sorry, come back latter."`

```python
from phi.api import *

[result, s, val] = Pipe(
    1.0,  #input 1
    (P + 3) / (P + 1), Write.s,  #4 / 2 == 2, saved as 's'
    dict(
        x = P + 1  #2 + 1 == 3
    ,
        y = P * 3  #2 * 3 == 6
    ),
    [
        Rec.x / Rec.y  #3 / 6 == 0.5
    ,
        Read.s + 3  # 2 + 3 == 5
    ,
        If( Rec.y > 7,
            Val(9) + 1  #input 9 and add 1, gives 10    
        ).Else(
            "Sorry, come back latter."
        )
    ]
)

assert result == 0.5
assert s == 5
assert val == "Sorry, come back latter."
```

Now, what you have to understand that everything you've done with these expression is to create and apply a single function. Using `Seq` we can get the standalone function and then use it to get the same values as before

```python
from phi.api import *

f = Seq(
    (P + 3) / (P + 1), Write.s,  #4 / 2 == 2, saved as 's'
    dict(
        x = P + 1  #2 + 1 == 3
    ,
        y = P * 3  #2 * 3 == 6
    ),
    [
        Rec.x / Rec.y  #3 / 6 == 0.5
    ,
        Read.s + 3  # 2 + 3 == 5
    ,
        If( Rec.y > 7,
            Val(9) + 1  #input 9 and add 1, gives 10    
        ).Else(
            "Sorry, come back latter."
        )
    ]
)

[result, s, val] = f(1.0)

assert result == 0.5
assert s == 5
assert val == "Sorry, come back latter."
```
### Even More Examples

```python
from phi.api import *

avg_word_length = Pipe(
    "1 22 333",
    Obj.split(" "), # ['1', '22', '333']
    P.map(len), # [1, 2, 3]
    P.sum() / P.len() # sum([1,2,3]) / len([1,2,3]) == 6 / 3 == 2
)

assert 2 == avg_word_length
```

```python
from phi.api import *

assert False == Pipe(
    [1,2,3,4], P
    .filter(P % 2 != 0)   #[1, 3], keeps odds
    .Contains(4)   #4 in [1, 3] == False
)
```

```python
from phi.api import *

assert {{'a': 97, 'b': 98, 'c': 99}} == Pipe(
    "a b c", Obj
    .split(' ').Write.keys  # keys = ['a', 'b', 'c']
    .map(ord),  # [ord('a'), ord('b'), ord('c')] == [97, 98, 99]
    lambda it: zip(Ref.keys, it),  # [('a', 97), ('b', 98), ('c', 99)]
    dict   # {{'a': 97, 'b': 98, 'c': 99}}
)
```

## Installation

    pip install phi


#### Bleeding Edge

    pip install git+https://github.com/cgarciae/phi.git@develop

## Status
* Version: **{0}**.
* Documentation coverage: 100%. Please create an issue if documentation is unclear, it is a high priority of this library.
* Milestone: reach 1.0.0 after feedback from the community.
