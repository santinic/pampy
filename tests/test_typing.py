import unittest
from typing import (
    Callable,
    List,
    Set,
    FrozenSet,
    Mapping,
    Iterable,
    Dict,
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


class A:
    pass


class B(A):
    pass


class C(A):
    pass


class Z:
    pass

E = NewType("E", B)
lol = NewType("lol", int)
kek = NewType("kek", lol)
cat = NewType("cat", str)
double_kek = NewType('double_kek', Tuple[kek, kek])
composite_kek = NewType("CKek", Union[cat, double_kek])


def annotated(a: int) -> float:
    pass


def big_annotated(a: Tuple[int, float], b: str, c: E) -> double_kek:
    pass


def wrong_annotated(b: str) -> str:
    pass


def not_annotated(q):
    pass


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
        self.assertEqual(match_value(lol, 3), (True, [3]))
        self.assertEqual(match_value(kek, 3), (True, [3]))
        self.assertEqual(match_value(double_kek, (13, 37)), (True, [13, 37]))
        self.assertEqual(match_value(composite_kek, "Barsik"), (True, ["Barsik"]))
        self.assertEqual(match_value(composite_kek, (13, 37)), (True, [13, 37]))

    def test_match_type(self):
        self.assertEqual(match_value(Type[int], int), (True, [int]))
        self.assertEqual(match_value(Type[int], 1), (False, []))
        self.assertEqual(match_value(Type[E], "cat"), (False, []))
        self.assertEqual(match_value(Type[A], "cat"), (False, []))

        self.assertEqual(match_value(Type[lol], int), (True, [int]))
        self.assertEqual(match_value(Type[kek], int), (True, [int]))
        self.assertEqual(match_value(Type[kek], str), (False, []))

        self.assertEqual(match_value(Type[A], A), (True, [A]))
        self.assertEqual(match_value(Type[A], B), (True, [B]))
        self.assertEqual(match_value(Type[B], C), (False, []))
        self.assertEqual(match_value(Type[E], B), (True, [B]))

        self.assertEqual(match_value(Type[A], E), (True, [E]))

        self.assertEqual(match_value(Type[E], C), (False, []))
        self.assertEqual(match_value(Type[C], A), (False, []))

        self.assertEqual(match_value(Type[Any], A), (True, [A]))
        self.assertEqual(match_value(Type[Any], Z), (True, [Z]))
        self.assertEqual(match_value(Type[Any], int), (True, [int]))

    def test_match_callable(self):
        self.assertEqual(match_value(Callable[[int], float], annotated), (True, [annotated]))
        self.assertEqual(
            match_value(Callable[[Tuple[int, float], str, E], double_kek], big_annotated), (True, [big_annotated])
        )
        self.assertEqual(match_value(Callable[[int], float], not_annotated), (False, []))
        self.assertEqual(match_value(Callable[[Any], Any], not_annotated), (True, [not_annotated]))
        self.assertEqual(match_value(Callable[[int], float], wrong_annotated), (False, []))

    def test_match_tuple(self):
        self.assertEqual(
            match_value(Tuple[int, str], (1, "a")),
            (True, [1, "a"])
        )
        self.assertEqual(
            match_value(Tuple[int, str], (1, 1)),
            (False, [])
        )
        self.assertEqual(
            match_value(
                Tuple[
                    Union[int, float],
                    Callable[[int], float],
                    Tuple[str, Type[E]]
                ],
                (1.0, annotated, ("ololo", B))
            ),
            (True, [1.0, annotated, "ololo", B])
        )
        self.assertEqual(
            match_value(
                Tuple[
                    Union[int, float],
                    Callable[[int], float],
                    Tuple[str, Type[E]]
                ],
                (1.0, False, ("ololo", B))
            ),
            (False, [])
        )
        self.assertEqual(
            match_value(
                Tuple[
                    Union[int, float],
                    Callable[[int], float],
                    Tuple[str, Type[E]]
                ],
                ("kek", annotated, ("ololo", B))
            ),
            (False, [])
        )
        self.assertEqual(
            match_value(
                Tuple[
                    Union[int, float],
                    Callable[[int], float],
                    Tuple[str, Type[E]]
                ],
                (1, annotated, ("ololo", B, 1488))
            ),
            (False, [])
        )
        self.assertEqual(
            match_value(
                Tuple[
                    Union[int, float],
                    Callable[[int], float],
                    Tuple[str, Type[A]]
                ],
                (1, annotated, ("ololo", E))
            ),
            (True, [1, annotated, "ololo", E])
        )

    def test_match_mapping(self):
        self.assertEqual(match_value(Dict[str, int], {"a": 1, "b": 2}), (True, [{"a": 1, "b": 2}]))
        self.assertEqual(match_value(Mapping[str, lol], {"a": 1, "b": 2}), (True, [{"a": 1, "b": 2}]))
        self.assertEqual(match_value(Dict[str, lol], {"a": 1, "b": 2}), (True, [{"a": 1, "b": 2}]))
        self.assertEqual(match_value(Dict[str, int], {"a": 1.0, "b": 2.0}), (False, []))
        self.assertEqual(match_value(Dict[str, int], {1: 1, 2: 2}), (False, []))
        self.assertEqual(match_value(Mapping[str, int], {1: 1, 2: 2}), (False, []))
        self.assertEqual(match_value(Dict[Union[str, int], int], {1: 1, 2: 2}), (True, [{1: 1, 2: 2}]))
        self.assertEqual(match_value(Dict[Union[str, lol], int], {1: 1, 2: 2}), (True, [{1: 1, 2: 2}]))
        self.assertEqual(
            match_value(Dict[str, Callable[[int], float]], {"a": annotated, "b": annotated}),
            (True, [{"a": annotated, "b": annotated}])
        )

    def test_match_iterable(self):
        self.assertEqual(match_value(List[int], [1, 2, 3]), (True, [[1, 2, 3]]))
        self.assertEqual(match_value(List[int], range(10)), (False, []))
        self.assertEqual(match_value(Iterable[int], [1, 2, 3]), (True, [[1, 2, 3]]))
        self.assertEqual(match_value(Iterable[int], range(10)), (True, [range(10)]))
        self.assertEqual(match_value(List[lol], [1, 2, 3]), (True, [[1, 2, 3]]))
        self.assertEqual(match_value(List[str], [1, 2, 3]), (False, []))
        self.assertEqual(match_value(Iterable[str], [1, 2, 3]), (False, []))
        a_vals = [B(), C(), B()]
        self.assertEqual(match_value(List[A], a_vals), (True, [a_vals]))
        self.assertEqual(match_value(List[str], ["lol", "kek"]), (True, [["lol", "kek"]]))
        self.assertEqual(match_value(List[Union[str, int]], ["lol", "kek"]), (True, [["lol", "kek"]]))
        self.assertEqual(match_value(List[Union[str, int]], [1, 2, 3]), (True, [[1, 2, 3]]))
        self.assertEqual(match_value(List[int], {1, 2, 3}), (False, []))
        self.assertEqual(match_value(Set[int], {1, 2, 3}), (True, [{1, 2, 3}]))
        self.assertEqual(match_value(FrozenSet[int], frozenset([1, 2, 3])), (True, [frozenset([1, 2, 3])]))
