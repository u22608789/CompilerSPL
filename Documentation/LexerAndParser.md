# File Structure 
``` 
│   .gitignore
│   dump_tokens.py                            (used to run lexer)
│   parse_file.py                            (used to run parser)
│   README.md
│   requirements.txt
│   test_input.spl
│
├───.pytest_cache
│   └─── ...
│
├───Documentation
│       GrammarConversion.md
│       LexerAndParser.md
│       TypeChecker.md
│       HowToRun.md
│
├───examples                              (Source Program/Inputs)
│       hello.spl                                        (simple)
│       rich.spl                                 (mid complexity)
│       richer.spl                       (little more complexity)
│
├───src
│   ├───spl
│   │   │   astnodes.py        (Define python dataclasses / Nodes)
│   │   │   ast_printer.py                (Prints the syntax tree)
│   │   │   errors.py                        (not yet implemented)
│   │   │   lexer.py                 (core lexer logic, tonkenise)
│   │   │   parser.py           (core parser logic, check grammar)
│   │   │   tokens.py                           (define vocablary)
│   │   │   __init__.py                          (not implemented)
│   │   │
│   │   └───__pycache__
│   │           ...
│   │
│   └───__pycache__
│           ...
│
└───tests
    │   conftest.py            (issues w/ install path bc of `src`)
    │   test_lexer_basic.py                            (test lexer)
    │   test_parser_assignments.py                    (test parser)
    │   test_parser_errors.py                 (not implemented yet)
    │   test_parser_happy.py                  (not implemented yet)
    │
    └───__pycache__
            ...
```

# 1) How it works 

## Pipeline overview
1. **Lexer (`src/spl/lexer.py`)**
   * Scans characters → emits tokens (`spl/tokens.py`).
   * Rules from the spec:
     * **Identifiers**: `[a–z][a–z0–9]*` (no underscores, lowercase only).
     * **Numbers**: `0 | [1–9][0–9]*` (no leading zeros like `01`).
     * **Strings**: `"[A-Za-z0-9]{0,15}"` (alnum, ≤15 chars).
     * **Keywords** reserved: `glob, proc, func, main, local, var, return, halt, print, while, do, until, if, else, neg, not, eq, or, and, plus, minus, mult, div, >`.
     * Whitespace separates tokens; it’s ignored.

2. **Parser (`src/spl/parser.py`)**
   * Recursive-descent using an LL(1)-friendly version of the grammar (G′).
   * Builds an **AST** (see `spl/astnodes.py`).
   * Notes:
     * `ALGO` parses ≥1 instruction and uses a small **lookahead guard** so it doesn’t swallow the `;` before `return` in function bodies.
     * **Terms** allowed: `ATOM` | `( UNOP TERM )` | `( TERM BINOP TERM )`. There’s **no** plain grouping `(TERM)`.
     * Distinguishes:
       * **Proc call (stmt)**: `NAME ( INPUT )`
       * **Assignment to func call**: `x = f(args)`
       * **Assignment to general term**: `x = (a plus 1)` or `x = 42`

3. **AST (`spl/astnodes.py`)**
   * Dataclasses: `Program`, `ProcDef`, `FuncDef`, `Body`, `Main`, `Algo`, and nodes for `Assign`, `Call`, `LoopWhile`, `LoopDoUntil`, `BranchIf`, `Print`, `Halt`, and expression forms (`TermAtom`, `TermUn`, `TermBin`, `VarRef`, `NumberLit`, `StringLit`).

4. **AST pretty-printer (`spl/ast_printer.py`)**
   * `print_ast(ast)` gives a readable tree for debugging.

5. **Tests (`tests/`)**
   * Lexer tests (keywords/idents/numbers/strings/punct/positions).
   * Parser tests (assignments, calls, loops, branches, function body `; return` edge).

## Key constraints to remember
* **No underscores** in identifiers (`iszero`, not `is_zero`).
* **Strings** must be alnum and ≤15 chars.
* **No extra parentheses** around terms (only the three `TERM` shapes above).
* Function bodies: at least **one instruction** before `; return …` (we typically use `halt`).

---

# 2) How to run it
## Install prerequisites

```bash
# From repo root
python -m pip install -r requirements.txt   # currently just pytest
```

## Inspect tokens (lexer)

```bash
python dump_tokens.py examples/hello.spl
```

## Parse and print AST
Use `parse_file.py` and run:

```bash
python parse_file.py examples/rich.spl
python parse_file.py examples/richer.spl
```

## Run tests

```bash
python -m pytest -q
```

---

# 3) Additional info to keep the project moving

## Common pitfalls (and quick fixes)

* **Imports won’t resolve**
  * We’re using the **src layout**: package is `spl` under `src/`.
  * In code under `spl/`, use *relative* imports: `from .tokens import T`.
  * In tests or scripts, import via package: `from spl.parser import Parser`.
  * If a standalone script fails to import, prepend `src/` to `sys.path` (see `dump_tokens.py`) or do `pip install -e .`.
