🧩 Overview

The Code Generation Phase is the third stage of our SPL compiler pipeline.

It takes the Abstract Syntax Tree (AST) produced by the parser and converts it into executable target code — a textual, assembly-like format that reflects the semantics of the SPL program.

This phase corresponds directly to the specifications in code-gen.pdf and implements the translation techniques discussed in lectures (especially those covering Figures 6.3–6.8 from the textbook).

===============================================================================

⚙️ The Compilation Pipeline

The compiler now operates in three phases:
| Phase                            | Module                                | Description                                            |
| -------------------------------- | ------------------------------------- | ------------------------------------------------------ |
| **1. Lexical & Syntax Analysis** | `lexer.py`, `parser.py`               | Tokenizes SPL source and builds the AST                |
| **2. Scope & Naming Analysis**   | `scope_checker.py`, `symbol_table.py` | Builds symbol tables, checks duplicates and visibility |
| **3. Code Generation**           | `codegen.py`                          | Traverses AST and emits target code                    |

🗂️ Files Added / Modified
| File                                       | Purpose                                                                        |
| ------------------------------------------ | ------------------------------------------------------------------------------ |
| **`src/spl/codegen.py`**                   | New module implementing the full code generation logic                         |
| **`parse_file.py`**                        | Extended CLI to add `--codegen` and `--out` flags, integrating code generation |
| **`Documentation/CodeGenerationPhase.md`** | This documentation file                                                        |

===============================================================================

🧱 New Components

1️⃣ src/spl/codegen.py

The CodeGenerator class implements the translation rules from code-gen.pdf.

Each AST node type (e.g., Assign, Print, LoopWhile, BranchIf) has a corresponding trans_* method that outputs textual code lines.

Core responsibilities:

- AST Traversal: Visits each node recursively (using the Visitor pattern)

- Label Management: Generates unique labels for branching and looping

- Conditional Logic: Uses REM for labels and IF … THEN label for control flow

- Symbol Table Lookup: Optionally maps variable names via the existing SymbolTable

Output Emission: Writes .txt file with ASCII code

            Example of output (examples/rich.spl → examples/rich.txt):
            i = 3
            CALL p i
            REM WH1
            IF i > 0 THEN WB2
            GOTO WE3
            REM WB2
            PRINT i
            i = (i - 1)
            GOTO WH1
            REM WE3
            IF i = 0 THEN T4
            PRINT "done"
            GOTO X5
            REM T4
            PRINT "oops"
            REM X5
            STOP

2️⃣ Modifications to parse_file.py

New functionality added:

--codegen: triggers code generation phase

--out: specifies output file (defaults to <input>.txt)

Integration with ScopeChecker so the symbol table can be reused

Automatically writes output to a text file in examples/

Example Command:
    python parse_file.py examples/rich.spl --check-scopes --codegen
Output:
    Variable Naming and Function Naming accepted
    Generating target code → examples/rich.txt
    Code generation completed successfully.

===============================================================================

🔍 Integration with Symbol Table

codegen.py can optionally use the SymbolTable built by the scope checker.
This ensures correct name resolution even if identifiers have been internally renamed for disambiguation.

Hook used:
cg.symbol_table = st
Lookup Method:
def lookup(self, name: str) -> str:
    if not hasattr(self, "symbol_table") or self.symbol_table is None:
        return name
    entry = self.symbol_table.lookup_chain(
        self.symbol_table.base_scopes["main"], name
    )
    return entry.name if entry else name

===============================================================================

🧠 Inlining Procedures & Functions
Both procedures (proc) and functions (func) are parsed into the AST and stored in lists (program.procs, program.funcs).

In this phase:

- Their AST subtrees are cached in memory (self.procs, self.funcs).

- Direct calls (e.g. p(i) or x = f(i)) can be inlined instead of emitting external calls.

Inlining benefits:

- Simplifies final target code (no separate call stack).

- Matches lecture requirements (as per “Lecture of 2nd October” in the spec).

- Enables later optimization or instruction scheduling if desired.

===============================================================================

🧮 Target Language Rules Implemented
| SPL Construct                   | Translation Rule (per `code-gen.pdf`)    | Example Output |
| ------------------------------- | ---------------------------------------- | -------------- |
| `halt`                          | `STOP`                                   | `STOP`         |
| `print x`                       | `PRINT x`                                | `PRINT i`      |
| `print "hi"`                    | `PRINT "hi"`                             |                |
| `x = (a plus 1)`                | `x = (a + 1)`                            |                |
| `if cond {A} else {B}`          | Uses `REM`, `IF`, and `GOTO` labels      | See above      |
| `while cond {A}`                | Loop using `REM` and `GOTO`              | See above      |
| `do {A} until cond`             | Post-check loop form                     |                |
| `f(args)` / `CALL f`            | Inlined or emitted as `CALL f arg1 arg2` |                |
| `eq, >, plus, minus, mult, div` | Mapped to `=, >, +, -, *, /`             |                |
| `not`, `or`, `and`              | Expanded via label-based logic           |                |

===============================================================================

🧰 How to Run
1️⃣ Build / Parse / Check Scopes / Generate Code

    python parse_file.py examples/rich.spl --check-scopes --codegen

2️⃣ Specify Output File

    python parse_file.py examples/rich.spl --check-scopes --codegen --out build/rich_output.txt


3️⃣ View Output

    Open examples/rich.txt or your custom file — it will contain the full generated code.

💡 Design Decisions
| Decision                                        | Reason                                                                                                 |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **Separate module (`codegen.py`)**              | Keeps code generation isolated from parsing and semantic analysis. Simplifies maintenance and testing. |
| **Visitor-style traversal (`trans_*` methods)** | Clear mapping between grammar nonterminals and translation logic (mirrors textbook figures).           |
| **Plain `.txt` output**                         | Matches `code-gen.pdf` requirement: “Generated target code must be stored in a *.txt (ASCII) file.”    |
| **REM instead of LABEL**                        | Required by the specification: “Our Target Language uses REM instead of LABEL.”                        |
| **GOTO-based flow control**                     | Matches minimal target language without ELSE/ENDIF keywords.                                           |
| **Symbol Table Hook**                           | Ensures consistent variable naming if renaming is introduced in earlier phases.                        |
| **Inlining for proc/func**                      | Prepares compiler for optimization phase and matches lecture notes.                                    |

===============================================================================

🧾 Verification

Scope Checking: Verified via ScopeChecker → no naming conflicts.

Code Generation: Successfully generates target text for all test examples (hello.spl, rich.spl, richer.spl).

Conformance: Matches every translation rule described in code-gen.pdf.

===============================================================================