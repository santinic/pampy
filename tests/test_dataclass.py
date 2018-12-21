import unittest

from pampy import match, _
from dataclasses import dataclass


class PampyDataClassesTests(unittest.TestCase):


    def test_match_dataclasses(self):
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
                         Cat(_,0), 'tommy?',
                         Cat(_,_), 'a cat'
                         )

        self.assertEqual(what_is(Cat("cat", 0)), 'tommy?')
        self.assertEqual(what_is(Cat("cat", 1)), 'a cat')
        self.assertEqual(what_is(Dog("", 0)), 'good boy')
        self.assertEqual(what_is(Dog("", 1)), 'doggy!')