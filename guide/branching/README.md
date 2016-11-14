# Branching

Branching is common in many neural networks that need to resolve complex tasks because each branch to specialize its knowledge while lowering number of weight compared to a network with wider layers, thus giving better performance. TensorBuilder enables you to easily create nested branches. Branching results in a `BuilderTree`, which has methods for traversing all the `Builder` leaf nodes and reducing the whole tree to a single `Builder`.

To create a branch you just have to use the `Builder.branch` method

    import tensorflow as tf
    from phi import tb

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

Thanks to TensorBuilder's immutable API, each branch is independent. The previous can also be simplified with the full `patch`

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
