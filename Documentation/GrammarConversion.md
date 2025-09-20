# CompilerSPL
---
## Grammar G
---
SPL_PROG    ::= glob { VARIABLES } proc { PROCDEFS } func { FUNCDEFS } main { MAINPROG }

VARIABLES   ::= 
VARIABLES   ::= VAR VARIABLES

VAR         ::= user-defined-name 

NAME        ::= user-defined-name

PROCDEFS    ::= 
PROCDEFS    ::= PDEF PROCDEFS

PDEF        ::= NAME ( PARAM ) { BODY }

FDEF        ::= NAME ( PARAM ) { BODY ; return ATOM }

FUNCDEFS    ::= FDEF FUNCDEFS
FUNCDEFS    ::= 

BODY        ::= local { MAXTHREE } ALGO 

PARAM       ::= MAXTHREE 

MAXTHREE    ::= 
MAXTHREE    ::= VAR
MAXTHREE    ::= VAR VAR
MAXTHREE    ::= VAR VAR VAR

MAINPROG    ::= var { VARIABLES } ALGO

ATOM        ::= VAR
ATOM        ::= number 

ALGO        ::= INSTR 
ALGO        ::= INSTR ; ALGO

INSTR       ::= halt
INSTR       ::= print OUTPUT
INSTR       ::= NAME ( INPUT )          //procedure call
INSTR       ::= ASSIGN
INSTR       ::= LOOP
INSTR       ::= BRANCH

ASSIGN      ::= VAR = NAME ( INPUT )    //function call
ASSIGN      ::= VAR = TERM

LOOP        ::= while TERM { ALGO }
LOOP        ::= do { ALGO } until TERM

BRANCH      ::= if TERM { ALGO }
BRANCH      ::= if TERM { ALGO } else { ALGO }

OUTPUT      ::= ATOM
OUTPUT      ::= string

INPUT       ::= 
INPUT       ::= ATOM
INPUT       ::= ATOM ATOM
INPUT       ::= ATOM ATOM ATOM 

TERM        ::= ATOM
TERM        ::= ( UNOP TERM )
TERM        ::= ( TERM BINOP TERM )

UNOP        ::= neg
UNOP        ::= not

BINOP       ::= eq
BINOP       ::= >
BINOP       ::= or
BINOP       ::= and
BINOP       ::= plus
BINOP       ::= minus
BINOP       ::= mult
BINOP       ::= div


## Suitability of Grammar G for LL(1) Parsing
---
In the original grammar G, several productions exhibit FIRST/FIRST conflicts that make the grammar unsuitable for LL(1) parsing:
(i) ALGO → INSTR | INSTR ; ALGO (both branches begin with FIRST(INSTR)),
(ii) INPUT and MAXTHREE where multiple alternatives begin with the same token class (ATOM/VAR), and
(iii) ASSIGN where both alternatives begin with VAR.
These violate the LL(1) requirements that for any A → α | β, FIRST(α) ∩ FIRST(β) = ∅, and if ε ∈ FIRST(α) then FIRST(β) ∩ FOLLOW(A) = ∅. We therefore refactor G into an equivalent LL(1)-friendly grammar G′ by introducing tail nonterminals (for lists), consolidating bounded lists (0..3) without ambiguous prefixes, and left-factoring common prefixes.

## Alternative Grammar G' in EBNF shorthand 
---
SPL_PROG    ::= glob { VARIABLES } proc { PROCDEFS } func { FUNCDEFS } main { MAINPROG }

VARIABLES   ::= (VAR)*

VAR         ::= IDENT               // user-defined name (not a keyword)
NAME        ::= IDENT

PROCDEFS    ::= (PDEF)*

PDEF        ::= NAME ( PARAM ) { BODY }

FDEF        ::= NAME ( PARAM ) { BODY ; return ATOM }

FUNCDEFS    ::= (FDEF)*

BODY        ::= local { MAXTHREE } ALGO

PARAM       ::= MAXTHREE

MAXTHREE    ::= (VAR (VAR (VAR)?)?)?    // up to 3 variables

MAINPROG    ::= var { VARIABLES } ALGO

