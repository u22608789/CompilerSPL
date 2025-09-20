# ast_printer.py
from __future__ import annotations
from dataclasses import is_dataclass, fields
from typing import Any
from io import StringIO

_IND = "  "  # two spaces

def ast_to_str(node: Any) -> str:
    """Return a human-readable tree for any AST node/list/primitive."""
    buf = StringIO()
    _pp(node, buf, 0)
    return buf.getvalue()

def print_ast(node: Any) -> None:
    """Print the AST to stdout (convenience wrapper)."""
    print(ast_to_str(node))

def _pp(node: Any, buf: StringIO, indent: int) -> None:
    ind = _IND * indent

    # None
    if node is None:
        buf.write(f"{ind}None\n")
        return

    # Primitive leaves
    if isinstance(node, (str, int, float, bool)):
        buf.write(f"{ind}{repr(node)}\n")
        return

    # Lists (e.g., Algo.instrs, Program.globals, args, params, etc.)
    if isinstance(node, list):
        buf.write(f"{ind}List[{len(node)}]\n")
        for i, item in enumerate(node):
            buf.write(f"{ind}{_IND}[{i}]\n")
            _pp(item, buf, indent + 2)
        return

    # Dataclasses (all AST nodes)
    if is_dataclass(node):
        cls = node.__class__.__name__
        # If all fields are primitive (nice inline single-line like VarRef/NumberLit)
        flds = fields(node)
        values = [getattr(node, f.name) for f in flds]
        if all(isinstance(v, (str, int, float, bool)) or v is None for v in values):
            inner = ", ".join(f"{f.name}={repr(getattr(node, f.name))}" for f in flds)
            buf.write(f"{ind}{cls}({inner})\n")
            return

        buf.write(f"{ind}{cls}\n")
        for f in flds:
            buf.write(f"{ind}{_IND}{f.name}:\n")
            _pp(getattr(node, f.name), buf, indent + 2)
        return

    # Fallback (shouldn't really happen with your AST types)
    buf.write(f"{ind}{repr(node)}\n")
