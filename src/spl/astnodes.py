"""
AST Node Definitions for SPL Compiler (Phase 2 Updated)

Each node now includes:
- node_id: int (default -1, assigned by ast_ids.assign_ids())
- resolved: Optional[SymbolTableEntry] for VarRef (filled by scope checker)
"""

from dataclasses import dataclass
from typing import List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .symbol_table import SymbolTableEntry


# ============================================================================
# Top-level program structure
# ============================================================================

@dataclass
class Program:
    """Root: glob { VARIABLES } proc { PROCDEFS } func { FUNCDEFS } main { MAINPROG }"""
    globals: List[str]
    procs: List['ProcDef']
    funcs: List['FuncDef']
    main: 'Main'
    node_id: int = -1


@dataclass
class ProcDef:
    """Procedure: NAME ( PARAM ) { BODY }"""
    name: str
    params: List[str]
    body: 'Body'
    node_id: int = -1


@dataclass
class FuncDef:
    """Function: NAME ( PARAM ) { BODY ; return ATOM }"""
    name: str
    params: List[str]
    body: 'Body'
    ret: 'Atom'
    node_id: int = -1


@dataclass
class Body:
    """Body: local { MAXTHREE } ALGO"""
    locals: List[str]
    algo: 'Algo'
    node_id: int = -1


@dataclass
class Main:
    """Main: var { VARIABLES } ALGO"""
    variables: List[str]
    algo: 'Algo'
    node_id: int = -1


# ============================================================================
# Algorithms (instruction sequences)
# ============================================================================

@dataclass
class Algo:
    """Sequence of instructions: INSTR ( ; INSTR )*"""
    instrs: List['Instr']
    node_id: int = -1


# ============================================================================
# Instructions
# ============================================================================

@dataclass
class Halt:
    """halt instruction"""
    node_id: int = -1


@dataclass
class Print:
    """print OUTPUT"""
    output: 'Output'
    node_id: int = -1


@dataclass
class Call:
    """Procedure/function call: NAME ( INPUT )"""
    name: str
    args: List['Atom']
    node_id: int = -1


@dataclass
class Assign:
    """Assignment: VAR = TERM or VAR = NAME ( INPUT )"""
    var: str
    rhs: Union['Term', 'Call']
    node_id: int = -1


@dataclass
class LoopWhile:
    """while TERM { ALGO }"""
    cond: 'Term'
    body: 'Algo'
    node_id: int = -1


@dataclass
class LoopDoUntil:
    """do { ALGO } until TERM"""
    body: 'Algo'
    cond: 'Term'
    node_id: int = -1


@dataclass
class BranchIf:
    """if TERM { ALGO } [else { ALGO }]"""
    cond: 'Term'
    then_: 'Algo'
    else_: Optional['Algo'] = None
    node_id: int = -1


# ============================================================================
# Atoms and Literals
# ============================================================================

@dataclass
class VarRef:
    """Variable reference - Phase 2: includes resolved field for name resolution"""
    name: str
    node_id: int = -1
    resolved: Optional['SymbolTableEntry'] = None


@dataclass
class NumberLit:
    """Numeric literal"""
    value: int
    node_id: int = -1


@dataclass
class StringLit:
    """String literal"""
    value: str
    node_id: int = -1


# ============================================================================
# Terms (Expressions)
# ============================================================================

@dataclass
class TermAtom:
    """Term: ATOM"""
    atom: 'Atom'
    node_id: int = -1


@dataclass
class TermUn:
    """Term: ( UNOP TERM )"""
    op: str  # 'neg' or 'not'
    term: 'Term'
    node_id: int = -1


@dataclass
class TermBin:
    """Term: ( TERM BINOP TERM )"""
    left: 'Term'
    op: str  # eq, >, or, and, plus, minus, mult, div
    right: 'Term'
    node_id: int = -1


# ============================================================================
# Type aliases (using Union for Python 3.7+ compatibility)
# ============================================================================

Atom = Union[VarRef, NumberLit]
Output = Union[VarRef, NumberLit, StringLit]
Term = Union[TermAtom, TermUn, TermBin]
Instr = Union[Halt, Print, Call, Assign, LoopWhile, LoopDoUntil, BranchIf]