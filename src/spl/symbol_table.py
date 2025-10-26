"""
Symbol Table Module for SPL Compiler (Phase 2)

Provides core data structures and operations for name resolution and scope checking.

Key components:
- SymbolTableEntry: Information about a declared identifier
- Scope: A namespace with parent-child relationships
- SymbolTable: Complete collection of all scopes

SPL Scope Structure:
    Everywhere (root)
    ├── Global (global variables)
    ├── Procedure (procedure names)
    ├── Function (function names)
    ├── Main (main's local variables)
    └── [Local scopes for each proc/func]
        └── Local:name (parameters + locals)
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class SymbolTableEntry:
    """
    A single declared identifier in the symbol table.
    
    Attributes:
        name: The identifier's name
        kind: 'var', 'param', 'proc', or 'func'
        scope_id: Which scope this entry belongs to
        decl_node_id: AST node ID where declared (for error reporting)
        type_info: Reserved for Phase 3 type checking
    """
    name: str
    kind: str  # 'var', 'param', 'proc', 'func'
    scope_id: int
    decl_node_id: int
    type_info: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Entry({self.kind} '{self.name}' @ scope#{self.scope_id}, node#{self.decl_node_id})"


@dataclass
class Scope:
    """
    A single scope (namespace) in the program.
    
    Attributes:
        id: Unique identifier for this scope
        kind: 'Everywhere', 'Global', 'Procedure', 'Function', 'Main', or 'Local'
        parent_id: ID of parent scope (None only for Everywhere)
        table: Dictionary mapping names to entries
        name: Optional descriptive name (e.g., "Local:increment")
    """
    id: int
    kind: str
    parent_id: Optional[int]
    table: Dict[str, SymbolTableEntry] = field(default_factory=dict)
    name: Optional[str] = None
    
    def declare(self, entry: SymbolTableEntry) -> None:
        """
        Add a new entry to this scope.
        
        Raises:
            ValueError: If the name already exists in this scope
        """
        if entry.name in self.table:
            existing = self.table[entry.name]
            raise ValueError(
                f"Duplicate declaration of '{entry.name}' in {self.kind} scope "
                f"(previous @ node#{existing.decl_node_id}, current @ node#{entry.decl_node_id})"
            )
        self.table[entry.name] = entry
    
    def lookup_local(self, name: str) -> Optional[SymbolTableEntry]:
        """Look up a name only in this scope (no parent chain)."""
        return self.table.get(name)
    
    def all_names(self) -> Set[str]:
        """Get all names declared in this scope."""
        return set(self.table.keys())
    
    def __repr__(self) -> str:
        desc = self.name or self.kind
        parent_str = f"parent=#{self.parent_id}" if self.parent_id is not None else "root"
        return f"Scope#{self.id}({desc}, {parent_str})"


class SymbolTable:
    """
    The complete symbol table for an SPL program.
    
    Manages all scopes and provides operations for:
    - Creating scopes with parent-child relationships
    - Declaring names in scopes
    - Looking up names with scope chain traversal
    - Enforcing SPL's scoping rules
    """
    
    def __init__(self):
        self.scopes: Dict[int, Scope] = {}
        self._next_scope_id = 1
        # Reverse index: declaration node_id → entry
        self.nodes: Dict[int, SymbolTableEntry] = {}
        # Store base scope IDs for convenience
        self.base_scopes: Dict[str, int] = {}
    
    def new_scope(self, kind: str, parent_id: Optional[int], name: Optional[str] = None) -> int:
        """
        Create a new scope as a child of parent_id.
        
        Args:
            kind: Type of scope (Everywhere, Global, Local, etc.)
            parent_id: ID of parent scope, or None for root
            name: Optional descriptive name for debugging
        
        Returns:
            The ID of the newly created scope
        """
        scope_id = self._next_scope_id
        self._next_scope_id += 1
        
        scope = Scope(
            id=scope_id,
            kind=kind,
            parent_id=parent_id,
            name=name
        )
        self.scopes[scope_id] = scope
        return scope_id
    
    def get_scope(self, scope_id: int) -> Scope:
        """
        Get a scope by ID.
        
        Raises:
            KeyError: If scope_id doesn't exist
        """
        if scope_id not in self.scopes:
            raise KeyError(f"Scope #{scope_id} not found")
        return self.scopes[scope_id]
    
    def declare(self, scope_id: int, entry: SymbolTableEntry) -> None:
        """
        Declare a new name in the given scope.
        
        Updates both the scope's table and the nodes reverse index.
        
        Args:
            scope_id: ID of scope to declare in
            entry: The symbol table entry to add
        
        Raises:
            ValueError: If the name already exists in that scope
            KeyError: If scope_id doesn't exist
        """
        scope = self.get_scope(scope_id)
        scope.declare(entry)
        # Maintain reverse lookup by declaration node
        self.nodes[entry.decl_node_id] = entry
    
    def lookup_local(self, scope_id: int, name: str) -> Optional[SymbolTableEntry]:
        """
        Look up a name only in the specified scope (no parent traversal).
        
        Args:
            scope_id: ID of scope to search
            name: Name to look up
        
        Returns:
            SymbolTableEntry if found, None otherwise
        """
        scope = self.get_scope(scope_id)
        return scope.lookup_local(name)
    
    def lookup_chain(self, scope_id: int, name: str) -> Optional[SymbolTableEntry]:
        """
        Look up a name starting from scope_id and walking up the parent chain.
        
        This implements natural scoping rules: local → parent → grandparent → ...
        
        Args:
            scope_id: Starting scope ID
            name: Name to look up
        
        Returns:
            First SymbolTableEntry found, or None if not found anywhere
        
        Example:
            In a proc's local scope, lookup_chain checks:
            1. Local scope (params and locals)
            2. Global scope (if Local's parent is Global)
            3. Everywhere (if reached)
        """
        current_id: Optional[int] = scope_id
        while current_id is not None:
            scope = self.get_scope(current_id)
            entry = scope.lookup_local(name)
            if entry:
                return entry
            current_id = scope.parent_id
        return None
    
    def get_scope_path(self, scope_id: int) -> List[str]:
        """
        Get the path from root to the given scope (for error messages).
        
        Args:
            scope_id: ID of target scope
        
        Returns:
            List of scope names from root to target
        
        Example:
            ['Everywhere', 'Global', 'Local:increment']
        """
        path = []
        current_id: Optional[int] = scope_id
        while current_id is not None:
            scope = self.get_scope(current_id)
            path.append(scope.name or scope.kind)
            current_id = scope.parent_id
        return list(reversed(path))
    
    def pretty_print(self) -> str:
        """
        Generate a human-readable representation of the entire symbol table.
        
        Returns:
            Formatted string showing scope tree with all entries
        """
        lines = ["=" * 70]
        lines.append("SYMBOL TABLE")
        lines.append("=" * 70)
        
        def print_scope(scope_id: int, indent: int = 0) -> None:
            scope = self.get_scope(scope_id)
            prefix = "  " * indent
            
            # Scope header
            desc = scope.name or scope.kind
            lines.append(f"{prefix}Scope #{scope_id} [{desc}]")
            
            # Entries in this scope
            if scope.table:
                for name in sorted(scope.table.keys()):
                    entry = scope.table[name]
                    lines.append(
                        f"{prefix}  {entry.kind:6} {name:20} "
                        f"(decl @ node#{entry.decl_node_id})"
                    )
            else:
                lines.append(f"{prefix}  (empty)")
            
            # Children scopes
            children = [sid for sid, s in self.scopes.items() if s.parent_id == scope_id]
            for child_id in sorted(children):
                print_scope(child_id, indent + 1)
        
        # Find root scope(s) (parent_id == None)
        roots = [sid for sid, s in self.scopes.items() if s.parent_id is None]
        for root_id in roots:
            print_scope(root_id)
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"SymbolTable({len(self.scopes)} scopes, {len(self.nodes)} declarations)"


def create_base_scopes(st: SymbolTable) -> Dict[str, int]:
    """
    Create the standard SPL scope hierarchy:
        Everywhere (root)
        ├── Global
        ├── Procedure
        ├── Function
        └── Main
    
    Args:
        st: SymbolTable to populate
    
    Returns:
        Dictionary mapping scope names to their IDs:
        {
            'everywhere': scope_id,
            'global': scope_id,
            'procedure': scope_id,
            'function': scope_id,
            'main': scope_id
        }
    """
    everywhere_id = st.new_scope('Everywhere', None, name='Everywhere')
    global_id = st.new_scope('Global', everywhere_id, name='Global')
    proc_id = st.new_scope('Procedure', everywhere_id, name='Procedure')
    func_id = st.new_scope('Function', everywhere_id, name='Function')
    main_id = st.new_scope('Main', everywhere_id, name='Main')
    
    # Store in symbol table for easy access
    st.base_scopes = {
        'everywhere': everywhere_id,
        'global': global_id,
        'procedure': proc_id,
        'function': func_id,
        'main': main_id
    }
    
    return st.base_scopes


# ============================================================================
# Smoke test / demonstration
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Symbol Table Module - Smoke Test")
    print("=" * 70)
    print()
    
    # Create table and base scopes
    st = SymbolTable()
    scopes = create_base_scopes(st)
    
    print("✓ Created base scope hierarchy:")
    for name, scope_id in scopes.items():
        scope = st.get_scope(scope_id)
        parent = f"parent=#{scope.parent_id}" if scope.parent_id else "root"
        print(f"  {name:12} → Scope #{scope_id} ({parent})")
    print()
    
    # Declare some entries
    print("✓ Declaring sample entries...")
    st.declare(scopes['global'], 
               SymbolTableEntry('x', 'var', scopes['global'], 1))
    st.declare(scopes['global'], 
               SymbolTableEntry('y', 'var', scopes['global'], 2))
    st.declare(scopes['procedure'], 
               SymbolTableEntry('inc', 'proc', scopes['procedure'], 3))
    st.declare(scopes['function'], 
               SymbolTableEntry('double', 'func', scopes['function'], 4))
    print("  - Global vars: x, y")
    print("  - Procedure: inc")
    print("  - Function: double")
    print()
    
    # Create a local scope for proc 'inc'
    print("✓ Creating local scope for proc 'inc'...")
    inc_local = st.new_scope('Local', scopes['global'], name='Local:inc')
    st.declare(inc_local, 
               SymbolTableEntry('n', 'param', inc_local, 5))
    st.declare(inc_local, 
               SymbolTableEntry('tmp', 'var', inc_local, 6))
    print("  - Param: n")
    print("  - Local: tmp")
    print()
    
    # Print the complete symbol table
    print(st.pretty_print())
    print()
    
    # Test lookup operations
    print("✓ Testing lookup operations:")
    print(f"  lookup_local 'n' in inc_local:  {st.lookup_local(inc_local, 'n')}")
    print(f"  lookup_chain 'n' in inc_local:  {st.lookup_chain(inc_local, 'n')}")
    print(f"  lookup_chain 'x' in inc_local:  {st.lookup_chain(inc_local, 'x')}")
    print(f"  lookup_chain 'z' in inc_local:  {st.lookup_chain(inc_local, 'z')}")
    print()
    
    # Test scope path
    print("✓ Testing scope path:")
    path = st.get_scope_path(inc_local)
    print(f"  Path to inc_local: {' → '.join(path)}")
    print()
    
    # Test duplicate detection
    print("✓ Testing duplicate detection:")
    try:
        st.declare(scopes['global'], 
                   SymbolTableEntry('x', 'var', scopes['global'], 99))
        print("  ✗ FAILED: Should have caught duplicate!")
    except ValueError as e:
        print(f"  ✓ Correctly caught duplicate: {e}")
    print()
    
    print("=" * 70)
    print("✓ All smoke tests passed!")
    print("=" * 70)