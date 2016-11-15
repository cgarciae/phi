from phi import dsl, _, _1, _2, Obj, Rec, Builder, val, utils

class TestDSL(object):
    """docstring for TestDSL."""

    def test_compile(self):
        code = (_ + 1, _ * 2)
        f, refs = dsl.Compile(code, {})
        assert f(2) == 6

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
            _ + 1, {'a'},
            _ * 2, {'b'},
            _ * 100, {'c', r },
            ['c', 'a', 'b']
        )

        f, refs = dsl.Compile(code, {})

        assert [600, 3, 6] == f(2)

    def test_input(self):
        code = (
            {'a'},
            _ + 1,
            [
            (
                val(10),
                _ * 2
            )
            ,
                'a'
            ,
                utils.identity
            ]
        )

        f, refs = dsl.Compile(code, {})

        assert [20, 2, 3] == f(2)

    def test_class(self):

        code = (
            str,
            _ + '0',
            int
        )

        f, refs = dsl.Compile(code, {})
        assert 20 == f(2)


        ast = dsl.parse(str)
        assert type(ast) is dsl.Function

    def test_list(self):
        code = (
            [
                _ + 1
            ,
                _ * 2
            ],
            [
                lambda l: map(str, l)
            ,
                ()
            ]
        )

        f, refs = dsl.Compile(code, {})
        assert [['4', '6'], [4, 6]] == f(3)