ATOM        ::= VAR
ATOM        ::= NUMBER

ALGO        ::= INSTR ( ; INSTR )*          // sequence of ≥1 instructions

INSTR       ::= halt
INSTR       ::= print OUTPUT
INSTR       ::= NAME ( INPUT )             // procedure call
INSTR       ::= ASSIGN
INSTR       ::= LOOP
INSTR       ::= BRANCH

ASSIGN      ::= VAR = NAME ( INPUT )      // function call assignment
ASSIGN      ::= VAR = TERM                // plain expression assignment

LOOP        ::= while TERM { ALGO }
LOOP        ::= do { ALGO } until TERM

BRANCH      ::= if TERM { ALGO }
BRANCH      ::= if TERM { ALGO } else { ALGO }

OUTPUT      ::= ATOM
OUTPUT      ::= STRING

INPUT       ::= (ATOM (ATOM (ATOM)?)?)?    // up to 3 atoms, optional

TERM        ::= ATOM
TERM        ::= ( UNOP TERM )
TERM        ::= ( TERM BINOP TERM )

UNOP        ::= neg
UNOP        ::= not

BINOP       ::= eq
BINOP       ::= GT
BINOP       ::= or
BINOP       ::= and
BINOP       ::= plus
BINOP       ::= minus
BINOP       ::= mult
BINOP       ::= div

## Alternative Grammar G' in pure CFG form 
---
// Top Level
SPL_PROG    ::= glob { VARIABLES } proc { PROCDEFS } func { FUNCDEFS } main { MAINPROG }


// Variable list
VARIABLES   ::= VAR VARIABLES
VARIABLES   ::= ε
VAR         ::= IDENT
NAME        ::= IDENT


// Procedures and functions
PROCDEFS    ::= PDEF PROCDEFS
PROCDEFS    ::= ε

PDEF        ::= NAME ( PARAM ) { BODY }

FUNCDEFS    ::= FDEF FUNCDEFS
FUNCDEFS    ::= ε

FDEF        ::= NAME ( PARAM ) { BODY ; return ATOM }


// Bodies and params 
BODY        ::= local { MAXTHREE } ALGO
PARAM       ::= MAXTHREE

MAXTHREE    ::= VAR MAXTWO
MAXTHREE    ::= ε

MAXTWO      ::= VAR MAXONE
MAXTWO      ::= ε

MAXONE      ::= VAR
MAXONE      ::= ε


// Main Program 
MAINPROG    ::= var { VARIABLES } ALGO


// Atoms 
ATOM        ::= VAR
ATOM        ::= NUMBER


// Algorithms and instructions 
ALGO        ::= INSTR ALGO_TAIL

ALGO_TAIL   ::= ; INSTR ALGO_TAIL
ALGO_TAIL   ::= ε

INSTR       ::= halt
INSTR       ::= print OUTPUT
INSTR       ::= NAME ( INPUT )
INSTR       ::= ASSIGN
INSTR       ::= LOOP
INSTR       ::= BRANCH


// Assignments 
ASSIGN      ::= VAR = NAME ( INPUT )
ASSIGN      ::= VAR = TERM


// Loops and branches 
LOOP        ::= while TERM { ALGO }
LOOP        ::= do { ALGO } until TERM

BRANCH      ::= if TERM { ALGO }
BRANCH      ::= if TERM { ALGO } else { ALGO }


// Output and input 
OUTPUT      ::= ATOM
OUTPUT      ::= STRING

INPUT       ::= ATOM INPUT_TAIL
INPUT       ::= ε

INPUT_TAIL  ::= ATOM INPUT_TAIL2
INPUT_TAIL  ::= ε

INPUT_TAIL2 ::= ATOM
INPUT_TAIL2 ::= ε


// Terms 
TERM        ::= ATOM
TERM        ::= ( UNOP TERM )
TERM        ::= ( TERM BINOP TERM )

UNOP        ::= neg
UNOP        ::= not

BINOP       ::= eq
BINOP       ::= GT
BINOP       ::= or
BINOP       ::= and
BINOP       ::= plus
BINOP       ::= minus
BINOP       ::= mult
BINOP       ::= div
