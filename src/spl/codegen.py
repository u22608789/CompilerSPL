"""
Code generator for SPL -> target text file

Drop this file into src/spl/codegen.py. It expects the AST node classes described
in your parser (Program, Main, Algo, Assign, Call, LoopWhile, LoopDoUntil,
BranchIf, Print, Halt, TermAtom, TermUn, TermBin, VarRef, NumberLit, StringLit).

This generator follows the translation advice in code-gen.pdf and emits a plain
ASCII .txt file. It tries to be conservative about condition translation: boolean
`and`/`or` are expanded into conditional jumps (cascading), and `not` is
implemented by swapping branches.

Notes / TODOs:
- The generator currently uses `node.name` / `node.var` etc. These attribute
  names assume the AST dataclasses implemented in your parser. If your
  attribute names differ, adjust the accessors accordingly.
- Symbol-table lookups (for internal numbering of variables) are left as a
  simple identity (emit the variable name). If you want to use `symbol_table`,
  import and map names via it (there is a placeholder hook `self.lookup(name)`).
"""

from typing import Optional

# Try to import AST node types for isinstance checks (not required at runtime)
try:
    from .astnodes import (
        Program, Main, Algo, Assign, Call, LoopWhile, LoopDoUntil,
        BranchIf, Print, Halt, TermAtom, TermUn, TermBin, VarRef,
        NumberLit, StringLit
    )
except Exception:
    # If import fails, we still operate with duck typing
    pass


