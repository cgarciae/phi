from phi import dsl, P, If
import pytest

class TestDSL(object):
    """docstring for TestDSL."""

    def test_compile(self):
        code = (P + 1, P * 2)
        f = dsl.Compile(code, {})
        assert f(2) == 6

    def test_compile_single_function(self):
        f = P * 2
        code = f
        f_compiled = dsl.Compile(code, {})
        assert f == f_compiled

    def test_read(self):
        refs = dict(
            x=dsl.Ref('x', 10)
        )
        code = ('x',)
        f = dsl.Compile(code, refs)

        assert refs == refs #read doesnt modify
        assert f(None) == 10

    def test_write(self):
        r = dsl.Ref('r')
        code = (
            P + 1, {'a'},
            P * 2, {'b'},
            P * 100, {'c', r },
            ['c', 'a', 'b']
        )

        f = dsl.Compile(code, {})

        assert [600, 3, 6] == f(2)

        r = P.Ref('r')
        code = (
            P + 1, {'a'},
            P * 2, {'b'},
            P * 100, {'c', r },
            ['c', 'a', 'b']
        )

        f = dsl.Compile(code, {})

        assert [600, 3, 6] == f(2)
        assert r() == 600

    def test_write_tree(self):

        code = (
            P + 1,
            P * 2,
            [
                P * 100, {'c'}
            ,
                P - 3
            ,
                'c'
            ]
        )

        f = dsl.Compile(code, {})

        assert [600, 3, 600] == f(2)

    def test_write_tree(self):

        code = (
            P + 1,
            P * 2,
            [
                P * 100
            ,
                P.Write('c')
            ,
                P - 3
            ,
                'c'
            ]
        )

        f = dsl.Compile(code, {})

        assert [600, 6, 3, 6] == f(2)

    def test_input(self):
        code = (
            {'a'},
            P + 1,
            [
            (
                P.Val(10),
                P * 2
            )
            ,
                'a'
            ,
                ()
            ]
        )

        f = dsl.Compile(code, {})

        assert [20, 2, 3] == f(2)

    def test_identities(self):

        code = [
            (),
            []
        ]

        f = dsl.Compile(code, {})

        assert [4, []] == f(4)

    def test_single_functions(self):

        code = [
            (P * 2),
            [P + 1]
        ]

        f = dsl.Compile(code, {})

        assert [2, [2]] == f(1)

    def test_class(self):

        code = (
            str,
            P + '0',
            int
        )

        f = dsl.Compile(code, {})
        assert 20 == f(2)


        ast = dsl._parse(str)
        assert type(ast) is dsl.Function

    def test_list(self):
        code = (
            [
                P + 1
            ,
                P * 2
            ],
            [
            (
                lambda l: map(str, l),
                list
            )
            ,
                ()
            ]
        )

        f = dsl.Compile(code, {})
        assert [['4', '6'], [4, 6]] == f(3)

    def test_dict(self):
        code = (
            dict(
                original = (),
                upper = P.Obj.upper(),
                len = len
            ),
            [
                ()
            ,
            (
                P.Rec.len,
                P * 2
            )
            ]
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
            P.Obj.lower()
        )

    def test_record_object(self):

        x = P.Pipe(
            [1,2,3],
            dict(
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
            dict(
                sum = sum
            ,
                len = len
            ,
                x = 'x'
            ,
                z = P.Read('y') + 2
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

        f = P.Make(
            P.If( P > 2,
                {'s'}
            ),
            's'
        )

        assert f(3) == 3


        with pytest.raises(Exception):
            f(1)


    def test_nested_compiles(self):

        assert 1 == P.Pipe(
            1, {'s'},
            P.Make(
                P + 1, {'s'}
            ),
            's'
        )

        assert 2 == P.Pipe(
            1, {'s'},
            P.NMake(
                P + 1, {'s'}
            ),
            's'
        )

    def test_if(self):

        f = P.Make(
            If( P > 0,
                P
            ).Else(
                P.Val(0)
            )
        )

        assert f(5) == 5
        assert f(-3) == 0

