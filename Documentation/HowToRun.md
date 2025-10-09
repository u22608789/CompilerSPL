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