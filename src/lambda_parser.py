"""
The tokenizer and parser for a simple lambda calculus language

Grammar:
E := F E'

E' := F E'
    | epsilon

F := \ v . E
   | v
   | ( E )

v = [a-z][a-zA-Z0-9]*

"""

from lambda_tokenizer import Tokenizer, Token
from lambda_ast import *


class ParseError(Exception):
    pass


ParseResult = LambdaExpr | str


def match_token(tok: Tokenizer, tok_type: str) -> Token:
    next_tok = tok.next()
    if next_tok.type == tok_type:
        return next_tok
    raise ParseError('Parse error at %s: Got %s, expected %s' % (next_tok.pos, next_tok.type, tok_type))


def parse_util(s: str) -> ParseResult:
    try:
        return bind_vars(parse_lambda(Tokenizer(s)))
    except ParseError as err:
        return err.args[0]


def parse_lambda(tok: Tokenizer, match_eof=True) -> LambdaExpr:
    expr = parse_e(tok)
    if match_eof:
        match_token(tok, 'EOF')
    return expr


def parse_e(tok: Tokenizer) -> LambdaExpr:
    f = parse_f(tok)
    return parse_e_(tok, f)


def parse_e_(tok: Tokenizer, so_far: LambdaExpr) -> LambdaExpr:
    next_tok = tok.peak()
    match next_tok.type:
        case "LAMBDA" | "VAR" | "LPAREN":
            next_expr = parse_f(tok)
            return parse_e_(tok, App(None, so_far.loc, so_far, next_expr))
        case _:
            return so_far


def parse_f(tok: Tokenizer) -> LambdaExpr:
    next_tok = tok.next()
    match next_tok.type:
        case 'LAMBDA':
            var_token = match_token(tok, 'VAR')
            match_token(tok, 'DOT')
            body = parse_e(tok)
            return Function(None, next_tok.pos, var_token.value, body)
        case 'VAR':
            return FreeVar(None, next_tok.pos, next_tok.value)
        case 'LPAREN':
            body = parse_e(tok)
            match_token(tok, 'RPAREN')
            return body
        case _:
            raise ParseError('Parse error at %s: Got %s, expected LAMBDA, LPAREN or VAR' % (next_tok.pos, next_tok.type))
