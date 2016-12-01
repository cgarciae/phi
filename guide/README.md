# Phi
Python is a very nice language that favor readability, its not very strong at functional programming and this often leads to repetitive code.
Phi is a library for [fluent](https://en.wikipedia.org/wiki/Fluent_interface) functional programming in Python which includes a DSL based on [applicatives](http://learnyouahaskell.com/functors-applicative-functors-and-monoids) + a Builder class that helps you to port/create libraries that integrate with the DSL.

#### Goals

* Comming Soon!

## DSL
Phi uses a DSL that allows you to express complex computations by building on simple functions

### Composing
The most simple thing the DSL does is function composition

    from phi import Compile

    f = Compile(
      lambda x: x + 1,
      lambda x: x * 2,
      lambda x: x + 3
    )

    assert 11 == f(3)

The above computation is the same as:

    f(x) = (x + 1) * 2 + 3

Using `fn.py`s `_` object included with Phi one can rewrite the previous code as:

    from phi import Compile, _

    f = Compile(
      _ + 1,
      _ * 2,
      _ + 3
    )

    assert 11 == f(3)

In general, if express function composition

    lambda f, g: lambda x: f(g(x))

as

    f . g

then

    Compile(f1, f2, ..., fn-1, fn) = fn . fn-1 . (...) . f2 . f1

in other words functions are composed backwards to express the natural flow of the computation.

##### P

You can also *P*ipe a value directly into an expression with the *P* object

    from phi import P, _

    assert 11 == P(
      3,
      _ + 1,
      _ * 2,
      _ + 3
    )

Most of the time this is more convenient, plus `P` contains some helper methods that we will see later, so `P` will be used instead of `Compile` from here on.

### Branching
Branching is express via lists and allows you to express a branched computation where a list with the values of the different paths is returned.

    import phi import P, _

    assert [8, 7] == P(
      3,
      _ + 1,
      [
        _ * 2
      ,
        _ + 3
      ]
    )

the above computation is the same as

    f(x) = [(x + 1) * 2, (x + 1) + 3]

Branching has some subtle rules that you should checkout on the DSL's documentation.

## Installation

    pip install phi==0.1.1



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
