import unittest
from datetime import datetime
from typing import (
    Union,
    Optional,
    Tuple,
    List,
    NewType,
)

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
                         3, "the integer 3",
                         float, "any float number",
                         int, "any integer",
                         "ciao", "the string ciao",
                         dict, "any dictionary",
                         str, "any string",
                         (int, int), "a tuple made of two ints",
                         [1], "the list [1]",
                         [1, 2, 3], "the list [1, 2, 3]",
                         [1, _, 3], "the list [1, _, 3]",
                         (str, str), lambda a, b: "%s %s" % (a, b),
                         [1, 2, _], lambda x: "the list [1, 2, _]",
                         [1, 2, 4], "the list [1, 2, 4]",  # this can never be matched

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
        assert parser([1, [2, 3], 4]) == "[1, [2, 3], 4]"

    def test_lisp(self):
        # A Lisp interpreter in 5 lines
        def lisp(exp):
            return match(exp,
                         int, lambda x: x,
                         callable, lambda x: x,
                         (callable, REST), lambda f, rest: f(*map(lisp, rest)),
                         tuple, lambda t: list(map(lisp, t)),
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
                         ([], []), [],
                         ([_, TAIL], [_, TAIL]), lambda ha, ta, hb, tb: [(ha, hb)] + myzip(ta, tb)
                         )

        self.assertEqual(myzip([1, 2, 3], [4, 5, 6]), [(1, 4), (2, 5), (3, 6)])
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

    def test_animals(self):
        pets = [
            {'type': 'dog', 'pet-details': {'name': 'carl', 'cuteness': 4}},
            {'type': 'dog', 'pet-details': {'name': 'john', 'cuteness': 3}},
            {'type': 'cat', 'pet-details': {'name': 'fuffy', 'cuty': 4.6}},
            {'type': 'cat', 'cat-details': {'name': 'bonney', 'cuty': 7}},
        ]

        def avg_cuteness_pampy():
            cutenesses = []
            for pet in pets:
                match(pet,
                      {_: {"cuteness": _}}, lambda key, x: cutenesses.append(x),
                      {_: {"cuty": _}}, lambda key, x: cutenesses.append(x)
                      )
            return sum(cutenesses) / len(cutenesses)

        self.assertEqual(avg_cuteness_pampy(), (4 + 3 + 4.6 + 7) / 4)

    def test_advanced_lambda(self):
        def either(pattern1, pattern2):
            """Matches values satisfying pattern1 OR pattern2"""
            def repack(*args):
                return True, list(args)

            def f(var):
                return match(var,
                     pattern1, repack,
                     pattern2, repack,
                     _,        (False, [])
                )

            return f

        self.assertEqual(match('str', either(int, str), 'success'), 'success')

        def datetime_p(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0):
            """Matches a datetime with these values"""
            def f(var: datetime):
                if not isinstance(var, datetime):
                    return False, []

                args = []
                for pattern, actual in [(year, var.year), (month, var.month), (day, var.day),
                                        (hour, var.hour), (minute, var.minute), (second, var.second)]:
                    if pattern is _:
                        args.append(actual)
                    elif pattern != actual:
                        return False, []

                return True, args

            return f

        def test(var):
            return match(var,
                datetime_p(2018, 12, 23), 'full match',
                datetime_p(2018, _, _), lambda month, day: f'{month}/{day} in 2018',
                datetime_p(_, _, _, _, _, _), 'any datetime',
                _, 'not a datetime'
            )

        self.assertEqual(test(datetime(2018, 12, 23)), 'full match')
        self.assertEqual(test(datetime(2018, 1, 2)), '1/2 in 2018')
        self.assertEqual(test(datetime(2017, 1, 2, 3, 4, 5)), 'any datetime')
        self.assertEqual(test(11), 'not a datetime')

    def test_typing_example(self):

        timestamp = NewType("timestamp", Union[float, int])
        year, month, day, hour, minute, second = int, int, int, int, int, int
        day_tuple = Tuple[year, month, day]
        dt_tuple = Tuple[year, month, day, hour, minute, second]

        def datetime_p(patterns: List[str]):
            def f(dt: str):
                for pattern in patterns:
                    try:
                        return True, [datetime.strptime(dt, pattern)]
                    except Exception:
                        continue
                else:
                    return False, []
            return f

        def to_datetime(dt: Union[
            timestamp,
            day_tuple,
            dt_tuple,
            str,
        ]) -> Optional[datetime]:
            return match(dt,
                timestamp, lambda x: datetime.fromtimestamp(x),
                Union[day_tuple, dt_tuple], lambda *x: datetime(*x),
                datetime_p(["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]), lambda x: x,
                _, None
            )

        key_date_tuple = (2018, 1, 1)
        detailed_key_date_tuple = (2018, 1, 1, 12, 5, 6)
        key_date = datetime(*key_date_tuple)
        detailed_key_date = datetime(*detailed_key_date_tuple)

        self.assertEqual(to_datetime(key_date_tuple), key_date)
        self.assertEqual(to_datetime(detailed_key_date_tuple), detailed_key_date)

        key_date_ts = key_date.timestamp()
        detailed_key_date_ts = int(detailed_key_date.timestamp())
        self.assertEqual(to_datetime(key_date_ts), key_date)
        self.assertEqual(to_datetime(detailed_key_date_ts), detailed_key_date)

        key_date_ts_str_a = key_date.strftime("%Y-%m-%d")
        key_date_ts_str_f = key_date.strftime("%Y-%m-%d %H:%M:%S")
        key_date_ts_str_w = key_date.strftime("%m-%Y-%d")
        self.assertEqual(to_datetime(key_date_ts_str_a), key_date)
        self.assertEqual(to_datetime(key_date_ts_str_f), key_date)
        self.assertEqual(to_datetime(key_date_ts_str_w), None)

        detailed_key_date_ts_str = detailed_key_date.strftime("%Y-%m-%d %H:%M:%S")
        self.assertEqual(to_datetime(detailed_key_date_ts_str), detailed_key_date)

        self.assertEqual(to_datetime(set(key_date_tuple)), None)
