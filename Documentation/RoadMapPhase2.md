perfect—here’s a lean, do-this-then-that roadmap you can run in order. Each step names files, who owns it (M1–M4), and the concrete output to review at the next checkpoint.

---

# Minimal Phase-2 Roadmap (ordered)

## 0) Bootstrap branch & script hooks (30–45 min)

**Owner:** M4
**Files:**

* `README.md` (+Phase 2 section)
* `Documentation/HowToRun.md` (+new flag usage)
* (optional) `Makefile` or `package.json` scripts

**Output:** New branch `phase2/scopes`, `make check-scopes` (or `python parse_file.py --check-scopes <file>` placeholder that currently just parses).

---

## 1) Add stable `node_id` to AST (foundation)

**Owner:** M1
**Files (edit):** `src/spl/astnodes.py`, `src/spl/parser.py`
**Files (new):** `src/spl/ast_ids.py` (helper)

**What:**

* Add `node_id: int` to every AST dataclass (default `-1`).
* Implement `assign_ids(ast)` DFS in `ast_ids.py`; call it at the end of `parse_file.py` after parsing.

**Output:** Running `parse_file.py examples/hello.spl --print-ast` shows node ids.

---

## 2) Symbol table core types & API

**Owner:** M1
**Files (new):** `src/spl/symbol_table.py`
**What:**

* `Scope(kind, parent_id)` + auto `id`.
* `SymbolTableEntry { name, kind: ('var'|'param'|'proc'|'func'), scope_id, decl_node_id }`.
* `SymbolTable` with:

  * `new_scope(kind, parent_id)`
  * `declare(scope_id, entry) -> ok/raises`
  * `lookup_chain(start_scope_id, name) -> entry|None`
  * Pretty printer for debug.

**Output:** Unit-style smoke in a quick `__main__` block or doctest.

---

## 3) Top-level scope layout (“Everywhere” tree)

**Owner:** M1
**Files (new):** `src/spl/scope_checker.py` (skeleton)
**What:**

* Build scopes: `Everywhere` → children: `Global`, `Procedure`, `Function`, `Main`.
* Wire into `parse_file.py --check-scopes` so it builds the scope tree (no declarations yet) and prints it.

**Output:** `--check-scopes` prints the 5 base scopes with IDs.

---

## 4) Declarations: globals, proc names, func names (no bodies)

**Owner:** M2
**Files (edit):** `src/spl/scope_checker.py`
**What:**

* Insert **global variable** names into `Global` (reject dups).
* Insert **procedure** names into `Procedure` (reject dups).
* Insert **function** names into `Function` (reject dups).
* Enforce **cross-category clashes** at “Everywhere” (a var name cannot equal a proc/func name; procs & funcs cannot share a name).
* Attach `(decl_node_id → entry)` map.

**Output:** On `examples/rich*.spl`, a table showing global/func/proc entries; failing duplicates raise a clean diagnostic (temporary `print` ok).

---

## 5) Per-def local scopes + params + locals (no ALGO yet)

**Owner:** M2
**Files (edit):** `src/spl/scope_checker.py`
**What:**

* For each `PDEF`/`FDEF`, create a **Local** scope.
* Insert **params** (reject dups).
* Insert **locals** (reject dups; **and** reject if collides with any param in the same def).
* For `Main`, insert its locals (reject dups).

**Output:** Pretty-printed scope tree shows Local scopes with entries; param-shadowing violations reported.

---

## 6) Name-use resolution in ALGO (procedures & functions)

**Owner:** M3
**Files (edit):** `src/spl/scope_checker.py`, `src/spl/astnodes.py`
**What:**

* Add optional `resolved: Optional[SymbolTableEntry]` to identifier/`VarRef` node(s).
* Walk each `ALGO` under `PDEF`/`FDEF`: resolve `name` with **param → local → global** priority.
* If not found: emit `UndeclaredVariable` (collect, don’t crash).

**Output:** A debug “Uses → Decl” mapping (use node_id → decl node_id) printed for `examples/richer.spl`.

---

## 7) Name-use resolution in Main’s ALGO

**Owner:** M3
**Files (edit):** `src/spl/scope_checker.py`
**What:**

* Resolve in `Main` with **main-locals → global** priority; else `UndeclaredVariable`.

**Output:** Same debug mapping for `examples/hello.spl` + a tiny negative sample.

---

## 8) Diagnostics model & error collection

**Owner:** M4
**Files (edit/new):** `src/spl/errors.py`
**What:**

* `Diagnostic { kind, message, node_id, line, col, scope_path }`
* Kinds: `DuplicateName`, `CrossCategoryClash`, `ParamShadowed`, `UndeclaredVariable`.
* Make checker **return `[Diagnostic]`**. Only at the very end: pretty-print list.

**Output:** Clean, consistent error lines with file/line/col if available from tokens.

---

## 9) CLI integration & stable output formats

**Owner:** M4
**Files (edit):** `parse_file.py`
**What:**

* `--check-scopes` runs: parse → assign_ids → build scopes → decl pass → use-res → print “OK” or diagnostics.
* Add `--dump-scopes` to pretty-print the scope tree (handy in reviews).

**Output:** Two commands demo’d in the meeting.

---

## 10) Tests: happy + negative coverage

**Owner:** M4 (author), all review
**Files (new):**

* `tests/test_scope_happy.py`
* `tests/test_scope_errors.py`
* `tests/test_scope_resolution.py`

**What:**

* **Happy:** small programs hitting global/main/proc/func resolution.
* **Errors:**

  * duplicate globals / procs / funcs,
  * duplicate params / locals,
  * local shadowing param,
  * cross-category clash,
  * undeclared uses (in proc/func/main).
* Assert on **diagnostic kinds and messages** (exact or regex).

**Output:** Green tests for happy; red→green iteratively for negatives.

---

## 11) Docs pass

**Owner:** M4
**Files (new):** `Documentation/ScopesAndNames.md`
**What:**

* One page: scope tree diagram, resolution rules table, sample diagnostics, how to run.

**Output:** Short, marker-friendly doc.

---

## 12) Final polish & merge

**Owners:** All
**What:**

* Remove debug prints; keep `--dump-scopes`.
* Re-run examples and record expected outputs in `Documentation/HowToRun.md`.
* Merge `phase2/scopes` → `main`.

---

# Who does what (fixed mapping)

* **M1:** AST `node_id` + `symbol_table.py` + top-level scope layout (Steps 1–3).
* **M2:** Declarations pass + local scopes (Steps 4–5).
* **M3:** Use-resolution passes for proc/func/main (Steps 6–7).
* **M4:** Diagnostics + CLI + tests + docs (Steps 0, 8–11).

(Everyone helps on Step 12.)

---

## Quick acceptance checklist (use in PR reviews)
* [ ] `--check-scopes` prints **OK** for `examples/hello.spl`, `rich.spl`, `richer.spl`.
* [ ] `--dump-scopes` shows **Everywhere / Global / Procedure / Function / Main / Local** tree with entries.
* [ ] All **diagnostic kinds** appear in tests with clear messages.
* [ ] Each identifier use in ALGO has a **`resolved`** link to a decl node (spot-checked in tests).
* [ ] No shadowing of params by locals; no cross-category name clashes slip through.

