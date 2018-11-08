import inspect
from collections import Iterable
from itertools import zip_longest
from typing import Tuple, List

from helpers import UnderscoreType, HeadType, TailType, BoxedArgs, PaddedValue, pairwise

ValueType = (int, float, str, bool)
_ = UnderscoreType()
HEAD = HeadType()
REST = TAIL = TailType()


def run(action, var):
    if callable(action):
        if isinstance(var, Iterable):
            try:
                return action(*var)
            except TypeError as err:
                code = inspect.getsource(action)
                raise MatchError("Error passing argument %s here:\n%s\n%s" % (var, code, err))
        elif isinstance(var, BoxedArgs):
            return action(var.get())
        else:
            return action(var)
    elif isinstance(action, ValueType):
        return action
    else:
        raise MatchError("Action %s is neither callable nor a value." % action)


def match_value(pattern, value) -> Tuple[bool, List]:
    if isinstance(pattern, ValueType):
        return pattern == value, []
    elif isinstance(pattern, type):
        if isinstance(value, pattern):
            return True, [value]
        else:
            return False, []
    elif isinstance(pattern, list):
        return match_iterable(pattern, value)
    elif pattern is _:
        return True, [value]
    return False, []


def only_padded_values_follow(padded_pairs, i):
    i += 1
    while i < len(padded_pairs):
        pattern, value = padded_pairs[i]
        if pattern is not PaddedValue:
            return False
        i += 1
    return True


def match_iterable(patterns, values) -> Tuple[bool, List]:
    total_extracted = []
    padded_pairs = list(zip_longest(patterns, values, fillvalue=PaddedValue))

    for i, (pattern, value) in enumerate(padded_pairs):
        if pattern is HEAD:
            if i is not 0:
                raise MatchError("HEAD can only be in first position of a pattern.")
            else:
                if value is PaddedValue:
                    return False, []
                else:
                    total_extracted += [value]
        elif pattern is TAIL:
            # check TAIL is in the last position of the pattern, before a sequence of PaddedValues
            # TODO: infinite patterns ? maybe I should not do this.
            if not only_padded_values_follow(padded_pairs, i):
                raise MatchError("TAIL must me in last position of a pattern.")
            else:
                tail = [value for (pattern, value) in padded_pairs[i:]]
                total_extracted += tail
                break
        else:
            matched, extracted = match_value(pattern, value)
            if not matched:
                return False, []
            else:
                total_extracted += extracted
    return True, total_extracted


def match(var, *args, strict=True):
    if len(args) % 2 != 0:
        raise MatchError("Every guard must have an action.")

    pairs = list(pairwise(args))
    patterns = [patt for (patt, action) in pairs]

    for patt, action in pairs:
        matched_as_value, args = match_value(patt, var)

        if matched_as_value:
            lambda_args = args if len(args) > 0 else BoxedArgs(var)
            return run(action, lambda_args)

    if strict:
        if _ not in patterns:
            raise MatchError("'_' not provided. This case is not handled:\n%s" % str(var))
    else:
        return False


class MatchError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
