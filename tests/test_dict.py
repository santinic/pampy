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

        self.assertEqual(match(pet, {'details': {'age': _}},    lambda age: age),       3)
        self.assertEqual(match(pet, {        _: {'age': _}},    lambda a, b: (a, b)),   ('details', 3))

    def test_exclude_previously_used_keys(self):
        x = {"a": 1, "b": 2}
        self.assertEqual(match_dict({"a": _, _: _  }, x), (True, [1, "b", 2]))
        self.assertEqual(match_dict({"a": _, _: int}, x), (True, [1, "b", 2]))
        self.assertEqual(match_dict({"a": _, _: int}, x), (True, [1, "b", 2]))

    # def test_ambiguous_double_match(self):
    #     self.assertEqual(match_dict({"a": _, _: int},
    #                                 {"a": 1, "b": 2, "c": 3}), (True, [1, "b", 2]))

    # def test_multi_underscore_key_and_value(self):
    #     x = {"type": "pet", "cat-name": "bonney", "info": {"age": 1}},
    #     self.assertEqual(match_dict({"type": _, "cat-name": str},   x),   (True, ["pet", "bonney"]))
    #     self.assertEqual(match_dict({"type": _,          _: str},   x),   (True, ["pet", "cat-name", "bonney"]))

    # def test_wild_dicts(self):
    #     data = [
    #         {"type": "dog", "dog-name": "fuffy", "info": {"age": 2}},
    #         {"type": "pet", "dog-name": "puffy", "info": {"age": 1}},
    #         {"type": "cat", "cat-name": "buffy", "cat-info": {"age": 3}},
    #     ]
    #
    #     # I want the average age of a pet, but the data is inconsistent :/
    #     ages = [match(row, {_: {"age": int}}, lambda field, age: age) for row in data]
    #     average_age = sum(ages) / len(ages)
    #
    #     # I want al the names, but data is inconsistent!
    #     names = [match(row, {"type": _, _: str}, lambda type, name: name) for row in data]

