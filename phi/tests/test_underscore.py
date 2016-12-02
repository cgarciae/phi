from phi import _, ph

def test_ops():

    assert 2 == ph.Pipe(
        1,
        _ + 1
    )
