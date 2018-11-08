import unittest

from pampy import match, REST, TAIL, HEAD, _, match_value, match_iterable, MatchError


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

    def test_match_value_var_extraction(self):
        self.assertEqual(match_value(3, 3), (True, []))
        self.assertEqual(match_value(_, 3), (True, [3]))
        self.assertEqual(match_value(_, 'ok'), (True, ['ok']))

    def test_match_iterable(self):
        self.assertEquals(match_iterable([1, 2, 3], [1, 2, 3]), (True, []))
        self.assertEquals(match_iterable([1, 2], [1, 3]), (False, []))

        self.assertEquals(match_iterable([1, 2], [1]), (False, []))

    def test_match_iterable_underscore(self):
        self.assertEqual(match_iterable([1, _, 3], [1, 2, 3]), (True, [2]))
        self.assertEqual(match_iterable([1, _, _], [1, 2, 3]), (True, [2, 3]))
        self.assertEqual(match_iterable([_, 2, _], [1, 2, 3]), (True, [1, 3]))

    def test_match_iterable_nested(self):
        self.assertEqual(match_iterable([1, [2, 3]], [1, [2, 3]]), (True, []))
        self.assertEqual(match_iterable([1, [2, _]], [1, [2, 3]]), (True, [3]))
        self.assertEqual(match_iterable([1, [2, _], _],
                                        [1, [2, 3], 4]), (True, [3, 4]))
        self.assertEqual(match_iterable([1, [2, [_, 4], _], _],
                                        [1, [2, [3, 4], 5], 6]), (True, [3, 5, 6]))

    def test_match_iterable_basic_HEAD(self):
        self.assertEqual(match_iterable([HEAD], [1]), (True, [1]))
        self.assertEqual(match_iterable([HEAD], []), (False, []))

    def test_match_iterable_HEAD(self):
        self.assertEqual(match_iterable([HEAD, 2], [1, 2]), (True, [1]))
        self.assertEqual(match_iterable([HEAD, _], [1, 2]), (True, [1, 2]))

    def test_match_iterable_TAIL(self):
        self.assertEqual(match_iterable([TAIL], [1, 2, 3]), (True, [1, 2, 3]))
        self.assertEqual(match_iterable([_, TAIL], [1, 2, 3]), (True, [1, 2, 3]))
        self.assertEqual(match_iterable([_, _, TAIL], [1, 2, 3]), (True, [1, 2, 3]))

        self.assertEqual(match_iterable([_, _, TAIL], [1, 2]), (False, []))

    def test_match_iterable_HEAD_TAIL(self):
        self.assertEqual(match_iterable([HEAD, TAIL], [1, 2, 3]), (True, [1, [2, 3]]))
        self.assertEqual(match_iterable([HEAD, TAIL], [1]), (True, [1, []]))
        self.assertEqual(match_iterable([HEAD, TAIL], []), (False, []))

    def test_match_iterable_HEAD_should_be_in_first_position(self):
        with self.assertRaises(MatchError):
            match_iterable([1, HEAD], [1, 2])

        with self.assertRaises(MatchError):
            match_iterable([1, HEAD, 3], [1, 2, 3])

    def test_match_iterable_TAIL_should_be_in_last_position(self):
        with self.assertRaises(MatchError):
            match_iterable([1, TAIL, 3], [1, 2, 3])

        with self.assertRaises(MatchError):
            match_iterable([TAIL, 2], [1, 2, 3])

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
