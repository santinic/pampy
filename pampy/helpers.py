import inspect


class UnderscoreType:
    def __repr__(self):
        return '_'


class HeadType:
    def __repr__(self):
        return 'HEAD'


class TailType:
    def __repr__(self):
        return 'TAIL'


class PaddedValueType:
    def __repr__(self):
        return 'PaddedValue'


PaddedValue = PaddedValueType()


class BoxedArgs:
    def __init__(self, obj):
        self.obj = obj

    def get(self):
        return self.obj


def pairwise(l):
    i = 0
    while i < len(l):
        yield l[i], l[i + 1]
        i += 2


def get_lambda_args_error_msg(action, var, err):
    try:
        code = inspect.getsource(action)
        return "Error passing arguments %s here:\n%s\n%s" % (var, code, err)
    except OSError:
        return "Error passing arguments %s:\n%s" % (var, err)


def is_dataclass(value):
    """
    Dataclass support is only enabled in Python 3.7+, or in 3.6 with the `dataclasses` backport installed
    """
    try:
        from dataclasses import is_dataclass
        return is_dataclass(value)
    except ImportError:
        return False
