
from phi import P, Obj, Rec


class TestExamples(object):
    """docstring for TestExamples."""

    def test_example_1(self):

        text = "a bb ccc"
        average_word_length = P.Pipe(
            text,
            Obj.split(" "), #['a', 'bb', 'ccc']
            P.map(len), #[1, 2, 3]
            P._(sum) / len #6 / 3 == 2
        )

        assert 2 == average_word_length
