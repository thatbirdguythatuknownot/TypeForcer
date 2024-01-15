import typing

def force_types(func: typing.Callable):
    def wrapper(*args, **kwargs):
        annotations = func.__annotations__

        kwargs_list = list(annotations.keys())
        for i, arg in enumerate(args):
            kwargs[kwargs_list[i]] = arg

        for kwarg, value in kwargs.items():
            if not isinstance(value, annotations[kwarg]):
                raise TypeError(f'{value} is not of type {annotations[kwarg]}. Please submit parameters in their hinted type.')

        return func(**kwargs)
    return wrapper

def async_force_types(func: typing.Coroutine):
    async def wrapper(*args, **kwargs):
        annotations = func.__annotations__

        kwargs_list = list(annotations.keys())
        for i, arg in enumerate(args):
            kwargs[kwargs_list[i]] = arg

        for kwarg, value in kwargs.items():
            if not isinstance(value, annotations[kwarg]):
                raise TypeError(f'{value} is not of type {annotations[kwarg]}. Please submit parameters in their hinted type.')

        return await func(**kwargs)
    return wrapper
