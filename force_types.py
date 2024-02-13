import typing

def force_types(func: typing.Callable):
    def wrapper(*args, **kwargs):
        annotations = func.__annotations__

        for missing_kwarg, arg in zip(annotations.keys(), args):
            kwargs[missing_kwarg] = arg  

        for kwarg, value in reversed(kwargs.items()):
            annotation = annotations[kwarg]
            annotation_origin = getattr(annotation, "__origin__", annotation)

            if not isinstance(value, annotation_origin):
                raise TypeError(f'{value} -> Invalid type {type(value)} for argument "{kwarg}" with hinted type {annotation}')

            # GenericAlias support (nested hints): list[str | int], dict[int, int]
            if isinstance(value, typing.Union[typing.Iterable, typing.AsyncIterable, typing.Iterator, typing.AsyncIterator]) and hasattr(annotation, '__args__'):
                    raise_exception = False
                    if isinstance(annotation.__origin__, type(dict)) and len(annotation.__args__) > 1:
                        if len(list(filter(lambda x: isinstance(x, annotation.__args__[0]) and isinstance(value[x], annotation.__args__[1]), value))) < len(value):
                            raise_exception = True
                    else:
                        if len(list(filter(lambda x: isinstance(x, annotation.__args__), value))) < len(value):
                            raise_exception = True

                    if raise_exception:
                        raise TypeError(f'Invalid return type {type(value)} [{value}] should be of type {annotation}')

        return func(**kwargs)
    return wrapper

def async_force_types(func: typing.Coroutine):
    async def wrapper(*args, **kwargs):
        annotations = func.__annotations__

        for missing_kwarg, arg in zip(annotations.keys(), args):
            kwargs[missing_kwarg] = arg  

        for kwarg, value in reversed(kwargs.items()):
            annotation = annotations[kwarg]
            annotation_origin = getattr(annotation, "__origin__", annotation)

            if not isinstance(value, annotation_origin):
                raise TypeError(f'{value} -> Invalid type {type(value)} for argument "{kwarg}" with hinted type {annotation}')

            # GenericAlias support (nested hints): list[str | int], dict[int, int]
            if isinstance(value, typing.Union[typing.Iterable, typing.AsyncIterable, typing.Iterator, typing.AsyncIterator]) and hasattr(annotation, '__args__'):
                    raise_exception = False
                    if isinstance(annotation.__origin__, type(dict)) and len(annotation.__args__) > 1:
                        if len(list(filter(lambda x: isinstance(x, annotation.__args__[0]) and isinstance(value[x], annotation.__args__[1]), value))) < len(value):
                            raise_exception = True
                    else:
                        if len(list(filter(lambda x: isinstance(x, annotation.__args__), value))) < len(value):
                            raise_exception = True

                    if raise_exception:
                        raise TypeError(f'Invalid return type {type(value)} [{value}] should be of type {annotation}')

        return await func(**kwargs)
    return wrapper
