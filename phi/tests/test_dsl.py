from phi import dsl, P

class TestDSL(object):
    """docstring for TestDSL."""

    def test_compile(self):
        code = (P + 1, P * 2)
        f, refs = dsl.Compile(code, {})
        assert f(2) == 6

    def test_compile_single_function(self):
        f = P * 2
        code = f
        f_compiled, refs = dsl.Compile(code, {})
        assert f == f_compiled

    def test_read(self):
        refs = dict(
            x=dsl.Ref('x', 10)
        )
        code = ('x',)
        f, refs = dsl.Compile(code, refs)

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

        f, refs = dsl.Compile(code, {})

        assert [600, 3, 6] == f(2)

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

        f, refs = dsl.Compile(code, {})

        assert [600, 3, 600] == f(2)

    def test_write_tree(self):

        code = (
            P + 1,
            P * 2,
            [
                P * 100
            ,
                P.On('c')
            ,
                P - 3
            ,
                'c'
            ]
        )

        f, refs = dsl.Compile(code, {})

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

        f, refs = dsl.Compile(code, {})

        assert [20, 2, 3] == f(2)

    def test_identities(self):

        code = [
            (),
            []
        ]

        f, refs = dsl.Compile(code, {})

        assert [4, []] == f(4)

    def test_single_functions(self):

        code = [
            (P * 2),
            [P + 1]
        ]

        f, refs = dsl.Compile(code, {})

        assert [2, [2]] == f(1)

    def test_class(self):

        code = (
            str,
            P + '0',
            int
        )

        f, refs = dsl.Compile(code, {})
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
                lambda l: map(str, l)
            ,
                ()
            ]
        )

        f, refs = dsl.Compile(code, {})
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

        f, refs = dsl.Compile(code, {})
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
