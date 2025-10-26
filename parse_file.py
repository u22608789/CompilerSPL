# parse_file.py
import sys, os, argparse
ROOT = os.path.join(os.path.dirname(__file__), "src")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from spl.parser import Parser
from spl.ast_printer import print_ast
from spl.ast_ids import assign_ids
from spl.scope_checker import ScopeChecker
from spl.codegen import CodeGenerator
from spl.type_checker import TypeChecker
from spl.ic_html import write_intermediate_html
from spl.basicify import intermediate_to_basic

def main():
    ap = argparse.ArgumentParser(
        description="SPL parser / scope & type checker / code generator"
    )
    ap.add_argument("file", help="SPL source file (e.g., examples/hello.txt or .spl)")
    ap.add_argument("--print-ast", action="store_true",
                    help="Print the AST (Phase 1 output)")
    ap.add_argument("--check-scopes", action="store_true",
                    help="Build symbol table (Phase 2). Prints OK or diagnostics.")
    ap.add_argument("--dump-scopes", action="store_true",
                    help="Pretty-print the symbol table tree (Phase 2).")
    ap.add_argument("--type-check", action="store_true",
                    help="Run SPL type checker (Phase 2.5)")
    ap.add_argument("--codegen", action="store_true",
                    help="Generate unnumbered intermediate code (Phase 3) → <input>.int.txt (also .html & .basic.txt for Type A/B)")
    ap.add_argument("--emit-basic", action="store_true",
                    help="Emit numbered BASIC with label resolution (FINAL Type A) → <input>.basic.txt")
    ap.add_argument("--out", help="Override Phase 3 intermediate output file (defaults to <input>.int.txt)")

    args = ap.parse_args()

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Syntax error: file '{args.file}' not found")
        sys.exit(1)

    # ---------- Phase 1: parse (also confirms lexing) ----------
    try:
        ast = Parser(text).parse()
        print("Tokens accepted")
        print("Syntax accepted")
    except ValueError as e:
        print(f"Lexical error: {e}")
        sys.exit(1)
    except SyntaxError as e:
        print(f"Syntax error: {e}")
        sys.exit(1)

    if not (args.check_scopes or args.dump_scopes or args.print_ast or args.type_check or args.codegen or args.emit_basic):
        args.print_ast = True
    if args.print_ast:
        print_ast(ast)

    # ---------- Phase 2: Scopes ----------
    st = None
    if args.check_scopes or args.dump_scopes or args.type_check or args.codegen or args.emit_basic:
        assign_ids(ast)
        checker = ScopeChecker(ast)
        st = checker.check()

        if args.dump_scopes:
            print(st.pretty_print())

        if checker.diagnostics:
            print("Naming error:")
            for d in checker.diagnostics:
                print(f"  - {d}")
            sys.exit(1)
        else:
            print("Variable Naming and Function Naming accepted")

    # ---------- Phase 3: Types ----------
    if args.type_check or args.codegen or args.emit_basic:
        tc = TypeChecker()
        try:
            tc.visit(ast)
            print("Types accepted")
        except Exception as e:
            print(f"Type error: {e}")
            sys.exit(1)

    # ---------- Phase 4: Intermediate code ----------
    generated_int_path = None
    generated_lines = None
    if args.codegen or args.emit_basic:
        base, _ = os.path.splitext(args.file)
        int_file = args.out or f"{base}.int.txt"
        html_file = f"{base}.html"
        basic_file = f"{base}.basic.txt"

        print(f"Generating target code → {int_file}")
        cg = CodeGenerator(ast)
        if st is not None:
            cg.symbol_table = st
        cg.generate(int_file)  
        print("Intermediate code (TXT) generated.")
        generated_int_path = int_file
        generated_lines = cg.output[:]  

        try:
            write_intermediate_html(generated_lines, html_file)
            print(f"Intermediate code (HTML) generated → {html_file}")
        except Exception as e:
            print(f"Warning: failed to write HTML ({e})")

    # ---------- Phase 5: Executable BASIC .txt ----------
    if args.emit_basic:
        if generated_lines is None:
            base, _ = os.path.splitext(args.file)
            int_file = args.out or f"{base}.int.txt"
            print(f"(Note) Generating intermediate code for BASIC emission → {int_file}")
            cg = CodeGenerator(ast)
            if st is not None:
                cg.symbol_table = st
            cg.generate(int_file)
            generated_int_path = int_file
            generated_lines = cg.output[:]

            html_file = f"{base}.html"
            try:
                write_intermediate_html(generated_lines, html_file)
                print(f"Intermediate code (HTML) generated → {html_file}")
            except Exception as e:
                print(f"Warning: failed to write HTML ({e})")

        base, _ = os.path.splitext(args.file)
        basic_file = f"{base}.basic.txt"

        basic_lines = intermediate_to_basic(generated_lines, start=10, step=10)
        with open(basic_file, "w", encoding="ascii") as f:
            f.write("\n".join(basic_lines) + "\n")
        print(f"Executable BASIC emitted → {basic_file}")

if __name__ == "__main__":
    main()
