# tests/test_parser_assignments.py
from spl.parser import Parser
from spl.astnodes import *


def parse(s): return Parser(s).parse()


def test_assign_term_number():
    prog = """
glob { } proc { } func { } main { var { } x = 42 }
"""
    tree = parse(prog)
    alg = tree.main.algo
    assert isinstance(alg.instrs[0], Assign)
    assert isinstance(alg.instrs[0].rhs, TermAtom)
    assert isinstance(alg.instrs[0].rhs.atom, NumberLit)


def test_assign_term_paren_binary():
    prog = """
glob { } proc { } func { } main { var { } x = (a plus 1) }
"""
    tree = parse(prog)
    a = tree.main.algo.instrs[0]
    assert isinstance(a, Assign)


def test_assign_func_call():
    prog = """
glob { } proc { } func { f(a) { local { } halt ; return a } } main { var { x } x = f(a) }
"""
    tree = parse(prog)
    a = tree.main.algo.instrs[0]
    assert isinstance(a.rhs, Call)
    assert a.rhs.name == "f"


def test_proc_call_stmt():
    prog = """
glob { } proc { p(a) { local { } halt } } func { } main { var { } p(x) }
"""
    tree = parse(prog)
    c = tree.main.algo.instrs[0]
    assert isinstance(c, Call)
    assert c.name == "p"
