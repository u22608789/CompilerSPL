# SPL Phase 2 — Scopes & Names

**Goal:** Build a symbol table and enforce static scoping/name rules. Phase 3 will resolve variable uses and attach links.

## Scope hierarchy

Everywhere (root)
├─ Global # global variables
├─ Procedure # procedure names
├─ Function # function names
└─ Main # main block variables
└─ (no children here)

## For each ProcDef/FuncDef we add:
Local:<name> # params + locals, parent = Global


## What Phase 2 enforces (implemented)

- **No duplicates within a scope**
  - Global variable names unique.
  - Procedure names unique.
  - Function names unique.
  - In each Local:<name> scope: params unique, locals unique.
- **No shadowing of parameters by locals**
  - In Local:<name>, a local cannot reuse a parameter’s name.
- **Cross-category clashes are illegal (Everywhere)**
  - Any variable name (global or main) must not equal any procedure or function name.
  - Procedures and Functions cannot share a name.

## Data structures

- `SymbolTableEntry { name, kind('var'|'param'|'proc'|'func'), scope_id, decl_node_id }`
- `Scope { id, kind('Everywhere'|'Global'|'Procedure'|'Function'|'Main'|'Local'), parent_id, table }`
- `SymbolTable { scopes, nodes_by_decl_id, base_scopes }`

Helper: `_proxy_id(anchor_node_id, bucket, idx)` generates deterministic `decl_node_id` for declarations represented as strings (globals, params, locals, main variables).

## AST notes (Phase 1 → Phase 2)

- `Main.variables: List[str]`
- `Body.locals: List[str]`
- `VarRef` has `resolved: Optional[SymbolTableEntry]` (M3 fills it).
- `assign_ids(ast)` assigns unique `node_id` to all AST nodes.

## Driver entry points

- `assign_ids(ast)` (Phase 1 utility)
- `ScopeChecker(ast).check()` builds base scopes, collects declarations, creates local scopes, and records diagnostics.
- `parse_file.py --check-scopes` prints `Scopes OK.` or diagnostics; `--dump-scopes` prints the symbol table tree.

## What M3 must implement

### Resolution rules

- **In procedure/function algos:** `param → local → global → (error: undeclared)`
- **In main algo:** `main → global → (error: undeclared)`
- For each `VarRef`, set `varref.resolved = SymbolTableEntry` on success.

### Methods to implement in `scope_checker.py`

- `_resolve_uses()`
  - For each `ProcDef`/`FuncDef`, call `_resolve_algo(def.body.algo, local_scope_id)`.
  - For `Main`, call `_resolve_algo(main.algo, base_scopes['main'])`.
- `_resolve_algo(algo, scope_id)`
  - Walk instructions (`Print`, `Assign`, `Call`, `LoopWhile`, `LoopDoUntil`, `BranchIf`) recursively.
  - For each expression/term, delegate to `_resolve_term`.
- `_resolve_term(term, scope_id)`
  - `TermAtom` → if `VarRef`, `_resolve_varref`.
  - `TermUn` → recurse into `term`.
  - `TermBin` → recurse into `left` and `right`.
- `_resolve_varref(varref, scope_id)`
  - `entry = symbol_table.lookup_chain(scope_id, varref.name)`
  - If found: `varref.resolved = entry`
  - Else: `diagnostics.append(f"Undeclared variable '{varref.name}' at node #{varref.node_id}")`

*(Optional) In `Assign`, you may also check that the LHS variable exists in the current chain, but the spec only requires resolution of uses within expressions/terms.*

## Diagnostics (current Phase 2 strings)

- Duplicate in a scope: raised by `declare()` as
  - `Duplicate declaration of 'X' in {ScopeKind} scope (previous @ node#..., current @ node#...)`
- Cross-category clashes:
  - `Variable 'X' conflicts with procedure name`
  - `Variable 'X' conflicts with function name`
  - `Main variable 'X' conflicts with procedure name`
  - `Main variable 'X' conflicts with function name`
- Parameters/locals:
  - `Duplicate parameter 'X' in proc 'P'` (or `func 'F'`)
  - `Local variable 'X' shadows parameter in proc 'P'` (or `func 'F'`)

M4 will later replace string messages with structured `Diagnostic` objects and include line/col (if available).

## How to run

```bash
# Print AST
python parse_file.py examples/richer.spl

# Build & print scopes
python parse_file.py examples/richer.spl --check-scopes --dump-scopes

# See failures
python parse_file.py examples/bad_duplicate_params.spl --check-scopes
```

## Negative samples overview
```bash
python parse_file.py examples/bad_duplicate_globals.spl --check-scopes --dump-scopes
# ... shows SYMBOL TABLE then:
# Diagnostics:
#   - Duplicate declaration of 'x' in Global scope (...)

python parse_file.py examples/bad_proc_func_name_clash.spl --check-scopes
# Diagnostics:
#   - Function 'foo' conflicts with procedure name

python parse_file.py examples/bad_main_var_conflicts_with_func.spl --check-scopes
# Diagnostics:
#   - Main variable 'inc' conflicts with function name

python parse_file.py examples/bad_duplicate_params.spl --check-scopes
# Diagnostics:
#   - Duplicate parameter 'a' in proc 'echo'

python parse_file.py examples/bad_local_shadows_param.spl --check-scopes
# Diagnostics:
#   - Local variable 'x' shadows parameter in proc 'p'

python parse_file.py examples/bad_duplicate_locals.spl --check-scopes
# Diagnostics:
#   - Duplicate declaration of 'a' in Local scope (...)
```

