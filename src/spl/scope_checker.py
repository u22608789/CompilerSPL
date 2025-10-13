# from typing import Dict, List, Optional, Set
# from .symbol_table import SymbolTable, SymbolTableEntry, create_base_scopes
# from .astnodes import *


# class ScopeChecker:
#     """
#     Main scope checking driver.
    
#     Responsibilities:
#     - Build the scope tree
#     - Collect declarations (filled in by M2)
#     - Resolve variable uses (filled in by M3)
#     - Enforce scoping rules and report errors
    
#     Current status (M1 deliverable):
#     - Builds the base scope hierarchy
#     - Provides structure for M2/M3 to fill in
#     """
    
#     def __init__(self, ast: Program):
#         """
#         Initialize the checker with an AST that has node_ids assigned.
        
#         Args:
#             ast: Root Program node with node_ids already assigned
#         """
#         self.ast = ast
#         self.symbol_table = SymbolTable()
        
#         # Store scope IDs for easy reference
#         self.base_scopes: Dict[str, int] = {}
        
#         # Map proc/func names to their local scope IDs (filled during decl pass)
#         self.local_scopes: Dict[str, int] = {}  # name → scope_id
        
#         # Track errors/diagnostics (to be implemented by M4)
#         self.diagnostics: List[str] = []
    
#     def check(self) -> SymbolTable:
#         """
#         Main entry point: run all checking passes.
        
#         Returns:
#             The completed symbol table
        
#         Raises:
#             Exception with diagnostic messages if errors are found
#         """
#         # Step 1: Build base scope hierarchy (M1 - DONE)
#         self._build_base_scopes()
        
#         # Step 2: Collect top-level declarations (M2 - TODO)
#         # self._collect_global_declarations()
#         # self._collect_proc_declarations()
#         # self._collect_func_declarations()
        
#         # Step 3: Build local scopes for each proc/func (M2 - TODO)
#         # self._build_local_scopes()
        
#         # Step 4: Resolve variable uses (M3 - TODO)
#         # self._resolve_uses()
        
#         # Step 5: Report errors if any (M4 - TODO)
#         # if self.diagnostics:
#         #     raise Exception("\n".join(self.diagnostics))
        
#         return self.symbol_table
    
#     def _build_base_scopes(self) -> None:
#         """
#         Create the standard SPL scope hierarchy.
        
#         This is M1's core deliverable (Step 3):
#             Everywhere (root)
#             ├── Global (for global variables)
#             ├── Procedure (for procedure names)
#             ├── Function (for function names)
#             └── Main (for main block variables)
        
#         Why this structure?
#         - SPL requires that variable names cannot clash with proc/func names
#         - Having separate 'Procedure' and 'Function' scopes (both under Everywhere)
#           allows us to easily check for cross-category clashes
#         - Main is a sibling to Global because main vars only see globals, not
#           other procs/funcs' internals
#         """
#         self.base_scopes = create_base_scopes(self.symbol_table)
        
#         # For debugging: print what we created
#         print("Base scope hierarchy created:")
#         for name, scope_id in self.base_scopes.items():
#             scope = self.symbol_table.get_scope(scope_id)
#             parent = f"parent=#{scope.parent_id}" if scope.parent_id else "root"
#             print(f"  {name:12} → Scope #{scope_id:2} ({parent})")
    
#     # ===================================================================
#     # DECLARATION PASSES (M2's responsibility)
#     # These are stubs showing the intended structure
#     # ===================================================================
    
#     def _collect_global_declarations(self) -> None:
#         """
#         Insert global variables into the Global scope.
        
#         M2 TODO:
#         - Iterate over self.ast.globals (list of variable names)
#         - For each name, create a SymbolTableEntry with kind='var'
#         - Use node_id from... where? Globals are just strings in current AST!
#           (This might need adjustment - M2 will figure out best approach)
#         - Call self.symbol_table.declare(self.base_scopes['global'], entry)
#         - Catch ValueError for duplicates and add to self.diagnostics
        
