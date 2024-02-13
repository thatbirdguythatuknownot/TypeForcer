# TypeForcer
Simple copy-paste decorators to 'force' types for function parameters in Python with only type hinting!

Comes with `GenericAlias` support! (nested type hints in Iterables such as `list[int]`)

Its easy to use:
```py
from force_types import *
# force types supports ONE level of type hint nesting: -> list[str | int]
# does NOT support: -> list[dict[str, int]] (TWO level hint nesting)


@force_types # when stacking decorators, force_type must be applied as last (bottom)
def your_function(foo: list[str | int], bar: int) -> None:
    pass


@async_force_types # when stacking decorators, async_force_type must be applied as last (bottom)
async def async_your_function(foo: str, bar: int) -> None:
   pass


```
```py
your_function(['hi', 5.0], bar=5) # will throw a TypeError (due to invalid passed list (float instead of int))

>>> TypeError: ['hi', 5.0] -> Invalid type <class 'list'> for argument "foo" with hinted type list[str | int]
```
