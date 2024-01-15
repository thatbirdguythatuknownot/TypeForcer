# TypeForcer
Simple copy-paste decorators to 'force' types for function parameters in Python with only type hinting!

Currently does not support hinted returned values. Will add this in a bit!

Its easy to use:
```py
from force_types import *

@force_types # when stacking decorators, force_type must be applied as last (bottom)
def your_function(foo: str, bar: int):
   pass


@async_force_types # when stacking decorators, async_force_type must be applied as last (bottom)
async def your_async_function(foo: str, bar: int):
   pass


f = your_function(2, bar='test') # will throw a TypeError
```
