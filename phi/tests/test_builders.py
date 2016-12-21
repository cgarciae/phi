from phi import P, Obj, Val, Rec, Context, Read, Write
import math
import pytest
# from phi import tb

add2 = P + 2
mul3 = P * 3
get_list = lambda x: [1,2,3]
a2_plus_b_minus_2c = lambda a, b, c: a ** 2 + b - 2*c


@P.Register("test.lib")
def add(a, b):
    """Some docs"""
    return a + b

@P.Register2("test.lib")
def pow(a, b):
    return a ** b

@P.RegisterMethod("test.lib")
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
        pass

    def test_C_1(self):
        assert P.Then(add2)(4) == 6
        assert P.Then(add2).Then(mul3)(4) == 18

        assert P.Make(add2)(4) == 6
        assert P.Make(add2, mul3)(4) == 18

    def test_methods(self):
        x = P.Pipe(
            "hello world",
            Obj.split(" ")
            .filter(P.Contains("w").Not())
            .map(len)
            .First()
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
        builder = P.Make(
            P + 1,
            P * 2,
            P + 4
        )

        assert 10 == 2 >> builder

    def test_compose(self):
        f = P.Make(
            P + 1,
            P * 2,
            P + 4
        )

        assert 10 == f(2)


    def test_compose_list(self):
        f = P.Make(
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

        f = P.Make(
            P + 1,
            P * 2,
            P + 4,
            [
                (P + 2).Write('x')
            ,
                P / 2
            ,
                'x'
            ]
        )

        assert [12, 5, 12] == f(2)

    def test_compose_list_reduce(self):
        f = P.Make(
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

        t1 = 2 >> P.Make(
            P + 1,
            P.Then0(datetime.now)
        )

        assert t1 > t0

    def test_1(self):
        assert 9 == 2 >> P.Make(
            P + 1,
            P.Then(math.pow, 2)
        )

    def test_2(self):
        assert [2, 4] == [1, 2, 3] >> P.Make(
            P
            .Then2(map, P + 1)
            .Then2(filter, P % 2 == 0)
            .list() #list only needed in Python 3
        )

        assert [2, 4] == P.Pipe(
            [1, 2, 3],
            P
            .Then2(map, P + 1)
            .Then2(filter, P % 2 == 0)
            .list() #list only needed in Python 3
        )


    def test_underscores(self):
        assert P.Then(a2_plus_b_minus_2c, 2, 4)(3) == 3 # (3)^2 + 2 - 2*4
        assert P.Then2(a2_plus_b_minus_2c, 2, 4)(3) == -1 # (2)^2 + 3 - 2*4
        assert P.Then3(a2_plus_b_minus_2c, 2, 4)(3) == 2 # (2)^2 + 4 - 2*3

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

    def test_context(self):
        y = P.Ref('y')

        length = P.Pipe(
            "phi/tests/test.txt",
            P.With( open,
                Context,
                Obj.read(), { y },
                len
            )
        )

        assert length == 11
        assert y() == "hello world"

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

        assert 8 == 3 >> P.Make(P.add(2).Write(add_ref).add(3))
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
                P + P.Context,
                P.With( DummyContext("text"),
                    P + P.Context
                )
            )
            )
        )

        with pytest.raises(Exception):
            P.Context() #Cannot use it outside of With

    def test_ref_integraton_with_dsl(self):

        y = P.Ref('y')


        assert 5 == P.Pipe(
            1,
            P + 4,
            P.Write(y),
            P * 10,
            'y'
        )

        assert 5 == P.Pipe(
            1,
            P + 4,
            P.Write(y),
            P * 10,
            'y'
        )

        assert 5 == P.Pipe(
            1,
            P + 4,
            P.Write('y'),
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
                P.Then2(map, str).list() #list only needed in Python 3
            ,
                ()
            ]
        )

    def test_read_method(self):

        assert 1 == P.Pipe(
            1,
            P + 1, {'s'},
            P * 100,
            's', P - 1
        )

        assert 1 == P.Pipe(
            1,
            P + 1, {'s'},
            P * 100,
            Read('s') - 1
        )

        assert 1 == P.Pipe(
            1,
            P + 1, {'s'},
            P * 100,
            Read.s - 1
        )

        assert 1 == P.Pipe(
            1,
            P + 1, {'s'},
            P * 100,
            Read['s'] - 1
        )

        assert 1 == P.Pipe(
            1,
            P + 1, Write.s,
            P * 100,
            Read.s - 1
        )

        assert 1 == P.Pipe(
            1,
            P + 1, Write('s'),
            P * 100,
            Read.s - 1
        )

        assert 1 == P.Pipe(
            1,
            P + 1, Write['s'],
            P * 100,
            Read.s - 1
        )