#         Also enforce: no global variable can have same name as any proc/func
#         (cross-category clash check at Everywhere level)
#         """
#         pass
    
#     def _collect_proc_declarations(self) -> None:
#         """
#         Insert procedure names into the Procedure scope.
        
#         M2 TODO:
#         - Iterate over self.ast.procs
#         - For each ProcDef, create entry with kind='proc'
#         - Use pdef.node_id for decl_node_id
#         - Check for duplicates within Procedure scope
#         - Check for clash with func names (both are under Everywhere)
#         """
#         pass
    
#     def _collect_func_declarations(self) -> None:
#         """
#         Insert function names into the Function scope.
        
#         M2 TODO:
#         - Similar to _collect_proc_declarations
#         - Iterate over self.ast.funcs
#         - Create entries with kind='func'
#         """
#         pass
    
#     def _build_local_scopes(self) -> None:
#         """
#         For each proc/func definition, create a Local scope and populate it.
        
#         M2 TODO:
#         - For each ProcDef in self.ast.procs:
#           - Create a new Local scope with parent = Global scope
#           - Insert parameters (kind='param')
#           - Insert locals from body (kind='var')
#           - Enforce: no duplicate params, no duplicate locals, locals cannot shadow params
#         - Repeat for each FuncDef
#         - Store the local scope ID in self.local_scopes[def_name] for M3's use
        
#         Also handle Main:
#         - Main's variables go directly into the Main scope
#         - No params, just locals
#         """
#         pass
    
#     # ===================================================================
#     # RESOLUTION PASS (M3's responsibility)
#     # ===================================================================
    
#     def _resolve_uses(self) -> None:
#         """
#         Walk all ALGO blocks and resolve each variable use to its declaration.
        
#         M3 TODO:
#         - For each ProcDef, call _resolve_algo(pdef.body.algo, local_scope_id)
#         - For each FuncDef, call _resolve_algo(fdef.body.algo, local_scope_id)
#         - For Main, call _resolve_algo(main.algo, main_scope_id)
        
#         _resolve_algo should recursively walk instructions and resolve any
#         VarRef nodes, setting their .resolved field and checking for undeclared vars
#         """
#         pass
    
#     def _resolve_algo(self, algo: Algo, scope_id: int) -> None:
#         """
#         Resolve all variable uses within an algorithm block.
        
#         M3 TODO:
#         - Walk algo.instrs
#         - For each instruction, find VarRef nodes (in assigns, prints, terms, etc.)
#         - For each VarRef:
#           - Look up the name using self.symbol_table.lookup_chain(scope_id, name)
#           - If found: set varref.resolved = entry
#           - If not found: add diagnostic about undeclared variable
#         """
#         pass


# def check_scopes(ast: Program) -> SymbolTable:
#     """
#     Convenience function: run scope checking on an AST.
    
#     Args:
#         ast: Program node with node_ids assigned
    
#     Returns:
#         Completed SymbolTable
    
#     Example:
#         from spl.parser import Parser
#         from spl.ast_ids import assign_ids
#         from spl.scope_checker import check_scopes
        
#         text = open('example.spl').read()
#         ast = Parser(text).parse()
#         assign_ids(ast)
#         st = check_scopes(ast)
#         print(st.pretty_print())
#     """
#     checker = ScopeChecker(ast)
#     return checker.check()


# # Quick demonstration
# if __name__ == '__main__':
#     # This won't work standalone since we need a full AST,
#     # but shows the intended usage pattern
#     print("Scope Checker Module")
#     print("=" * 60)
#     print("This module provides the ScopeChecker class for Phase 2.")
#     print("Use check_scopes(ast) after parsing and assigning node IDs.")
#     print()
#     print("Current status (M1 deliverable):")
#     print("  ✓ Base scope hierarchy creation")
#     print("  ⧗ Declaration collection (M2)")
#     print("  ⧗ Variable resolution (M3)")
#     print("  ⧗ Error reporting (M4)")
#     print("=" * 60)


