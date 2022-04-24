import dataclasses
from typing import Iterable, Callable, TypeVar, Any

from lambda_ast import *


def substitute(expr: LambdaExpr, arg: LambdaExpr, ix=0) -> LambdaExpr:
    match expr:
        case Function(abbr, _, _, body) as f:
            new_body = substitute(body, arg, ix=ix + 1)
            return dataclasses.replace(f,
                                       abbreviation=abbr if alpha_equivalent(body, new_body) else None,
                                       body=new_body)
        case App(abbr, loc, function, argument):
            new_function = substitute(function, arg, ix)
            new_argument = substitute(argument, arg, ix)
            return App(
                abbr if alpha_equivalent(function, new_function) and alpha_equivalent(arg, new_argument) else None,
                loc,
                new_function,
                new_argument)
        case BoundVar(index=i) if i == ix:
            return arg
        case _:
            return expr


def beta_reduce(expr: LambdaExpr, lazy: bool = True) -> LambdaExpr | None:
    match expr:
        case Function(body=body) as fn:
            new_body = beta_reduce(body, lazy=lazy)
            if new_body is None:
                return None
            else:
                return dataclasses.replace(fn, body=new_body, abbreviation=None)
        case App(function=fn, argument=arg) as app:
            match fn:
                case Function(body=fn_body):
                    return substitute(fn_body, arg)
                case _:
                    new_fn = beta_reduce(fn, lazy=lazy)
                    if new_fn is not None:
                        return dataclasses.replace(app, function=new_fn, abbreviation=None)
                    new_arg = beta_reduce(arg, lazy=lazy)
                    if new_arg is not None:
                        return dataclasses.replace(app, argument=new_arg, abbreviation=None)
                    return None
        case _:
            return None


def full_reduce(expr: LambdaExpr, lazy: bool = True) -> Iterable[LambdaExpr]:
    while expr is not None:
        yield expr
        expr = beta_reduce(expr, lazy=lazy)


def limit_reduce(expr: LambdaExpr, steps: int) -> (LambdaExpr, bool):
    for i, e in enumerate(full_reduce(expr)):
        if i > steps:
            return e, True
        expr = e
    return expr, False

