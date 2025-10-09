# 1) What Phase 2 actually wants

Phase 2 is a **name & scope checker** (static semantics) that walks your AST, builds a **symbol table** (hash-table is fine), and enforces SPL’s **static scoping rules**. Every AST node must have a **unique node ID** that links to its symbol-table info. You must report (a) **name-rule violations** like duplicate declarations or illegal clashes and (b) **undeclared variable** uses. 

Key rules to enforce (high level):

* **Global layout:** The whole program is “Everywhere”, with sub-scopes for **Global** (glob vars), **Procedure** (all procs), **Function** (all funcs), and **Main**. Within “Everywhere”, variable names must not be identical to any function or procedure name; functions and procedures also may not share names. 
* **No duplicates in same list/scope:**
  – Global `VARIABLES`: no duplicate names.
  – `PROCDEFS`: no duplicate procedure names.
  – `FUNCDEFS`: no duplicate function names.
  – `MAXTHREE` (parameters or locals): no duplicates. 
* **Local scopes per def:** Each `PDEF` and `FDEF` has its own **Local** scope. In each, **locals must not shadow parameters** (same name is illegal). 
* **Name resolution for uses (`VAR` inside ALGO):**
  – In a **proc’s** ALGO: prefer param → then local → else global, otherwise “undeclared”.
  – In a **func’s** ALGO: prefer param → then local → else global, otherwise “undeclared”.
  – In **main**: prefer main-locals → else global, otherwise “undeclared”. Update the symbol table to point to the resolved declaration. 

(Grammar context from Phase 1 stays the same. ) 

# 2) How to approach it (architecture & workflow)

**A. Minimal new modules (drop into `src/spl/`)**

* `symbol_table.py`
  A small framework, not a DB:

  ```text
  SymbolTableEntry {
    name: str
    kind: 'var' | 'param' | 'proc' | 'func'
    scope_id: int
    decl_node_id: int      # AST node that declared it
    # (phase 3+ could add type info; keep slot now)
  }

  Scope {
    id: int
    kind: 'Everywhere' | 'Global' | 'Procedure' | 'Function' | 'Main' | 'Local'
    parent_id: Optional[int]
    table: Dict[str, SymbolTableEntry]  # per-scope hash map
  }

  SymbolTable {
    scopes: Dict[int, Scope]
    nodes: Dict[int, SymbolTableEntry]  # optional reverse map by decl node id
  }
  ```
* `scope_checker.py` (tree-crawler)
  Walks the AST (produced by your `parser.py`), **creates scopes**, **inserts declarations**, enforces **duplicate/name-clash rules**, and **resolves VAR uses** to their declaration (recording that link).
* `errors.py` (you already stubbed it)
  Define structured diagnostics:

  ```python
  class NameRuleViolation(Exception): ...
  class UndeclaredVariable(Exception): ...
  ```

  plus a non-exception `Diagnostic` struct if you’d rather **collect** all errors then print.

**B. AST updates (tiny but important)**

* In `astnodes.py` give **every node** a `node_id: int` (auto-increment assigned during construction or a post-parse pass) so each node can be a **foreign key** into the symbol table. 
* For identifier nodes (`Var`, `Name`), add an optional `resolved: SymbolTableEntry | None` field. The checker fills it when a use is bound.

**C. Scope creation strategy**

1. Create the **Everywhere** scope (root). Under it, create **Global**, **Procedure**, **Function**, **Main** child scopes to mirror the top-level AST sections. Enforce the cross-category “no clashes” rule across **variables vs procs vs funcs** at the **Everywhere** level. 
2. For each `PDEF` / `FDEF` create a **Local** child scope. Insert **params** (as `kind='param'`) then **locals** from `MAXTHREE`; reject any local that duplicates a param (“no shadowing”). 
3. In **Main**, add its `VARIABLES` (no dups). 

**D. Name resolution algorithm (for `VAR` uses inside ALGO)**

