"""
AST Node ID Assignment Module

Assigns unique sequential IDs to every node in the AST.
These IDs are essential for Phase 2's symbol table, enabling:
- Symbol table entries to reference declaration nodes (decl_node_id)
- Variable uses to link back to their declarations
- Diagnostics to reference specific nodes
- Later phases to track nodes through compilation

Usage:
    from spl.parser import Parser
    from spl.ast_ids import assign_ids
    
    ast = Parser(source).parse()
    assign_ids(ast)  # All nodes now have unique node_ids
"""

from typing import Any
from .astnodes import *


class ASTIDAssigner:
    """
    Visitor that traverses the entire AST and assigns unique sequential IDs
    to every node, starting from 1.
    """
    
    def __init__(self):
        self.next_id = 1
    
    def assign_id(self, node: Any) -> None:
        """Assign an ID to a node if it doesn't have one yet."""
        if hasattr(node, 'node_id'):
            if node.node_id == -1:  # Only assign if not yet assigned
                node.node_id = self.next_id
                self.next_id += 1
    
    def visit_program(self, node: Program) -> None:
        """Visit the root Program node and all its children."""
        self.assign_id(node)
        
        # Global variables are just strings (no node objects)
        # Visit procedure definitions
        for pdef in node.procs:
            self.visit_procdef(pdef)
        
        # Visit function definitions
        for fdef in node.funcs:
            self.visit_funcdef(fdef)
        
        # Visit main
        self.visit_main(node.main)
    
    def visit_procdef(self, node: ProcDef) -> None:
        """Visit a procedure definition."""
        self.assign_id(node)
        # params are just strings
        self.visit_body(node.body)
    
    def visit_funcdef(self, node: FuncDef) -> None:
        """Visit a function definition."""
        self.assign_id(node)
        # params are just strings
        self.visit_body(node.body)
        self.visit_atom(node.ret)
    
    def visit_body(self, node: Body) -> None:
        """Visit a procedure/function body."""
        self.assign_id(node)
        # locals are just strings
        self.visit_algo(node.algo)
    
    def visit_main(self, node: Main) -> None:
        """Visit the main program block."""
        self.assign_id(node)
        # variables are just strings
        self.visit_algo(node.algo)
    
    def visit_algo(self, node: Algo) -> None:
        """Visit an algorithm (sequence of instructions)."""
        self.assign_id(node)
        for instr in node.instrs:
            self.visit_instruction(instr)
    
    def visit_instruction(self, node: Any) -> None:
        """Visit any instruction node."""
        self.assign_id(node)
        
        if isinstance(node, Halt):
            pass  # No children
        
        elif isinstance(node, Print):
            self.visit_output(node.output)
        
        elif isinstance(node, Call):
            # name is just a string
            for arg in node.args:
                self.visit_atom(arg)
        
        elif isinstance(node, Assign):
            # var is just a string
            if isinstance(node.rhs, Call):
                self.visit_instruction(node.rhs)  # Call is also an instruction
            else:
                self.visit_term(node.rhs)
        
        elif isinstance(node, LoopWhile):
            self.visit_term(node.cond)
            self.visit_algo(node.body)
        
        elif isinstance(node, LoopDoUntil):
            self.visit_algo(node.body)
            self.visit_term(node.cond)
        
        elif isinstance(node, BranchIf):
            self.visit_term(node.cond)
            self.visit_algo(node.then_)
            if node.else_:
                self.visit_algo(node.else_)
    
    def visit_output(self, node: Any) -> None:
        """Visit an output node (for print statements)."""
        if isinstance(node, (VarRef, NumberLit)):
            self.visit_atom(node)
        elif isinstance(node, StringLit):
            self.assign_id(node)
    
    def visit_atom(self, node: Any) -> None:
        """Visit an atomic value (variable reference or number literal)."""
        self.assign_id(node)
    
    def visit_term(self, node: Any) -> None:
        """Visit a term (expression) node."""
        self.assign_id(node)
        
        if isinstance(node, TermAtom):
            self.visit_atom(node.atom)
        
        elif isinstance(node, TermUn):
            # op is just a string
            self.visit_term(node.term)
        
        elif isinstance(node, TermBin):
            self.visit_term(node.left)
            # op is just a string
            self.visit_term(node.right)


