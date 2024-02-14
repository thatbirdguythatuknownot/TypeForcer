import inspect
import types
import typing
from dataclasses import dataclass
from itertools import chain

def type_name(typ: type) -> str:
    if hasattr(typ, "__qualname__"):
        return typ.__qualname__
    if hasattr(typ, "__name__"):
        return typ.__name__
    return repr(typ)

@dataclass
class Annotation:
    annotation: object
    idx: int | None = None
    level: int | None = None

    def __str__(self):
        annotation_s = type_name(self.annotation)

        if self.idx is None:
            if self.level is None:
                return annotation_s
            return f"{annotation_s} (at level {self.level})"

        if self.level is None:
            return f"{annotation_s} (index {self.idx})"
        return f"{annotation_s} (at level {self.level}, index {self.idx})"

@dataclass
class Failed:
    value: object
    annotation: object

    def __str__(self):
        value_typename = type_name(type(self.value))
        return f"type: {value_typename} -> fails: {self.annotation} (from value: {self.value!r})"

# returns [Failed(offending_value, annotation), ...] if it failed, otherwise None
def recursive_check(value, annotation, level=0):
    if annotation is None:
        if value is None:
            return None
        return [Failed(value, Annotation(None, level=level))]

    annotation_origin = getattr(annotation, "__origin__", annotation)
    if not isinstance(value, annotation_origin):
        return [Failed(value, Annotation(annotation, level=level))]

    # check for things like str | int and typing.Union[str, int] and
    # turn them into (str, int)
    # also turns Optional[str] into (str, type(None))
    if isinstance(annotation, (types.UnionType, typing._UnionGenericAlias)):
        annotation = annotation.__args__
    if isinstance(annotation, tuple):
        for annot in annotation:
            if not recursive_check(value, annot, level + 1):
                return None
        return [Failed(value, Annotation(annotation, level=level))]

    fail = None
    # GenericAlias support (nested hints): list[str | int], dict[int, int]
    if isinstance(
        value,
        (
            typing.Iterable,
            typing.AsyncIterable,
        )
    ) and not isinstance(
        value,
        (
            typing.Iterator,
            typing.AsyncIterator,
        )
    ) and hasattr(annotation, "__args__") and isinstance(
        annotation,
        (
            types.GenericAlias,
            typing._GenericAlias,
        )
    ):
        if ann_args := annotation.__args__:
            if annotation_origin in (tuple, typing.Tuple):
                if len(value) != len(ann_args):
                    return [Failed(value, Annotation(annotation, level=level))]

                for i, (x, typ) in enumerate(zip(value, ann_args)):
                    if fail := recursive_check(x, typ, level + 1):
                        fail.append(Failed(value, Annotation(annotation, i, level)))
                        break

            elif annotation_origin in (dict, typing.Dict):
                tkey, tval = ann_args

                for i, (key, val) in enumerate(value.items()):
                    if fail := recursive_check(key, tkey, level + 1):
                        fail.append(Failed(value, Annotation(annotation, i, level)))
                        break
                    if fail := recursive_check(val, tval, level + 1):
                        fail.append(Failed(value, Annotation(annotation, i, level)))
                        break

            else:
                if len(ann_args) == 1:
                    ann_args, = ann_args

                for i, x in enumerate(value):
                    if fail := recursive_check(x, ann_args, level + 1):
                        fail.append(Failed(value, Annotation(annotation, i, level)))
                        break
    return fail

def force_types(func: typing.Callable):
    sig = inspect.signature(func)
    annotations = func.__annotations__
    has_return = 'return' in annotations
    if has_return:
        return_annotation = annotations['return']

    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)

        for arg, value in chain(bound.arguments.items(),
                                bound.kwargs):
            if arg not in annotations:
                continue

            if fail := recursive_check(value, annotations[arg]):
                err = TypeError(f'argument "{arg}" type mismatch!')
                err.add_note("recursive checker traceback (deepest layer first):")
                for failure in fail:
                    err.add_note(f"    {failure}")
                raise err

        res = func(*args, **kwargs)
        if has_return:
            if fail := recursive_check(res, return_annotation):
                err = TypeError(f'return type mismatch!')
                err.add_note("recursive checker traceback (deepest layer first):")
                for failure in fail:
                    err.add_note(f"    {failure}")

        return res
    return wrapper

def async_force_types(func: typing.Callable):
    sig = inspect.signature(func)
    annotations = func.__annotations__
    has_return = 'return' in annotations
    if has_return:
        return_annotation = annotations['return']

    async def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)

        for arg, value in chain(bound.arguments.items(),
                                bound.kwargs):
            if arg not in annotations:
                continue

            if fail := recursive_check(value, annotations[arg]):
                err = TypeError(f'argument "{arg}" type mismatch!')
                err.add_note("recursive checker traceback (deepest layer first):")
                for failure in fail:
                    err.add_note(f"    {failure}")
                raise err

        res = await func(*args, **kwargs)
        if has_return:
            if fail := recursive_check(res, return_annotation):
                err = TypeError(f'return type mismatch!')
                err.add_note("recursive checker traceback (deepest layer first):")
                for failure in fail:
                    err.add_note(f"    {failure}")

        return res
    return wrapper
