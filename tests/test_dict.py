import unittest

from pampy import match_dict, _, match


class IterableTests(unittest.TestCase):

    def test_match_dict(self):
        self.assertEqual(match_dict({'a': _, 'b': 2}, {'a': 1, 'b': 2}), (True, [1]))

    def test_match_dict_ordering(self):
        for i in range(100):
            self.assertEqual(match_dict({'a': _, 'b': _}, {'a': 1, 'b': 2}), (True, [1, 2]))

    def test_match_asymmetric(self):
        self.assertEqual(match_dict({'a': _, 'b': 2},           {'a': 1, 'b': 2, 'c': 3}),    (True, [1]))
        self.assertEqual(match_dict({'a': _, 'b': 2, 'c': 3},   {'a': 1, 'b': 2}),            (False, []))

    def test_match_nested(self):
        self.assertEqual(match_dict({'a': {'b': _}, 'c': _},
                                    {'a': {'b': 1}, 'c': 2}), (True, [1, 2]))

    def test_dog(self):
        pet = {'type': 'dog', 'details': {'age': 3}}

        self.assertEqual(match(pet, {'details': {'age': _}},    lambda age: age),
                         3)
        self.assertEqual(match(pet, {_: {'age': _}},            lambda a, b: (a, b)),
                         ('details', 3))