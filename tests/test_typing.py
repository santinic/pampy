import unittest
from typing import (
    List,
    Any,
    Union,
    Tuple,
    NewType,
    Optional,
    Type,
)

from pampy import (
    match,
    match_value,
)


class PampyTypingTests(unittest.TestCase):

    def test_match_any(self):
        self.assertEqual(match_value(Any, 3), (True, [3]))
        self.assertEqual(match_value(Any, 'ok'), (True, ['ok']))

    def test_match_union(self):
        self.assertEqual(match_value(Union[int, str], 3), (True, [3]))
        self.assertEqual(match_value(Union[int, str], 'ok'), (True, ['ok']))
        self.assertEqual(match_value(Union[int, str, float], 5.25), (True, [5.25]))
        self.assertEqual(match_value(Optional[int], None), (True, [None]))
        self.assertEqual(match_value(Optional[int], 1), (True, [1]))
        self.assertEqual(match_value(Optional[int], 1.0), (False, []))

    def test_match_newtype(self):
        lol = NewType("lol", int)
        kek = NewType("kek", lol)
        cat = NewType("cat", str)
        double_kek = NewType('double_kek', Tuple[kek, kek])
        composite_kek = NewType("CKek", Union[cat, double_kek])

        self.assertEqual(match_value(lol, 3), (True, [3]))
        self.assertEqual(match_value(kek, 3), (True, [3]))
        # self.assertEqual(match_value(double_kek, (13, 37)), (True, [13, 37]))
        # self.assertEqual(match_value(composite_kek, "Barsik"), (True, ["Barsik"]))
        # self.assertEqual(match_value(composite_kek, (13, 37)), (True, [13, 37]))

    def test_match_type(self):
        lol = NewType("lol", int)
        kek = NewType("kek", lol)

        self.assertEqual(match_value(Type[int], int), (True, [int]))
        self.assertEqual(match_value(Type[int], 1), (False, []))

        self.assertEqual(match_value(Type[lol], lol), (True, [lol]))
        self.assertEqual(match_value(Type[int], lol), (True, [lol]))
        self.assertEqual(match_value(Type[lol], int), (False, []))