* **Parser errors around parentheses**
  * Remember: `(TERM)` isn’t a thing; use `( a plus 1 )`, `( neg a )`, or an atom.
* **Strings rejected**
  * Must be alnum only and ≤15 chars: `"OK123"`, not `"hello world"` or `"abc_123"`.

## Coding habits / style (so we’re consistent)
* Keep token kinds in **one place** (`spl/tokens.py`), update keyword map there first.
* Parser functions mirror grammar nonterminals (`_algo`, `_instr`, `_term`, …).
* Raise `SyntaxError` with **line:col** (already built-in via tokens).
* Keep tests close to features you add (lexer rules, new parse cases).
* Use `print_ast()` during development to eyeball tree shapes.




---
# How it all flows
# Big picture

```
.spl source  --(Lexer)-->  Tokens  --(Parser)-->  AST  --(Pretty-printer)-->  Human-readable tree
```

* **Lexer** (`spl/lexer.py`): reads chars, emits `Token` objects.
* **Parser** (`spl/parser.py`): reads tokens, builds an AST (from `spl/astnodes.py`).
* **Pretty-printer** (`spl/ast_printer.py`): prints the AST nicely for debugging.

You can run each stage by itself (token dump) or together (parse + print).

---
# The Token object (what the lexer outputs)
From `spl/tokens.py`:
* `typ`: enum (e.g., `GLOB`, `IDENT`, `NUMBER`, `LPAREN`, `PLUS`, `EOF`, …)
* `lexeme`: the source text (e.g., `"glob"`, `"x"`, `"42"`, `"plus"`)
* `line` / `col`: position for error messages

---
# 1) Lexer flow (input → tokens)
## Files involved
* `spl/lexer.py` (implementation)
* `spl/tokens.py` (token types + keywords)
* `dump_tokens.py` (utility to run the lexer and print tokens)

## What triggers it?
* Directly: `python dump_tokens.py examples/hello.spl`
* Indirectly: when the parser constructs `Lexer(text)` and repeatedly calls `next_token()`.
## How it works (step-by-step)
1. **Construction**

   ```python
   lx = Lexer(text)  # stores text, sets i=0, line=1, col=1
   ```
2. **Tokenization loop (`next_token`)**
   * `_skip_ws()` consumes spaces/tabs/newlines and updates line/col.
   * Look at the next char (`_peek()`), then:
     * If it’s a **punctuator/operator** from `PUNCT`, emit that token and advance 1 char (`{ } ( ) ; = >`).
     * If it’s a **quote** `"`, match a **string** `"([A-Za-z0-9]{0,15})"`, else raise error (unterminated/invalid).
     * Try **number**: `(0|[1-9][0-9]*)`.
     * Try **identifier**: `[a-z][a-z0-9]*`. If the lexeme is a **reserved keyword** (e.g., `while`, `plus`), emit its keyword token; otherwise emit `IDENT`.
     * If none match, raise a `ValueError` with `line:col`.
   * At end of text, emit `EOF`.
3. **Output**
   * A stream of `Token` objects until `EOF`.

## Example: run the lexer
Input (`examples/hello.spl`):
```spl
glob { } proc { } func { } main { var { } x = (a plus 1) }
```

Command:
```bash
python dump_tokens.py examples/hello.spl
```

Output (abridged):
```
1:1   GLOB  'glob'
...
1:43  IDENT 'x'
1:45  ASSIGN '='
1:47  LPAREN '('
1:48  IDENT 'a'
1:50  PLUS  'plus'
1:55  NUMBER '1'
1:56  RPAREN ')'
1:58  RBRACE '}'
1:59  EOF   ''
```

## Error flow (lexer)
* Bad string (underscore, space, >15 chars, or no closing `"`): raises `ValueError("Invalid string at L:C ...")`.
* Unknown character (e.g., `@`): raises `ValueError('Unknown character "@" at L:C')`.

---
# 2) Parser flow (tokens → AST)
## Files involved
* `spl/parser.py` (implementation)
* `spl/astnodes.py` (node classes)
* `spl/ast_printer.py` (pretty output)
* `parse_file.py` (utility to run parser and print AST)

## What triggers it?
* `tree = Parser(text).parse()` — usually from `parse_file.py`.

## How it works (step-by-step)
1. **Construction & lookahead**

   ```python
   p = Parser(text)
   # Internally:
   self.lexer = Lexer(text)
   self.cur = self.lexer.next_token()  # current token
   self.nxt = self.lexer.next_token()  # one-token lookahead
   ```

   * `_advance()` moves `cur ← nxt`, `nxt ← lexer.next_token()`.
   * `_eat(T.X)` asserts `cur.typ == T.X`, then `_advance()`. Else raises `SyntaxError("expected X, found Y at L:C")`.

