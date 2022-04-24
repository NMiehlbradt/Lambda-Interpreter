import cmd
from enum import Enum
from lambda_ast import pretty_print_expr
from lambda_parser import parse_util
from lambda_eval import beta_reduce, full_reduce, limit_reduce


class LambdaShell(cmd.Cmd):
    intro = 'Welcome to the λ-calculus interpreter'
    prompt = 'λ> '

    def __init__(self):
        super().__init__()
        self.step: bool = False  # Whether to evaluate in interactive stepped mode
        self.lazy_eval: bool = True  # Whether to use lazy evaluation (NOT implemented)
        self.verbose: bool = True  # Whether to show the full derivation or just the result
        self.eval_steps: int = 100  # How many evaluation steps to do before terminating
        self.expand_abbr: bool = True

    def do_exit(self, arg):
        """Exits the interpreter"""
        return True

    def do_ast(self, arg):
        """Shows the raw AST of the expression"""
        expr = parse_util(arg)
        if isinstance(expr, str):
            print(expr)
            return
        print(expr)

    def do_free(self, arg):
        """Gets the free variables from an expression"""

    def default(self, arg):
        expr = parse_util(arg)
        if isinstance(expr, str):
            print(expr)
            return

        if self.step:
            reduced = expr
            while reduced is not None:
                print((pretty_print_expr(reduced)))
                reduced = beta_reduce(reduced, lazy=self.lazy_eval)

        else:
            reduced, limit_hit = limit_reduce(expr, self.eval_steps)
            print(pretty_print_expr(reduced))
            if limit_hit:
                print(f'Evaluation stopped after {self.eval_steps} steps')


if __name__ == '__main__':
    LambdaShell().cmdloop()

    # expr = parse_util(r'(\x.\y.x y) (\x.x) (\x.x)')
    # expr = parse_util(r'(\x.\y.x y) (\x.x)')
    # expr = parse_util(r'(\x.x) (\x.x) z')
    # r = beta_reduce(expr)
    # print(r)
    # print(pretty_print_expr(r))
