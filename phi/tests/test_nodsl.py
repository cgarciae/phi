from phi.dsl import Expression

P = Expression()

class TestNoDSL(object):

    def test_seq(self):

        f = P.Seq(
            P + 2,
            P * 2
        )

        assert 10 == f(3)

    def test_branch(self):

        f = P.List(
            P + 2,
            P * 2
        )

        assert [5, 6] == f(3)

        f = P.List(
            P + 2,
            P.Seq(
                P + 1,
                P * 2
            )
        )

        assert [5, 8] == f(3)