def assign_ids(ast: Program) -> Program:
    """
    Assign unique IDs to all nodes in the AST tree.
    
    Args:
        ast: The root Program node of the AST
    
    Returns:
        The same ast object (modified in place) for convenience
    
    Example:
        >>> from spl.parser import Parser
        >>> ast = Parser(source).parse()
        >>> assign_ids(ast)
        >>> # Now all nodes have unique node_id values >= 1
    """
    assigner = ASTIDAssigner()
    assigner.visit_program(ast)
    return ast


def count_nodes(node: Any) -> int:
    """
    Count total number of nodes in an AST subtree.
    Useful for verifying that assign_ids() visited everything.
    
    Args:
        node: Root node of subtree to count
    
    Returns:
        Total number of nodes in the subtree
    """
    count = 1  # Count this node
    
    if isinstance(node, Program):
        count += sum(count_nodes(p) for p in node.procs)
        count += sum(count_nodes(f) for f in node.funcs)
        count += count_nodes(node.main)
    
    elif isinstance(node, (ProcDef, FuncDef)):
        count += count_nodes(node.body)
        if isinstance(node, FuncDef):
            count += count_nodes(node.ret)
    
    elif isinstance(node, Body):
        count += count_nodes(node.algo)
    
    elif isinstance(node, Main):
        count += count_nodes(node.algo)
    
    elif isinstance(node, Algo):
        count += sum(count_nodes(i) for i in node.instrs)
    
    elif isinstance(node, Print):
        count += count_nodes(node.output)
    
    elif isinstance(node, Call):
        count += sum(count_nodes(a) for a in node.args)
    
    elif isinstance(node, Assign):
        count += count_nodes(node.rhs)
    
    elif isinstance(node, (LoopWhile, LoopDoUntil)):
        count += count_nodes(node.cond)
        count += count_nodes(node.body)
    
    elif isinstance(node, BranchIf):
        count += count_nodes(node.cond)
        count += count_nodes(node.then_)
        if node.else_:
            count += count_nodes(node.else_)
    
    elif isinstance(node, TermAtom):
        count += count_nodes(node.atom)
    
    elif isinstance(node, TermUn):
        count += count_nodes(node.term)
    
    elif isinstance(node, TermBin):
        count += count_nodes(node.left)
        count += count_nodes(node.right)
    
    # Leaf nodes (VarRef, NumberLit, StringLit, Halt) have no children
    
    return count


def get_all_node_ids(node: Any) -> list[int]:
    """
    Collect all node_ids from an AST subtree.
    Useful for debugging and verification.
    
    Args:
        node: Root node of subtree
    
    Returns:
        List of all node_ids in the subtree
    """
    ids = []
    
    def collect(n):
        if hasattr(n, 'node_id'):
            ids.append(n.node_id)
        
        # Recurse into children
        if isinstance(n, Program):
            for p in n.procs:
                collect(p)
            for f in n.funcs:
                collect(f)
            collect(n.main)
        
        elif isinstance(n, (ProcDef, FuncDef)):
            collect(n.body)
            if isinstance(n, FuncDef):
                collect(n.ret)
        
        elif isinstance(n, (Body, Main)):
            collect(n.algo)
        
        elif isinstance(n, Algo):
            for i in n.instrs:
                collect(i)
        
        elif isinstance(n, Print):
            collect(n.output)
        
        elif isinstance(n, Call):
            for a in n.args:
                collect(a)
        
        elif isinstance(n, Assign):
            collect(n.rhs)
        
        elif isinstance(n, (LoopWhile, LoopDoUntil)):
            collect(n.cond)
            collect(n.body)
        
        elif isinstance(n, BranchIf):
            collect(n.cond)
            collect(n.then_)
            if n.else_:
                collect(n.else_)
        
        elif isinstance(n, TermAtom):
            collect(n.atom)
        
        elif isinstance(n, TermUn):
            collect(n.term)
        
        elif isinstance(n, TermBin):
            collect(n.left)
            collect(n.right)
    
    collect(node)
    return ids


