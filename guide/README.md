# Phi
Python is a very nice language that favor readability, its not very strong at functional programming and this often leads to repetitive code.
Phi is a library for [fluent](https://en.wikipedia.org/wiki/Fluent_interface) functional programming in Python which includes a DSL based On [applicatives](http://learnyouahaskell.com/functors-applicative-functors-and-monoids) + a Builder class that helps you to port/create libraries that integrate with the DSL.

#### Goals

* Comming Soon!

## DSL
Phi uses a DSL that allows you to express complex computations by building On simple functions

### Composing
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

Using `P` to create quick lambdas we can rewrite the previous as:

```python
from phi import P

f = P.Make(
  P + 1,
  P * 2,
  P + 3
)

assert 11 == f(3)
```

##### Pipe

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

As you the the `[...]` element is compiled to a function that returns a list of values.

## Nice Examples

```python
from phi import P, Obj

text = "a bb ccc"

average_word_length = P.Pipe(
    text,
    Obj.split(" "), # ['a', 'bb', 'ccc']
    P.map(len), # [1, 2, 3]
    P._(sum) / len # 6 / 3 == 2
)

assert 2 == average_word_length
```

## Installation

    pip install phi==0.2.0



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