"""
Scope Checker Module for SPL Compiler (Phase 2)

This module walks the AST and builds the symbol table, enforcing SPL's
name resolution and scoping rules.

The checker operates in multiple passes:
1. Build the base scope hierarchy (Everywhere → Global/Procedure/Function/Main) [M1 - DONE]
2. Collect top-level declarations (globals, proc names, func names) [M2 - TODO]
3. For each proc/func, create Local scopes and collect params/locals [M2 - TODO]
4. Resolve all variable uses in ALGO blocks [M3 - TODO]
"""

from typing import Dict, List, Optional
from .symbol_table import SymbolTable, SymbolTableEntry, create_base_scopes
from .astnodes import *


class ScopeChecker:
    """
    Main scope checking driver.
    
    Current status:
    - M1: Base scope hierarchy ✓
    - M2: Declaration collection (TODO)
    - M3: Variable use resolution (TODO)
    - M4: Error reporting (TODO)
    """
    
    def __init__(self, ast: Program):
        """
        Initialize the checker with an AST that has node_ids assigned.
        
        Args:
            ast: Root Program node with node_ids already assigned
        """
        self.ast = ast
        self.symbol_table = SymbolTable()
        
        # Map proc/func names to their local scope IDs (filled during decl pass)
        self.local_scopes: Dict[str, int] = {}
        
        # Track errors/diagnostics (to be implemented by M4)
        self.diagnostics: List[str] = []
    
    def check(self) -> SymbolTable:
        """
        Main entry point: run all checking passes.
        
        Returns:
            The completed symbol table
        
        Raises:
            Exception with diagnostic messages if errors are found
        """
        # Step 1: Build base scope hierarchy (M1 - DONE)
        self._build_base_scopes()
        
        # Step 2: Collect top-level declarations (M2 - TODO)
        # self._collect_global_declarations()
        # self._collect_proc_declarations()
        # self._collect_func_declarations()
        # self._collect_main_variables()
        
        # Step 3: Build local scopes for each proc/func (M2 - TODO)
        # self._build_local_scopes()
        
        # Step 4: Resolve variable uses (M3 - TODO)
        # self._resolve_uses()
        
        # Step 5: Report errors if any (M4 - TODO)
        # if self.diagnostics:
        #     raise Exception("\n".join(self.diagnostics))
        
        return self.symbol_table
    
    # ========================================================================
    # M1: BASE SCOPE HIERARCHY (COMPLETE)
    # ========================================================================
    
    def _build_base_scopes(self) -> None:
        """
        Create the standard SPL scope hierarchy:
            Everywhere (root)
            ├── Global (for global variables)
            ├── Procedure (for procedure names)
            ├── Function (for function names)
            └── Main (for main block variables)
        
        Why this structure?
        - SPL requires that variable names cannot clash with proc/func names
        - Having separate 'Procedure' and 'Function' scopes (both under Everywhere)
          allows us to easily check for cross-category clashes
        - Main is a sibling to Global because main vars only see globals, not
          other procs/funcs' internals
        """
        create_base_scopes(self.symbol_table)
    
    # ========================================================================
    # M2: DECLARATION PASSES (TODO)
    # ========================================================================
    
    def _collect_global_declarations(self) -> None:
        """
        Insert global variables into the Global scope.
        
        M2 TODO:
        1. Iterate over self.ast.globals (list of variable names)
        2. For each name, create a SymbolTableEntry with:
           - kind='var'
           - scope_id=self.symbol_table.base_scopes['global']
           - decl_node_id=??? (globals are just strings, no node!)
             Option A: Use Program node_id as proxy
             Option B: Extend AST to have VarDecl nodes
             For now, can use Program.node_id + index
        3. Call self.symbol_table.declare(global_scope_id, entry)
        4. Catch ValueError for duplicates and add to self.diagnostics
        
        Example:
            global_id = self.symbol_table.base_scopes['global']
            for idx, name in enumerate(self.ast.globals):
                entry = SymbolTableEntry(
                    name=name,
                    kind='var',
                    scope_id=global_id,
                    decl_node_id=self.ast.node_id + idx + 1  # proxy ID
                )
                try:
                    self.symbol_table.declare(global_id, entry)
                except ValueError as e:
                    self.diagnostics.append(str(e))
        """
        pass
    
    def _collect_proc_declarations(self) -> None:
        """
        Insert procedure names into the Procedure scope.
        
        M2 TODO:
        1. Iterate over self.ast.procs
        2. For each ProcDef, create entry with:
           - kind='proc'
           - scope_id=self.symbol_table.base_scopes['procedure']
           - decl_node_id=pdef.node_id
        3. Check for duplicates within Procedure scope
        4. IMPORTANT: Check for clash with function names
           (both procs and funcs are under Everywhere, so names must be unique)
        
        Example:
            proc_id = self.symbol_table.base_scopes['procedure']
            func_id = self.symbol_table.base_scopes['function']
            
            for pdef in self.ast.procs:
                # Check if name already used as function
                if self.symbol_table.lookup_local(func_id, pdef.name):
                    self.diagnostics.append(
                        f"Procedure '{pdef.name}' conflicts with function name"
                    )
                
                entry = SymbolTableEntry(
                    name=pdef.name,
                    kind='proc',
                    scope_id=proc_id,
                    decl_node_id=pdef.node_id
                )
                try:
                    self.symbol_table.declare(proc_id, entry)
                except ValueError as e:
                    self.diagnostics.append(str(e))
        """
        pass
    
    def _collect_func_declarations(self) -> None:
        """
        Insert function names into the Function scope.
        
        M2 TODO:
        Similar to _collect_proc_declarations but for functions.
        Also check for clash with procedure names.
        """
        pass
    
    def _collect_main_variables(self) -> None:
        """
        Insert main block variables into the Main scope.
        
        M2 TODO:
        1. Iterate over self.ast.main.variables
        2. Create entries with kind='var', scope_id=main_scope_id
        3. Similar proxy node_id issue as globals
        """
        pass
    
    def _check_cross_category_clashes(self) -> None:
        """
        Enforce that no variable name (global or main) equals any proc/func name.
        
        M2 TODO:
        This is the "Everywhere" level check mentioned in the spec.
        After collecting all declarations, check that:
        - No global variable name matches any proc name
        - No global variable name matches any func name
        - No main variable name matches any proc name
        - No main variable name matches any func name
        
        Example:
            global_id = self.symbol_table.base_scopes['global']
            proc_id = self.symbol_table.base_scopes['procedure']
            func_id = self.symbol_table.base_scopes['function']
            
            global_scope = self.symbol_table.get_scope(global_id)
            proc_scope = self.symbol_table.get_scope(proc_id)
            func_scope = self.symbol_table.get_scope(func_id)
            
            for var_name in global_scope.all_names():
                if var_name in proc_scope.all_names():
                    self.diagnostics.append(
                        f"Variable '{var_name}' conflicts with procedure name"
                    )
                if var_name in func_scope.all_names():
                    self.diagnostics.append(
                        f"Variable '{var_name}' conflicts with function name"
                    )
        """
        pass
    
    def _build_local_scopes(self) -> None:
        """
        For each proc/func definition, create a Local scope and populate it.
        
        M2 TODO:
        1. For each ProcDef in self.ast.procs:
           a. Create a new Local scope with parent = Global scope
           b. Insert parameters (kind='param', use proxy node_ids)
           c. Insert locals from body (kind='var', use proxy node_ids)
           d. Enforce: no duplicate params, no duplicate locals
           e. Enforce: locals cannot shadow params (same name is illegal)
           f. Store the local scope ID in self.local_scopes[pdef.name]
        
        2. Repeat for each FuncDef in self.ast.funcs
        
        Example:
            global_id = self.symbol_table.base_scopes['global']
            
            for pdef in self.ast.procs:
                # Create local scope
                local_id = self.symbol_table.new_scope(
                    kind='Local',
                    parent_id=global_id,
                    name=f'Local:{pdef.name}'
                )
                self.local_scopes[pdef.name] = local_id
                
                # Insert parameters
                param_names = set()
                for idx, param in enumerate(pdef.params):
                    if param in param_names:
                        self.diagnostics.append(
                            f"Duplicate parameter '{param}' in proc '{pdef.name}'"
                        )
                    param_names.add(param)
                    
                    entry = SymbolTableEntry(
                        name=param,
                        kind='param',
                        scope_id=local_id,
                        decl_node_id=pdef.node_id + idx + 1  # proxy
                    )
                    try:
                        self.symbol_table.declare(local_id, entry)
                    except ValueError as e:
                        self.diagnostics.append(str(e))
                
                # Insert locals
                for idx, local in enumerate(pdef.body.locals):
                    if local in param_names:
                        self.diagnostics.append(
                            f"Local variable '{local}' shadows parameter in proc '{pdef.name}'"
                        )
                    
                    entry = SymbolTableEntry(
                        name=local,
                        kind='var',
                        scope_id=local_id,
                        decl_node_id=pdef.body.node_id + idx + 1  # proxy
                    )
                    try:
                        self.symbol_table.declare(local_id, entry)
                    except ValueError as e:
                        self.diagnostics.append(str(e))
        """
        pass
    
    # ========================================================================
    # M3: RESOLUTION PASS (TODO)
    # ========================================================================
    
    def _resolve_uses(self) -> None:
        """
        Walk all ALGO blocks and resolve each variable use to its declaration.
        
        M3 TODO:
        1. For each ProcDef, call:
           self._resolve_algo(pdef.body.algo, self.local_scopes[pdef.name])
        
        2. For each FuncDef, call:
           self._resolve_algo(fdef.body.algo, self.local_scopes[fdef.name])
        
        3. For Main, call:
           self._resolve_algo(main.algo, self.symbol_table.base_scopes['main'])
        
        Example:
            for pdef in self.ast.procs:
                local_scope_id = self.local_scopes[pdef.name]
                self._resolve_algo(pdef.body.algo, local_scope_id)
        """
        pass
    
    def _resolve_algo(self, algo: Algo, scope_id: int) -> None:
        """
        Resolve all variable uses within an algorithm block.
        
        M3 TODO:
        This is the heart of name resolution. You need to:
        1. Walk all instructions in algo.instrs
        2. For each instruction, find all VarRef nodes
        3. For each VarRef:
           a. Look up the name using lookup_chain(scope_id, name)
           b. If found: set varref.resolved = entry
           c. If not found: add diagnostic about undeclared variable
        
        Where to find VarRefs:
        - In Assign: the var is a string, but rhs might contain VarRefs
        - In Print: output might be a VarRef
        - In Call: args are atoms (could be VarRefs)
        - In LoopWhile/LoopDoUntil: cond is a term (could contain VarRefs)
        - In BranchIf: cond is a term (could contain VarRefs)
        - Recursively in nested Algos (loop bodies, branch bodies)
        
        Example:
            for instr in algo.instrs:
                if isinstance(instr, Print):
                    if isinstance(instr.output, VarRef):
                        self._resolve_varref(instr.output, scope_id)
                
                elif isinstance(instr, Assign):
                    # Resolve the variable being assigned to
                    # (it's a string, not a VarRef, but we might want to check it exists)
                    # Resolve the RHS
                    if isinstance(instr.rhs, Call):
                        for arg in instr.rhs.args:
                            if isinstance(arg, VarRef):
                                self._resolve_varref(arg, scope_id)
                    else:  # rhs is a Term
                        self._resolve_term(instr.rhs, scope_id)
                
                elif isinstance(instr, Call):
                    for arg in instr.args:
                        if isinstance(arg, VarRef):
                            self._resolve_varref(arg, scope_id)
                
                elif isinstance(instr, LoopWhile):
                    self._resolve_term(instr.cond, scope_id)
                    self._resolve_algo(instr.body, scope_id)  # Recursive!
                
                elif isinstance(instr, LoopDoUntil):
                    self._resolve_algo(instr.body, scope_id)  # Recursive!
                    self._resolve_term(instr.cond, scope_id)
                
                elif isinstance(instr, BranchIf):
                    self._resolve_term(instr.cond, scope_id)
                    self._resolve_algo(instr.then_, scope_id)  # Recursive!
                    if instr.else_:
                        self._resolve_algo(instr.else_, scope_id)  # Recursive!
        """
        pass
    
    def _resolve_varref(self, varref: VarRef, scope_id: int) -> None:
        """
        Resolve a single variable reference.
        
        M3 TODO:
        Look up the name and set the resolved field.
        
        Example:
            entry = self.symbol_table.lookup_chain(scope_id, varref.name)
            if entry:
                varref.resolved = entry
            else:
                self.diagnostics.append(
                    f"Undeclared variable '{varref.name}' at node #{varref.node_id}"
                )
        """
        pass
    
    def _resolve_term(self, term: Any, scope_id: int) -> None:
        """
        Resolve all VarRefs in a term (expression).
        
        M3 TODO:
        Terms can be:
        - TermAtom: contains an atom (VarRef or NumberLit)
        - TermUn: contains another term
        - TermBin: contains two terms
        
        Example:
            if isinstance(term, TermAtom):
                if isinstance(term.atom, VarRef):
                    self._resolve_varref(term.atom, scope_id)
            
            elif isinstance(term, TermUn):
                self._resolve_term(term.term, scope_id)  # Recursive!
            
            elif isinstance(term, TermBin):
                self._resolve_term(term.left, scope_id)   # Recursive!
                self._resolve_term(term.right, scope_id)  # Recursive!
        """
        pass


