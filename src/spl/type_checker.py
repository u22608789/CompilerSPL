# src/spl/type_checker.py
from .astnodes import *
from typing import Dict, List, Optional, Union


class TypeChecker:
    """
    Visitor-based type checker for SPL AST.
    Follows the SPL semantic rules for numeric and boolean types.
    """

    def __init__(self):
        self.scopes: List[Dict[str, str]] = [{}]
        self.current_func_ret_type: Optional[str] = None
        self.procs: Dict[str, int] = {}
        self.funcs: Dict[str, int] = {}
        # self.errors: List[str] = []
        self._call_context: str = "stmt"
        self.errors = []
        self._collect = False

    def report(self, msg: str):
        self.errors.append(msg)

    def get_errors(self):
        return self.errors

    def check_program(self, ast) -> bool:
        self.errors.clear()
        self._collect = True
        try:
            self.visit(ast)
        except Exception as e:
            # top-level fall-through; most errors should be captured below
            self.errors.append(str(e))
        finally:
            self._collect = False
        return len(self.errors) == 0

    # ------------------------
    # Scope management
    # ------------------------
    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def define_var(self, name: str, expected_type: str = "numeric"):
        if name in self.scopes[-1]:
            raise Exception(
                f"Variable '{name}' already declared in this scope")
        self.scopes[-1][name] = expected_type

    def lookup_var(self, name: str) -> str:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Variable '{name}' not declared")

    # ------------------------
    # General visit dispatcher
    # ------------------------
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method implemented")

    # ------------------------
    # Top-level program
    # ------------------------
    def visit_Program(self, node: Program):
        # register globals (numeric)
        for g in node.globals:
            self.define_var(g, "numeric")

        # collect proc/func signatures (arity only; ScopeChecker already
        # enforces name disjointness)
        for p in node.procs:
            self.procs[p.name] = len(p.params)
        for f in node.funcs:
            self.funcs[f.name] = len(f.params)

        # now type-check bodies
        for p in node.procs: self.visit(p)
        for f in node.funcs: self.visit(f)
        self.visit(node.main)

    def visit_ProcDef(self, node: ProcDef):
        self.push_scope()
        for param in node.params:
            self.define_var(param, "numeric")
        self.visit(node.body)
        self.pop_scope()
        return "procedure"

    def visit_FuncDef(self, node: FuncDef):
        self.push_scope()
        for param in node.params:
            self.define_var(param, "numeric")
        self.current_func_ret_type = "numeric"
        self.visit(node.body)
        ret_type = self.visit(node.ret)
        if ret_type != "numeric":
            raise Exception(
                f"Function '{node.name}' must return numeric, got '{ret_type}'")
        self.pop_scope()
        self.current_func_ret_type = None
        return "function"

    # ------------------------
    # Body / Main
    # ------------------------
    def visit_Body(self, node: Body):
        for var in node.locals:
            self.define_var(var, "numeric")
        self.visit(node.algo)

    def visit_Main(self, node: Main):
        for var in node.variables:
            self.define_var(var, "numeric")
        self.visit(node.algo)

    # ------------------------
    # Algorithms (sequence of instructions)
    # ------------------------
    def visit_Algo(self, node: Algo):
        for instr in node.instrs:
            if self._collect:
                try:
                    self.visit(instr)
                except Exception as e:
                    self.errors.append(str(e))
            else:
                self.visit(instr)

    # ------------------------
    # Instructions
    # ------------------------
    def visit_Halt(self, node: Halt):
        return "void"

    def visit_Print(self, node: Print):
        output_node = node.output
        if isinstance(output_node, StringLit):
            return "string"
        typ = self.visit(output_node)
        if typ != "numeric":
            raise Exception(
                f"Print can only output numeric or string values, got '{typ}'")
        return typ


    def visit_Call(self, node: Call):
        # Check argument count (≤ 3) & types
        arity = len(node.args)
        if arity > 3:
            raise Exception(f"Too many arguments: {arity} (max 3)")
        for arg in node.args:
            aty = self.visit(arg)
            if aty != "numeric":
                raise Exception(
                    f"Arguments must be numeric ATOMs, got '{aty}'")

        if self._call_context == "expr":
            # must be a function
            if node.name not in self.funcs:
                raise Exception(f"'{node.name}' is not a function")
            if self.funcs[node.name] != arity:
                raise Exception(
                    f"Function '{node.name}' arity mismatch: expected {self.funcs[node.name]}, got {arity}")
            return "numeric"
        else:
            # statement position: must be a procedure
            if node.name not in self.procs:
                raise Exception(f"'{node.name}' is not a procedure")
            if self.procs[node.name] != arity:
                raise Exception(
                    f"Procedure '{node.name}' arity mismatch: expected {self.procs[node.name]}, got {arity}")
            return "void"

    def visit_Assign(self, node: Assign):
        # LHS must be numeric variable
        lhs_type = self.lookup_var(node.var)
        if lhs_type != "numeric":
            raise Exception(f"Assignment LHS '{node.var}' must be numeric")

        if isinstance(node.rhs, Call):
            # Calling a function in expression position
            old = self._call_context; self._call_context = "expr"
            try:
                rty = self.visit(node.rhs)
            finally:
                self._call_context = old
            if rty != "numeric":
                raise Exception("Function call in assignment must be numeric")
        else:
            rhs_type = self.visit(node.rhs)
            if rhs_type != "numeric":
                raise Exception(f"Assignment RHS must be numeric, got '{rhs_type}'")
        return "numeric"

    def visit_LoopWhile(self, node: LoopWhile):
        cond_type = self.visit(node.cond)
        if cond_type != "boolean":
            raise Exception(f"While condition must be boolean, got '{cond_type}'")
        self.visit(node.body)

    def visit_LoopDoUntil(self, node: LoopDoUntil):
        cond_type = self.visit(node.cond)
        if cond_type != "boolean":
            raise Exception(f"Do-until condition must be boolean, got '{cond_type}'")
        self.visit(node.body)

    def visit_BranchIf(self, node: BranchIf):
        cond_type = self.visit(node.cond)
        if cond_type != "boolean":
            raise Exception(f"If condition must be boolean, got '{cond_type}'")
        self.visit(node.then_)
        if node.else_:
            self.visit(node.else_)

    # ------------------------
    # Terms
    # ------------------------
    def visit_TermAtom(self, node: TermAtom):
        return self.visit(node.atom)

    def visit_TermUn(self, node: TermUn):
        t = self.visit(node.term)
        if node.op == "neg":
            if t != "numeric":
                raise Exception(f"Unary 'neg' requires numeric, got '{t}'")
            return "numeric"
        if node.op == "not":
            if t != "boolean":
                raise Exception(f"Unary 'not' requires boolean, got '{t}'")
            return "boolean"
        raise Exception(f"Unknown unary operator '{node.op}'")

    def visit_TermBin(self, node: TermBin):
        lt = self.visit(node.left)
        rt = self.visit(node.right)
        if node.op in ("plus", "minus", "mult", "div"):
            if lt != "numeric" or rt != "numeric":
                raise Exception(f"Binary '{node.op}' requires numeric operands")
            return "numeric"
        elif node.op in ("or", "and"):
            if lt != "boolean" or rt != "boolean":
                raise Exception(f"Binary '{node.op}' requires boolean operands")
            return "boolean"
        elif node.op in ("eq", ">"):
            if lt != "numeric" or rt != "numeric":
                raise Exception(f"Comparison '{node.op}' requires numeric operands")
            return "boolean"
        else:
            raise Exception(f"Unknown binary operator '{node.op}'")

    # ------------------------
    # Atoms
    # ------------------------
    def visit_VarRef(self, node: VarRef):
        return self.lookup_var(node.name)

    def visit_NumberLit(self, node: NumberLit):
        return "numeric"

    def visit_StringLit(self, node: StringLit):
        return "string"