2. **Entry point**: `parse()`
   Implements the top rule:

   ```
   SPL_PROG → glob { VARIABLES } proc { PROCDEFS } func { FUNCDEFS } main { MAINPROG }
   ```

   * Calls helpers for each nonterminal:
     * `_variables()` → list of `IDENT`
     * `_procdefs()` / `_pdef()`
     * `_funcdefs()` / `_fdef()`
     * `_mainprog()`

3. **The “lists” pattern** (LL(1) friendly)
   * `VARIABLES`, `PROCDEFS`, `FUNCDEFS` are parsed as “zero or more” loops: read `IDENT` while present.

4. **Bodies & params**
   * `_body()` parses `local { MAXTHREE } ALGO`, producing `Body(locals=[...], algo=...)`.
   * `_maxthree_vars()` consumes up to 3 identifiers (params or locals).

5. **ALGO (sequence of statements)**
   * `_algo()` parses `INSTR` then repeats `; INSTR` **only if** the token after `;` can start an instruction.

     * That small guard uses `self.nxt` and prevents swallowing the `;` that belongs to `; return` in a function body.

6. **INSTR choices**
   * `halt` → `Halt()`
   * `print OUTPUT` → `Print(NumberLit/VarRef/StringLit)`
   * `NAME ( INPUT )` → `Call(name, args)` (procedure call as a statement)
   * assignments:
     * `VAR = NAME ( INPUT )` → `Assign(var, rhs=Call(...))` (function call)
     * `VAR = TERM` → `Assign(var, rhs=Term...)`
   * `while TERM { ALGO }` → `LoopWhile(cond, body)`
   * `do { ALGO } until TERM` → `LoopDoUntil(body, cond)`
   * `if TERM { ALGO } [else { ALGO }]` → `BranchIf(cond, then, else or None)`

7. **Terms & atoms**
   * `_term()` supports exactly 3 shapes:
     * `ATOM` → `TermAtom(VarRef/NumberLit)`
     * `( UNOP TERM )` → `TermUn(op, term)`
     * `( TERM BINOP TERM )` → `TermBin(left, op, right)`
   * `_atom()` is `IDENT` → `VarRef(name)` or `NUMBER` → `NumberLit(value)`.
   * **No plain `(TERM)` grouping** is allowed by the spec we implemented.

8. **Output**
   * A fully built AST (`Program`) that mirrors the structure of the SPL program.

## Example: run the parser
Input (`examples/rich.spl`):

```spl
glob { g }
proc {
  p(a) { local { } print a }
}
func {
  iszero(n) { local { } halt ; return n }
}
main {
  var { i }
  i = 3;
  p(i);
  while ( i > 0 ) {
    print i;
    i = ( i minus 1 )
  };
  if ( i eq 0 ) { print "done" } else { print "oops" }
}
```

Command:

```bash
python parse_file.py examples/rich.spl
```

Output (abridged):

```
Program
  globals: ['g']
  procs: [ ProcDef(name='p', params=['a'], body=...) ]
  funcs: [ FuncDef(name='iszero', params=['n'], body=..., ret=VarRef('n')) ]
  main:
    Algo
      Assign(var='i', rhs=NumberLit(3))
      Call(name='p', args=[VarRef('i')])
      LoopWhile(cond=TermBin(VarRef('i') '>' NumberLit(0)),
                body=Algo([Print(VarRef('i')),
                           Assign('i', TermBin(VarRef('i') 'minus' NumberLit(1)))]))
      BranchIf(cond=TermBin(VarRef('i') 'eq' NumberLit(0)),
               then_=Algo([Print("done")]),
               else_=Algo([Print("oops")]))
```

## Error flow (parser)
* Wrong token where a specific terminal is expected:
  * `SyntaxError: expected RPAREN, found SEMI at L:C`
* Bad `TERM` shape (e.g., extra parens):
  * `SyntaxError: expected binary op at L:C`

---

# 3) End-to-end: which file to run for what?
* **Token stream only** (debug lexer):
  ```
  python dump_tokens.py examples/hello.spl
  ```
  Output: lines of `line:col  TOKEN  'lexeme'` until `EOF`.

* **Parse & print AST** (full frontend):
  ```
  python parse_file.py examples/rich.spl
  ```
  Output: Pretty tree of the AST.

* **Run tests** (CI confidence):
  ```
  python -m pytest -q
  ```

---

# 4) Cheat sheet 

* Identifiers must be **lowercase letters/digits**, starting with a letter — **no underscores**.
* Strings are alnum only and **≤ 15 chars**.
* `TERM` is **atom**, **unary in parens**, or **binary in parens** — not plain `(term)`.
* Function bodies must have **≥1 instruction** before `; return`. We often use `halt`.

---

# 5) How to extend
* New keyword? Add it in `spl/tokens.py` (enum + `KEYWORDS`), then use it in grammar & parser.
* New AST node? Add a dataclass in `spl/astnodes.py`, and print automatically works.
* New grammar feature? Add a parser method mirroring the nonterminal; write tests; try on an example; use `print_ast()` to verify shape.


