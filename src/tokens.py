# tokens.py
from enum import Enum, auto
from dataclasses import dataclass

class T(Enum):
    # punctuation
    LBRACE=auto(); RBRACE=auto(); LPAREN=auto(); RPAREN=auto(); SEMI=auto(); ASSIGN=auto()
    # keywords
    GLOB=auto(); PROC=auto(); FUNC=auto(); MAIN=auto(); LOCAL=auto(); VAR=auto(); RETURN=auto()
    HALT=auto(); PRINT=auto(); WHILE=auto(); DO=auto(); UNTIL=auto(); IF=auto(); ELSE=auto()
    NEG=auto(); NOT=auto(); EQ=auto(); OR=auto(); AND=auto(); PLUS=auto(); MINUS=auto(); MULT=auto(); DIV=auto(); GT=auto()
    # literals
    IDENT=auto(); NUMBER=auto(); STRING=auto()
    EOF=auto()

KEYWORDS = {
  "glob":T.GLOB,"proc":T.PROC,"func":T.FUNC,"main":T.MAIN,"local":T.LOCAL,"var":T.VAR,"return":T.RETURN,
  "halt":T.HALT,"print":T.PRINT,"while":T.WHILE,"do":T.DO,"until":T.UNTIL,"if":T.IF,"else":T.ELSE,
  "neg":T.NEG,"not":T.NOT,"eq":T.EQ,"or":T.OR,"and":T.AND,"plus":T.PLUS,"minus":T.MINUS,"mult":T.MULT,"div":T.DIV,
}

@dataclass
class Token:
    typ: T
    lexeme: str
    line: int
    col: int
