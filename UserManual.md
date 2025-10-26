# HOW TO RUN COMPILER 
---

```
python parse_file.py examples/demo.spl --check-scopes --type-check --emit-basic
```

replace `<examples/demo.spl>` with the input file which you wish to convert to BASIC

## For specific phases of the project
```
# Phase 1: print AST
python parse_file.py examples/demo.spl --print-ast

# Phase 2: scope checker (symbol tables)
python parse_file.py examples/demo.spl --check-scopes --dump-scopes

# Phase 3: type checker
python parse_file.py examples/demo.spl --type-check

# Phase 4: generate unnumbered intermediate code (examples/demo.txt)
python parse_file.py examples/demo.spl --codegen

# Phase 5: emit numbered BASIC with label resolution (examples/demo.bas)
python parse_file.py examples/demo.spl --emit-basic
```

