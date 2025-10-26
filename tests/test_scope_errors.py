import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "src")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

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
    """
    diags may be:
      - a list of Diagnostic objects (preferred)
      - a plain string (older calls)
      - any iterable of items
    We convert each item to str() and search for substr.
    """
    # If someone accidentally passed a single string, handle that:
    if isinstance(diags, str):
        return substr in diags
    # Otherwise iterate and check stringified diagnostics
    try:
        for d in diags:
            if substr in str(d):
                return True
    except TypeError:
        # Not iterable: stringify and check
        return substr in str(diags)
    return False


def test_dup_globals():
    d = run("bad_duplicate_globals.spl")
    assert contains(d, "Duplicate") and contains(d, "global") or contains(d, "Duplicate declaration"), \
        f"Expected duplicate-global diagnostic, got: {d}"


def test_proc_func_name_clash():
    d = run("bad_proc_func_name_clash.spl")
    assert contains(d, "conflicts with procedure name") or contains(d, "conflicts with function name"), \
        f"Expected proc/func name clash, got: {d}"


def test_main_var_conflict():
    d = run("bad_main_var_conflicts_with_func.spl")
    assert contains(d, "Main variable 'inc' conflicts with function name"), \
        f"Expected main-var vs func clash, got: {d}"


def test_dup_params():
    d = run("bad_duplicate_params.spl")
    assert contains(d, "Duplicate parameter 'a' in proc 'echo'") or contains(d, "Duplicate parameter 'a'"), \
        f"Expected duplicate-parameter diagnostic, got: {d}"


def test_local_shadows_param():
    d = run("bad_local_shadows_param.spl")
    assert contains(d, "shadows parameter in proc 'p'") or contains(d, "ParamShadowed") or contains(d, "shadows parameter"), \
        f"Expected local-shadowing diagnostic, got: {d}"


def test_dup_locals():
    d = run("bad_duplicate_locals.spl")
    # the diagnostic message text may vary; check for key words
    assert contains(d, "Duplicate") and contains(d, "Local") or contains(d, "Duplicate declaration of 'a'"), \
        f"Expected duplicate-local diagnostic, got: {d}"
