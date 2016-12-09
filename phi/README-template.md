# Phi
Python is a very nice language that favors readability but its not very strong at functional programming and this often leads to repetitive code. Phi eases your functional programming experience in Python by providing the following modules

* [dsl](https://cgarciae.github.io/phi/dsl.m.html): a neat way to compose computations + more.
* [lambdas](https://cgarciae.github.io/phi/lambdas.m.html): easy way to create quick lambdas with a mathematical flavor.
* [builder](https://cgarciae.github.io/phi/builder.m.html): an extensible class that enables you to integrate other libraries into the DSL through a [fluent](https://en.wikipedia.org/wiki/Fluent_interface) API.

Also check out the complete [documentation](https://cgarciae.github.io/phi/index.m.html). Even though there are 3 main modules, the `builder` module integrates both the `lambda` and `dsl` modules. The object `phi.P` exposes the entire API and all of the libraries functionalities.

### Mini-Tutorial
The most simple thing the DSL does is function composition

```python
from phi import P

f = P.Make(
  lambda x: x + 1,
  lambda x: x * 2,
  lambda x: x + 3
)

assert 11 == f(3)
```

The above computation is equivalent to

```python
lambda x: (x + 1) * 2 + 3
```

`P.Make` can compile any valid expression of the DSL into a function, what you are seeing here is the compilation of the `*args` tuple. Check out the documentation of the [dsl](https://cgarciae.github.io/phi/dsl.m.html).

Now lets rewrite the previous using `P`'s [lambdas](https://cgarciae.github.io/phi/lambdas.m.html) capabilities

```python
from phi import P

f = P.Make(
  P + 1,
  P * 2,
  P + 3
)

assert 11 == f(3)
```

**Pipe**

You can also pipe a value directly into an expression with `P.Pipe`

```python
from phi import P

assert 11 == P.Pipe(
  3,
  P + 1,
  P * 2,
  P + 3
)
```

### Branching
Sometimes we have do separate computations, this is where branching comes in. It is express via a list (iterable in general) where each element is a different computational path and a list is returned by the Branch element:

```python
import phi import P

assert [0, 4] == P.Pipe(
  1,
  P + 1,
  [
    P * 2
  ,
    P - 2
  ]
)
```

The above computation equivalent to

```python
lambda x: [(x + 1) * 2, (x + 1) - 2]
```

As you the the `[...]` element is compiled to a function that returns a list of values. Check out the documentation of the [dsl](https://cgarciae.github.io/phi/dsl.m.html) for more information.

## Nice Examples

```python
from phi import P, Obj

text = "1 22 33"

avg_word_length = P.Pipe(
    text,
    Obj.split(" "), # ['1', '22', '333']
    P.map(len), # [1, 2, 3]
    P.sum() / P.len() # sum([1,2,3]) / len([1,2,3]) == 6 / 3 == 2
)

assert 2 == avg_word_length
```

## Installation

    pip install phi=={0}


#### Bleeding Edge

    pip install git+https://github.com/cgarciae/phi.git@develop


## Getting Started


## Features
Comming Soon!

## Documentation
[Complete Documentation](http://cgarciae.github.io/phi/index.html)

## The Guide
Check out [The Guide](https://cgarciae.gitbooks.io/phi/content/) to learn to code in Phi. (Comming Soon!)

## Full Example
Comming Soon!
