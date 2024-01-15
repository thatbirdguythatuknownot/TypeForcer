import typing

def force_types(func: typing.Callable):
    def wrapper(*args, **kwargs):
        annotations = func.__annotations__
        for missing_kwarg, arg in zip(annotations.keys(), args):
            kwargs[missing_kwarg] = arg  

        for kwarg, value in kwargs.items():
            if not isinstance(value, annotations[kwarg]):
                raise TypeError(f'{value} is not of type {annotations[kwarg]}. Please submit parameters in their hinted type.')

        return func(**kwargs)
    return wrapper

def async_force_types(func: typing.Coroutine):
    async def wrapper(*args, **kwargs):
        annotations = func.__annotations__
        for missing_kwarg, arg in zip(annotations.keys(), args):
            kwargs[missing_kwarg] = arg  

        for kwarg, value in kwargs.items():
            if not isinstance(value, annotations[kwarg]):
                raise TypeError(f'{value} is not of type {annotations[kwarg]}. Please submit parameters in their hinted type.')

        return await func(**kwargs)
    return wrapper
