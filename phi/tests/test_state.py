from phi.api import *


class TestState(object):

    def test_seq(self):

        f = Seq(lambda x: x + 1)

        assert f(1) == 2
