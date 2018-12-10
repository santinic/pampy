import unittest

import re

from pampy import match_value, match, HEAD, TAIL, _, MatchError, register_pattern

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class RegisteredTests(unittest.TestCase):

    def test_match_value(self):
        p1 = Point(1, 1)
        p2 = Point(1, 1)
        pattern_work = False

        def point_comparer(p1, p2):
            if p1.x == p2.x and p1.y == p2.y:
                return True, [p2]

            return False, [p2]

        def pattern_ok(vals):
            pattern_work = True

        register_pattern(point_comparer)

        match(p1, p2, pattern_ok)

        self.assertTrue(pattern_ok)
