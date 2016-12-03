import tensorflow as tf
from phi import ph, Builder, _, C, P
import math
# from phi import tb

add2 = _ + 2
mul3 = _ * 3
get_list = lambda x: [1,2,3]
a2_plus_b_minus_2c = lambda a, b, c: a ** 2 + b - 2*c


@Builder.Register1("test.lib")
def add(a, b):
    """Some docs"""
    return a + b

@Builder.Register2("test.lib")
def pow(a, b):
    return a ** b

@Builder.RegisterMethod("test.lib")
def get_function_name(self):
    return self._f.__name__

class DummyContext:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self.value
    def __exit__(self, type, value, traceback):
        pass


class TestBuilder(object):
    """docstring for TestBuilder"""

    @classmethod
    def setup_method(self):
        self.x = tf.placeholder(tf.float32, shape=[None, 5])

    def test_C_1(self):
        assert ph.Map(add2)(4) == 6
        assert ph.Map(add2).Map(mul3)(4) == 18

        assert ph.Compile(add2)(4) == 6
        assert ph.Compile(add2, mul3)(4) == 18

    def test_methods(self):
        assert 9 == ph.Pipe(
            "hello world !!!",
            _.split(" "),
            ph.filter(ph.Contains("wor").Not)
            .map(len),
            sum,
            _ + 0.5,
            round
        )

        assert not ph.Pipe(
            [1,2,3],
            ph.Contains(5)
        )

        class A(object):
            def something(self, x):
                return "y" * x


        assert "yyy" == ph.Pipe(
            A(),
            _.something(3) #used something
        )

    def test_rrshift(self):
        builder = ph.Compile(
            _ + 1,
            _ * 2,
            _ + 4
        )

        assert 10 == 2 >> builder

    def test_compose(self):
        f = ph.Compile(
            _ + 1,
            _ * 2,
            _ + 4
        )

        assert 10 == f(2)


    def test_compose_list(self):
        f = ph.Compile(
            _ + 1,
            _ * 2, {'x'},
            _ + 4,
            [
                _ + 2
            ,
                _ / 2
            ,
                'x'
            ]
        )

        assert [12, 5, 6] == f(2)

    def test_compose_list_reduce(self):
        f = ph.Compile(
            _ + 1,
            _ * 2,
            _ + 4,
            [
                _ + 2
            ,
                _ / 2
            ],
            sum
        )

        assert 17 == f(2)

    def test_random(self):

        assert 9 == ph.Pipe(
            "Hola Cesar",
            _.split(" "),
            ph.map(len)
            .sum()
        )

    def test_0(self):
        from datetime import datetime
        import time

        t0 = datetime.now()

        time.sleep(0.01)

        t1 = 2 >> ph.Compile(
            _ + 1,
            ph.Map0(datetime.now)
        )

        assert t1 > t0

    def test_1(self):
        assert 9 == 2 >> ph.Compile(
            _ + 1,
            ph.Map(math.pow, 2)
        )

    def test_2(self):
        assert [2, 4] == [1, 2, 3] >> ph.Compile(
            ph.Map2(map, _ + 1),
            ph.Map2(filter, _ % 2 == 0)
        )

        assert [2, 4] == ph.Pipe(
            [1, 2, 3],
            ph.Map2(map, _ + 1),
            ph.Map2(filter, _ % 2 == 0)
        )


    def test_underscores(self):
        assert ph.Map(a2_plus_b_minus_2c, 2, 4)(3) == 3 # (3)^2 + 2 - 2*4
        assert ph.Map2(a2_plus_b_minus_2c, 2, 4)(3) == -1 # (2)^2 + 3 - 2*4
        assert ph.Map3(a2_plus_b_minus_2c, 2, 4)(3) == 2 # (2)^2 + 4 - 2*3

    def test_pipe(self):
        assert ph.Pipe(4, add2, mul3) == 18

        assert [18, 14] == ph.Pipe(
            4,
            [
            (
                add2,
                mul3
            )
            ,
            (
                mul3,
                add2
            )
            ]
        )

        assert [18, 18, 15, 16] == ph.Pipe(
            4,
            [
                (
                    add2,
                    mul3
                )
            ,
                [
                    (
                        add2,
                        mul3
                    )
                ,
                    (
                        mul3,
                        add2,
                        [
                            _ + 1,
                            _ + 2
                        ]
                    )
                ]
            ],
            flatten=True
        )

        assert [18, [18, 14, get_list(None)]] == ph.Pipe(
            4,
            [
            (
                add2,
                mul3
            )
            ,
                [
                (
                    add2,
                    mul3
                )
                ,
                (
                    mul3,
                    add2
                )
                ,
                    get_list
                ]
            ]
        )

        [a, [b, c]] = ph.Pipe(
            4,
            [
            (
                add2,
                mul3
            )
            ,
                [
                (
                    add2,
                    mul3
                )
                ,
                (
                    mul3,
                    add2
                )
                ]
            ]
        )

        assert a == 18 and b == 18 and c == 14

    def test_scope(self):
        y = ph.Ref('y')

        z = ph.Pipe(
            self.x,
            ph.With( tf.name_scope('TEST'),
            (
                _ * 2,
                _ + 4,
                { y }
            )),
            _ ** 3
        )

        assert "TEST/" in y().name
        assert "TEST/" not in z.name

    def test_register_1(self):

        #register
        assert 5 == ph.Pipe(
            3,
            ph.add(2)
        )

        #Register2
        assert 8 == ph.Pipe(
            3,
            ph.pow(2)
        )

        #RegisterMethod
        assert "identity" == ph.get_function_name()

    def test_reference(self):
        add_ref = ph.Ref('add_ref')

        assert 8 == 3 >> ph.Compile(ph.add(2).On(add_ref).add(3))
        assert 5 == add_ref()

    def test_ref_props(self):

        a = ph.Ref('a')
        b = ph.Ref('b')

        assert [7, 3, 5] == ph.Pipe(
            1,
            add2, a.set,
            add2, b.set,
            add2,
            [
                (),
                a,
                b
            ]
        )

    def test_scope_property(self):

        assert "some random text" == ph.Pipe(
            "some ",
            ph.With( DummyContext("random "),
            (
                lambda s: s + ph.Scope(),
                ph.With( DummyContext("text"),
                    lambda s: s + ph.Scope()
                )
            )
            )
        )

        assert ph.Scope() == None

    def test_ref_integraton_with_dsl(self):

        y = ph.Ref('y')


        assert 5 == ph.Pipe(
            1,
            _ + 4,
            ph.On(y),
            _ * 10,
            'y'
        )

        assert 5 == ph.Pipe(
            1,
            _ + 4,
            ph.On(y),
            _ * 10,
            'y'
        )

        assert 5 == ph.Pipe(
            1,
            _ + 4,
            ph.On('y'),
            _ * 10,
            'y'
        )

    def test_list(self):

        assert [['4', '6'], [4, 6]] == ph.Pipe(
            3,
            [
                _ + 1
            ,
                _ * 2
            ],
            [
                ph.Map2(map, str)
            ,
                ()
            ]
        )
