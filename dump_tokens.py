# dump_tokens.py
import sys, os

# Ensure we can import the 'spl' package from src/
PKG_ROOT = os.path.join(os.path.dirname(__file__), "src")
if PKG_ROOT not in sys.path:
    sys.path.insert(0, PKG_ROOT)

from spl.lexer import Lexer
from spl.tokens import T

def dump(text: str):
    lx = Lexer(text)
    while True:
        tok = lx.next_token()
        print(f"{tok.line}:{tok.col}\t{tok.typ.name}\t{tok.lexeme!r}")
        if tok.typ == T.EOF:
            break

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dump_tokens.py <file.spl>")
        sys.exit(1)
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        dump(f.read())
