# parse_file.py
import sys, os
ROOT = os.path.join(os.path.dirname(__file__), "src")
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from spl.parser import Parser
from spl.ast_printer import print_ast

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_file.py <file.spl>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        text = f.read()

    tree = Parser(text).parse()
    print_ast(tree)
