import unittest

from functools import reduce

from pampy import match, REST, TAIL, HEAD, _, match_value, match_iterable


class PampyElaborateTests(unittest.TestCase):

    def test_fibonacci(self):
        def fib(n):
            return match(n,
                1, 1,
                2, 1,
                _, lambda x: fib(x - 1) + fib(x - 2))

        self.assertEqual(fib(1), 1)
        self.assertEqual(fib(7), 13)

    def test_slide1(self):
        _input = [1, 2, 3]
        pattern = [1, _, 3]
        action = lambda x: "it's {}".format(x)
        self.assertEqual(match(_input, pattern, action), "it's 2")

    def test_parser(self):
        def parser(exp):
            return match(exp,
                3,              "the integer 3",
                float,          "any float number",
                int,            "any integer",
                "ciao",         "the string ciao",
                dict,           "any dictionary",
                str,            "any string",
                (int, int),     "a tuple made of two ints",
                [1],            "the list [1]",
                [1, 2, 3],      "the list [1, 2, 3]",
                [1, _, 3],      "the list [1, _, 3]",
                (str, str),     lambda a, b: "%s %s" % (a, b),
                [1, 2, _],      lambda x: "the list [1, 2, _]",
                [1, 2, 4],      "the list [1, 2, 4]",   # this can never be matched

                [1, [2, _], _], lambda a, b: "[1, [2, %s], %s]" % (a, b),
            )

        assert parser(3) == "the integer 3"
        assert parser(5) == "any integer"
        assert parser("ciao") == "the string ciao"
        assert parser("x") == "any string"
        assert parser({'a': 1}) == "any dictionary"
        assert parser([1]) == "the list [1]"
        assert parser([1, 2, 3]) == "the list [1, 2, 3]"
        assert parser([1, 2, 4]) == "the list [1, 2, _]"
        assert parser([1, 3, 3]) == "the list [1, _, 3]"
        assert parser(("hello", "world")) == "hello world"
        assert parser([1, [2, 3],    4]) == "[1, [2, 3], 4]"

    def test_lisp(self):
        # A Lisp interpreter in 5 lines
        def lisp(exp):
            return match(exp,
                int,                lambda x: x,
                callable,           lambda x: x,
                (callable, REST),   lambda f, rest: f(*map(lisp, rest)),
                tuple,              lambda t: list(map(lisp, t)),
            )

        plus = lambda a, b: a + b
        minus = lambda a, b: a - b
        self.assertEqual(lisp((plus, 1, 2)), 3)
        self.assertEqual(lisp((plus, 1, (minus, 4, 2))), 3)
        self.assertEqual(lisp((reduce, plus, (1, 2, 3))), 6)
        self.assertEqual(lisp((reduce, plus, (range, 10))), 45)

    def test_myzip(self):
        def myzip(a, b):
            return match((a, b),
                ([], []),                   [],
                ([_, TAIL], [_, TAIL]),     lambda ha, ta, hb, tb: [(ha, hb)]+myzip(ta, tb)
            )

        self.assertEqual(myzip([1,2,3], [4, 5, 6]), [(1, 4), (2, 5), (3, 6)])
        self.assertEqual(myzip(range(5), range(5)), list(zip(range(5), range(5))))

    def test_lambda_cond(self):
        cond = lambda x: x < 10
        self.assertEqual(match(3, cond, "action", _, "else"), "action")
        self.assertEqual(match(11, cond, "action1", _, "else"), "else")

    def test_lambda_cond_arg_passing(self):
        def f(x):
            return match(x,
                lambda x: x % 2 == 0, lambda x: "even %d" % x,
                lambda x: x % 2 != 0, lambda x: "odd %d" % x
            )
        self.assertEqual(f(3), "odd 3")
        self.assertEqual(f(18), "even 18")
        self.assertEqual(f(18), "even 18")

    def test_dataclasses(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        @dataclass
        class Point:
            x: float
            y: float

        def f(x):
            return match(x,
                Point(1, 2), '1',
                Point(_, 2), str,
                Point(1, _), str,
                Point(_, _), lambda a, b: str(a + b)
            )

        self.assertEqual(f(Point(1, 2)), '1')
        self.assertEqual(f(Point(2, 2)), '2')
        self.assertEqual(f(Point(1, 3)), '3')
        self.assertEqual(f(Point(2, 3)), '5')


    # def test_tree_traversal(self):
    #     class Node:
    #         def __init__(self, name, childs):
    #             self.name, self.childs = name, childs
    #
    #         def __extract__(self):
    #             return self.name, self.childs
    #
    #     tree = Node(1, [Node(2), Node(3, [Node(4, [Node(5)), Node(6)])])])
    #
    #
    #     def breadth_first(node):
    #         return match(node,
    #                      Node(_, []),       lambda name, childs: name,
    #                      Node(_, [TAIL]),   lambda name, childs: breadth_first()
    #         )


    # def test_animals(self):
    #     pets = [
    #         { 'type': 'dog', 'pet-details': { 'name': 'carl',   'cuteness': 4   } },
    #         { 'type': 'dog', 'pet-details': { 'name': 'john',   'cuteness': 3   } },
    #         { 'type': 'cat', 'pet-details': { 'name': 'fuffy',  'cuty':     4.6 } },
    #         { 'type': 'cat', 'cat-details': { 'name': 'bonney', 'cuty':     7   } },
    #     ]
    #
    #     def avg_cuteness_pythonic():
    #         cutenesses = []
    #         for pet in pets:
    #             if 'pog-details' in pet:
    #                 if 'cuteness' in pet['pog-detail']:
    #                     cutenesses.append(pet['pog-detail']['cuteness'])
    #                 elif 'cuty' in pet['pet-details']:
    #                     cutenesses.append(pet[''])
    #             elif 'cat-detail' in pet:
    #                 if 'cuty' in pet['cat-details']:
    #                     cutenesses.append(pet[''])
    #         return sum(cutenesses) / len(cutenesses)
    #
    #     def avg_cuteness_pampy():
    #         cutenesses = []
    #         for pet in pets:
    #             match(pet,
    #                 { "pet-details": { "cuteness": _ }},  lambda x: cutenesses.append(x),
    #                 { "cat-details": { "cuty":     _ }},  lambda x: cutenesses.append(x)
    #             )
    #         return sum(cutenesses) / len(cutenesses)


