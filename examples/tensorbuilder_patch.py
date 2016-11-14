
##############################
##### GETTING STARTED
##############################

# TensorBuilder includes a set of primitives that you can use to wrap, around

import tensorflow as tf
from tensorflow.contrib import layers as layers
from phi import tb

x = tf.placeholder(tf.float32, shape=[None, 40])
keep_prob = tf.placeholder(tf.float32)

h = (
	tb.build(x)
	.map(layers.fully_connected, 100, activation_fn=tf.nn.tanh)
	.map(tf.nn.dropout, keep_prob)
	.map(layers.fully_connected, 30, activation_fn=tf.nn.softmax)
	.tensor()
)

print(h)

# The previous is equivalent to this next example using the `slim_patch`, which includes the `fully_connected` method that is taken from `tf.contrib.layers`

import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 5])
keep_prob = tf.placeholder(tf.float32)

h = (
	tb.build(x)
	.fully_connected(10, activation_fn=tf.nn.tanh) # tanh(x * w + b)
	.map(tf.nn.dropout, keep_prob) # dropout(x, keep_prob)
	.fully_connected(3, activation_fn=tf.nn.softmax) # softmax(x * w + b)
	.tensor()
)

print(h)

# The `phi.patch` includes a lot more methods that register functions from the `tf`, `tf.nn` and `tf.contrib.layers` modules plus some custom methods based on `fully_connected` to create layers:

import tensorflow as tf
from phi import tb
import phi.patch

x = tf.placeholder(tf.float32, shape=[None, 5])
keep_prob = tf.placeholder(tf.float32)

h = (
	tb.build(x)
	.tanh_layer(10) # tanh(x * w + b)
	.dropout(keep_prob) # dropout(x, keep_prob)
	.softmax_layer(3) # softmax(x * w + b)
	.tensor()
)

print(h)

##############################
##### BRANCHING
##############################

#To create a branch you just have to use the `phi.phi.Builder.branch` method

import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 5])
keep_prob = tf.placeholder(tf.float32)

h = (
    tb.build(x)
    .fully_connected(10)
    .branch(lambda root:
    [
        root
        .fully_connected(3, activation_fn=tf.nn.relu)
    ,
        root
        .fully_connected(9, activation_fn=tf.nn.tanh)
        .branch(lambda root2:
        [
          root2
          .fully_connected(6, activation_fn=tf.nn.sigmoid)
        ,
          root2
          .map(tf.nn.dropout, keep_prob)
          .fully_connected(8, tf.nn.softmax)
        ])
    ])
    .fully_connected(6, activation_fn=tf.nn.sigmoid)
    .tensor()
)

print(h)

#Thanks to TensorBuilder's immutable API, each branch is independent. The previous can also be simplified with the full `patch`

import tensorflow as tf
from phi import tb
import phi.patch

x = tf.placeholder(tf.float32, shape=[None, 5])
keep_prob = tf.placeholder(tf.float32)

h = (
    tb.build(x)
    .fully_connected(10)
    .branch(lambda root:
    [
        root
        .relu_layer(3)
    ,
        root
        .tanh_layer(9)
        .branch(lambda root2:
        [
          root2
          .sigmoid_layer(6)
        ,
          root2
          .dropout(keep_prob)
          .softmax_layer(8)
        ])
    ])
    .sigmoid_layer(6)
    .tensor()
)

print(h)


##############################
##### DSL
##############################

#Lets see an example, here is the previous example about branching with the the full `patch`, this time using the `dsl` module

import tensorflow as tf
from phi import tb
import phi.patch
import phi.dsl as dl #<== Notice the alias

x = tf.placeholder(tf.float32, shape=[None, 5])
keep_prob = tf.placeholder(tf.float32)

h = tb.build(x).pipe(
    dl.fully_connected(10),
    [
        dl.relu_layer(3)
    ,
        (dl.tanh_layer(9),
        [
          	dl.sigmoid_layer(6)
        ,
			dl
			.dropout(keep_prob)
			.softmax_layer(8)
        ])
    ],
    dl.sigmoid_layer(6)
    .tensor()
)

