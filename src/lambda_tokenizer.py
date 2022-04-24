from typing import NamedTuple
import re

Token = NamedTuple('Token', [('type', str), ('value', str), ('pos', tuple[int, int])])


def tokenize(s):
    token_specification = [
        ('LAMBDA', r'\\'),
        ('DOT', r'\.'),
        ('VAR', r'[a-z][a-zA-Z0-9_]*'),
        ('LPAREN', r'\('),
        ('RPAREN', r'\)'),
        ('SKIP', r'[ \t\n]'),  # Skip over spaces and tabs
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    get_token = re.compile(tok_regex).match
    line = 1
    pos = line_start = 0
    mo = get_token(s)
    while mo is not None:
        typ = mo.lastgroup
        if typ == 'NEWLINE':
            line_start = pos
            line += 1
        elif typ != 'SKIP':
            val = mo.group(typ)
            yield Token(typ, val, (line, mo.start() - line_start))
        pos = mo.end()
        mo = get_token(s, pos)
    if pos != len(s):
        raise RuntimeError('Unexpected character %r on line %d' % (s[pos], line))
    yield Token('EOF', '', (line, pos - line_start))


class Tokenizer:

    def __init__(self, s: str):
        self.gen = tokenize(s)
        self.next_token = None

    def next(self):
        if self.next_token is None:
            return self.gen.__next__()
        else:
            tok = self.next_token
            self.next_token = None
            return tok

    def peak(self):
        if self.next_token is None:
            self.next_token = self.gen.__next__()
        return self.next_token



