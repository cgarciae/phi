
class A(object):
    """docstring for A."""

    _S = None

    @property
    def S(self):
        return A._S

class B(A):
    """docstring for B."""

class Compile(A):
    """docstring for Compile ."""


class TestDummy(object):
    """docstring for TestDummy."""

    def test_global(self):
        a = A()
        b = B()
        c = Compile()

        A._S = "HOLA"

        assert b.S == a.S + ""