print(h)

#As you see a lot of noise is gone, some `dl` terms appeared, and a few `,` where introduced, but the end result better reveals the structure of you network, plus its very easy to modify.

## API

##############################
##### FUNCTIONS
##############################


##############################
##### builder
##############################

# The following example shows you how to construct a `phi.phi.Builder` from a tensorflow Tensor.

import tensorflow as tf
from phi import tb

a = tf.placeholder(tf.float32, shape=[None, 8])
a_builder = tb.build(a)

print(a_builder)

# The previous is the same as

a = tf.placeholder(tf.float32, shape=[None, 8])
a_builder = a.builder()

print(a_builder)

##############################
##### branches
##############################

# Given a list of Builders and/or BuilderTrees you construct a `phi.phi.BuilderTree`.

import tensorflow as tf
from phi import tb

a = tf.placeholder(tf.float32, shape=[None, 8]).builder()
b = tf.placeholder(tf.float32, shape=[None, 8]).builder()

tree = tb.branches([a, b])

print(tree)

#`phi.phi.BuilderTree`s are usually constructed using `phi.phi.Builder.branch` of the `phi.phi.Builder` class, but you can use this for special cases



##############################
##### BUILDER
##############################


##############################
##### fully_connected
##############################

# This method is included by many libraries so its "sort of" part of TensorBuilder. The following builds the computation `tf.nn.sigmoid(tf.matmul(x, w) + b)`
import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 5])

h = (
	tb.build(x)
	.fully_connected(3, activation_fn=tf.nn.sigmoid)
	.tensor()
)

print(h)

# Using `phi.patch` the previous is equivalent to

import tensorflow as tf
from phi import tb
import phi.patch

x = tf.placeholder(tf.float32, shape=[None, 5])

h = (
	tb.build(x)
	.sigmoid_layer(3)
	.tensor()
)

print(h)


# You can chain various `fully_connected`s to get deeper neural networks

import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 40])

h = (
	tb.build(x)
	.fully_connected(100, activation_fn=tf.nn.tanh)
	.fully_connected(30, activation_fn=tf.nn.softmax)
	.tensor()
)

print(h)

# Using `phi.patch` the previous is equivalent to

import tensorflow as tf
from phi import tb
import phi.patch

x = tf.placeholder(tf.float32, shape=[None, 5])

h = (
	tb.build(x)
	.tanh_layer(100)
	.softmax_layer(30)
	.tensor()
)

print(h)

##############################
##### map
##############################

#The following constructs a neural network with the architecture `[40 input, 100 tanh, 30 softmax]` and and applies `dropout` to the tanh layer

import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 40])
keep_prob = tf.placeholder(tf.float32)

h = (
	tb.build(x)
	.fully_connected(100, activation_fn=tf.nn.tanh)
	.map(tf.nn.dropout, keep_prob)
	.fully_connected(30, activation_fn=tf.nn.softmax)
	.tensor()
)

print(h)


##############################
##### then
##############################

# The following *manually* constructs the computation `tf.nn.sigmoid(tf.matmul(x, w) + b)` while updating the `phi.tensorbuiler.Builder.variables` dictionary.

import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 40])
keep_prob = tf.placeholder(tf.float32)

def sigmoid_layer(builder, size):
	x = builder.tensor()
	m = int(x.get_shape()[1])
	n = size

	w = tf.Variable(tf.random_uniform([m, n], -1.0, 1.0))
	b = tf.Variable(tf.random_uniform([n], -1.0, 1.0))

	y = tf.nn.sigmoid(tf.matmul(x, w) + b)

	return y.builder()

h = (
	tb.build(x)
	.then(sigmoid_layer, 3)
	.tensor()
)

# Note that the previous if equivalent to
import tensorflow as tf
from phi import tb
import phi.slim_patch
h = (
	tb.build(x)
	.fully_connected(3, activation_fn=tf.nn.sigmoid)
	.tensor()
)

print(h)

##############################
##### branch
##############################

