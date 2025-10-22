### Files Modified / Added

- **`src/scope_checker.py`**

  - Implemented all **Phase 3 (use-resolution)** and **Phase 4 (diagnostic)** features.
  - Added:

    - `_resolve_uses()`, `_resolve_algo()`, `_resolve_term()`, `_resolve_varref()` – perform variable-use resolution.
    - `uses_to_decls` map (for debugging use–decl linkage).

  - Updated existing code to store structured diagnostics instead of raw strings.

- **`src/errors.py`**

  - Created new `Diagnostic` dataclass for consistent error reporting.
  - Fields: `kind`, `message`, `node_id`, `scope_path`.
  - Replaces old string-based messages.

- **`parse_file.py`**

  - Added proper success/error messages:

    - ✅ `Variable Naming and Function Naming accepted`
    - ❌ `Naming error: <message>`

  - Exits with code `1` on any naming errors (for testing and automation).

- **`tests/test_scope_*.py`**

  - Updated to work with `Diagnostic` objects instead of strings.
  - All naming-related tests pass successfully.

---

### New / Changed Functionality

1. **Name-Use Resolution**

   - Every `VarRef` in the AST now links to its declaration via `.resolved`.
   - Lookup order:

     - Procedures/Functions → param → local → global.
     - Main → main locals → global.

   - Undeclared identifiers trigger `UndeclaredVariable` diagnostics.

2. **Structured Diagnostics**

   - All name/scope errors (duplicates, shadowing, clashes, undeclared) recorded as `Diagnostic` objects.
   - Diagnostics are non-fatal and printed in a standardized format.

3. **Command-Line Operation**

   - The compiler can now be fully tested from the terminal using:

     ```bash
     python parse_file.py examples/<file>.spl --check-scopes
     ```

   - Add `--dump-scopes` to view the full scope hierarchy.
   - Examples:

     ```bash
     python parse_file.py examples/richer.spl --check-scopes
     # Output: Variable Naming and Function Naming accepted

     python parse_file.py examples/bad_duplicate_globals.spl --check-scopes
     # Output: Naming error(s):
     #   - DuplicateName: Duplicate parameter 'x' in ...
     ```

4. **Testing and Verification**

   - Verified with example files:

     - `richer.spl` → no diagnostics
     - `bad_*.spl` → expected naming diagnostics

   - `pytest` suite updated and all tests passing.

---
