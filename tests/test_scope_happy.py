import os, sys
ROOT = os.path.join(os.path.dirname(__file__), "..", "src")
if ROOT not in sys.path: sys.path.insert(0, ROOT)

from spl.parser import Parser
from spl.ast_ids import assign_ids
from spl.scope_checker import ScopeChecker

def test_richer_ok():
    text = open(os.path.join(os.path.dirname(__file__), "..", "examples", "richer.spl"), encoding="utf-8").read()
    ast = Parser(text).parse()
    assign_ids(ast)
    checker = ScopeChecker(ast)
    checker.check()
    assert checker.diagnostics == []
