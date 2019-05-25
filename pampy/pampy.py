from collections.abc import Iterable
from itertools import zip_longest
from enum import Enum
from typing import Tuple, List
from typing import Pattern as RegexPattern

from pampy.helpers import *

_ = ANY = UnderscoreType()
HEAD = HeadType()
REST = TAIL = TailType()


def run(action, var):
    if callable(action):
        if isinstance(var, Iterable):
            try:
                return action(*var)
            except TypeError as err:
                raise MatchError(get_lambda_args_error_msg(action, var, err))
        elif isinstance(var, BoxedArgs):
            return action(var.get())
        else:
            return action(var)
    else:
        return action


def match_value(pattern, value) -> Tuple[bool, List]:
    if value is PaddedValue:
        return False, []
    elif isinstance(pattern, (int, float, str, bool, Enum)):
        eq = pattern == value
        type_eq = type(pattern) == type(value)
        return eq and type_eq, []
    elif pattern is None:
        return value is None, []
    elif isinstance(pattern, type):
        if isinstance(value, pattern):
            return True, [value]
    elif isinstance(pattern, (list, tuple)):
        return match_iterable(pattern, value)
    elif isinstance(pattern, dict):
        return match_dict(pattern, value)
    elif callable(pattern):
        return_value = pattern(value)

        if isinstance(return_value, bool):
            return return_value, [value]
        elif isinstance(return_value, tuple) and len(return_value) == 2 \
                and isinstance(return_value[0], bool) and isinstance(return_value[1], list):
            return return_value
        else:
            raise MatchError("Warning! pattern function %s is not returning a boolean "
                             "nor a tuple of (boolean, list), but instead %s" %
                             (pattern, return_value))
    elif isinstance(pattern, RegexPattern):
        rematch = pattern.search(value)
        if rematch is not None:
            return True, list(rematch.groups())
    elif pattern is _:
        return True, [value]
    elif pattern is HEAD or pattern is TAIL:
        raise MatchError("HEAD or TAIL should only be used inside an Iterable (list or tuple).")
    elif is_dataclass(pattern) and pattern.__class__ == value.__class__:
        return match_dict(pattern.__dict__, value.__dict__)
    return False, []


def match_dict(pattern, value) -> Tuple[bool, List]:
    if not isinstance(value, dict) or not isinstance(pattern, dict):
        return False, []

    total_extracted = []
    still_usable_value_keys = set(value.keys())
    still_usable_pattern_keys = set(pattern.keys())
    for pkey, pval in pattern.items():
        if pkey not in still_usable_pattern_keys:
            continue
        matched_left_and_right = False
        for vkey, vval in value.items():
            if vkey not in still_usable_value_keys:
                continue
            if pkey not in still_usable_pattern_keys:
                continue
            key_matched, key_extracted = match_value(pkey, vkey)
            if key_matched:
                value_matched, value_extracted = match_value(pval, vval)
                if value_matched:
                    total_extracted += key_extracted + value_extracted
                    matched_left_and_right = True
                    still_usable_pattern_keys.remove(pkey)
                    still_usable_value_keys.remove(vkey)
                    break
        if not matched_left_and_right:
            return False, []
    return True, total_extracted


def only_padded_values_follow(padded_pairs, i):
    i += 1
    while i < len(padded_pairs):
        pattern, value = padded_pairs[i]
        if pattern is not PaddedValue:
            return False
        i += 1
    return True


def match_iterable(patterns, values) -> Tuple[bool, List]:
    if not isinstance(patterns, Iterable) or not isinstance(values, Iterable):
        return False, []

    total_extracted = []
    padded_pairs = list(zip_longest(patterns, values, fillvalue=PaddedValue))

    for i, (pattern, value) in enumerate(padded_pairs):
        if pattern is HEAD:
            if i != 0:
                raise MatchError("HEAD can only be in first position of a pattern.")
            else:
                if value is PaddedValue:
                    return False, []
                else:
                    total_extracted += [value]
        elif pattern is TAIL:
            if not only_padded_values_follow(padded_pairs, i):
                raise MatchError("TAIL must me in last position of the pattern.")
            else:
                tail = [value for (pattern, value) in padded_pairs[i:] if value is not PaddedValue]
                total_extracted.append(tail)
                break
        else:
            matched, extracted = match_value(pattern, value)
            if not matched:
                return False, []
            else:
                total_extracted += extracted
    return True, total_extracted





def match(var, *args, default=NoDefault, strict=True, run_callable=True):
    """
    Match `var` against a number of potential patterns.

    Example usage:
    ```
    match(x,
        3,              "this matches the number 3",
        int,            "matches any integer",
        (str, int),     lambda a, b: "a tuple (a, b) you can use in a function",
        [1, 2, _],      "any list of 3 elements that begins with [1, 2]",
        {'x': _},       "any dict with a key 'x' and any value associated",
        _,              "anything else"
    )
    ```

    :param var: The variable to test patterns against.
    :param args: Alternating patterns and actions. There must be an action for every pattern specified.
                 Patterns can take many forms, see README.md for examples.
                 Actions can be either a literal value or a callable which will be called with the arguments that were
                    matched in corresponding pattern.
    :param default: If `default` is specified then it will be returned if none of the patterns match.
                    If `default` is unspecified then a `MatchError` will be thrown instead.
    :return: The result of the action which corresponds to the first matching pattern.
    """
    if len(args) % 2 != 0:
        raise MatchError("Every guard must have an action.")

    if default is NoDefault and strict is False:
        default = False

    pairs = list(pairwise(args))
    patterns = [patt for (patt, action) in pairs]

    for patt, action in pairs:
        matched_as_value, args = match_value(patt, var)

        if matched_as_value:
            lambda_args = args if len(args) > 0 else BoxedArgs(var)
            return run(action, lambda_args) if run_callable else action

    if default is NoDefault:
        if _ not in patterns:
            raise MatchError("'_' not provided. This case is not handled:\n%s" % str(var))
    else:
        return default


class MatchError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
