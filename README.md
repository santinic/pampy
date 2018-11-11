![Pampy in Star Wars](https://raw.githubusercontent.com/santinic/pampy/master/imgs/pampy.png "Pampy in Star Wars")

# Pampy: Pattern Matching for Python
[![License MIT](https://go-shields.herokuapp.com/license-MIT-blue.png)]()
[![Travis-CI Status](https://api.travis-ci.org/santinic/pampy.svg?branch=master)](https://travis-ci.org/santinic/pampy)
[![Coverage Status](https://coveralls.io/repos/github/santinic/pampy/badge.svg?branch=master)](https://coveralls.io/github/santinic/pampy?branch=master)
[![PyPI version](https://badge.fury.io/py/pampy.svg)](https://badge.fury.io/py/pampy)

Pampy is pretty small (150 lines), reasonably fast, and often makes your code more readable, and easier to reason about.

<kbd>
  <img src="https://raw.githubusercontent.com/santinic/pampy/master/imgs/slide1.png" width="700">
</kbd>

## You can write many patterns

Patterns are evaluated in the order they appear.

<kbd>
  <img src="https://raw.githubusercontent.com/santinic/pampy/master/imgs/slide2.png" width="700">
</kbd>


## You can write Fibonacci
The operator _ means "any other case I didn't think of".

```python
from pampy import match, _

def fibonacci(n):
    return match(n,
        1, 1,
        2, 1,
        _, lambda x: fibonacci(x-1) + fibonacci(x-2)
    )
```

## You can write a Lisp calculator in 5 lines

```python
from pampy import match, REST, _

def lisp(exp):
    return match(exp,
        int,                lambda x: x,
        callable,           lambda x: x,
        (callable, REST),   lambda f, rest: f(*map(lisp, rest)),
        tuple,              lambda t: list(map(lisp, t)),
    )

plus = lambda a, b: a + b
minus = lambda a, b: a - b
from functools import reduce

lisp((plus, 1, 2))                 	# => 3
lisp((plus, 1, (minus, 4, 2)))     	# => 3
lisp((reduce, plus, (1, 2, 3)))   	# => 6
```

## You can match so many things!

```python
match(x,
    3,              "this matches the number 3",

    int,            "matches any integer",

    (str, int),     lambda a, b: "a tuple (a, b) you can use in a function",

    [1, 2, _],      "any list of 3 elements that begins with [1, 2]",

    {'x': _},       "any dict with a key 'x' and any value associated",

    _,              "anything else"
)
```

## You can match [HEAD, TAIL]

```python
from pampy import match, HEAD, TAIL, _

x = [1, 2, 3]

match(x, [1, TAIL],     lambda t: t)            # => [2, 3]

match(x, [HEAD, TAIL],  lambda h, t: (h, t))    # => (1, [2, 3])

```
`TAIL` and `REST` actually mean the same thing.

## You can nest lists and tuples

```python
from pampy import match, _

x = [1, [2, 3], 4]

match(x, [1, [_, 3], _], lambda a, b: [1, [a, 3], b])           # => [1, [2, 3], 4]
```

## You can nest dicts. And you can use _ as key!

```python

pet = { 'type': 'dog', 'details': { 'age': 3 } }

match(pet, { 'details': { 'age': _ } }, lambda age: age)        # => 3

match(pet, { _ : { 'age': _ } },        lambda a, b: (a, b))    # => ('details', 3)
```

It feels like putting multiple _ inside dicts shouldn't work. Isn't ordering in dicts not guaranteed ?
But it does because
[in Python 3.7, dict is an OrderedDict by default](https://mail.python.org/pipermail/python-dev/2017-December/151283.html)

## You can match class hierarchies

```python
class Pet:          pass
class Dog(Pet):     pass
class Cat(Pet):     pass
class Hamster(Pet): pass

def what_is(x):
    return match(x,
        Dog, 		'dog',
        Cat, 		'cat',
        Pet, 		'any other pet',
          _, 		'this is not a pet at all',
    )

what_is(Cat())      # => 'cat'
what_is(Dog())      # => 'dog'
what_is(Hamster())  # => 'any other pet'
what_is(Pet())      # => 'any other pet'
what_is(42)         # => 'this is not a pet at all'
```

## All the things you can match

As Pattern you can use any Python type, any class, or any Python value.

The operator `_` and types like `int` or `str`, extract variables that are passed to functions.

Types and Classes are matched via `instanceof(value, pattern)`.

`Iterable` Patterns match recursively through all their elements.  The same goes for dictionaries.

| Pattern Example | What it means | Matched Example |  Arguments Passed to function | NOT Matched Example |
| --------------- | --------------| --------------- | ----------------------------- | ------------------ |
| `"hello"` |  only the string `"hello"` matches | `"hello"` | nothing | any other value |
| `None` | only `None` | `None` | nothing | any other value |
| `int` | Any integer | `42` | `42` | any other value |
| `float` | Any float number | `2.35` | `2.35` | any other value |
| `str` | Any string | `"hello"` | `"hello"` | any other value |
| `tuple` | Any tuple | `(1, 2)` | `(1, 2)` | any other value |
| `list` | Any list | `[1, 2]` | `[1, 2]` | any other value |
| `MyClass` | Any instance of MyClass. **And any object that extends MyClass.** | `MyClass()` | that instance | any other object |
| `_` | Any object (even None) |  | that value | |
| `ANY` | The same as `_` | | that value | |
| `(int, int)` | A tuple made of any two integers | `(1, 2)` | `1` and `2` | (True, False) |
| `[1, 2, _]`  | A list that starts with 1, 2 and ends with any value | `[1, 2, 3]` | `3` | `[1, 2, 3, 4]` |
| `[1, 2, TAIL]` | A list that start with 1, 2 and ends with any sequence | `[1, 2, 3, 4]`| `[3, 4]` | `[1, 7, 7, 7]` |
| `{'type':'dog', age: _ }` | Any dict with `type: "dog"` and with an age | `{"type":"dog", "age": 3}` | `3` | `{"type":"cat", "age":2}` |
| `{'type':'dog', age: int }` | Any dict with `type: "dog"` and with an `int` age | `{"type":"dog", "age": 3}` | `3` | `{"type":"dog", "age":2.3}` |
| `re.compile('(\w+)-(\w+)-cat$')` | Any string that matches that regular expression expr | `"my-fuffy-cat"` | `"my"` and `"puffy"` | `"fuffy-dog"` | 

## Using strict=False

By default `match()` is strict. If no pattern matches, it raises a `MatchError`.

You can prevent it using `strict=False`. In this case `match` just returns `False` if nothing matches.

```
>>> match([1, 2], [1, 2, 3], "whatever")
MatchError: '_' not provided. This case is not handled: [1, 2]

>>> match([1, 2], [1, 2, 3], "whatever", strict=False)
False
```

## Using Regular Expressions
Pampy supports Python's Regex. You just need to pass a compiled regex as pattern, and Pampy is going to run `patter.search()`, and pass to the action function the result of `.groups()`.

```python 
def what_is(pet):
    return match(pet,
        re.compile('(\w+)-(\w+)-cat$'),     lambda name, my: 'cat '+name,
        re.compile('(\w+)-(\w+)-dog$'),     lambda name, my: 'dog '+name,
        _,                                  "something else"
    )

what_is('fuffy-my-dog')  		# => 'dog fuffy'
what_is('puffy-her-dog') 		# => 'dog puffy'
what_is('carla-your-cat') 	 	# => 'cat carla'
what_is('roger-my-hamster') 	# => 'something else'
```

## Install

Currently it works only in Python > 3.6 [Because dict matching can work only in the latest Pythons](https://mail.python.org/pipermail/python-dev/2017-December/151283.html).

I'm currently working on a backport with some minor syntax changes for Python2.

To install it:

```$ pip install pampy```

or
```$ pip3 install pampy```


<!--We could port it also to Python 2 but we'd need to change the dict matching syntax.-->