def print_node_ids(node: Any, indent: int = 0) -> None:
    """
    Debug helper: print the AST with node IDs visible.
    Useful for verifying that IDs are assigned correctly.
    
    Args:
        node: Root node to print
        indent: Current indentation level (for recursive calls)
    """
    prefix = "  " * indent
    node_id = getattr(node, 'node_id', -1)
    node_type = type(node).__name__
    print(f"{prefix}{node_type} [id={node_id}]")
    
    if isinstance(node, Program):
        print(f"{prefix}  globals: {node.globals}")
        for p in node.procs:
            print_node_ids(p, indent + 1)
        for f in node.funcs:
            print_node_ids(f, indent + 1)
        print_node_ids(node.main, indent + 1)
    
    elif isinstance(node, (ProcDef, FuncDef)):
        print(f"{prefix}  name: {node.name}")
        print(f"{prefix}  params: {node.params}")
        print_node_ids(node.body, indent + 1)
        if isinstance(node, FuncDef):
            print(f"{prefix}  return:")
            print_node_ids(node.ret, indent + 2)
    
    elif isinstance(node, Body):
        print(f"{prefix}  locals: {node.locals}")
        print_node_ids(node.algo, indent + 1)
    
    elif isinstance(node, Main):
        print(f"{prefix}  variables: {node.variables}")
        print_node_ids(node.algo, indent + 1)
    
    elif isinstance(node, Algo):
        for i in node.instrs:
            print_node_ids(i, indent + 1)
    
    elif isinstance(node, Halt):
        pass  # No children
    
    elif isinstance(node, Print):
        print_node_ids(node.output, indent + 1)
    
    elif isinstance(node, Call):
        print(f"{prefix}  name: {node.name}")
        for arg in node.args:
            print_node_ids(arg, indent + 1)
    
    elif isinstance(node, Assign):
        print(f"{prefix}  var: {node.var}")
        print(f"{prefix}  rhs:")
        print_node_ids(node.rhs, indent + 1)
    
    elif isinstance(node, LoopWhile):
        print(f"{prefix}  cond:")
        print_node_ids(node.cond, indent + 1)
        print(f"{prefix}  body:")
        print_node_ids(node.body, indent + 1)
    
    elif isinstance(node, LoopDoUntil):
        print(f"{prefix}  body:")
        print_node_ids(node.body, indent + 1)
        print(f"{prefix}  cond:")
        print_node_ids(node.cond, indent + 1)
    
    elif isinstance(node, BranchIf):
        print(f"{prefix}  cond:")
        print_node_ids(node.cond, indent + 1)
        print(f"{prefix}  then:")
        print_node_ids(node.then_, indent + 1)
        if node.else_:
            print(f"{prefix}  else:")
            print_node_ids(node.else_, indent + 1)
    
    elif isinstance(node, (VarRef, NumberLit, StringLit)):
        val = node.name if isinstance(node, VarRef) else node.value
        print(f"{prefix}  value: {val}")
    
    elif isinstance(node, TermAtom):
        print_node_ids(node.atom, indent + 1)
    
    elif isinstance(node, TermUn):
        print(f"{prefix}  op: {node.op}")
        print_node_ids(node.term, indent + 1)
    
    elif isinstance(node, TermBin):
        print(f"{prefix}  left:")
        print_node_ids(node.left, indent + 1)
        print(f"{prefix}  op: {node.op}")
        print(f"{prefix}  right:")
        print_node_ids(node.right, indent + 1)


# ============================================================================
# Smoke test
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("AST Node ID Assignment - Smoke Test")
    print("=" * 70)
    print()
    print("This module assigns unique IDs to all AST nodes.")
    print("To test it properly, you need a parsed AST.")
    print()
    print("Usage example:")
    print()
    print("    from spl.parser import Parser")
    print("    from spl.ast_ids import assign_ids, count_nodes, get_all_node_ids")
    print()
    print("    source = open('example.spl').read()")
    print("    ast = Parser(source).parse()")
    print("    assign_ids(ast)")
    print()
    print("    total = count_nodes(ast)")
    print("    ids = get_all_node_ids(ast)")
    print("    print(f'Assigned {len(ids)} unique IDs to {total} nodes')")
    print()
    print("=" * 70)