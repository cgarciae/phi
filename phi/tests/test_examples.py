from phi.api import *

class TestExamples(object):
    """docstring for TestExamples."""

    def test_example_1(self):

        text = "a bb ccc"
        avg_word_length = P.Pipe(
            text,
            Obj.split(" "), #['a', 'bb', 'ccc']
            P.map(len), #[1, 2, 3]
            list, # python 3 only
            P.sum() / len #6 / 3 == 2
        )

        assert 2 == avg_word_length


        text = "a bb ccc"
        avg_word_length = P.Pipe(
            text,
            Obj.split(" "), #['a', 'bb', 'ccc']
            P.map(len), #[1, 2, 3]
            list, # python 3 only
            Seq(sum) / len #6 / 3 == 2
        )

        assert 2 == avg_word_length


        text = "a bb ccc"
        avg_word_length = P.Pipe(
            text,
            Obj.split(" "), #['a', 'bb', 'ccc']
            P.map(len), #[1, 2, 3]
            list, # python 3 only
            P.sum() / P.len() #6 / 3 == 2
        )

        assert 2 == avg_word_length


        avg_word_length = P.Pipe(
            "1 22 333",
            Obj.split(' '), # ['1', '22', '333']
            P.map(len), # [1, 2, 3]
            list, # python 3 only
            List(
                sum # 1 + 2 + 3 == 6
            ,
                len # len([1, 2, 3]) == 3
            ),
            P[0] / P[1] # sum / len == 6 / 3 == 2
        )

        assert avg_word_length == 2

    def test_getting_started(self):
        from phi import P

        def add1(x): return x + 1
        def mul3(x): return x * 3

        x = P.Pipe(
            1.0,     #input 1
            add1,  #1 + 1 == 2
            mul3   #2 * 3 == 6
        )

        assert x == 6

        ################
        ################

        from phi import P

        x = P.Pipe(
            1.0,      #input 1
            P + 1,  #1 + 1 == 2
            P * 3   #2 * 3 == 6
        )

        assert x == 6

        ################
        ################

        from phi import P, List

        [x, y] = P.Pipe(
            1.0,  #input 1
            List(
                P + 1  #1 + 1 == 2
            ,
                P * 3  #1 * 3 == 3
            )
        )

        assert x == 2
        assert y == 3

        ################
        ################

        from phi import P, List

        [x, y] = P.Pipe(
            1.0,  #input 1
            P * 2,  #1 * 2 == 2
            List(
                P + 1  #2 + 1 == 3
            ,
                P * 3  #2 * 3 == 6
            )
        )

        assert x == 3
        assert y == 6

        ################
        ################

        from phi import P, Rec

        result = P.Pipe(
            1.0,  #input 1
            P * 2,  #1 * 2 == 2
            Dict(
                x = P + 1  #2 + 1 == 3
            ,
                y = P * 3  #2 * 3 == 6
            )
        )

        assert result.x == 3
        assert result.y == 6

        ################
        ################

        from phi import P, Rec

        result = P.Pipe(
            1.0,  #input 1
            P * 2,  #1 * 2 == 2
            Dict(
                x = P + 1  #2 + 1 == 3
            ,
                y = P * 3  #2 * 3 == 6
            ),
            Rec.x / Rec.y  #3 / 6 == 0.5
        )

        assert result == 0.5

        ################
        ################

        from phi import P, Rec, List, Write, Read

        [result, s] = P.Pipe(
            1.0,  #input 1
            Write(s = P * 2),  #s = 2 * 1 == 2
            Dict(
                x = P + 1  #2 + 1 == 3
            ,
                y = P * 3  #2 * 3 == 6
            ),
            List(
                Rec.x / Rec.y  #3 / 6 == 0.5
            ,
                Read('s')  #load 's' == 2
            )
        )

        assert result == 0.5
        assert s == 2

        ################
        ################

        from phi import P, Rec, Write, Read, List

        [result, s] = P.Pipe(
            1.0,  #input 1
            Write(s = P * 2),  #s = 2 * 1 == 2
            Dict(
                x = P + 1  #2 + 1 == 3
            ,
                y = P * 3  #2 * 3 == 6
            ),
            List(
                Rec.x / Rec.y  #3 / 6 == 0.5
            ,
                Read.s + 3  # 2 + 3 == 5
            )
        )

        assert result == 0.5
        assert s == 5

        ################
        ################

        from phi import P, Rec, Read, Write

        [result, s] = P.Pipe(
            1.0,  #input 1
            Write(s = P * 2),  #s = 2 * 1 == 2
            Dict(
                x = P + 1  #2 + 1 == 3
            ,
                y = P * 3  #2 * 3 == 6
            ),
            List(
                Rec.x / Rec.y  #3 / 6 == 0.5
            ,
                Read.s + 3  # 2 + 3 == 5
            )
        )

        assert result == 0.5
        assert s == 5

        ################
        ################

        from phi import P, Rec, Val

        [result, s, val] = P.Pipe(
            1.0,  #input 1
            Write(s = P * 2),  #s = 2 * 1 == 2
            Dict(
                x = P + 1  #2 + 1 == 3
            ,
                y = P * 3  #2 * 3 == 6
            ),
            List(
                Rec.x / Rec.y  #3 / 6 == 0.5
            ,
                Read.s + 3  # 2 + 3 == 5
            ,
                Val(9) + 1  #input 9 and add 1, gives 10
            )
        )

        assert result == 0.5
        assert s == 5
        assert val == 10

        #########################
        #########################

        from phi import P, Rec, Read, Write, Val, If

        [result, s, val] = P.Pipe(
            1.0,  #input 1
            Write(s = (P + 3) / (P + 1)), #s = 4 / 2 == 2
            Dict(
                x = P + 1  #2 + 1 == 3
            ,
                y = P * 3  #2 * 3 == 6
            ),
            List(
                Rec.x / Rec.y  #3 / 6 == 0.5
            ,
                Read.s + 3  # 2 + 3 == 5
            ,
                If( Rec.y > 7,
                    Val(9) + 1  #input 9 and add 1, gives 10
                ).Elif( Rec.y < 4,
                    "Yes"
                ).Else(
                    "Sorry, come back latter."
                )
            )
        )

        assert result == 0.5
        assert s == 5
        assert val == "Sorry, come back latter."


        ######################################
        #######################################

        from phi import P, Rec, Read, Write, Val, If

        f = P.Seq(
            Write(s = (P + 3) / (P + 1)), #s = 4 / 2 == 2
            Dict(
                x = P + 1  #2 + 1 == 3
            ,
                y = P * 3  #2 * 3 == 6
            ),
            List(
                Rec.x / Rec.y  #3 / 6 == 0.5
            ,
                Read.s + 3  # 2 + 3 == 5
            ,
                If( Rec.y > 7,
                    Val(9) + 1  #input 9 and add 1, gives 10
                ).Else(
                    "Sorry, come back latter."
                )
            )
        )

        [result, s, val] = f(1.0)

        assert result == 0.5
        assert s == 5
        assert val == "Sorry, come back latter."



    def test_builder_MakeRefContext(self):

        from phi import P

        assert 2 == P.Pipe(
            Write(s = 1),   #s = 1
            P.Seq(
                Write(s = P + 1),   #s = 2
            ),
            Read('s')   # s == 2
        )

        ################################
        ################################




    def test_builder_NPipe(self):

        from phi import P

        assert 1 == P.Pipe(
            Write(s = 1), # write s == 1, outer context
            lambda x: P.Pipe(
                x,
                Write(s = P + 1) # write s == 2, inner context
            ),
            Read('s')  # read s == 1, outer context
        )

        #############################
        #############################

    def test_not(self):

        from phi import P

        assert True == P.Pipe(
            1,
            P + 1,  # 1 + 1 == 2
            P > 5,  # 2 > 5 == False
            P.Not() # not False == True
        )

        ################################
        ################################

        from phi import P

        assert True == P.Pipe(
            1,
            (P + 1 > 5).Not()  # not 1 + 1 > 5 == not 2 > 5 == not False == True
        )

        ############################
        #############################

        from phi import P

        f = (P + 1 > 5).Not()   #lambda x: not x + 1 > 5

        assert f(1) == True

    def test_contains(self):

        from phi import P

        assert False == P.Pipe(
            [1,2,3,4],
            P.filter(P % 2 != 0)   #[1, 3], keeps odds
            .Contains(4)   #4 in [1, 3] == False
        )

    def test_ref(self):

        from phi import P, Obj, Ref

        assert {'a': 97, 'b': 98, 'c': 99} == P.Pipe(
            "a b c", Obj
            .split(' ')  #['a', 'b', 'c']
            .Write(keys = P)  # key = ['a', 'b', 'c']
            .map(ord),  # [ord('a'), ord('b'), ord('c')] == [97, 98, 99]
            lambda it: zip(Ref.keys, it),  # [('a', 97), ('b', 98), ('c', 99)]
            dict   # {'a': 97, 'b': 98, 'c': 99}
        )

    def test_if(self):

        from phi import P, Val

        assert "Between 2 and 10" == P.Pipe(
            5,
            P.If(P > 10,
                "Greater than 10"
            ).Elif(P < 2,
                "Less than 2"
            ).Else(
                "Between 2 and 10"
            )
        )

    def test_pipe_branch(self):

        assert [11, 12] == 10 >> List( P + 1, P + 2)


    def test_state(self):

        f = Read("a") + 5 >> Write(a = P)
        assert f(None, True, a=0) == (5, {"a": 5})


        f = Read.a + 5 >> Write(a = P)
        assert f(None, True, a=0) == (5, {"a": 5})


    def test_math(self):
        import math

        f = P.map(P ** 2) >> list >> P[0] + P[1] >> math.sqrt

        assert f([3, 4]) == 5


    def test_operators(self):

        f = (P * 6) / (P + 2)

        assert f(2) == 3  # (2 * 6) / (2 + 2) == 12 / 4 == 3

        ###########################

    def test_get_item(self):

        f = P[0] + P[-1]  #add the first and last elements

        assert f([1,2,3,4]) == 5   #1 + 4 == 5

        ##################

    def test_field_access(self):

        from collections import namedtuple
        Point = namedtuple('Point', ['x', 'y'])

        f = Rec.x + Rec.y  #add the x and y fields

        assert f(Point(3, 4)) == 7   #point.x + point.y == 3 + 4 == 7

    def test_method_calling(self):

        f = Obj.upper() + ", " + Obj.lower()  #lambda s: s.upper() + ", " + s.lower()

        assert f("HEllo") == "HELLO, hello"   # "HEllo".upper() + ", " + "HEllo".lower() == "HELLO" + ", " + "hello" == "HELLO, hello"

        #############################

    def test_rshif_and_lshift(arg):
        import math

        f = P + 7 >> math.sqrt  #executes left to right

        assert f(2) == 3  # math.sqrt(2 + 7) == math.sqrt(9) == 3

        ################

        f =  math.sqrt << P + 7 #executes right to left

        assert f(2) == 3  # math.sqrt(2 + 7) == math.sqrt(9) == 3

        #######################

    def test_seq_and_pipe(arg):
        import math

        f = Seq(
          str,
          P + "00",
          int,
          math.sqrt
        )

        assert f(1) == 10  # sqrt(int("1" + "00")) == sqrt(100) == 10

        ##################################

        assert 10 == Pipe(
          1,  #input
          str,  # "1"
          P + "00",  # "1" + "00" == "100"
          int,  # 100
          math.sqrt  #sqrt(100) == 10
        )

        ######################################


    def test_list_tuple_ect(arg):
        f = List( P + 1, P * 10 )  #lambda x: [ x +1, x * 10 ]

        assert f(3) == [ 4, 30 ]  # [ 3 + 1, 3 * 10 ] == [ 4, 30 ]


        ##################################

        f = Dict( x = P + 1, y = P * 10 )  #lambda x: [ x +1, x * 10 ]

        d = f(3)

        assert d == { 'x': 4, 'y': 30 }  # { 'x': 3 + 1, 'y': 3 * 10 } == { 'x': 4, 'y': 30 }
        assert d.x == 4   #access d['x'] via field access as d.x
        assert d.y == 30  #access d['y'] via field access as d.y

        #########################################


    def test_state_read_write(arg):
        assert [70, 30] == Pipe(
          3,
          Write(s = P * 10),  #s = 3 * 10 == 30
          P + 5,  #30 + 5 == 35
          List(
            P * 2  # 35 * 2 == 70
          ,
            Read('s')  #s == 30
          )
        )

        ###########################


    def test_thens(arg):
        def repeat_word(word, times, upper=False):
            if upper:
                word = word.upper()

            return [ word ] * times

        f = P[::-1] >> Then(repeat_word, 3)
        g = P[::-1] >> Then(repeat_word, 3, upper=True)

        assert f("ward") == ["draw", "draw", "draw"]
        assert g("ward") == ["DRAW", "DRAW", "DRAW"]

        ###########################

        # since map and filter receive the iterable on their second argument, you have to use `Then2`
        f = Then2(filter, P % 2 == 0) >> Then2(map, P**2) >> list  #lambda x: map(lambda z: z**2, filter(lambda z: z % 2 == 0, x))

        assert f([1,2,3,4,5]) == [4, 16]  #[2**2, 4**2] == [4, 16]


        ######################################

        f = P.filter(P % 2 == 0) >> P.map(P**2) >> list  #lambda x: map(lambda z: z**2, filter(lambda z: z % 2 == 0, x))

        assert f([1,2,3,4,5]) == [4, 16]  #[2**2, 4**2] == [4, 16]


        ######################################

    def test_val(self):

        f = Val(42)  #lambda x: 42

        assert f("whatever") == 42

        #####################################

    def test_others(self):
        f = Obj.split(' ') >> P.map(len) >> sum >> If( (P < 15).Not(), "Great! Got {0} letters!".format).Else("Too short, need at-least 15 letters")

        assert f("short frase") == "Too short, need at-least 15 letters"
        assert f("some longer frase") == "Great! Got 15 letters!"

        ###########################################

    def test_dsl(self):
        f = P**2 >> List( P, Val(3), Val(4) )  #lambda x: [ x**2]

        assert f(10) == [ 100, 3, 4 ]  # [ 10**2, 3, 4 ]  == [ 100, 3, 4 ]

        ############################################

        f = P**2 >> List( P, 3, 4 )

        assert f(10) == [ 100, 3, 4 ]  # [ 10 ** 2, 3, 4 ]  == [ 100, 3, 4 ]


        ###########################################

        f = P**2 >> [ P, 3, 4 ]

        assert f(10) == [ 100, 3, 4 ]  # [ 10 ** 2, 3, 4 ]  == [ 100, 3, 4 ]


        ############################################

        assert [ 100, 3, 4 ] == Pipe(
          10,
          P**2,  # 10**2 == 100
          [ P, 3, 4 ]  #[ 100, 3, 4 ]
        )


    def test_f(self):

        f = F((P + "!!!", 42, Obj.upper()))  #Tuple(P + "!!!", Val(42), Obj.upper())

        assert f("some tuple") == ("some tuple!!!", 42, "SOME TUPLE")

        #############################################

        f = F([ P + n for n in range(5) ])  >> [ len, sum ]  # lambda x: [ len([ x, x+1, x+2, x+3, x+4]), sum([ x, x+1, x+2, x+3, x+4]) ]

        assert f(10) == [ 5, 60 ]  # [ len([10, 11, 12, 13, 14]), sum([10, 11, 12, 13, 14])] == [ 5, (50 + 0 + 1 + 2 + 3 + 4) ] == [ 5, 60 ]

    def test_fluent(self):

        f = Dict(
          x = 2 * P,
          y = P + 1
        ).Tuple(
          Rec.x + Rec.y,
          Rec.y / Rec.x
        )

        assert f(1) == (4, 1)  # ( x + y, y / x) == ( 2 + 2, 2 / 2) == ( 4, 1 )

        #################################

        f = Obj.split(' ') >> P.map(len) >> sum >> If( (P < 15).Not(), "Great! Got {0} letters!".format).Else("Too short, need at-least 15 letters")

        assert f("short frase") == "Too short, need at-least 15 letters"
        assert f("some longer frase") == "Great! Got 15 letters!"

        ######################################################

        f = (
          Obj.split(' ')
          .map(len)
          .sum()
          .If( (P < 15).Not(),
            "Great! Got {0} letters!".format
          ).Else(
            "Too short, need at-least 15 letters"
          )
        )

        assert f("short frase") == "Too short, need at-least 15 letters"
        assert f("some longer frase") == "Great! Got 15 letters!"

        ###########################################################

    def test_Register(self):

        from phi import PythonBuilder

        class MyBuilder(PythonBuilder):
            pass

        M = MyBuilder()

        @MyBuilder.Register("my.lib.")
        def remove_longer_than(some_list, n):
            return [ elem for elem in some_list if len(elem) <= n ]

        f = Obj.lower() >> Obj.split(' ') >> M.remove_longer_than(6)

        assert f("SoMe aRe LONGGGGGGGGG") == ["some", "are"]

        #######################################################

