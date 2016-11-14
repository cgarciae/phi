# Basics
Here we will cover the basics of Tensor Builder, for this we will solve one of the simplest classical examples in the history of neural network: the XOR.

We will assume that you have already installed TensorBuilder, if not click [here](https://cgarciae.gitbooks.io/phi/content/). Remember that you must have a working installation of TensorFlow.

## Setup
First we will setup our imports, you'll need to have `numpy` installed.

```python
import numpy as np

import tensorflow as tf
from phi import tb
```

As you see `tb` is **not** an alias for the `phi` module, its actually an object that we import from this library. There are several reason behind exposing the API as an object, one is that implementing it this way reduced a lot of code internally, but it also plays better with the DSL as you might see later.

> **Note:** `tb` is of type `Applicative` and all of its methods are immutable, so down worry about "breaking" it.

Next we are going to create our data and placeholders

```python
#TRUTH TABLE (DATA)
X =     [[0.0,0.0]]; Y =     [[0.0]]
X.append([1.0,0.0]); Y.append([1.0])
X.append([0.0,1.0]); Y.append([1.0])
X.append([1.0,1.0]); Y.append([0.0])

X = np.array(X)
Y = np.array(Y)

x = tf.placeholder(tf.float32, shape=[None, 2])
y = tf.placeholder(tf.float32, shape=[None, 1])
```

## Building Networks
Now we need to construct smallest the neural network that can solve the XOR, its architecture is going to be `[2 input, 2 sigmoid, 1 sigmoid]`. To do that we will first calculate the `logit` of the last layer, and then using it we will calculate 2 things:

1. The `activation` function (sometimes denoted `h`) by using the `sigmoid` function
2. The networks `trainer` by creating a loss function and feeding it to a training algorithm.

Here is the code

```python
logit = (
    tb
    .build(x)
    .sigmoid_layer(2)
    .linear_layer(1)
)

activation = (
  logit
  .sigmoid()
  .tensor()
)

trainer = (
  logit
  .sigmoid_cross_entropy_with_logits(y) # loss
  .map(tf.train.AdamOptimizer(0.01).minimize)
  .tensor()
)
```

As you see `TensorBuilder`s API is fluent, meaning that you can keep chaining methods to *build* the computation.

### The Builder class
The first thing we should talk about when reviewing this code is the `Builder` class. When we executed

```python
tb
.build(x)
```

we created a `Builder` that holds our input Tensor `x`. Having our `Builder` we proceeded to use the methods

```python
.sigmoid_layer(2)
.linear_layer(1)
```

If the acronym "What You Read is Mostly What You Get (WYRMWYG)" were a thing, this code would be it. Its telling you that the input is connected to a layer of *2 sigmoid* units, and then this is connected to a layer of *1 linear* unit. You might be wondering where do these methods come from? Or what kinds of methods are there?

#### Method Families

`TensorBuilder` decided to become a library that doesn't implement the core methods that actually deal with Tensors. Instead it has some class methods to **register** instance methods and during import we actually include a bunch of functions from other libraries (yeah we are basically just stealing other libraries for the greater good). Currently most of these methods come from the `tensorflow` library, but there are also some from `tflearn`. The the current practice is the following

1. The function `tf.contrib.layers.fully_connected` is a very special function that is registered as a method of this class. Its importance is due to the fact that the most fundamental operations in the creation of neural networks involve creating/connecting layers.
2. If `f` is a funciton in `tf` or `tf.nn`, it will *most likely* be registered as method of the `Builder` class. The process that registers these functions *lifts* them from being functions that accept a `Tensor` (plus some extra arguments) to functions that accept a `Builder` (plus some extra arguments). Due to this, not all methods will work as expected, an obvious example is [tf.placeholder](https://www.tensorflow.org/versions/r0.9/api_docs/python/io_ops.html#placeholder), this function is automatically included but it doesn't take a Tensor as its first parameter so it doesn't make any sense a method of this class. Right now the current policy of which of these functions are include/exclude is a blacklist approach so that only functions that are known to cause serious problems (like having the same name as basic methods) are excluded and all the functions you are likely going to use are included.
3. Based on point 1 and 2, the next set of function are defined as: if `f` is a function in `tf` or `tf.nn` with name `fname`, then the method `fname_layer` exists in this class. These methods use `fully_connected` and `f` to create a layer with `f` as its activation function. While you don't REALLY need them, `.softmax_layer(5)` reads much better than `.fully_connected(5, activation_fn=tf.nn.softmax)`.

#### Using the methods

So we used the methods `.sigmoid_layer(2)` and `.linear_layer(1)` to create our `logit`. Now to create the `activation` function (rather Tensor) of our network we did the following

```python
activation = (
  logit
  .sigmoid()
  .tensor()
)
```

This was basically just applying `tf.sigmoid` over the `logit`. The method `.tensor` allows us to actually get back the `Tensor` inside the Builder.

#### The map method

Finally we created our network `trainer` doing the following

```python
trainer = (
  logit
  .sigmoid_cross_entropy_with_logits(y) # loss
  .map(tf.train.AdamOptimizer(0.01).minimize)
  .tensor()
)
```

Initially we just indirectly applyed the function `tf.nn.sigmoid_cross_entropy_with_logits` over the `login` and the target's placeholder `y`, to get out our *loss* Tensor. But then we used a custom method from the `Builder` class: [map](http://cgarciae.github.io/phi/core/index.html#phi.core.BuilderBase.map).

`map` takes any function that accepts a Tensor as its first parameter (and some extra arguments), applies that function to the Tensor inside our Builder (plus the extra arguments), and returns a Builder with the new Tensor. In this case our function was the *unbounded method* `minimize` of the `AdamOptimizer` instace (created in-line) that expect a loss Tensor and returns a Tensor that performs the computation that trains our network.

The thing is, given that we have `map` we actually don't REALLY need most of the other methods! We could e.g. have written the initial structure of our network like this

```python
logit = (
    tb
    .build(x)
    .map(tf.contrib.layers.fully_connected, 2, activation_fn=tf.nn.sigmoid)
    .map(tf.contrib.layers.fully_connected, 1, activation_fn=None)
)
```

instead of

```python
logit = (
    tb
    .build(x)
    .sigmoid_layer(2)
    .linear_layer(1)
)
```

but as you see the latter is more compact and readable. The important thing is that you understand that you can use `map` to incorporate functions not registered in the Builder class naturally into the computation.

## Training
Finally, given that we have constructed the `trainer` and `activation` Tensors, lets use regular TensorFlow operations to trainer the network. We will train for 2000 epochs using full batch training (given that we only have 4 training examples) and then print out the prediction for each case of the XOR using the `activation` Tensor.

```python
# create session
sess = tf.Session()
sess.run(tf.initialize_all_variables())

# train
for i in range(2000):
    sess.run(trainer, feed_dict={x: X, y: Y})

# test
for i in range(len(X)):
    print "{0} ==> {1}".format(X[i], sess.run(activation, feed_dict={x: X[i:i+1,:]}))
```

Congratulations! You have just solved the XOR problem using TensorBuilder. Not much of a feat for a serious Machine Learning Engineer, but you have the basic knowledge of the TensorBuilder API.

## What's Next?
In the next chapters you will learn how to create branched neural networks (important in many architectures), use scoping mechanisms to specify some attributes about the Tensor we build, and explore the Domain Specific Language (DSL) using all the previous knowledge to enable you to code even faster.

