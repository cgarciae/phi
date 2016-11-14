# DSL

TensorBuilder's DSL enables you to express the computation do desire to do into a single flexible structure. The DSL preserves all features of given to you by the `Builder` class:

* Composing operations
* Branching
* Scoping

The `Applicative` was built to create elements that are accepted/play well will this language. It also two very import methods

* `compile`: generates a function out a given valid **ast**/structure (compiles it)
* `pipe`: given `Builder` or `Tensor` and an **ast**, compile it to a function and apply it to the Tensor/Builder.

## Rules

* All final elements in the "AST" must be functions, non final elements are compiled to a function.
* A Tuple `()` denotes a sequential operation. Results in the composition of all elements within it.
* A List `[]` denotes a branching operation. Results in the creation of a function that applies the `.branch` method to its argument, and each element in the list results in a branch. It compiles to a function of type `Builder -> BuilderTree`.
* A Dict `{}` denotes a scoping operation. It only accepts a single key-value pair, its key must me a [Disposable](https://www.python.org/dev/peps/pep-0343/) and its value can be any element of the language. It results in the creation of a function that takes a `Builder` as its argument, applies the `with` statemente to the `key` and applies the function of the `value` to its argument inside the `with` block.

## Example

Its easier to see the actual DSL with an example, especially because you can see a direct mapping of the concepts brought by the `Builder` class into the DSL:

    import tensorflow as tf
    from phi import tb

    x = placeholder(tf.float32, shape=[None, 10])
    y = placeholder(tf.float32, shape=[None, 5])

    [h, trainer] = tb.pipe(
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
        tb.relu_layer(10)
        .linear_layer(5),
        [
            tb.softmax() # h
        ,
            tb.softmax_cross_entropy_with_logits(y)
            .reduce_mean()
            .map(tf.trainer.AdamOptimizer(0.01).minimize) # trainer
        ],
        tb.tensors()
    )

Lets go step by step to what is happening here:

1. The Tensor `x` pluged inside a `Builder` and *piped* through the computational structured defined. All the arguments of `pipe` after `x` are grouped as if they were in a tuple `()` and the whole expression is compiled to a single function with is then applied to the `Buider` containing `x`.
1. **final** elements you see here like `tb.softmax()` are `Applicative`s which as you've been told are functions. As you see, *almost* all methods from the `Builder` class are also methods from the `Applicative` class, the diference is that the methods of the `Builder` class actually perform the computation they intend (construct a new Tensor), but the methods from the `Applicative` class rather *compose/define* the computation to be done later.
1. There is an implicit Tuple `()` element that is performing a sequential composition of all the other elements. As a result, the visual/spatial ordering of the code corresponds to the intended behavior.
1. Lists very naturally express branches. Notice how indentation and an intentional positioning of the `,` comma help to diferentiate each branch.
1. Expresions like `tb.relu_layer(10)` are polymorphic and work for `Builder`s or `BuilderTree`s regardless.
1. Scoping is very clean with the `{}` notation. In constrast to using `then_with` from the `Builder` class, here you can actually use the original functions from `tensorflow` unchanged in the `key` of the dict.