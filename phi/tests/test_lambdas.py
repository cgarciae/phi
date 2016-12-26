from phi.api import *

class TestExpressions(object):
    """docstring for TestExpressions."""

    def test_ops(self):

        assert 2 == P.Pipe(
            1,
            P + 1
        )

        #####################
        #####################

        f = P * [ P ]

        assert f(0) == []
        assert f(1) == [1]
        assert f(3) == [3,3,3]

    def test_rshift(self):

        f = P + 1 >> P * 2

        assert 6 == f(2)


        f = lambda x: x * 3
        g = lambda x: x + 2

        h = f >> P.Seq(g)

        assert 11 == h(3)


        h = P.Seq(f) >> g
        assert 11 == h(3)


        y = 1 >> P + 1 >> P * 2
        assert 4 == y


        y = P * 2 << P + 1 << 1
        assert 4 == y

    def test_lshift(self):

        f = P * 2 << P + 1

        assert 6 == f(2)


        f = lambda x: x * 3
        g = lambda x: x + 2

        h = g << Seq(f)

        assert 11 == h(3)


        h = Seq(g) << f

        assert 11 == h(3)

    def test_reverse(self):

        f = 12 / P

        assert f(3) == 4

    def test_lambda_opt_lambda(self):

        assert 3 == Pipe(
            0,
            List(
                P + 1
            ,
                P + 2
            ),
            P[0] + P[1]
        )

        assert 3 == P.Pipe(
            Dict(
                a = 1,
                b = 2
            ),
            Rec.a + Rec.b
        )

        assert 5 == P.Pipe(
            Dict(
                a = 10,
                b = 2
            ),
            Rec.a / Rec.b
        )


        assert 6 == 1 >> (P + 1) * (P + 2)

        assert 6 == 10 >> (P * 3) / (P - 5)
