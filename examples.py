from force_types import *

@force_type # when stacking decorators, force_type must be applied as last (bottom)
def your_function(foo: str, bar: int):
   pass


@async_force_type # when stacking decorators, async_force_type must be applied as last (bottom)
async def your_function(foo: str, bar: int):
   pass
