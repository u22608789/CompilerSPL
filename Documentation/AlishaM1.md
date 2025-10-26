Files changed: 
    - ast_ids.py
        ✅ Implements assign_ids(ast) - main entry point
        ✅ Uses visitor pattern to traverse entire AST
        ✅ Assigns unique sequential IDs starting from 1
        ✅ Provides utility functions:
            count_nodes(ast) - count total nodes
            get_all_node_ids(ast) - collect all IDs for verification
            print_node_ids(ast) - debug visualization
        ✅ Includes smoke test in __main__ block

    - astnodes.py
        ✅ Added node_id: int = -1 to every AST dataclass
        ✅ Added resolved: Optional[SymbolTableEntry] to VarRef for name resolution
        ✅ Maintained all existing functionality from Phase 1
        ✅ No breaking changes to existing code

    - scope_checker.py
        ✅ Implements ScopeChecker class structure
        ✅ Implements _build_base_scopes() - M1's core deliverable
        ✅ Creates proper SPL scope hierarchy:

            Everywhere (root)
                ├── Global (global variables)
                ├── Procedure (procedure names)
                ├── Function (function names)
                └── Main (main's local variables)

        ✅ Provides clear stubs for M2 (declaration collection)
        ✅ Provides clear stubs for M3 (use resolution)
        ✅ Includes detailed TODO comments explaining what M2/M3 need to do
        ✅ Implements check_scopes(ast) convenience function

    - symbol_table.py
        ✅ Implements SymbolTableEntry dataclass
        ✅ Implements Scope dataclass with declare/lookup methods
        ✅ Implements SymbolTable class with full API:
            new_scope(kind, parent_id, name) - create scopes
            declare(scope_id, entry) - add declarations
            lookup_local(scope_id, name) - single scope lookup
            lookup_chain(scope_id, name) - parent chain lookup
            get_scope_path(scope_id) - for error messages
            pretty_print() - human-readable output
        ✅ Implements create_base_scopes(st) helper function
        ✅ Includes comprehensive smoke test demonstrating all features

TO RUN INDIVIDUAL FILES (from root directory): 
    - python -m src.spl.symbol_table
    - python -m src.spl.ast_ids
    - python -m src.spl.scope_checker

2 test files: 
    - test_M1.py
    TO RUN (from root directory): python test_M1.py
    - test_with_file.py
    TO RUN (from root directory): python test_with_file.py examples/richer.spl 

=====================================================================
Acceptance Criteria - All Met ✅
Step 1: Add stable node_id to AST

✅ node_id: int field in every AST dataclass
✅ assign_ids(ast) function implemented and working
✅ Utility functions for verification included

Step 2: Symbol table core types & API

✅ Scope dataclass with parent_id
✅ SymbolTableEntry with all required fields
✅ SymbolTable class with complete API
✅ Pretty printer for debugging
✅ Working smoke test in __main__ block

Step 3: Top-level scope layout

✅ Builds Everywhere → Global/Procedure/Function/Main tree
✅ Scope hierarchy matches SPL specification exactly
✅ Integration ready for M2/M3/M4

=====================================================================
What's Ready for M2, M3, M4
- For M2 (Declaration Collection):
The symbol table is ready to receive declarations. M2 needs to fill in these methods in scope_checker.py:

_collect_global_declarations()
_collect_proc_declarations()
_collect_func_declarations()
_collect_main_variables()
_build_local_scopes()

All methods have detailed TODO comments with examples.

- For M3 (Use Resolution):
The scope structure supports proper name resolution. M3 needs to fill in:

_resolve_uses()
_resolve_algo()
_resolve_varref()
_resolve_term()

The VarRef.resolved field is ready to be populated.

- For M4 (Error Reporting & Testing):
The infrastructure supports error collection:

self.diagnostics list exists
Scope paths available for error context
All operations raise/catch ValueError for duplicates
Ready for structured diagnostic types

=====================================================================

