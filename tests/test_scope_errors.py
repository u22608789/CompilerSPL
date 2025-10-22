import os, sys
ROOT = os.path.join(os.path.dirname(__file__), "..", "src")
if ROOT not in sys.path: sys.path.insert(0, ROOT)

from spl.parser import Parser
from spl.ast_ids import assign_ids
from spl.scope_checker import ScopeChecker

def run(file):
    text = open(os.path.join(os.path.dirname(__file__), "..", "examples", file), encoding="utf-8").read()
    ast = Parser(text).parse()
    assign_ids(ast)
    checker = ScopeChecker(ast)
    checker.check()
    return checker.diagnostics

def contains(diags, substr):
    return any(substr in d for d in diags)

def test_dup_globals():
    d = run("bad_duplicate_globals.spl")
    assert contains(d, "Duplicate declaration of 'x' in Global scope")

def test_proc_func_name_clash():
    d = run("bad_proc_func_name_clash.spl")
    assert contains(d, "conflicts with procedure name") or contains(d, "conflicts with function name")

def test_main_var_conflict():
    d = run("bad_main_var_conflicts_with_func.spl")
    assert contains(d, "Main variable 'inc' conflicts with function name")

def test_dup_params():
    d = run("bad_duplicate_params.spl")
    assert contains(d, "Duplicate parameter 'a' in proc 'echo'")

def test_local_shadows_param():
    d = run("bad_local_shadows_param.spl")
    assert contains(d, "shadows parameter in proc 'p'")

def test_dup_locals():
    d = run("bad_duplicate_locals.spl")
    assert contains(d, "Duplicate declaration of 'a' in Local scope")