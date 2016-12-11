# Phi
Python is a very nice language that favors readability but its not very strong at functional programming and this often leads to repetitive code. Phi intends to remove as much of the pain as possible from your functional programming experience in Python by providing the following modules

* [dsl](https://cgarciae.github.io/phi/dsl.m.html): a small DSL that helps you compose computations in various ways & more.
* [lambdas](https://cgarciae.github.io/phi/lambdas.m.html): easy way to create quick lambdas with a mathematical flavor.
* [builder](https://cgarciae.github.io/phi/builder.m.html): an extensible class that enables you to integrate other libraries into the DSL through a [fluent](https://en.wikipedia.org/wiki/Fluent_interface) API.
* [patch](https://cgarciae.github.io/phi/patch.m.html): this module contains some helpers that enable you to integrate a complete existing module or class into the DSL be registering its methods/functions into a [Builder](https://cgarciae.github.io/phi/builder.m.html#phi.builder.Builder).

## Documentation
Check out the [complete documentation](https://cgarciae.github.io/phi/).

## Getting Started
The global `phi.P` object exposes most of the API and preferably should be imported directly. The most simple thing the DSL does is function composition:

```python
from phi import P

def add1(x): return x + 1
def mul3(x): return x * 3

x = P.Pipe(
    1,     #input 1
    add1,  #1 + 1 == 2
    mul3   #2 * 3 == 6
)

assert x == 6
```

Use phi [lambdas](https://cgarciae.github.io/phi/lambdas.m.html) to create the functions

```python
from phi import P

x = P.Pipe(
    1,      #input 1
    P + 1,  #1 + 1 == 2
    P * 3   #2 * 3 == 6
)

assert x == 6
```

Create a branched computation instead

```python
from phi import P

[x, y] = P.Pipe(
    1,  #input 1
    [
        P + 1  #1 + 1 == 2
    ,
        P * 3  #1 * 3 == 3
    ]
)

assert x == 2
assert y == 3
```

Compose it with a multiplication by 2 (`P * 2`)

```python
from phi import P

[x, y] = P.Pipe(
    1,  #input 1
    P * 2,  #1 * 2 == 2
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
    1,  #input 1
    P * 2,  #1 * 2 == 2
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
    1,  #input 1
    P * 2,  #1 * 2 == 2
    dict(
        x = P + 1  #2 + 1 == 3
    ,
        y = P * 3  #2 * 3 == 6
    ),
    Rec.x / Rec.y  #3 / 6 == 0.5
)

assert result == 0.5
```

Save the value from the `P * 2` computation as `s` and load it at the end in a branch

```python
from phi import P, Rec

[result, s] = P.Pipe(
    1,  #input 1
    P * 2, {{'s'}}  #2 * 1 == 2, saved as 's'
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

Add 3 to the `s` loaded s... because you can

```python
from phi import P, Rec, Read

[result, s] = P.Pipe(
    1,  #input 1
    P * 2, {{'s'}}  #2 * 1 == 2, saved as 's'
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

Use the `Write` object instead of `{{...}}` just because

```python
from phi import P, Rec, Read, Write

[result, s] = P.Pipe(
    1,  #input 1
    P * 2, Write.s  #2 * 1 == 2, saved as 's'
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
from phi import P, Rec, Val

[result, s, val] = P.Pipe(
    1,  #input 1
    P * 2, Write.s  #2 * 1 == 2, saved as 's'
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

## Installation

    pip install phi


#### Bleeding Edge

    pip install git+https://github.com/cgarciae/phi.git@develop

## Status
* Version: **{0}**.
* Current effort: Documentation (> 60%). Please create an issue if documentation is unclear, its of great priority for this library.
* Milestone: reach 1.0.0 after docs completed + feedback from the community.

## Nice Examples

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
