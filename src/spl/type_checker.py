# src/spl/type_checker.py
from .astnodes import *
from typing import Dict, List, Optional, Union

class TypeChecker:
    """
    Visitor-based type checker for SPL AST.
    Follows the SPL semantic rules for numeric and boolean types.
    """

    def __init__(self):
        # Simple symbol table stack for locals/globals
        self.scopes: List[Dict[str, str]] = [{}]  # top of stack is current scope
        self.current_func_ret_type: Optional[str] = None

    # ------------------------
    # Scope management
    # ------------------------
    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def define_var(self, name: str, expected_type: str = "numeric"):
        if name in self.scopes[-1]:
            raise Exception(f"Variable '{name}' already declared in this scope")
        self.scopes[-1][name] = expected_type

    def lookup_var(self, name: str) -> str:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Undeclared variable '{name}'")

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
        # Add globals to current scope
        for g in node.globals:
            self.define_var(g, "numeric")

        # Visit procedures
        for p in node.procs:
            self.visit(p)

        # Visit functions
        for f in node.funcs:
            self.visit(f)

        # Visit main program
        self.visit(node.main)

    # ------------------------
    # Procedure / Function
    # ------------------------
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
            raise Exception(f"Function '{node.name}' must return numeric, got '{ret_type}'")
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
            raise Exception(f"Print can only output numeric or string values, got '{typ}'")
        return typ

    def visit_Call(self, node: Call):
        # Calls are allowed; we assume functions are numeric and procedures void
        for arg in node.args:
            self.visit(arg)
        return "numeric"  # for function calls in expressions

    def visit_Assign(self, node: Assign):
        if isinstance(node.rhs, Call):
            self.visit(node.rhs)
        else:
            rhs_type = self.visit(node.rhs)
            if rhs_type != "numeric":
                raise Exception(f"Assignment RHS must be numeric, got '{rhs_type}'")
        # LHS must be numeric
        lhs_type = self.lookup_var(node.var)
        if lhs_type != "numeric":
            raise Exception(f"Assignment LHS '{node.var}' must be numeric")
        return "numeric"

    def visit_LoopWhile(self, node: LoopWhile):
        cond_type = self.visit(node.cond)
        if cond_type not in ("numeric", "boolean"):
            raise Exception(f"LoopWhile condition must be numeric or boolean, got '{cond_type}'")
        self.visit(node.body)

    def visit_LoopDoUntil(self, node: LoopDoUntil):
        cond_type = self.visit(node.cond)
        if cond_type not in ("numeric", "boolean"):
            raise Exception(f"LoopDoUntil condition must be numeric or boolean, got '{cond_type}'")
        self.visit(node.body)

    def visit_BranchIf(self, node: BranchIf):
        cond_type = self.visit(node.cond)
        if cond_type not in ("numeric", "boolean"):
            raise Exception(f"If condition must be numeric or boolean, got '{cond_type}'")
        self.visit(node.then_)
        if node.else_:
            self.visit(node.else_)

    # ------------------------
    # Terms
    # ------------------------
    def visit_TermAtom(self, node: TermAtom):
        return self.visit(node.atom)

    def visit_TermUn(self, node: TermUn):
        term_type = self.visit(node.term)
        if node.op == "neg" and term_type != "numeric":
            raise Exception(f"Unary 'neg' requires numeric, got '{term_type}'")
        if node.op == "not" and term_type != "boolean":
            raise Exception(f"Unary 'not' requires boolean, got '{term_type}'")
        return term_type

    def visit_TermBin(self, node: TermBin):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)
        if node.op in ("plus", "minus", "mult", "div"):
            if left_type != "numeric" or right_type != "numeric":
                raise Exception(f"Binary '{node.op}' requires numeric operands")
            return "numeric"
        elif node.op in ("or", "and"):
            if left_type != "boolean" or right_type != "boolean":
                raise Exception(f"Binary '{node.op}' requires boolean operands")
            return "boolean"
        elif node.op in ("eq", ">"):
            if left_type != "numeric" or right_type != "numeric":
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
