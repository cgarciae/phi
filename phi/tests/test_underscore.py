from phi import P, P as P

def test_ops():

    assert 2 == P.Pipe(
        1,
        P + 1
    )