* In procs/funcs: **param → local → global → error**.
* In main: **main-local → global → error**.
  When found, set `node.resolved = entry` and (optionally) store a back-reference `(use_node_id → decl_node_id)` for later phases. 

**E. Diagnostics format**

* Print friendly messages with **scope path**, **line/column** (from lexer tokens if you carry positions), and **node_id**:

  ```
  Undeclared variable 'x' in Main at line 12, col 9. (node #143)
  Duplicate variable 'a' in function 'inc' locals. (node #77)
  Illegal clash: variable 'foo' conflicts with function 'foo' in Everywhere.
  ```

**F. Testing approach (add to `tests/`)**

* **Happy paths:** `test_scope_happy.py` with tiny programs covering:

  * globals + main + proc + func, proper resolution across all three.
* **Negative cases:** `test_scope_errors.py`:

  * duplicate globals; duplicate proc names; duplicate func names; duplicate params; duplicate locals; local shadows param; var use undeclared in proc/func/main; global name clashes with proc/func.
* **Snapshot/Golden:** assert rendered symbol table and resolved links for `examples/hello.spl`, `rich.spl`, `richer.spl`.

# 3) Delegation plan for 4 people (clear seams, minimal merge pain)

**Role A — Symbol Table & Scopes (Owner: Person 1)**

* Implement `SymbolTable`, `Scope`, create/lookup APIs, and scope stack helpers (`push_scope`, `pop_scope`, `declare`, `lookup_chain`).
* Top-level scope construction (Everywhere + Global/Procedure/Function/Main).
* Enforce **cross-category** name-clash rule at Everywhere. 

**Role B — Declarations Pass (Owner: Person 2)**

* Walk AST to **collect declarations** only:
  * Globals into Global scope (no dups).
  * Proc names into Procedure scope (no dups).
  * Func names into Function scope (no dups).
  * For each def, make a **Local** scope and insert **params** then **locals** (reject param-shadow).
* Emits **NameRuleViolation** where needed. 

**Role C — Uses/Resolution Pass (Owner: Person 3)**

* Second walk over `ALGO` trees to resolve each `VAR` use according to the per-scope rules (proc/func/main).
* Attach `resolved` links; emit **UndeclaredVariable** when needed. 

**Role D — Diagnostics, CLI integration & Tests (Owner: Person 4)**

* Finish `errors.py` with structured diagnostics; add a **`parse_file.py --check-scopes`** mode.
* Write unit tests and fixtures (`tests/test_scope_*.py`).
* Add docs page `Documentation/ScopesAndNames.md` with short examples + expected outputs.

> Why this split works: A & B can proceed in parallel (data structures vs decl-pass). C starts once B’s symbol table population is stable. D runs end-to-end on examples and tightens error messages.

# 4) Immediate action items:

* [ ] Add `node_id` to all AST nodes in `astnodes.py` and a tiny `assign_ids(ast)` helper. 
* [ ] Create stubs for `symbol_table.py`, `scope_checker.py`, and flesh out `errors.py`.
* [ ] Draft tests: one happy file, one per failure kind.
* [ ] Update `Documentation/HowToRun.md` with the new flag.

---

## Extras that will help you succeed fast

* **Keep scope nesting explicit**: store `parent_id` and walk up on lookup to naturally implement “param/local/global” priorities per scope type. 
* **Record both directions**: (decl node → entry) and (use node → decl entry). Later phases (type checking, IR, codegen) will love you for this.
* **Print a human-readable symbol table** (owner D) to quickly debug meetings:

  ```
  Scope #2 (Local func 'inc'):
    param n -> decl node #45
    local x -> decl node #52
  ```
* **Document the illegal global clashes** with a tiny example (var name colliding with proc/func name) so it’s crystal clear for markers. 

If you want, I can scaffold the `symbol_table.py` and `scope_checker.py` stubs next—but the plan above should give you a crisp meeting flow and clean division of labour.
