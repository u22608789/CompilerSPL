# HOW TO RUN COMPILER 
---

```
python parse_file.py examples/demo.spl --check-scopes --type-check --emit-basic
```

Replace `<examples/demo.spl>` with the input file which you wish to convert to BASIC.
The file will be saved to `<filename>.bas`.  

# Running the BASIC 
Paste the `.bas` file into Owlet BBC BASIC Editor: https://bbcmic.ro
Or any other online BASIC Emulators, however, we know the above one works for our dialect. 
If using OneCompiler, make sure to include `#lang "qb"` at the top.


# For specific phases of the project
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

