from pampy import match


class Var:
    def __init__(self):
        pass

    def __invert__(self):
        print("inverted", self.name)


def vars(n):
    return (Var() for i in range(n))



pets = [
    {'type': 'dog', 'details': {'age': 4}},
    {'type': 'cat', 'details': {'age': 2}},
    {'type': 'dog', 'details': {'age': 1}},
]


# typ, age = vars(3)
match(pets, [{'type': _, 'details': {'age': _ }}], lambda x: x)
