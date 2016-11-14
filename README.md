# Phi
TensorBuilder is light-weight extensible library that enables you to easily create complex deep neural networks through a functional [fluent](https://en.wikipedia.org/wiki/Fluent_interface) [immutable](https://en.wikipedia.org/wiki/Immutable_object) API based on the Builder Pattern. Tensor Builder also comes with a DSL based on [applicatives](http://learnyouahaskell.com/functors-applicative-functors-and-monoids) and function composition that enables you to express more clearly the structure of your network, make changes faster, and reuse code.

### Goals

* Be a light-wrapper around Tensor-based libraries
* Enable users to easily create complex branched topologies while maintaining a fluent API (see [Builder.branch](http://cgarciae.github.io/phi/api/builder.m.html#phi.api.builder.Builder.branch))
* Let users be expressive and productive through a DSL

## Installation
Tensor Builder assumes you have a working `tensorflow` installation. We don't include it in the `requirements.txt` since the installation of tensorflow varies depending on your setup.

#### From pypi
```
pip install phi==0.1.0

```

#### From github
For the latest development version
```
pip install git+https://github.com/cgarciae/phi.git@develop
```

## Getting Started

Create neural network with a [5, 10, 3] architecture with a `softmax` output layer and a `tanh` hidden layer through a Builder and then get back its tensor:

    import tensorflow as tf
    from phi import tb

    x = tf.placeholder(tf.float32, shape=[None, 5])
    keep_prob = tf.placeholder(tf.float32)

    h = (
      tb
      .build(x)
      .tanh_layer(10) # tanh(x * w + b)
      .dropout(keep_prob) # dropout(x, keep_prob)
      .softmax_layer(3) # softmax(x * w + b)
      .tensor()
    )

## Features
* **Branching**: Enable to easily express complex complex topologies with a fluent API. See [Branching](https://cgarciae.gitbooks.io/phi/content/branching/).
* **Scoping**: Enable you to express scopes for your tensor graph val methods such as `tf.device` and `tf.variable_scope` with the same fluent API. [Scoping](https://cgarciae.gitbooks.io/phi/content/scoping/).
* **DSL**: Use an abbreviated notation with a functional style to make the creation of networks faster, structural changes easier, and reuse code. See [DSL](https://cgarciae.gitbooks.io/phi/content/dsl/).
* **Patches**: Add functions from other Tensor-based libraries as methods of the Builder class. TensorBuilder gives you a curated patch plus some specific patches from `TensorFlow` and `TFLearn`, but you can build you own to make TensorBuilder what you want it to be. See [Patches](https://cgarciae.gitbooks.io/phi/content/patches/).

## Documentation
* [Complete API](http://cgarciae.github.io/phi/api/index.html).
* [Core API](http://cgarciae.github.io/phi/core/index.html).
* [Complete Documentation](http://cgarciae.github.io/phi/index.html)

## The Guide
Check out [The Guide](https://cgarciae.gitbooks.io/phi/content/) to learn to code in TensorBuilder.

## Full Example
Next is an example with all the features of TensorBuilder including the DSL, branching and scoping. It creates a branched computation where each branch is executed on a different device. All branches are then reduced to a single layer, but the computation is the branched again to obtain both the activation function and the trainer.

    import tensorflow as tf
    from phi import tb

    x = placeholder(tf.float32, shape=[None, 10])
    y = placeholder(tf.float32, shape=[None, 5])

    [activation, trainer] = tb._pipe(
        x,
        [
            { tf.device("/gpu:0"):
                tb.relu_layer(20)
            }
        ,
            { tf.device("/gpu:1"):
                tb.sigmoid_layer(20)
            }
        ,
            { tf.device("/cpu:0"):
                tb.tanh_layer(20)
            }
        ],
        tb.linear_layer(5),
        [
            tb.softmax() # activation
        ,
            tb
            .softmax_cross_entropy_with_logits(y) # loss
            .map(tf.train.AdamOptimizer(0.01).minimize) # trainer
        ],
        tb.tensors()
    )
