#!/usr/bin/env python3
"""
Test Phase 2 with an SPL file

Usage:
    python test_with_file.py examples/hello.spl
    python test_with_file.py examples/rich.spl
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(src_path))
print(f"[DEBUG] Added to sys.path: {src_path}")

from spl.parser import Parser
from spl.ast_ids import assign_ids, get_all_node_ids, count_nodes
from spl.scope_checker import check_scopes

if len(sys.argv) < 2:
    print("Usage: python test_with_file.py <file.spl>")
    print("Example: python test_with_file.py examples/hello.spl")
    sys.exit(1)

filename = sys.argv[1]

print("=" * 70)
print(f"Testing Phase 2 with: {filename}")
print("=" * 70)
print()

# Read file
try:
    with open(filename, 'r') as f:
        source = f.read()
    print(f"✓ Read {len(source)} characters from {filename}")
except FileNotFoundError:
    print(f"✗ File not found: {filename}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error reading file: {e}")
    sys.exit(1)

print()

# Step 1: Parse
print("[1/3] Parsing...")
try:
    ast = Parser(source).parse()
    print("      ✓ Parse successful")
    print(f"      - Globals: {len(ast.globals)}")
    print(f"      - Procedures: {len(ast.procs)}")
    print(f"      - Functions: {len(ast.funcs)}")
except Exception as e:
    print(f"      ✗ Parse failed: {e}")
    sys.exit(1)

# Step 2: Assign IDs
print("[2/3] Assigning node IDs...")
try:
    assign_ids(ast)
    ids = get_all_node_ids(ast)
    total = count_nodes(ast)
    print(f"      ✓ Assigned {len(ids)} unique IDs to {total} nodes")
except Exception as e:
    print(f"      ✗ ID assignment failed: {e}")
    sys.exit(1)

# Step 3: Build scopes
print("[3/3] Building scope hierarchy...")
try:
    symbol_table = check_scopes(ast)
    print(f"      ✓ Created {len(symbol_table.scopes)} scopes")
except Exception as e:
    print(f"      ✗ Scope checking failed: {e}")
    sys.exit(1)

print()
print(symbol_table.pretty_print())
print()
print("=" * 70)
print("✓ Success!")
print("=" * 70)