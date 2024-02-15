import inspect
import types
import typing
from dataclasses import dataclass
from itertools import chain
from sys import version_info

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
        return (
            f"type: {value_typename} -> fails: {self.annotation} "
            f"(from value: {self.value!r})"
        )

# Returns `[Failed(), ...]` if it failed, otherwise `None`
def recursive_check(value, annotation, level=0) -> list[Failed] | None:
    # `Any` and `object` succeed for *any* Python value.
    # Consider `...` (`Ellipsis`) an all-pass too.
    if annotation in (Any, object, Ellipsis):
        return None

    # `typing.NoReturn` and `typing.Never` fail for *any* Python value.
    if annotation in (typing.NoReturn, typing.Never):
        early_fail = True

    # `| None` or `Optional` case.
    if annotation in (None, types.NoneType):
        if value is None:
            return None
        early_fail = True

    else:
        if hasattr(annotation, "__origin__"):
            annotation_origin = annotation.__origin__
        else:
            annotation_origin = annotation

        # Check for things like `str | int` and `typing.Union[str, int]` and
        # turn them into `(str, int)`.
        # Also turns `typing.Optional[str]` into `(str, type(None)).`
        # After converting into a tuple, it falls through to the next `if`
        # statement.
        if (
            isinstance(annotation, types.UnionType)
            or annotation_origin is typing.Union
            or annotation_origin is typing.Optional
        ):
            annotation = annotation.__args__
        # Check `(str, int)` in the way that the valid type for
        # `value` is either `str` or `int`.
        if isinstance(annotation, tuple):
            for annot in annotation:
                if not recursive_check(value, annot, level + 1):
                    return None
            early_fail = True
        else:
            early_fail = not isinstance(value, annotation_origin)

    if early_fail:
        return [Failed(value, Annotation(annotation, level=level))]

    fail = None
    # GenericAlias support (nested hints): list[str | int], dict[int, int]
    if isinstance(
        annotation,
        (
            types.GenericAlias,
            typing._GenericAlias,
        )
    ):
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
        ):
            ann_args = annotation.__args__
            failed_idx = -1

            if issubclass(annotation_origin, typing.Tuple):
                # Handle something like `tuple[int, ...]` (homogenous tuple).
                if len(ann_args) == 2 and ann_args[1] is Ellipsis:
                    annot = ann_args[0]
                    for i, x in enumerate(value):
                        if fail := recursive_check(x, annot, level + 1):
                            failed_idx = i
                            break

                elif len(value) == len(ann_args):
                    for i, (x, typ) in enumerate(zip(value, ann_args)):
                        if fail := recursive_check(x, typ, level + 1):
                            failed_idx = i
                            break

                else:
                    fail = [Failed(value, Annotation(annotation, level=level))]

            elif issubclass(annotation_origin, typing.Mapping):
                tkey, tval = ann_args

                for i, (key, val) in enumerate(value.items()):
                    if fail := recursive_check(key, tkey, level + 1):
                        failed_idx = i
                        break
                    if fail := recursive_check(val, tval, level + 1):
                        failed_idx = i
                        break

            else: # Generic case
                if len(ann_args) == 1:
                    ann_args, = ann_args

                for i, x in enumerate(value):
                    if fail := recursive_check(x, ann_args, level + 1):
                        failed_idx = i
                        break

            if failed_idx >= 0:
                fail.append(Failed(
                    value,
                    Annotation(annotation, failed_idx, level)
                ))
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