class CodeGenerator:
    def __init__(self, program):
        self.program = program
        self.output = []  # lines of generated code
        self.label_count = 0

    # -------------------- utility helpers --------------------
    def new_label(self, base: str = "L") -> str:
        self.label_count += 1
        return f"{base}{self.label_count}"

    def emit(self, line: str) -> None:
        # strip trailing spaces and avoid emitting empty-lines except where
        # explicit blank lines are desired
        self.output.append(line.rstrip())

    def lookup(self, name: str) -> str:
    
        if not hasattr(self, "symbol_table") or self.symbol_table is None:
            return name

    # Try lookup in main/global scopes
        main_scope = self.symbol_table.base_scopes.get("main")
        global_scope = self.symbol_table.base_scopes.get("global")

        entry = None
        if main_scope:
            entry = self.symbol_table.lookup_chain(main_scope, name)
        if entry is None and global_scope:
            entry = self.symbol_table.lookup_chain(global_scope, name)

    # You can rename variables or mangle them here if needed
        return entry.name if entry else name


    # -------------------- top-level generate --------------------
    def generate(self, filename):
    # Cache procedure/function definitions for inlining
        self.procs = {p.name: p for p in getattr(self.program, "procs", [])}
        self.funcs = {f.name: f for f in getattr(self.program, "funcs", [])}

        self.trans_program(self.program)
        with open(filename, "w", encoding="ascii") as f:
            f.write("\n".join(self.output) + "\n")

    # -------------------- translations --------------------
    def trans_program(self, node) -> None:
        # node is expected to be Program with `main` child
        # We ignore globals/procs/funcs here (they are for inlining later)
        if hasattr(node, "main"):
            main = node.main
            # main has an `algo` attribute per the parser design
            if hasattr(main, "algo"):
                self.trans_algo(main.algo)

    def trans_algo(self, node) -> None:
        # node is Algo containing a sequence of instructions
        for instr in getattr(node, "instrs", getattr(node, "items", [])):
            self.trans_instr(instr)

    def trans_instr(self, node) -> None:
        # Dispatch based on node type (duck-typed)
        typ = type(node).__name__
        if typ == "Halt" or isinstance(node, Halt):
            self.emit("STOP")

        elif typ == "Print" or isinstance(node, Print):
            self.trans_print(node)

        elif typ == "Assign" or isinstance(node, Assign):
            self.trans_assign(node)

        elif typ == "Call" or isinstance(node, Call):
            self.trans_call(node)

        elif typ == "LoopWhile" or isinstance(node, LoopWhile):
            self.trans_while(node)

        elif typ == "LoopDoUntil" or isinstance(node, LoopDoUntil):
            self.trans_do_until(node)

        elif typ == "BranchIf" or isinstance(node, BranchIf):
            self.trans_if(node)

        else:
            # Fallback: try attribute-based detection
            if hasattr(node, "cond") and hasattr(node, "body"):
                # could be a while-like node
                self.trans_while(node)
            else:
                raise ValueError(f"Unknown instruction node type: {typ}")

    # -------------------- print --------------------
    def trans_print(self, node) -> None:
        # node.value could be StringLit, NumberLit, VarRef, or an Atom wrapper
        val = getattr(node, "value", None) or getattr(node, "arg", None)
        # unwrap if it's a TermAtom wrapper
        if val is None and hasattr(node, "atom"):
            val = node.atom

        if isinstance(val, StringLit) or type(val).__name__ == "StringLit":
            s = getattr(val, "value", None) or getattr(val, "lexeme", None)
            self.emit(f'PRINT "{s}"')

        elif isinstance(val, NumberLit) or type(val).__name__ == "NumberLit":
            self.emit(f"PRINT {getattr(val, 'value', getattr(val, 'lexeme', '0'))}")

        elif isinstance(val, VarRef) or type(val).__name__ == "VarRef":
            name = getattr(val, "name", getattr(val, "lexeme", None))
            self.emit(f"PRINT {self.lookup(name)}")

        else:
            # Could be a Term -> evaluate to expression string
            expr = self.trans_term(val)
            self.emit(f"PRINT {expr}")

    # -------------------- assignment & calls --------------------
    def trans_assign(self, node) -> None:
        # node.var (VarRef) = node.rhs (Term or Call)
        lhs = getattr(node, "var", None) or getattr(node, "target", None)
        rhs = getattr(node, "rhs", None) or getattr(node, "expr", None)
        lhs_name = getattr(lhs, "name", lhs) if lhs is not None else "_"

        if rhs is None:
            raise ValueError("Assign node missing rhs")

        # function-call assignment
        if type(rhs).__name__ == "Call" or isinstance(rhs, Call):
            name = getattr(rhs, "name", rhs)
            args = getattr(rhs, "args", [])
            args_txt = " ".join(self.atom_to_text(a) for a in args)
            self.emit(f"{self.lookup(lhs_name)} = CALL {name} {args_txt}".strip())
        else:
            rhs_txt = self.trans_term(rhs)
            self.emit(f"{self.lookup(lhs_name)} = {rhs_txt}")

    def trans_call(self, node):
        name = getattr(node, "name", None)
        args = getattr(node, "args", [])

        # Inline known procs
        if hasattr(self, "procs") and name in self.procs:
            proc_def = self.procs[name]
            self.emit(f"REM INLINE PROC {name}")
            self.trans_algo(proc_def.body.algo)
            self.emit(f"REM ENDINLINE PROC {name}")
            return

        # Inline known funcs
        if hasattr(self, "funcs") and name in self.funcs:
            func_def = self.funcs[name]
            self.emit(f"REM INLINE FUNC {name}")
            self.trans_algo(func_def.body.algo)
            self.emit(f"{func_def.body.locals[0]} = {self.trans_atom(func_def.ret)}")
            self.emit(f"REM ENDINLINE FUNC {name}")
            return

        # Fallback normal CALL
        args_txt = " ".join(self.atom_to_text(a) for a in args)
        self.emit(f"CALL {name} {args_txt}".strip())


    # -------------------- terms & atoms --------------------
    def atom_to_text(self, atom) -> str:
        if atom is None:
            return ""
        if isinstance(atom, VarRef) or type(atom).__name__ == "VarRef":
            return self.lookup(getattr(atom, "name", getattr(atom, "lexeme", "")))
        if isinstance(atom, NumberLit) or type(atom).__name__ == "NumberLit":
            return str(getattr(atom, "value", getattr(atom, "lexeme", "0")))
        if isinstance(atom, StringLit) or type(atom).__name__ == "StringLit":
            return f'"{getattr(atom, "value", getattr(atom, "lexeme", ""))}"'
        # If user passed a Term node directly, evaluate it
        return self.trans_term(atom)

    def trans_term(self, node) -> str:
        if node is None:
            return ""
        typ = type(node).__name__
        if typ == "TermAtom" or isinstance(node, TermAtom):
            a = getattr(node, "atom", node)
            return self.atom_to_text(a)

        if typ == "TermUn" or isinstance(node, TermUn):
            op = getattr(node, "op", getattr(node, "unop", None))
            term = getattr(node, "term", None)
            if op == "neg":
                # unary minus
                return f"-{self.trans_term(term)}"
            elif op == "not":
                # "not" should be handled at condition-level; as a string we
                # represent it with a NOT(...) wrapper
                return f"NOT({self.trans_term(term)})"
            else:
                return f"{op}({self.trans_term(term)})"

        if typ == "TermBin" or isinstance(node, TermBin):
            left = getattr(node, "left", None)
            right = getattr(node, "right", None)
            op = getattr(node, "op", getattr(node, "binop", None))
            op_map = {
                "eq": "=", "=": "=",
                ">": ">", "GT": ">", "gt": ">",
                "plus": "+", "minus": "-", "mult": "*", "div": "/",
            }
            if op in ("or", "and"):
                # produce a parenthesized textual form for printing; actual
                # control-flow expansion is done in trans_cond when used as a
                # condition.
                return f"({self.trans_term(left)} {op} {self.trans_term(right)})"

            op_txt = op_map.get(op, op)
            return f"{self.trans_term(left)} {op_txt} {self.trans_term(right)}"

        # Fallback: try common attributes
        if hasattr(node, "value"):
            return str(getattr(node, "value"))

        raise ValueError(f"Unknown term node: {node} / {typ}")

    # -------------------- condition translation (cascading for and/or) --------------------
    def trans_cond(self, node, true_label: str, false_label: Optional[str] = None) -> None:
        """
        Emit code that transfers control to `true_label` when `node` evaluates as true.
        If `false_label` is provided, ensure that if the condition is false execution
        ends up by jumping to `false_label` (typically we explicitly emit a GOTO
        after calling trans_cond). For simple relational ops we emit a single
        `IF left op right THEN true_label` and let the caller emit a GOTO false_label
        if needed.
        """
        # Handle unary not: swap true/false
        if type(node).__name__ == "TermUn" or isinstance(node, TermUn):
            op = getattr(node, "op", getattr(node, "unop", None))
            if op == "not":
                # swap the labels
                self.trans_cond(getattr(node, "term", None), false_label or self.new_label("F"), true_label)
                return

        # Binary case
        if type(node).__name__ == "TermBin" or isinstance(node, TermBin):
            op = getattr(node, "op", getattr(node, "binop", None))
            left = getattr(node, "left", None)
            right = getattr(node, "right", None)

            if op == "or":
                # if left true -> true_label; else if right true -> true_label
                mid = self.new_label("OR")
                # check left
                self.trans_cond(left, true_label, mid)
                # mark mid and check right
                self.emit(f"REM {mid}")
                self.trans_cond(right, true_label, false_label)
                return

            if op == "and":
                # if left false -> false_label; else check right
                mid = self.new_label("AND")
                # if left true continue to mid, else goto false
                self.trans_cond(left, mid, false_label)
                self.emit(f"REM {mid}")
                self.trans_cond(right, true_label, false_label)
                return

            # relational / simple boolean ops
            if op in ("eq", "=", ">", "GT", "gt"):
                left_txt = self.trans_term(left)
                right_txt = self.trans_term(right)
                op_map = {"eq": "=", "=": "=", ">": ">", "GT": ">"}
                op_txt = op_map.get(op, op)
                self.emit(f"IF {left_txt} {op_txt} {right_txt} THEN {true_label}")
                return

        # Fallback: evaluate term and compare to 0/non-empty (we simply emit IF term THEN true_label)
        cond_txt = self.trans_term(node)
        self.emit(f"IF {cond_txt} THEN {true_label}")

    # -------------------- if / branch --------------------
    def trans_if(self, node) -> None:
        # node.cond, node.then_, node.else_ (else_ may be None)
        cond = getattr(node, "cond", getattr(node, "condition", None))
        then_algo = getattr(node, "then_", None) or getattr(node, "then", None)
        else_algo = getattr(node, "else_", None) or getattr(node, "else", None)

        label_t = self.new_label("T")
        label_exit = self.new_label("X")

        # Per code-gen.pdf: emit IF cond THEN labelT
        self.trans_cond(cond, label_t)

        # generate else (or fallthrough) code first
        if else_algo:
            self.trans_algo(else_algo)

        # jump to exit after else
        self.emit(f"GOTO {label_exit}")

        # then label and then-code
        self.emit(f"REM {label_t}")
        self.trans_algo(then_algo)

        # exit label
        self.emit(f"REM {label_exit}")

    # -------------------- loops --------------------
    def trans_while(self, node) -> None:
        # node.cond, node.body
        cond = getattr(node, "cond", getattr(node, "condition", None))
        body = getattr(node, "body", None)

        label_start = self.new_label("WH")
        label_body = self.new_label("WB")
        label_exit = self.new_label("WE")

        # loop top
        self.emit(f"REM {label_start}")
        # if cond then go to body, else fall through to GOTO exit
        self.trans_cond(cond, label_body)
        self.emit(f"GOTO {label_exit}")

        self.emit(f"REM {label_body}")
        self.trans_algo(body)
        # go back to start
        self.emit(f"GOTO {label_start}")
        self.emit(f"REM {label_exit}")

    def trans_do_until(self, node) -> None:
        # node.body, node.cond
        cond = getattr(node, "cond", getattr(node, "condition", None))
        body = getattr(node, "body", None)

        label_do = self.new_label("DO")
        self.emit(f"REM {label_do}")
        self.trans_algo(body)
        # if cond then jump back to start (do-while semantics in pdf)
        self.trans_cond(cond, label_do)


# -------------------- standalone helper --------------------
if __name__ == "__main__":
    print("This module implements CodeGenerator. Import and call CodeGenerator(program).generate(path)")
