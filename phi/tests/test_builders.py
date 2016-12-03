import tensorflow as tf
from phi import P, Builder, C, P, P as P
import math
# from phi import tb

add2 = P + 2
mul3 = P * 3
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
        assert P.Map(add2)(4) == 6
        assert P.Map(add2).Map(mul3)(4) == 18

        assert P.Compile(add2)(4) == 6
        assert P.Compile(add2, mul3)(4) == 18

    def test_methods(self):
        assert 9 == P.Pipe(
            "hello world !!!",
            P.Obj.split(" "),
            P.filter(P.Contains("wor").Not)
            .map(len),
            sum,
            P + 0.5,
            round
        )

        assert not P.Pipe(
            [1,2,3],
            P.Contains(5)
        )

        class A(object):
            def something(self, x):
                return "y" * x


        assert "yyy" == P.Pipe(
            A(),
            P.Obj.something(3) #used something
        )

    def test_rrshift(self):
        builder = P.Compile(
            P + 1,
            P * 2,
            P + 4
        )

        assert 10 == 2 >> builder

    def test_compose(self):
        f = P.Compile(
            P + 1,
            P * 2,
            P + 4
        )

        assert 10 == f(2)


    def test_compose_list(self):
        f = P.Compile(
            P + 1,
            P * 2, {'x'},
            P + 4,
            [
                P + 2
            ,
                P / 2
            ,
                'x'
            ]
        )

        assert [12, 5, 6] == f(2)

    def test_compose_list_reduce(self):
        f = P.Compile(
            P + 1,
            P * 2,
            P + 4,
            [
                P + 2
            ,
                P / 2
            ],
            sum
        )

        assert 17 == f(2)

    def test_random(self):

        assert 9 == P.Pipe(
            "Hola Cesar",
            P.Obj.split(" "),
            P.map(len)
            .sum()
        )

    def test_0(self):
        from datetime import datetime
        import time

        t0 = datetime.now()

        time.sleep(0.01)

        t1 = 2 >> P.Compile(
            P + 1,
            P.Map0(datetime.now)
        )

        assert t1 > t0

    def test_1(self):
        assert 9 == 2 >> P.Compile(
            P + 1,
            P.Map(math.pow, 2)
        )

    def test_2(self):
        assert [2, 4] == [1, 2, 3] >> P.Compile(
            P.Map2(map, P + 1),
            P.Map2(filter, P % 2 == 0)
        )

        assert [2, 4] == P.Pipe(
            [1, 2, 3],
            P.Map2(map, P + 1),
            P.Map2(filter, P % 2 == 0)
        )


    def test_underscores(self):
        assert P.Map(a2_plus_b_minus_2c, 2, 4)(3) == 3 # (3)^2 + 2 - 2*4
        assert P.Map2(a2_plus_b_minus_2c, 2, 4)(3) == -1 # (2)^2 + 3 - 2*4
        assert P.Map3(a2_plus_b_minus_2c, 2, 4)(3) == 2 # (2)^2 + 4 - 2*3

    def test_pipe(self):
        assert P.Pipe(4, add2, mul3) == 18

        assert [18, 14] == P.Pipe(
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

        assert [18, 18, 15, 16] == P.Pipe(
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
                            P + 1,
                            P + 2
                        ]
                    )
                ]
            ],
            flatten=True
        )

        assert [18, [18, 14, get_list(None)]] == P.Pipe(
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

        [a, [b, c]] = P.Pipe(
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
        y = P.Ref('y')

        z = P.Pipe(
            self.x,
            P.With( tf.name_scope('TEST'),
            (
                P * 2,
                P + 4,
                { y }
            )),
            P ** 3
        )

        assert "TEST/" in y().name
        assert "TEST/" not in z.name

    def test_register_1(self):

        #register
        assert 5 == P.Pipe(
            3,
            P.add(2)
        )

        #Register2
        assert 8 == P.Pipe(
            3,
            P.pow(2)
        )

        #RegisterMethod
        assert "identity" == P.get_function_name()

    def test_reference(self):
        add_ref = P.Ref('add_ref')

        assert 8 == 3 >> P.Compile(P.add(2).On(add_ref).add(3))
        assert 5 == add_ref()

    def test_ref_props(self):

        a = P.Ref('a')
        b = P.Ref('b')

        assert [7, 3, 5] == P.Pipe(
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

        assert "some random text" == P.Pipe(
            "some ",
            P.With( DummyContext("random "),
            (
                lambda s: s + P.Scope(),
                P.With( DummyContext("text"),
                    lambda s: s + P.Scope()
                )
            )
            )
        )

        assert P.Scope() == None

    def test_ref_integraton_with_dsl(self):

        y = P.Ref('y')


        assert 5 == P.Pipe(
            1,
            P + 4,
            P.On(y),
            P * 10,
            'y'
        )

        assert 5 == P.Pipe(
            1,
            P + 4,
            P.On(y),
            P * 10,
            'y'
        )

        assert 5 == P.Pipe(
            1,
            P + 4,
            P.On('y'),
            P * 10,
            'y'
        )

    def test_list(self):

        assert [['4', '6'], [4, 6]] == P.Pipe(
            3,
            [
                P + 1
            ,
                P * 2
            ],
            [
                P.Map2(map, str)
            ,
                ()
            ]
        )