# The following will create a sigmoid layer but will branch the computation at the logit (z) so you get both the output tensor `h` and `trainer` tensor. Observe that first the logit `z` is calculated by creating a linear layer with `fully_connected(1)` and then its branched out

import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 5])
y = tf.placeholder(tf.float32, shape=[None, 1])

[h, trainer] = (
    tb.build(x)
    .fully_connected(1)
    .branch(lambda z:
    [
        z.map(tf.nn.sigmoid)
    ,
        z.map(tf.nn.sigmoid_cross_entropy_with_logits, y)
        .map(tf.train.AdamOptimizer(0.01).minimize)
    ])
    .tensors()
)

print(h)
print(trainer)

# Note that you have to use the `phi.phi.BuilderTree.tensors` method from the `phi.phi.BuilderTree` class to get the tensors back.

# Remember that you can also contain `phi.phi.BuilderTree` elements when you branch out, this means that you can keep branching inside branch. Don't worry that the tree keep getting deeper, `phi.phi.BuilderTree` has methods that help you flatten or reduce the tree.
#The following example will show you how create a (overly) complex tree and then connect all the leaf nodes to a single `sigmoid` layer

import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 5])
keep_prob = tf.placeholder(tf.float32)

h = (
    tb.build(x)
    .fully_connected(10)
    .branch(lambda base:
    [
        base
        .fully_connected(3, activation_fn=tf.nn.relu)
    ,
        base
        .fully_connected(9, activation_fn=tf.nn.tanh)
        .branch(lambda base2:
        [
        	base2
        	.fully_connected(6, activation_fn=tf.nn.sigmoid)
        ,
        	base2
        	.map(tf.nn.dropout, keep_prob)
        	.fully_connected(8, tf.nn.softmax)
        ])
    ])
    .fully_connected(6, activation_fn=tf.nn.sigmoid)
)

print(h)

##############################
##### BUILDER TREE
##############################

##############################
##### builders
##############################

import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 5])
y = tf.placeholder(tf.float32, shape=[None, 1])

[h_builder, trainer_builder] = (
    tb.build(x)
    .fully_connected(1)
    .branch(lambda z:
    [
        z.map(tf.nn.sigmoid)
    ,
        z.map(tf.nn.sigmoid_cross_entropy_with_logits, y)
        .map(tf.train.AdamOptimizer(0.01).minimize)
    ])
    .builders()
)

print(h_builder)
print(trainer_builder)

##############################
##### tensors
##############################

import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 5])
y = tf.placeholder(tf.float32, shape=[None, 1])

[h_tensor, trainer_tensor] = (
    tb.build(x)
    .fully_connected(1)
    .branch(lambda z:
    [
        z.map(tf.nn.sigmoid)
    ,
        z.map(tf.nn.sigmoid_cross_entropy_with_logits, y)
        .map(tf.train.AdamOptimizer(0.01).minimize)
    ])
    .tensors()
)

print(h_tensor)
print(trainer_tensor)

##############################
##### fully_connected
##############################

# The following example shows you how to connect two tensors (rather builders) of different shapes to a single `softmax` layer of shape [None, 3]

import tensorflow as tf
from phi import tb
import phi.slim_patch

a = tf.placeholder(tf.float32, shape=[None, 8]).builder()
b = tf.placeholder(tf.float32, shape=[None, 5]).builder()

h = (
	tb.branches([a, b])
	.fully_connected(3, activation_fn=tf.nn.softmax)
)

print(h)

# The next example show you how you can use this to pass the input layer directly through one branch, and "analyze" it with a `tanh layer` filter through the other, both of these are connect to a single `softmax` output layer

import tensorflow as tf
from phi import tb
import phi.slim_patch

x = tf.placeholder(tf.float32, shape=[None, 5])

h = (
	tb.build(x)
	.branch(lambda x:
	[
		x
	,
		x.fully_connected(10, activation_fn=tf.nn.tanh)
	])
	.fully_connected(3, activation_fn=tf.nn.softmax)
)

print(h)
