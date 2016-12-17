# Phi
Phi library for [fluent](https://en.wikipedia.org/wiki/Fluent_interface) functional programming in Python that intends to remove as much of the pain as possible from your functional programming experience in Python by providing the following modules

* [dsl](https://cgarciae.github.io/phi/dsl.m.html): a small DSL that helps you compose computations in various ways & more.
* [lambdas](https://cgarciae.github.io/phi/lambdas.m.html): easy way to create quick lambdas with a mathematical flavor.
* [builder](https://cgarciae.github.io/phi/builder.m.html): an extensible class that enables you to integrate other libraries into the DSL as a fluent API, to do it lets you [register](https://cgarciae.github.io/phi/builder.m.html#phi.builder.Builder.RegisterMethod) functions as methods or even [patch](https://cgarciae.github.io/phi/builder.m.html#phi.builder.Builder.PatchAt) an entire module with a few lines of code.

### Libraries
Phi currently powers the following libraries:

* [PythonBuilder](https://cgarciae.github.io/phi/python_builder.m.html) : helps you integrate Python's built-in functions and keywords into the phi DSL and it also includes a bunch of useful helpers for common stuff. `phi`'s global `P` object is an instance of this class. [Shipped with Phi]
* [TensorBuilder](https://github.com/cgarciae/tensorbuilder): a TensorFlow library enables you to easily create complex deep neural networks by leveraging the phi DSL to help define their structure.
* NumpyBuilder: Comming soon!

## Documentation
Check out the [complete documentation](https://cgarciae.github.io/phi/).

## Getting Started
The global `phi.P` object exposes most of the API and preferably should be imported directly. The most simple thing the DSL does is function composition:

```python
from phi import P

def add1(x): return x + 1
def mul3(x): return x * 3

x = P.Pipe(
    1.0,     #input 1
    add1,  #1 + 1 == 2
    mul3   #2 * 3 == 6
)

assert x == 6
```

Use phi [lambdas](https://cgarciae.github.io/phi/lambdas.m.html) to create the functions

```python
from phi import P

x = P.Pipe(
    1.0,      #input 1
    P + 1,  #1 + 1 == 2
    P * 3   #2 * 3 == 6
)

assert x == 6
```

Create a branched computation instead

```python
from phi import P

[x, y] = P.Pipe(
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
from phi import P

[x, y] = P.Pipe(
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
from phi import P

result = P.Pipe(
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

Divide the `x` by the `y`.

```python
from phi import P, Rec

result = P.Pipe(
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
from phi import P, Rec

[result, s] = P.Pipe(
    1.0,  #input 1
    (P + 3) / (P + 1), {'s'},  #4 / 2 == 2, saved as 's'
    dict(
        x = P + 1  #2 + 1 == 3
    ,
        y = P * 3  #2 * 3 == 6
    ),
    [
        Rec.x / Rec.y  #3 / 6 == 0.5
    ,
        's'  #load 's' == 2
    ]
)

assert result == 0.5
assert s == 2
```

Add 3 to the loaded `s` for fun and profit

```python
from phi import P, Rec, Read

[result, s] = P.Pipe(
    1.0,  #input 1
    (P + 3) / (P + 1), {'s'},  #4 / 2 == 2, saved as 's'
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

Use the `Write` object instead of `{...}` just because

```python
from phi import P, Rec, Read, Write

[result, s] = P.Pipe(
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
    ]
)

assert result == 0.5
assert s == 5
```

Add an input `Val` of 9 on a branch and add to it 1 just for the sake of it

```python
from phi import P, Rec, Read, Write, Val

[result, s, val] = P.Pipe(
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
from phi import P, Rec, Read, Write, Val, If

[result, s, val] = P.Pipe(
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
            Val("Sorry, come back latter.")
        )
    ]
)

assert result == 0.5
assert s == 5
assert val == "Sorry, come back latter."
```

Now, what you have to understand that everything you've done with these expression is to create and apply a single function. Using `Make` we can get the standalone function and then use it to get the same values as before

```python
from phi import P, Rec, Read, Write, Val, If

f = P.Make(
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
            Val("Sorry, come back latter.")
        )
    ]
)

[result, s, val] = f(1.0)

assert result == 0.5
assert s == 5
assert val == "Sorry, come back latter."
```
### Other Examples

```python
from phi import P, Obj

avg_word_length = P.Pipe(
    "1 22 333",
    Obj.split(" "), # ['1', '22', '333']
    P.map(len), # [1, 2, 3]
    P.sum() / P.len() # sum([1,2,3]) / len([1,2,3]) == 6 / 3 == 2
)

assert 2 == avg_word_length
```

```python
from phi import P

assert False == P.Pipe(
    [1,2,3,4],
    P.filter(P % 2 != 0)   #[1, 3], keeps odds
    .Contains(4)   #4 in [1, 3] == False
)
```

```python
from phi import P, Obj, Ref

assert {'a': 97, 'b': 98, 'c': 99} == P.Pipe(
    "a b c", Obj
    .split(' ').Write.keys  # keys = ['a', 'b', 'c']
    .map(ord),  # [ord('a'), ord('b'), ord('c')] == [97, 98, 99]
    lambda it: zip(Ref.keys, it),  # [('a', 97), ('b', 98), ('c', 99)]
    dict   # {'a': 97, 'b': 98, 'c': 99}
)
```

## Installation

    pip install phi


#### Bleeding Edge

    pip install git+https://github.com/cgarciae/phi.git@develop

## Status
* Version: **0.4.1**.
* Documentation coverage: 100%. Please create an issue if documentation is unclear, its of great priority for this library.
* Milestone: reach 1.0.0 after feedback from the community.
