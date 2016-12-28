from phi.api import *
from phi import dsl
import pytest

class TestDSL(object):
    """docstring for TestDSL."""

    def test_compile(self):
        f = Seq(P + 1, P * 2)
        assert f(2) == 6

    def test_read(self):
        refs = dict(
            x = 10
        )

        f = Read('x')

        y, new_refs = f(None, True, **refs)

        assert refs == new_refs #read doesnt modify
        assert y == 10

    def test_write(self):
        r = dsl.Ref('r')
        f = Seq(
            Write(a = P + 1),
            Write(b = P * 2),
            Write(c = P * 100),
            List(Read.c, Read.a, Read.b)
        )

        assert [600, 3, 6] == f(2)

        r = Ref('r')
        f = Seq(
            Write(a = P + 1),
            Write(b = P * 2),
            Write(c = P * 100), r.write,
            List(Read.c, Read.a, Read.b)
        )

        assert [600, 3, 6] == f(2)
        assert r() == 600

    def test_write_tree(self):

        f = Seq(
            P + 1,
            P * 2,
            List(
                Write(c = P * 100)
            ,
                P - 3
            ,
                Read.c
            )
        )

        assert [600, 3, 600] == f(2)

    def test_write_tree(self):

        f = Seq(
            P + 1,
            P * 2,
            List(
                P * 100
            ,
                Write(c = P)
            ,
                P - 3
            ,
                Read('c')
            )
        )

        assert [600, 6, 3, 6] == f(2)

    def test_input(self):
        f = Seq(
            Write(a = P),
            P + 1,
            List(
                Seq(
                    10,
                    P * 2
                )
            ,
                Read('a')
            ,
                P
            )
        )

        assert [20, 2, 3] == f(2)

    def test_identities(self):

        f = List(
            Seq(),
            List()
        )

        assert [4, []] == f(4)

    def test_single_functions(self):

        f = List(
            P * 2,
            List(P + 1)
        )

        assert [2, [2]] == f(1)

    def test_class(self):

        f = Seq(
            str,
            P + '0',
            int
        )
        assert 20 == f(2)


        ast = dsl._parse(str)
        assert type(ast) is dsl.Expression

    def test_list(self):
        f = Seq(
            List(
                P + 1
            ,
                P * 2
            ),
            List(
                Seq(
                    lambda l: map(str, l),
                    list
                )
            ,
                P
            )
        )

        assert [['4', '6'], [4, 6]] == f(3)

    def test_dict(self):
        f = Seq(
            Dict(
                original = P,
                upper = Obj.upper(),
                len = len
            ),
            List(
                P
            ,
                Seq(
                    Rec.len,
                    P * 2
                )
            )
        )

        [obj, double_len] = f("hello")

        assert obj.original == "hello"
        assert obj.upper == "HELLO"
        assert obj.len == 5
        assert double_len == 10

    def test_fn(self):

        assert "hola" == P.Pipe(
            "HOLA",
            Obj.lower()
        )

    def test_record_object(self):

        x = P.Pipe(
            [1,2,3],
            Dict(
                sum = sum
            ,
                len = len
            )
        )

        assert x.sum == 6
        assert x.len == 3

        assert x['sum'] == 6
        assert x['len'] == 3

    def test_compile_refs(self):

        x = P.Pipe(
            [1,2,3],
            Dict(
                sum = sum
            ,
                len = len
            ,
                x = Read.x
            ,
                z = Read('y') + 2
            ),
            refs = dict(
                x = 10,
                y = 5
            )
        )

        assert x.sum == 6
        assert x.len == 3
        assert x.x == 10
        assert x.z == 7

        assert x['sum'] == 6
        assert x['len'] == 3
        assert x['x'] == 10
        assert x['z'] == 7

        #############################


        f = P.Seq(
            If( P > 2,
                Write(s = P)
            ),
            Read('s')
        )

        assert f(3) == 3

        with pytest.raises(Exception):
            f(1)


    def test_nested_compiles(self):

        assert 2 == P.Pipe(
            1, Write(s = P),
            Seq(
                Write(s = P + 1)
            ),
            Write(s = P)
        )

    def test_if(self):

        f = P.Seq(
            If( P > 0,
                P
            ).Else(
                0
            )
        )

        assert f(5) == 5
        assert f(-3) == 0

    def test_right_hand(self):

        f = Seq(
            P + 1,
            [ P, 2, 3 ]
        )
        assert f(0) == [ 1, 2, 3 ]

        f = Seq(
            P + 1,
            ( P, 2, 3 )
        )
        assert f(0) == ( 1, 2, 3 )

        f = Seq(
            P + 1,
            { P, 2, 3 }
        )
        assert f(0) == { 1, 2, 3 }


        f = Seq(
            P + 1,
            {"a": P, "b": 2, "c": 3 }
        )
        assert f(0) == {"a": 1, "b": 2, "c": 3 }


    def test_readlist(self):

        assert [2, 4, 22] == Pipe(
            1,
            Write(a = P + 1),  #a = 1 + 1 == 2
            Write(b = P * 2),  #b = 2 * 2 == 4
            P * 5,   # 4 * 5 == 20
            P + 2,   # 20 + 2 == 22
            ReadList('a', 'b', P)  # [a, b, 22] == [2, 4, 22]
        )