def check_scopes(ast: Program) -> SymbolTable:
    """
    Convenience function: run scope checking on an AST.
    
    Args:
        ast: Program node with node_ids assigned
    
    Returns:
        Completed SymbolTable
    
    Raises:
        Exception: If errors are found (after M4 implements error reporting)
    
    Example:
        from spl.parser import Parser
        from spl.ast_ids import assign_ids
        from spl.scope_checker import check_scopes
        
        text = open('example.spl').read()
        ast = Parser(text).parse()
        assign_ids(ast)
        st = check_scopes(ast)
        print(st.pretty_print())
    """
    checker = ScopeChecker(ast)
    return checker.check()


# ============================================================================
# Demonstration
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Scope Checker Module - Phase 2")
    print("=" * 70)
    print()
    print("This module provides the ScopeChecker class for building and")
    print("checking the symbol table.")
    print()
    print("Usage:")
    print("    from spl.parser import Parser")
    print("    from spl.ast_ids import assign_ids")
    print("    from spl.scope_checker import check_scopes")
    print()
    print("    ast = Parser(source).parse()")
    print("    assign_ids(ast)")
    print("    symbol_table = check_scopes(ast)")
    print("    print(symbol_table.pretty_print())")
    print()
    print("Current implementation status:")
    print("  ✓ M1: Base scope hierarchy (Everywhere → Global/Proc/Func/Main)")
    print("  ⧗ M2: Declaration collection (TODO)")
    print("  ⧗ M3: Variable use resolution (TODO)")
    print("  ⧗ M4: Error reporting (TODO)")
    print()
    print("=" * 70)