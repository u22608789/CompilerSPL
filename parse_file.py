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
from spl.basicify import intermediate_to_basic


def main():
    ap = argparse.ArgumentParser(
        description="SPL parser / scope & type checker / code generator"
    )
    ap.add_argument("file", help="SPL source file (e.g., examples/hello.spl)")
    ap.add_argument("--print-ast", action="store_true",
                    help="Print the AST (Phase 1 output)")
    ap.add_argument("--check-scopes", action="store_true",
                    help="Build symbol table (Phase 2). Prints OK or diagnostics.")
    ap.add_argument("--dump-scopes", action="store_true",
                    help="Pretty-print the symbol table tree (Phase 2).")
    ap.add_argument("--type-check", action="store_true",
                    help="Run SPL type checker")
    ap.add_argument("--codegen", action="store_true",
                    help="Generate target code (Phase 3)")
    ap.add_argument("--emit-basic", action="store_true",
                    help="Emit numbered BASIC with label resolution (Phase 4)")
    ap.add_argument("--out", help="Output file for generated code (defaults to <input>.txt)")

    args = ap.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read()

    # Phase 1: parse
    ast = Parser(text).parse()

    if not (args.check_scopes or args.dump_scopes or args.print_ast or args.type_check or args.codegen or args.emit_basic):
        args.print_ast = True

    if args.print_ast:
        print_ast(ast)

    # Phase 2: assign IDs + scope checking (when requested)
    st = None
    if args.check_scopes or args.dump_scopes:
        assign_ids(ast)
        checker = ScopeChecker(ast)
        st = checker.check()  # populates declarations & local scopes

        if args.dump_scopes:
            print(st.pretty_print())

        # Diagnostics
        if checker.diagnostics:
            print("\nNaming Error:")
            for d in checker.diagnostics:
                print(f"  - {d}")
            sys.exit(1)
        else:
            print("Variable Naming and Function Naming accepted")

    # Phase 3: Type checking
    if args.type_check:
        assign_ids(ast)  # ensure nodes have IDs
        tc = TypeChecker()
        try:
            tc.visit(ast)
            print("Type checking passed ✅")
        except Exception as e:
            print(f"Type Error ❌: {e}")
            sys.exit(1)

    # Phase 4: Code generation
    generated_txt = None
    if args.codegen or args.emit_basic:
        output_file = args.out or os.path.splitext(args.file)[0] + ".txt"
        print(f"Generating target code → {output_file}")
        cg = CodeGenerator(ast)
        if st is not None:
            cg.symbol_table = st
        cg.generate(output_file)
        print("Code generation completed successfully.")
        generated_txt = output_file

    # Phase 5: BASIC finalization
    if args.emit_basic:
        if not generated_txt:
            # If user asked only for BASIC but not --codegen, we still need the .txt in memory
            output_file = args.out or os.path.splitext(args.file)[0] + ".txt"
            print(f"(Note) Generating intermediate code for BASIC emission → {output_file}")
            cg = CodeGenerator(ast)
            if st is not None:
                cg.symbol_table = st
            cg.generate(output_file)
            generated_txt = output_file

        bas_path = (args.out and os.path.splitext(args.out)[0] + ".bas") or os.path.splitext(args.file)[0] + ".bas"
        with open(generated_txt, "r", encoding="ascii") as f:
            lines = [ln.rstrip("\n") for ln in f]
        basic_lines = intermediate_to_basic(lines, start=10, step=10)
        with open(bas_path, "w", encoding="ascii") as f:
            f.write("\n".join(basic_lines) + "\n")
        print(f"BASIC emitted → {bas_path}")


if __name__ == "__main__":
    main()
