# 🧩 SPL Type Checking and Code Generation — Phase Documentation

## 📁 Files Involved
- `src/spl/type_checker.py` — Implements the **SPL Type Checker**  
- `src/spl/codegen.py` — Implements the **SPL Code Generator**  
- `parse_file.py` — Orchestrates all compiler phases (Parse, Scope Check, Type Check, Code Generation)

---

## 🔍 1. Type Checking (Phase 2.5)

### 📘 Overview

The **Type Checker** validates the **semantic correctness** of SPL programs beyond scope and syntax validation.  
It ensures that:
- Variables are declared before use  
- Operations are used on the correct data types (e.g., numeric vs boolean)  
- Function return types are consistent  
- Conditions in loops and branches evaluate to valid boolean/numeric types  

Implemented using a **Visitor pattern**, each AST node is traversed to ensure semantic consistency.

---

### ⚙️ Implementation Summary

**File:** `src/spl/type_checker.py`

**Main Class:** `TypeChecker`

| Component | Description |
|------------|--------------|
| `self.scopes` | Stack of symbol tables for variables in different scopes (global, local, main). |
| `visit_Program` | Entry point — visits globals, procedures, functions, and main. |
| `visit_ProcDef` | Creates a new scope for a procedure and checks its body. |
| `visit_FuncDef` | Validates function body and ensures it returns a numeric value. |
| `visit_Assign` | Ensures LHS and RHS of assignment are compatible numeric types. |
| `visit_TermBin` | Checks binary operations (e.g., `plus`, `minus`, `eq`) for correct operand types. |
| `visit_BranchIf` and `visit_LoopWhile` | Ensure conditions are numeric or boolean. |
| `visit_Print` | Allows only numeric or string outputs. |
| `visit_Call` | Validates procedure and function calls. |

---

### 🧠 Type Rules Enforced

| Expression | Valid Types | Result Type |
|-------------|--------------|--------------|
| `a plus b` / `a minus b` / `a mult b` / `a div b` | numeric × numeric | numeric |
| `a eq b` / `a > b` | numeric × numeric | boolean |
| `a or b` / `a and b` | boolean × boolean | boolean |
| `not a` | boolean | boolean |
| `neg a` | numeric | numeric |
| `print` | string or numeric | void |

---

### 🧪 Example Command

```bash
python parse_file.py examples/rich.spl --type-check

✅ Expected Output (Pass Case):

Type checking passed ✅

🧩 Example of a Valid SPL Program
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
  while (i > 0) {
    print i;
    i = ( i minus 1 )
  };
  if ( i eq 0 ) { print "done" } else { print "oops" }
}


✅ Type Check Result:

Type checking passed ✅

⚙️ 2. Code Generation (Phase 3)
📘 Overview

The Code Generation phase translates the validated SPL Abstract Syntax Tree (AST) into an intermediate assembly-like representation.

The generated code is linear, labeled, and follows the pseudo-instruction conventions defined in the project specification (e.g., PRINT, IF, GOTO, REM).

🏗️ File Summary

File: src/spl/codegen.py
Class: CodeGenerator

| Component                            | Description                                                           |
| ------------------------------------ | --------------------------------------------------------------------- |
| `generate()`                         | Orchestrates translation from AST to output `.txt` file               |
| `trans_program()`                    | Traverses the `main` algorithm node                                   |
| `trans_algo()`                       | Iterates through instruction sequences                                |
| `trans_assign()`                     | Emits assignment instructions                                         |
| `trans_print()`                      | Emits formatted `PRINT` statements                                    |
| `trans_while()` / `trans_do_until()` | Generates loop control flow with labeled blocks                       |
| `trans_if()`                         | Translates `if/else` constructs with conditional jumps                |
| `trans_term()` / `trans_cond()`      | Converts terms and boolean expressions to string form for code output |
| `emit()`                             | Writes lines to the final target code list                            |


🧾 Example Command
python parse_file.py examples/rich.spl --codegen

Output File: examples/rich.txt

📄 Example Generated Code

Input SPL File:
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
  while (i > 0) {
    print i;
    i = ( i minus 1 )
  };
  if ( i eq 0 ) { print "done" } else { print "oops" }
}

Generated Output (rich.txt):
i = 3
REM INLINE PROC p
PRINT i
REM ENDINLINE PROC p
REM WH1
IF i > 0 THEN WB2
GOTO WE3
REM WB2
PRINT i
i = i - 1
GOTO WH1
REM WE3
IF i = 0 THEN T4
PRINT "oops"
GOTO X5
REM T4
PRINT "done"
REM X5

🧾 Example for richer.spl
python parse_file.py examples/richer.spl --codegen

Generated Output (richer.txt):
x = 2
REM INLINE FUNC inc
STOP
y = n
REM ENDINLINE FUNC inc
REM DO1
REM INLINE PROC echo
PRINT y
REM ENDINLINE PROC echo
y = y - 1
IF y = 0 THEN DO1
IF x > 1 THEN T2
PRINT "bad"
GOTO X3
REM T2
PRINT "ok"
REM X3

🧩 3. Combined Usage

You can run all compiler phases sequentially or selectively using the following flags:

Command	Description
--print-ast	Prints the AST structure (Phase 1)
--check-scopes	Builds and validates the symbol table (Phase 2)
--type-check	Performs semantic type checking (Phase 2.5)
--codegen	Generates target pseudo-assembly (Phase 3)

🧱 Full Pipeline Example
python parse_file.py examples/rich.spl --check-scopes --type-check --codegen

Console Output:
Variable Naming and Function Naming accepted
Type checking passed ✅
Generating target code → examples/rich.txt
Code generation completed successfully.
