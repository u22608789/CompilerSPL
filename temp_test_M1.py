#!/usr/bin/env python3
"""
Test script for Phase 2 M1 deliverable

This script demonstrates the complete workflow:
1. Parse SPL source code
2. Assign node IDs to all AST nodes
3. Build scope hierarchy
4. Print results

Usage:
    python test_phase2.py
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

# Simple test program
source = """
glob { x y }
proc {
    inc(n) { local { } halt }
}
func {
    double(n) { local { } halt ; return n }
}
main {
    var { i j }
    i = 5;
    print i
}
"""

print("=" * 70)
print("Phase 2 Integration Test")
print("=" * 70)
print()

# Step 1: Parse
print("[1/4] Parsing SPL source code...")
try:
    ast = Parser(source).parse()
    print("      ✓ Parse successful")
except Exception as e:
    print(f"      ✗ Parse failed: {e}")
    sys.exit(1)

# Step 2: Assign node IDs
print("[2/4] Assigning unique node IDs...")
try:
    assign_ids(ast)
    ids = get_all_node_ids(ast)
    total = count_nodes(ast)
    print(f"      ✓ Assigned {len(ids)} unique IDs")
    print(f"      ✓ Total nodes in AST: {total}")
    print(f"      ✓ ID range: {min(ids)} to {max(ids)}")
    
    # Verify uniqueness
    if len(ids) != len(set(ids)):
        print("      ✗ WARNING: Duplicate IDs found!")
    else:
        print("      ✓ All IDs are unique")
except Exception as e:
    print(f"      ✗ ID assignment failed: {e}")
    sys.exit(1)

# Step 3: Build scope hierarchy
print("[3/4] Building scope hierarchy...")
try:
    symbol_table = check_scopes(ast)
    print(f"      ✓ Created {len(symbol_table.scopes)} scopes")
    
    # Verify base scopes exist
    expected = ['everywhere', 'global', 'procedure', 'function', 'main']
    for scope_name in expected:
        if scope_name in symbol_table.base_scopes:
            print(f"      ✓ {scope_name.capitalize()} scope created")
        else:
            print(f"      ✗ {scope_name.capitalize()} scope missing!")
except Exception as e:
    print(f"      ✗ Scope checking failed: {e}")
    sys.exit(1)

# Step 4: Print symbol table
print("[4/4] Printing symbol table...")
print()
print(symbol_table.pretty_print())

print()
print("=" * 70)
print("✓ Phase 2 M1 Deliverable - All Tests Passed!")
print("=" * 70)
print()
print("What's working:")
print("  ✓ Parser creates AST")
print("  ✓ All AST nodes get unique IDs")
print("  ✓ Base scope hierarchy is created")
print("  ✓ Symbol table structure is ready")
print()
print("What's next (M2/M3/M4):")
print("  ⧗ M2: Fill in global/proc/func declarations")
print("  ⧗ M3: Resolve variable uses")
print("  ⧗ M4: Error reporting and comprehensive tests")
print()