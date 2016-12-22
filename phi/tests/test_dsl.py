from phi.api import *
from phi import dsl
import pytest

class TestDSL(object):
    """docstring for TestDSL."""

    def test_compile(self):
        code = Seq(P + 1, P * 2)
        f = dsl.Compile(code, {})
        assert f(2) == 6

    def test_compile_single_function(self):
        f = P * 2
        code = f
        f_compiled = dsl.Compile(code, {})
        assert f == f_compiled

    def test_read(self):
        refs = dict(
            x = Ref('x', 10)
        )
        code = Read('x')
        f = dsl.Compile(code, refs)

        assert refs == refs #read doesnt modify
        assert f(None) == 10

    def test_write(self):
        r = dsl.Ref('r')
        code = Seq(
            P + 1, Write.a,
            P * 2, Write.b,
            P * 100, Write('c', r ),
            Branch(Read.c, Read.a, Read.b)
        )

        f = dsl.Compile(code, {})

        assert [600, 3, 6] == f(2)

        r = Ref('r')
        code = Seq(
            P + 1, Write.a,
            P * 2, Write.b,
            P * 100, Write('c', r),
            Branch(Read.c, Read.a, Read.b)
        )

        f = dsl.Compile(code, {})

        assert [600, 3, 6] == f(2)
        assert r() == 600

    def test_write_tree(self):

        code = Seq(
            P + 1,
            P * 2,
            Branch(
                (P * 100).Write("c")
            ,
                P - 3
            ,
                Read.c
            )
        )

        f = dsl.Compile(code, {})

        assert [600, 3, 600] == f(2)

    def test_write_tree(self):

        code = Seq(
            P + 1,
            P * 2,
            Branch(
                P * 100
            ,
                Write('c')
            ,
                P - 3
            ,
                Read('c')
            )
        )

        f = dsl.Compile(code, {})

        assert [600, 6, 3, 6] == f(2)

    def test_input(self):
        code = Seq(
            Write('a'),
            P + 1,
            Branch(
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

        f = dsl.Compile(code, {})

        assert [20, 2, 3] == f(2)

    def test_identities(self):

        code = Branch(
            Seq(),
            Branch()
        )

        f = dsl.Compile(code, {})

        assert [4, []] == f(4)

    def test_single_functions(self):

        code = Branch(
            P * 2,
            Branch(P + 1)
        )

        f = dsl.Compile(code, {})

        assert [2, [2]] == f(1)

    def test_class(self):

        code = Seq(
            str,
            P + '0',
            int
        )

        f = dsl.Compile(code, {})
        assert 20 == f(2)


        ast = dsl._parse(str)
        assert type(ast) is dsl.Expression

    def test_list(self):
        code = Seq(
            Branch(
                P + 1
            ,
                P * 2
            ),
            Branch(
                Seq(
                    lambda l: map(str, l),
                    list
                )
            ,
                P
            )
        )

        f = dsl.Compile(code, {})
        assert [['4', '6'], [4, 6]] == f(3)

    def test_dict(self):
        code = Seq(
            Rec(
                original = P,
                upper = Obj.upper(),
                len = len
            ),
            Branch(
                P
            ,
                Seq(
                    Rec.len,
                    P * 2
                )
            )
        )

        f = dsl.Compile(code, {})
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
            Rec(
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
            Rec(
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
                Write('s')
            ),
            Read('s')
        )

        assert f(3) == 3

        with pytest.raises(Exception):
            f(1)


    def test_nested_compiles(self):

        assert 1 == P.Pipe(
            1, Write('s'),
            P.Seq(
                P + 1, Write('s')
            ),
            Read('s')
        )

        assert 2 == P.Pipe(
            1, Write('s'),
            Seq(
                P + 1, Write('s')
            ),
            Write('s')
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
