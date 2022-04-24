"""
Defines the AST for the lambda calculus
Bound variables use De Brujin indices
"""

from __future__ import annotations
from dataclasses import dataclass, replace


@dataclass
class SrcLoc:
    loc: tuple[int, int]


@dataclass
class LambdaExpr:
    abbreviation: str | None
    loc: SrcLoc


@dataclass
class Function(LambdaExpr):
    arg_name: str
    body: LambdaExpr


@dataclass
class BoundVar(LambdaExpr):
    index: int


@dataclass
class FreeVar(LambdaExpr):
    var_name: str


@dataclass
class App(LambdaExpr):
    function: LambdaExpr
    argument: LambdaExpr


# A type that encapsulates both types of variables
Var = BoundVar | FreeVar


def pretty_print_expr(expr: LambdaExpr, expand_abbreviations=False, use_de_brujin=False) -> str:
    """
    Converts a lambda calculus AST type into a pretty printed expression that is human readable
    Alpha conversion should be performed on bound variables such that they do not interfere with free vars
    :param expr: A lambda calculus AST
    :param expand_abbreviations: Whether to fully print nodes with abbreviations marked
    :param use_de_brujin: Whether to print bound variables using names or de brujin indices
    :return: A string representation of the expression
    """

    def show_context(e: LambdaExpr, context: dict[int, str], prec: int = 0) -> str:
        if not expand_abbreviations and e.abbreviation is not None:
            return e.abbreviation
        match e:
            case Function(arg_name=n, body=b):
                new_context = {i + 1: v for i, v in context.items()}
                new_context[0] = n
                str_rep = '\\' + (' ' if use_de_brujin else n) + '.' + show_context(b, new_context, prec=1)
                return '(' + str_rep + ')' if prec > 1 else str_rep
            case BoundVar(index=ix):
                return str(ix) if use_de_brujin else context[ix]
            case FreeVar(var_name=n):
                return n
            case App(function=f, argument=a):
                str_rep = show_context(f, context, prec=2) + ' ' + show_context(a, context, prec=3)
                return '(' + str_rep + ')' if prec > 2 else str_rep
            case _:
                raise RuntimeError('Cannot print lambda expression type ' + str(e))

    return show_context(expr, {})


def alpha_equivalent(expr_a: LambdaExpr, expr_b: LambdaExpr) -> bool:
    """
    Determines whether two expressions are alpha equivalent.
    :param expr_a:
    :param expr_b:
    :return:
    """
    match (expr_a, expr_b):
        case (BoundVar(index=i_a), BoundVar(index=i_b)):
            return i_a == i_b
        case (FreeVar(var_name=n_a), FreeVar(var_name=n_b)):
            return n_a == n_b
        case (Function(body=body_a), Function(body=body_b)):
            return alpha_equivalent(body_a, body_b)
        case (App(function=fn_a, argument=arg_a), App(function=fn_b, argument=arg_b)):
            return alpha_equivalent(fn_a, fn_b) and alpha_equivalent(arg_a, arg_b)
        case _:
            return False


def bind_vars(expr: LambdaExpr, context: dict[str, int | LambdaExpr] | None = None) -> LambdaExpr:
    """
    Given a lambda expression finds all free vars which are bound by lambdas and replaces them with the relevant bound
    variable using de Brujin indices. Can also replace names with other lambda expressions. These expressions should
    already have their variables bound
    :param expr:
    :param context: A mapping from names to their bindings
    :return: The resulting expression
    """
    if context is None:
        context = {}

    match expr:
        case Function(arg_name=n, body=b) as fn:
            new_context = {v: (e+1 if type(e) is int else e) for v, e in context.items()}
            new_context[n] = 0
            return replace(fn, body=bind_vars(b, new_context))

        case FreeVar(var_name=n) as fv if n in context:
            if type(context[n]) is int:
                return BoundVar(fv.abbreviation, fv.loc, context[n])
            else:
                return context[n]
        case App(function=f, argument=a) as app:
            return replace(app, function=bind_vars(f, context), argument=bind_vars(a, context))
        case _:
            return expr


def get_free(expr: LambdaExpr) -> [FreeVar]:
    """
    Extracts a list of the free variables in an expression
    :param expr:
    :return:
    """
    match expr:
        case FreeVar() as fv:
            return [fv]
        case Function(body=b):
            return get_free(b)
        case App(function=f, argument=a):
            return get_free(f) + get_free(a)
        case _:
            return []

