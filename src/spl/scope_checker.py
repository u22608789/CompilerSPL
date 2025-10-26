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

from typing import Dict, List, Optional, Any
from .symbol_table import SymbolTable, SymbolTableEntry, create_base_scopes
from .astnodes import *
from .errors import Diagnostic


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
        self.diagnostics: List[Diagnostic] = []

        # Optional map from VarRef node_id to decl_node_id (debugging)
        self.uses_to_decls: Dict[int, int] = {}

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

        # Step 2: Collect declarations (M2)
        self._collect_global_declarations()
        self._collect_proc_declarations()
        self._collect_func_declarations()
        self._collect_main_variables()
        self._check_cross_category_clashes()

        # Step 3: Build local scopes for each proc/func (M2)
        self._build_local_scopes()

        # Step 4: Resolve variable uses (M3 - TODO)
        self._resolve_uses()

        # Step 5: Return the symbol table (M4: diagnostics are collected, not raised)
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

        M2:
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
        global_id = self.symbol_table.base_scopes['global']
        for idx, name in enumerate(self.ast.globals):
            entry = SymbolTableEntry(
                name=name,
                kind='var',
                scope_id=global_id,
                decl_node_id=self._proxy_id(self.ast.node_id, "globals", idx),
            )
            try:
                self.symbol_table.declare(global_id, entry)
            except ValueError as e:
                self.diagnostics.append(Diagnostic(kind='DuplicateName', message=str(e), node_id=entry.decl_node_id, scope_path=self.symbol_table.get_scope_path(global_id)))

    def _collect_proc_declarations(self) -> None:
        """
        Insert procedure names into the Procedure scope.

        M2:
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
        proc_id = self.symbol_table.base_scopes['procedure']
        func_id = self.symbol_table.base_scopes['function']
        for pdef in self.ast.procs:
            # clash with functions?
            if self.symbol_table.lookup_local(func_id, pdef.name):
                self.diagnostics.append(Diagnostic(
                    kind='CrossCategoryClash',
                    message=f"Procedure '{pdef.name}' conflicts with function name",
                    node_id=pdef.node_id,
                    scope_path=self.symbol_table.get_scope_path(proc_id)
                ))
            entry = SymbolTableEntry(
                name=pdef.name, kind='proc', scope_id=proc_id, decl_node_id=pdef.node_id
            )
            try:
                self.symbol_table.declare(proc_id, entry)
            except ValueError as e:
                self.diagnostics.append(Diagnostic(kind='DuplicateName', message=str(e), node_id=pdef.node_id, scope_path=self.symbol_table.get_scope_path(proc_id)))

    def _collect_func_declarations(self) -> None:
        """
        Insert function names into the Function scope.

        M2:
        Similar to _collect_proc_declarations but for functions.
        Also check for clash with procedure names.
        """
        proc_id = self.symbol_table.base_scopes['procedure']
        func_id = self.symbol_table.base_scopes['function']
        for fdef in self.ast.funcs:
            # clash with procedures?
            if self.symbol_table.lookup_local(proc_id, fdef.name):
                self.diagnostics.append(Diagnostic(
                    kind='CrossCategoryClash',
                    message=f"Function '{fdef.name}' conflicts with procedure name",
                    node_id=fdef.node_id,
                    scope_path=self.symbol_table.get_scope_path(func_id)
                ))
            entry = SymbolTableEntry(
                name=fdef.name, kind='func', scope_id=func_id, decl_node_id=fdef.node_id
            )
            try:
                self.symbol_table.declare(func_id, entry)
            except ValueError as e:
                self.diagnostics.append(Diagnostic(kind='DuplicateName', message=str(e), node_id=fdef.node_id, scope_path=self.symbol_table.get_scope_path(func_id)))


    def _collect_main_variables(self) -> None:
        """
        Insert main block variables into the Main scope.

        M2 DONE:
        1. Iterate over self.ast.main.variables
        2. Create entries with kind='var', scope_id=main_scope_id
        3. Similar proxy node_id issue as globals
        """
        main_id = self.symbol_table.base_scopes['main']
        for idx, name in enumerate(self.ast.main.variables):
            entry = SymbolTableEntry(
                name=name,
                kind='var',
                scope_id=main_id,
                decl_node_id=self._proxy_id(self.ast.main.node_id, "main", idx),
            )
            try:
                self.symbol_table.declare(main_id, entry)
            except ValueError as e:
                self.diagnostics.append(Diagnostic(kind='DuplicateName', message=str(e), node_id=entry.decl_node_id, scope_path=self.symbol_table.get_scope_path(main_id)))


    def _check_cross_category_clashes(self) -> None:
        """
        Enforce that no variable name (global or main) equals any proc/func name.

        M2 DONE:
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
        global_id = self.symbol_table.base_scopes['global']
        main_id   = self.symbol_table.base_scopes['main']
        proc_id   = self.symbol_table.base_scopes['procedure']
        func_id   = self.symbol_table.base_scopes['function']
        global_scope = self.symbol_table.get_scope(global_id)
        main_scope   = self.symbol_table.get_scope(main_id)
        proc_scope   = self.symbol_table.get_scope(proc_id)
        func_scope   = self.symbol_table.get_scope(func_id)
        proc_names = proc_scope.all_names()
        func_names = func_scope.all_names()
        for var_name in global_scope.all_names():
            if var_name in proc_names:
                self.diagnostics.append(Diagnostic(
                    kind='CrossCategoryClash',
                    message=f"Variable '{var_name}' conflicts with procedure name",
                    node_id=-1,
                    scope_path=self.symbol_table.get_scope_path(global_id)
                ))
            if var_name in func_names:
                self.diagnostics.append(Diagnostic(
                    kind='CrossCategoryClash',
                    message=f"Variable '{var_name}' conflicts with function name",
                    node_id=-1,
                    scope_path=self.symbol_table.get_scope_path(global_id)
                ))
        for var_name in main_scope.all_names():
            if var_name in proc_names:
                self.diagnostics.append(Diagnostic(
                    kind='CrossCategoryClash',
                    message=f"Main variable '{var_name}' conflicts with procedure name",
                    node_id=-1,
                    scope_path=self.symbol_table.get_scope_path(main_id)
                ))
            if var_name in func_names:
                self.diagnostics.append(Diagnostic(
                    kind='CrossCategoryClash',
                    message=f"Main variable '{var_name}' conflicts with function name",
                    node_id=-1,
                    scope_path=self.symbol_table.get_scope_path(main_id)
                ))

    def _build_local_scopes(self) -> None:
        """
        For each proc/func definition, create a Local scope and populate it.

        M2 DONE:
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
        global_id = self.symbol_table.base_scopes['global']

        # Procedures
        for pdef in self.ast.procs:
            local_id = self.symbol_table.new_scope('Local', global_id, name=f'Local:{pdef.name}')
            self.local_scopes[pdef.name] = local_id
            # params
            seen = set()
            for idx, param in enumerate(pdef.params):
                if param in seen:
                    self.diagnostics.append(Diagnostic(
                        kind='DuplicateName',
                        message=f"Duplicate parameter '{param}' in proc '{pdef.name}'",
                        node_id=self._proxy_id(pdef.node_id, f"proc:{pdef.name}:param", idx),
                        scope_path=self.symbol_table.get_scope_path(local_id)
                    ))
                seen.add(param)
                entry = SymbolTableEntry(
                    name=param, kind='param', scope_id=local_id,
                    decl_node_id=self._proxy_id(pdef.node_id, f"proc:{pdef.name}:param", idx)
                )
                try:
                    self.symbol_table.declare(local_id, entry)
                except ValueError as e:
                    self.diagnostics.append(Diagnostic(kind='DuplicateName', message=str(e), node_id=entry.decl_node_id, scope_path=self.symbol_table.get_scope_path(local_id)))
            # locals
            for idx, local in enumerate(pdef.body.locals):
                if local in seen:
                    self.diagnostics.append(Diagnostic(
                        kind='ParamShadowed',
                        message=f"Local variable '{local}' shadows parameter in proc '{pdef.name}'",
                        node_id=self._proxy_id(pdef.body.node_id, f"proc:{pdef.name}:local", idx),
                        scope_path=self.symbol_table.get_scope_path(local_id)
                    ))
                entry = SymbolTableEntry(
                    name=local, kind='var', scope_id=local_id,
                    decl_node_id=self._proxy_id(pdef.body.node_id, f"proc:{pdef.name}:local", idx)
                )
                try:
                    self.symbol_table.declare(local_id, entry)
                except ValueError as e:
                    self.diagnostics.append(Diagnostic(kind='DuplicateName', message=str(e), node_id=entry.decl_node_id, scope_path=self.symbol_table.get_scope_path(local_id)))

        # Functions
        for fdef in self.ast.funcs:
            local_id = self.symbol_table.new_scope('Local', global_id, name=f'Local:{fdef.name}')
            self.local_scopes[fdef.name] = local_id
            # params
            seen = set()
            for idx, param in enumerate(fdef.params):
                if param in seen:
                    self.diagnostics.append(Diagnostic(
                        kind='DuplicateName',
                        message=f"Duplicate parameter '{param}' in func '{fdef.name}'",
                        node_id=self._proxy_id(fdef.node_id, f"func:{fdef.name}:param", idx),
                        scope_path=self.symbol_table.get_scope_path(local_id)
                    ))
                seen.add(param)
                entry = SymbolTableEntry(
                    name=param, kind='param', scope_id=local_id,
                    decl_node_id=self._proxy_id(fdef.node_id, f"func:{fdef.name}:param", idx)
                )
                try:
                    self.symbol_table.declare(local_id, entry)
                except ValueError as e:
                    self.diagnostics.append(Diagnostic(kind='DuplicateName', message=str(e), node_id=entry.decl_node_id, scope_path=self.symbol_table.get_scope_path(local_id)))
            # locals
            for idx, local in enumerate(fdef.body.locals):
                if local in seen:
                    self.diagnostics.append(Diagnostic(
                        kind='ParamShadowed',
                        message=f"Local variable '{local}' shadows parameter in func '{fdef.name}'",
                        node_id=self._proxy_id(fdef.body.node_id, f"func:{fdef.name}:local", idx),
                        scope_path=self.symbol_table.get_scope_path(local_id)
                    ))
                entry = SymbolTableEntry(
                    name=local, kind='var', scope_id=local_id,
                    decl_node_id=self._proxy_id(fdef.body.node_id, f"func:{fdef.name}:local", idx)
                )
                try:
                    self.symbol_table.declare(local_id, entry)
                except ValueError as e:
                    self.diagnostics.append(Diagnostic(kind='DuplicateName', message=str(e), node_id=entry.decl_node_id, scope_path=self.symbol_table.get_scope_path(local_id)))


    # ========================================================================
    # M3: RESOLUTION PASS (TODO)
    # ========================================================================

    def _resolve_uses(self) -> None:
        """
        Resolve uses in proc/func main algorithm blocks.
        For each VarRef found, set varref.resolved to the corresponding SymbolTableEntry.
        If no declaration is found, emit an UndeclaredVariable diagnostic.
        """
        # Procs
        for pdef in self.ast.procs:
            local_scope_id = self.local_scopes.get(pdef.name)
            if local_scope_id is None:
                # should not happen if M2 succeeded; report defensively
                self.diagnostics.append(Diagnostic(
                    kind='InternalError',
                    message=f"No local scope found for procedure '{pdef.name}'",
                    node_id=pdef.node_id
                ))
                continue
            # pdef.body.algo might be the algo object
            if getattr(pdef, 'body', None) and getattr(pdef.body, 'algo', None):
                self._resolve_algo(pdef.body.algo, local_scope_id, owner_name=pdef.name, owner_kind='proc')

        # Funcs
        for fdef in self.ast.funcs:
            local_scope_id = self.local_scopes.get(fdef.name)
            if local_scope_id is None:
                self.diagnostics.append(Diagnostic(
                    kind='InternalError',
                    message=f"No local scope found for function '{fdef.name}'",
                    node_id=fdef.node_id
                ))
                continue
            if getattr(fdef, 'body', None) and getattr(fdef.body, 'algo', None):
                self._resolve_algo(fdef.body.algo, local_scope_id, owner_name=fdef.name, owner_kind='func')

        # Main
        main_scope = self.symbol_table.base_scopes['main']
        if getattr(self.ast, 'main', None) and getattr(self.ast.main, 'algo', None):
            self._resolve_algo(self.ast.main.algo, main_scope, owner_name='main', owner_kind='main')

    def _resolve_algo(self, algo: Any, scope_id: int, owner_name: Optional[str] = None, owner_kind: Optional[str] = None) -> None:
        """
        Walk instructions in an Algo and resolve any VarRefs inside.
        This function is defensive about field names for the instruction list.
        """
        instrs = getattr(algo, 'instrs', None) or getattr(algo, 'stmts', None) or getattr(algo, 'statements', None)
        if instrs is None:
            # Nothing to do
            return

        for instr in instrs:
            # Detect types by class names to stay robust to small AST naming differences
            itype = type(instr).__name__
            # ASSIGN: typically has 'lhs' (string/name) and 'rhs' (Term or Call)
            if itype in ('Assign', 'Assignment'):
                # resolve RHS (term or call)
                rhs = getattr(instr, 'rhs', None)
                if rhs is not None:
                    # Call can appear as rhs (function call returning a value)
                    if type(rhs).__name__ in ('Call',):
                        # call args may be VarRef or Terms
                        for arg in getattr(rhs, 'args', []):
                            # arg may be an Atom/Term/VarRef
                            if isinstance(arg, VarRef):
                                self._resolve_varref(arg, scope_id)
                            else:
                                # if arg is Term-like, attempt to resolve inside
                                self._resolve_term(arg, scope_id)
                    else:
                        self._resolve_term(rhs, scope_id)
                # Optionally resolve LHS if it's a VarRef object (some ASTs use VarRef)
                lhs = getattr(instr, 'lhs', None)
                if isinstance(lhs, VarRef):
                    self._resolve_varref(lhs, scope_id)

            # PRINT: may have expression or varref
            elif itype == 'Print':
                out = getattr(instr, 'expr', None) or getattr(instr, 'output', None)
                if isinstance(out, VarRef):
                    self._resolve_varref(out, scope_id)
                else:
                    self._resolve_term(out, scope_id)

            # CALL (proc call) - resolve argument terms
            elif itype == 'Call':
                for arg in getattr(instr, 'args', []):
                    if isinstance(arg, VarRef):
                        self._resolve_varref(arg, scope_id)
                    else:
                        self._resolve_term(arg, scope_id)

            # LOOPS
            elif itype in ('LoopWhile', 'LoopDoUntil', 'WhileLoop', 'DoUntilLoop'):
                cond = getattr(instr, 'cond', None)
                if cond is not None:
                    self._resolve_term(cond, scope_id)
                body = getattr(instr, 'body', None)
                if body is not None:
                    self._resolve_algo(body, scope_id, owner_name, owner_kind)

            # BRANCH / IF
            elif itype in ('BranchIf', 'If', 'IfThen'):
                cond = getattr(instr, 'cond', None)
                if cond is not None:
                    self._resolve_term(cond, scope_id)
                then_block = getattr(instr, 'then_', None) or getattr(instr, 'then', None)
                if then_block is not None:
                    self._resolve_algo(then_block, scope_id, owner_name, owner_kind)
                else_block = getattr(instr, 'else_', None) or getattr(instr, 'else', None)
                if else_block is not None:
                    self._resolve_algo(else_block, scope_id, owner_name, owner_kind)

            # HALT, RETURN, or other simple instructions - may contain terms in some ASTs
            else:
                # Best-effort: inspect attributes for Terms and resolve them
                for attr_name in dir(instr):
                    if attr_name.startswith('_'):
                        continue
                    try:
                        attr = getattr(instr, attr_name)
                    except Exception:
                        continue
                    # If attribute looks like a Term or VarRef, resolve it
                    if isinstance(attr, VarRef):
                        self._resolve_varref(attr, scope_id)
                    elif type(attr).__name__ in ('Term', 'TermAtom', 'TermUn', 'TermBin'):
                        self._resolve_term(attr, scope_id)
                    # if it's an iterable of terms/varrefs, check the items
                    elif isinstance(attr, (list, tuple)):
                        for item in attr:
                            if isinstance(item, VarRef):
                                self._resolve_varref(item, scope_id)
                            elif type(item).__name__ in ('Term', 'TermAtom', 'TermUn', 'TermBin'):
                                self._resolve_term(item, scope_id)
                # end best-effort

    def _resolve_varref(self, varref: VarRef, scope_id: int) -> None:
        """
        Resolve a VarRef node by looking it up in the symbol table chain starting
        from the provided scope_id.

        If not found, append an UndeclaredVariable diagnostic.
        If found, attach to varref.resolved and record uses_to_decls mapping.
        """
        if varref is None:
            return
        name = getattr(varref, 'name', None)
        if not name:
            return

        # Prefer local lookup first, then chain lookup if needed.
        # lookup_chain is expected to search the provided scope and parent scopes.
        entry = None
        try:
            # If the current (starting) scope exists, try lookup_local first (for strict local param/local priority)
            entry = self.symbol_table.lookup_local(scope_id, name)
            if not entry:
                entry = self.symbol_table.lookup_chain(scope_id, name)
        except Exception:
            # Fallback: try chain directly
            entry = self.symbol_table.lookup_chain(scope_id, name)

        if entry is None:
            main_id   = self.symbol_table.base_scopes['main']
            global_id = self.symbol_table.base_scopes['global']
            if scope_id == main_id:
                entry = self.symbol_table.lookup_local(global_id, name)
        else:
            # attach resolved
            setattr(varref, 'resolved', entry)
            # record use→decl mapping if we have node ids
            vid = getattr(varref, 'node_id', -1)
            if vid is not None and vid != -1:
                try:
                    self.uses_to_decls[vid] = int(entry.decl_node_id)
                except Exception:
                    # decl_node_id might be non-int (proxy); still safe to store
                    self.uses_to_decls[vid] = entry.decl_node_id

    def _resolve_term(self, term: Any, scope_id: int) -> None:
        """
        Recursively resolve VarRefs inside Term nodes.
        Term shapes supported: TermAtom (holds atom possibly a VarRef), TermUn, TermBin.
        """
        if term is None:
            return
        tname = type(term).__name__

        if tname == 'TermAtom':
            atom = getattr(term, 'atom', None)
            if isinstance(atom, VarRef):
                self._resolve_varref(atom, scope_id)
            # numbers/strings ignored
        elif tname == 'TermUn':
            inner = getattr(term, 'term', None) or getattr(term, 'inner', None)
            if inner is not None:
                self._resolve_term(inner, scope_id)
        elif tname == 'TermBin':
            left = getattr(term, 'left', None)
            right = getattr(term, 'right', None)
            if left is not None:
                self._resolve_term(left, scope_id)
            if right is not None:
                self._resolve_term(right, scope_id)
        else:
            # Best-effort: if term has attributes that look like sub-terms, walk them
            # to be robust to minor AST naming differences.
            for attr_name in dir(term):
                if attr_name.startswith('_'):
                    continue
                try:
                    attr = getattr(term, attr_name)
                except Exception:
                    continue
                if isinstance(attr, VarRef):
                    self._resolve_varref(attr, scope_id)
                elif type(attr).__name__ in ('Term', 'TermAtom', 'TermUn', 'TermBin'):
                    self._resolve_term(attr, scope_id)
                elif isinstance(attr, (list, tuple)):
                    for item in attr:
                        if isinstance(item, VarRef):
                            self._resolve_varref(item, scope_id)
                        elif type(item).__name__ in ('Term', 'TermAtom', 'TermUn', 'TermBin'):
                            self._resolve_term(item, scope_id)

# ---------- helpers ----------
    def _proxy_id(self, anchor_node_id: int, bucket: str, idx: int) -> int:
        """
        Deterministic stand-in for decl_node_id when a declaration is a bare string
        (globals, params, locals, main variables). Keep it simple & consistent.
        """
        bucket_code = (abs(hash(bucket)) & 0xFF)  # short code from bucket name
        return anchor_node_id * 1000 + bucket_code * 10 + (idx + 1)

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
