import unittest

import re

from pampy import match_value, match, HEAD, TAIL, _, MatchError


class PampyBasicTests(unittest.TestCase):

    def test_match_value(self):
        def match_value_bool(pat, var):
            return match_value(pat, var)[0]

        self.assertTrue(match_value_bool(3, 3))
        self.assertTrue(match_value_bool(int, 3))
        self.assertTrue(match_value_bool("ok", "ok"))
        self.assertTrue(match_value_bool(str, "ok"))
        self.assertTrue(match_value_bool(_, "ok"))
        self.assertTrue(match_value_bool(_, 3))
        self.assertTrue(match_value_bool(_, 3.3))
        self.assertTrue(match_value_bool(True, True))
        self.assertTrue(match_value_bool(False, False))
        self.assertFalse(match_value_bool(1, 3))

    def test_match_value_None(self):
        self.assertEqual(match_value(None, None), (True, []))

    def test_match_None(self):
        self.assertEqual(match(None, None, 'None', _, 'else'), 'None')

    def test_equality_comparison_should_be_strict(self):
        self.assertEqual(match_value(1, True), (False, []))
        self.assertEqual(match_value(0, False), (False, []))
        self.assertEqual(match_value(1.0, 1), (False, []))
        self.assertEqual(match_value(0.0, 0), (False, []))
        self.assertEqual(match_value(1.0, 1), (False, []))

    def test_match_value_is_vs_equal(self):
        a = 'x' * 1000000
        b = 'x' * 1000000
        self.assertEqual(a, b)
        self.assertFalse(a is b)
        self.assertEqual(match_value(a, b), (True, []))
        self.assertEqual(match(a, b, True), True)

    def test_match_value_var_extraction(self):
        self.assertEqual(match_value(3, 3), (True, []))
        self.assertEqual(match_value(_, 3), (True, [3]))
        self.assertEqual(match_value(_, 'ok'), (True, ['ok']))

    def test_match_value_callable_pattern(self):
        self.assertEqual(match_value(3, lambda: True), (False, []))

        func = lambda x: True
        self.assertEqual(match_value(callable, func), (True, [func]))

    def test_match_mylen(self):
        def mylen(l):
            return match(l,
                         [], 0,
                         [HEAD, TAIL], lambda head, tail: 1 + mylen(tail))

        self.assertEqual(mylen([]), 0)
        self.assertEqual(mylen([1]), 1)
        self.assertEqual(mylen([1, 2, 3]), 3)

    def test_match(self):
        self.assertTrue(match(3, 3, True))
        self.assertTrue(match(3, _, True))
        self.assertTrue(match(3,
                              1, False,
                              2, False,
                              _, True))

        self.assertTrue(match([1, 2],
                              [1], False,
                              [1, 2], True))

    def test_match_strict_raises(self):
        with self.assertRaises(MatchError):
            match(3, 2, True)

    def test_match_not_strict_returns_false(self):
        self.assertFalse(match(3, 2, True, strict=False))

    def test_match_arguments_passing(self):
        self.assertEqual(match([1, 2, 3], [1, _, 3], lambda x: x), 2)
        self.assertEqual(match([1, 2, 3], [1, 2, 3], lambda x: x), [1, 2, 3])

    def test_match_action_can_be_empty_list(self):
        self.assertEqual(match(True, True, []), [])

    def test_match_raise_lambda_error(self):
        with self.assertRaises(MatchError) as err:
            match([1, 2, 3], [1, _, 3], lambda: "xxxxx {}".format())
        self.assertIn('lambda', str(err.exception))
        self.assertIn('xxxxx', str(err.exception))
        # print(err.exception)

    def test_match_class_hierarchy(self):
        class Pet: pass
        class Dog(Pet): pass
        class Cat(Pet): pass
        class Hamster(Pet): pass

        def what_is(x):
            return match(x,
                Dog, 'dog',
                Cat, 'cat',
                Pet, 'any other pet',
                _, 'this is not a pet at all',
            )

        self.assertEqual(what_is(Cat()), 'cat')
        self.assertEqual(what_is(Dog()), 'dog')
        self.assertEqual(what_is(Hamster()), 'any other pet')
        self.assertEqual(what_is(Pet()), 'any other pet')
        self.assertEqual(what_is(True), 'this is not a pet at all')

    def test_regex_groups(self):
        def what_is(pet):
            return match(pet,
                re.compile('(\w+)-(\w+)-cat$'),     lambda name, my: 'cat '+name,
                re.compile('(\w+)-(\w+)-dog$'),     lambda name, my: 'dog '+name,
                _,                                  "something else"
            )

        self.assertEqual(what_is('fuffy-my-dog'), 'dog fuffy')
        self.assertEqual(what_is('puffy-her-dog'), 'dog puffy')
        self.assertEqual(what_is('carla-your-cat'), 'cat carla')
        self.assertEqual(what_is('roger-my-hamster'), 'something else')

    def test_regex_no_group(self):
        def what_is(pet):
            return match(pet,
                re.compile('fuffy-cat$'), lambda x: 'fuffy-cat',
                _, "something else"
            )

        self.assertEqual(what_is('my-fuffy-cat'), 'fuffy-cat')

