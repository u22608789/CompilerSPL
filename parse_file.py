# parse_file.py
import sys, os, argparse
ROOT = os.path.join(os.path.dirname(__file__), "src")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from spl.parser import Parser
from spl.ast_printer import print_ast
from spl.ast_ids import assign_ids
from spl.scope_checker import ScopeChecker  # using class to read diagnostics

def main():
    ap = argparse.ArgumentParser(
        description="SPL parser / scope checker"
    )
    ap.add_argument("file", help="SPL source file (e.g., examples/hello.spl)")
    ap.add_argument("--print-ast", action="store_true",
                    help="Print the AST (Phase 1 output)")
    ap.add_argument("--check-scopes", action="store_true",
                    help="Build symbol table (Phase 2). Prints OK or diagnostics.")
    ap.add_argument("--dump-scopes", action="store_true",
                    help="Pretty-print the symbol table tree (Phase 2).")
    args = ap.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read()

    # Phase 1: parse
    ast = Parser(text).parse()

    # Default behavior stays: if no flags provided, print AST
    if not (args.check_scopes or args.dump_scopes or args.print_ast):
        args.print_ast = True

    if args.print_ast:
        print_ast(ast)

    # Phase 2: assign IDs + scope checking (when requested)
    if args.check_scopes or args.dump_scopes:
        assign_ids(ast)
        checker = ScopeChecker(ast)
        st = checker.check()  # M2 populates declarations & local scopes

        if args.dump_scopes:
            print(st.pretty_print())

        # Diagnostics: use structured Diagnostic objects
        if checker.diagnostics:
            print("\nNaming Error:")
            for d in checker.diagnostics:
                print(f"  - {d}")
            # Non-zero exit helps CI catch mistakes later
            sys.exit(1)
        else:
            print("Variable Naming and Function Naming accepted")

if __name__ == "__main__":
    main()
