# astnodes.py
from dataclasses import dataclass
from typing import List, Optional, Union


@dataclass
class Program:
    globals: List[str]
    procs: List['ProcDef']
    funcs: List['FuncDef']
    main: 'Main'


@dataclass 
class ProcDef: 
    name: str
    params: List[str]
    body: 'Body'


@dataclass 
class FuncDef: 
    name: str
    params: List[str]
    body: 'Body'
    ret: 'Atom'


@dataclass 
class Body: 
    locals: List[str]
    algo: 'Algo'


@dataclass 
class Main: 
    locals: List[str]
    algo: 'Algo'

# Statements / expressions
@dataclass 
class Algo: 
    instrs: List['Instr']

@dataclass 
class Assign: 
    var: str
    rhs: Union['Call', 'Term']


@dataclass 
class Call: 
    name: str
    args: List['Atom']    # proc call (stmt) or func call (expr context)


@dataclass 
class LoopWhile: 
    cond: 'Term'
    body: 'Algo'


@dataclass 
class LoopDoUntil: 
    body: 'Algo'
    cond: 'Term'


@dataclass 
class BranchIf: 
    cond: 'Term'
    then_: 'Algo'
    else_: Optional['Algo']


@dataclass 
class Print: 
    out: Union['Atom', 'StringLit']

@dataclass 
class Halt: 
    pass

# Terms / atoms
Atom = Union['VarRef', 'NumberLit']

@dataclass 
class VarRef: 
    name: str

@dataclass 
class NumberLit: 
    value: int

@dataclass 
class StringLit: 
    value: str

@dataclass 
class TermAtom: 
    atom: Atom

@dataclass 
class TermUn: 
    op: str
    term: 'Term'


@dataclass 
class TermBin: 
    left: 'Term'
    op: str
    right: 'Term'

Term = Union[TermAtom, TermUn, TermBin]
Instr = Union[Assign, Call, LoopWhile, LoopDoUntil, BranchIf, Print, Halt]
