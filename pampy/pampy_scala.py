from pampy import match, _
from pampy.helpers import NoDefault


class Case:
    def __init__(self, case):
        self.case = case

    def __rshift__(self, then):
        self.then = then

        return self

    def pair(self):
        return self.case, self.then


class Match:
    """
    Wrapper to improve the pattern matching syntax (Scala-like style).
    Usage example:

        from pampy import Match

        def fibonacci(n):

            return Match(n).of(
                Case(1) >> 0,
                Case(2) >> 1,
                Case(_) >> ( lambda x: fibonacci(x-1) + fibonacci(x-2) )
            )

    To add a default:

        Match(n).with_default(42).of(
            Case(1) >> 0,
            ...
        )
    """

    def __init__(self, v):
        self.value = v
        self.default = None

    def with_default(self, default):
        self.default = default

        return self

    def of(self, *cases):
        pairs = [c.pair() for c in cases]

        return match(
            self.value,
            *[v for tp in pairs for v in tp],
            default=self.default if self.default else NoDefault
        )
