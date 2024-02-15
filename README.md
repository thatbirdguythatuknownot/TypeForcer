# TypeForcer
Simple copy-paste decorators to 'force' types for function parameters in Python with only type hinting!

Comes with `GenericAlias` support! (nested type hints in Iterables such as `list[int]`)

TODO: `Callable` (and subfeatures, e.g. `ParamSpec`) support, `TypeVar`/`TypeVarTuple` checking

Its easy to use:
```py
from force_types import *
# can now support more than one level of nesting: -> list[dict[str, int]] (TWO level hint nesting)


@force_types # when stacking decorators, force_type must be applied as last (bottom)
def your_function(foo: list[str | int], bar: int) -> None:
    pass


@async_force_types # when stacking decorators, async_force_type must be applied as last (bottom)
async def async_your_function(foo: str, bar: int) -> None:
   pass


```
```py
your_function(['hi', 5.0], bar=5) # will throw a TypeError (due to invalid passed list (float instead of int))

>>> TypeError: ['hi', 5.0] -> argument "foo" type mismatch!
>>> recursive checker traceback (deepest layer first):
>>>     type: float -> fails: str | int (at level 1) (from value: 5.0)
>>>     type: list -> fails: list (at level 0, index 1) (from value: ['hi', 5.0])
```
