# SPL Compiler – Frontend (Phase 1)

This repository contains the **frontend** of our compiler for the *Students’ Programming Language (SPL)*, as defined in the COS341 Semester Project 2025 spec.

Implemented components:

* **Token model** (`tokens.py`) – enums for SPL’s terminals and keywords
* **Lexer** (`lexer.py`) – converts raw `.spl` source into a stream of tokens
* **LL(1)-friendly grammar** – refactored from the given SPL grammar to support predictive parsing
* **AST nodes** (`astnodes.py`) – dataclasses to represent SPL programs structurally
* **Pretty-printer** (`ast_printer.py`) – prints ASTs in a tree-like format for debugging
* **Recursive-descent parser** (`parser.py`) – builds an AST from tokens
* **Tests** (`tests/`) – unit tests for lexer and parser behavior

---

## Project Structure

```
src/
  spl/
    __init__.py
    tokens.py
    lexer.py
    parser.py
    astnodes.py
    ast_printer.py
examples/
  hello.spl
  rich.spl
  richer.spl
tests/
  test_lexer_basic.py
  test_parser_assignments.py
  ...
```

---

## Requirements

* Python **3.10+**
* [`pytest`](https://docs.pytest.org/) for testing

Install dependencies (only pytest is needed right now):

```bash
python -m pip install -r requirements.txt
```

---

## Running the Lexer

You can inspect tokens with the `dump_tokens.py` helper:

```bash
python dump_tokens.py examples/hello.spl
```

Example output:

```
1:1   GLOB    'glob'
1:6   LBRACE  '{'
...
1:43  IDENT   'x'
1:45  ASSIGN  '='
1:47  LPAREN  '('
1:48  IDENT   'a'
1:50  PLUS    'plus'
1:55  NUMBER  '1'
1:56  RPAREN  ')'
```

---

## Running the Parser

Use `parse_file.py` to parse an SPL program and print its AST:

```bash
python parse_file.py examples/rich.spl
```

Example output:

```
Program
  globals:
    List[1]
      [0]
        'g'
  procs:
    List[1]
      [0]
        ProcDef
          name: 'p'
          ...
  main:
    Main
      algo:
        Algo
          instrs:
            List[4]
              [0] Assign(var='i', rhs=NumberLit(3))
              [1] Call(name='p', args=[VarRef('i')])
              [2] LoopWhile(...)
              [3] BranchIf(...)
```

---

## Running Tests

Run the unit test suite with:

```bash
python -m pytest -q
```

---

## Example Programs

* `examples/hello.spl` – minimal SPL program
* `examples/rich.spl` – includes proc call, while loop, if/else
* `examples/richer.spl` – also includes do–until and function calls in expressions

---

## Next Steps

* **Semantic Analysis** (Phase 2): scope checking, type checking, etc.
* **Code Generation** (Phase 3): translate AST into target code

---
