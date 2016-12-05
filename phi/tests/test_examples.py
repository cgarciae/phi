
from phi import P, Obj, Rec, M


class TestExamples(object):
    """docstring for TestExamples."""

    def test_example_1(self):

        text = "a bb ccc"
        avg_word_length = P.Pipe(
            text,
            Obj.split(" "), #['a', 'bb', 'ccc']
            P.map(len), #[1, 2, 3]
            P._(sum) / len #6 / 3 == 2
        )

        assert 2 == avg_word_length


        text = "a bb ccc"
        avg_word_length = P.Pipe(
            text,
            Obj.split(" "), #['a', 'bb', 'ccc']
            P.map(len), #[1, 2, 3]
            M(sum) / len #6 / 3 == 2
        )

        assert 2 == avg_word_length


        text = "a bb ccc"
        avg_word_length = P.Pipe(
            text,
            Obj.split(" "), #['a', 'bb', 'ccc']
            P.map(len), #[1, 2, 3]
            P.sum() / P.len() #6 / 3 == 2
        )

        assert 2 == avg_word_length


        avg_word_length = P.Pipe(
            "1 22 333",
            Obj.split(' '), # ['1', '22', '333']
            P.map(len), # [1, 2, 3]
            [
                sum # 1 + 2 + 3 == 6
            ,
                len # len([1, 2, 3]) == 3
            ],
            P[0] / P[1] # sum / len == 6 / 3 == 2
        )

        assert avg_word_length == 2
