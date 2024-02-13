from force_types import *
# force types supports ONE level of type hint nesting: -> list[str | int]
# does NOT support: -> list[dict[str, int]] (TWO level hint nesting)


@force_types # when stacking decorators, force_type must be applied as last (bottom)
def your_function(foo: list[str | int], bar: int) -> None:
    pass


@async_force_types # when stacking decorators, async_force_type must be applied as last (bottom)
async def async_your_function(foo: str, bar: int) -> None:
   pass


f = your_function(['hi', 5.0], bar=5) # will throw a TypeError (due to invalid passed list (float instead of int))