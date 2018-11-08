# Pampy: Pattern Matching for Python
Pampy is pretty small, pretty fast, and often makes your code more readable, and easier to reason about.

![Pampy logo](imgs/pampy.png "Pampy in Start Wars")

## How it works

The patterns are evaluated in the order they appear.

```python
from pampy import match, _

match(x,
    pattern1, action1,
    pattern2, action2,
    ...
)
```


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

## You can write a Lisp interpreter in 3 lines

```python
from pampy import match, REST, _

def lisp(exp):
    return match(exp,
        int,                lambda x: x,
        (callable, REST),   lambda f, rest: f(*[lisp(a) for a in args]))

lisp((+, 1, (-, 3, (sqrt 2))))         # => 1 + (3 - sqrt(2))
lisp((print (+ "hello " "lisp")))      # => "hello lisp"

```

## You can match so many things!

```python
match(x,
    3,          "this matches the number 3",
    int,        "matches any integer",
    (str, int), lambda a, b: "a (str, int) tuple used in a lambda",
    tuple,      "any other tuple not previously specified",
    _,          "anthing else"
)
```

## You can match [HEAD, TAIL]

```python
from pampy import match, HEAD, TAIL, _

x = [1,2,3,4]

match(x, [1, 2, TAIL],	lambda tail: tail)                   # => [3, 4]

match(x, [HEAD, TAIL], lambda head, tail: (head, tail))     # => (1, [2, 3, 4])

```

## You can nest lists and tuples

```python
from pampy import match, _

x = [1,[2,3],4]

match(x, [1, [_, 3], _], lambda a, b: [1, [a, 3], b])   # => [1,[2,3],4]
```

## You can go crazy, and implement match with match itself



## Install

It works for both python2 and python3. To install it:

```$ pip install pampy```

or
```$ pip3 install pampy```

or
```$ easy_install pampy```

