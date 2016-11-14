# Phi
Phi is a library for [fluent](https://en.wikipedia.org/wiki/Fluent_interface) functional programming in Python which includes a DSL based on [applicatives](http://learnyouahaskell.com/functors-applicative-functors-and-monoids) + facilities to create libraries that integrate with its DSL.

### Goals

* Comming Soon!

## Installation

    pip install phi=={0}


#### Bleeding Edge

    pip install git+https://github.com/cgarciae/phi.git@develop


## Getting Started

import phi import P, _

    assert 8 == P(
      3,
      _ + 1,
      _ * 2
    )

the above computation is the same as

    (3 + 1) * 2

## Features
Comming Soon!

## Documentation
[Complete Documentation](http://cgarciae.github.io/phi/index.html)

## The Guide
Check out [The Guide](https://cgarciae.gitbooks.io/phi/content/) to learn to code in Phi. (Comming Soon!)

## Full Example
Comming Soon!
