import unittest
import sys

from pampy import match, _


class PampyDataClassesTests(unittest.TestCase):
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

    def test_different_dataclasses(self):
        try:
            from dataclasses import dataclass
        except ImportError:
            return

        @dataclass
        class Cat:
            name: str
            chassed_squirels: int

        @dataclass
        class Dog:
            name: str
            chassed_cats: int

        def what_is(x):
            return match(x,
                         Dog(_, 0), 'good boy',
                         Dog(_, _), 'doggy!',
                         Cat(_, 0), 'tommy?',
                         Cat(_, _), 'a cat'
                         )

        self.assertEqual(what_is(Cat("cat", 0)), 'tommy?')
        self.assertEqual(what_is(Cat("cat", 1)), 'a cat')
        self.assertEqual(what_is(Dog("", 0)), 'good boy')
        self.assertEqual(what_is(Dog("", 1)), 'doggy!')
