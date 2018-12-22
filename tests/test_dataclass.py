import unittest
import pytest
import sys

from pampy import match, _


class PampyDataClassesTests(unittest.TestCase):

    @pytest.mark.skipif(sys.version_info < (3, 7),
                        reason="requires python3.7 or higher")
    def test_match_dataclasses(self):
        from dataclasses import dataclass
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