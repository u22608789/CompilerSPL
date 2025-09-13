# lexer.py
import re
from tokens import T, Token, KEYWORDS

IDENT_RE  = re.compile(r'[a-z][a-z0-9]*')    # lower-case only, per spec
NUM_RE    = re.compile(r'(0|[1-9][0-9]*)')
STR_RE    = re.compile(r'"([A-Za-z0-9]{0,15})"')  # ≤ 15 alnum chars

PUNCT = {'{':T.LBRACE,'}':T.RBRACE,'(':T.LPAREN,')':T.RPAREN,';':T.SEMI,'=':T.ASSIGN,'>':T.GT}

class Lexer:
    def __init__(self, text:str):
        self.s=text; self.i=0; self.line=1; self.col=1; self.n=len(text)

    def _peek(self): return self.s[self.i] if self.i<self.n else '\0'
    def _adv(self, k=1):
        for _ in range(k):
            if self.i<self.n:
                ch=self.s[self.i]; self.i+=1
                if ch=='\n': self.line+=1; self.col=1
                else: self.col+=1

    def _skip_ws(self):
        while self.i<self.n and self._peek().isspace():
            self._adv()

    def next_token(self)->Token:
        self._skip_ws()
        if self.i>=self.n: return Token(T.EOF,'',self.line,self.col)

        ch=self._peek()

        # punctuators
        if ch in PUNCT:
            t=PUNCT[ch]; tok=Token(t,ch,self.line,self.col); self._adv(); return tok

        # string
        if ch=='"':
            m=STR_RE.match(self.s, self.i)
            if not m:
                raise ValueError(f'Invalid string at {self.line}:{self.col} (only alnum, ≤15, closed with ")')
            lex=m.group(0); val=m.group(1)
            tok=Token(T.STRING,val,self.line,self.col); self._adv(len(lex)); return tok

        # number
        m=NUM_RE.match(self.s, self.i)
        if m:
            lex=m.group(0); tok=Token(T.NUMBER,lex,self.line,self.col); self._adv(len(lex)); return tok

        # identifier / keyword
        m=IDENT_RE.match(self.s, self.i)
        if m:
            lex=m.group(0)
            # keyword?
            if lex in KEYWORDS: tok=Token(KEYWORDS[lex],lex,self.line,self.col)
            else: tok=Token(T.IDENT,lex,self.line,self.col)
            self._adv(len(lex)); return tok

        raise ValueError(f'Unknown character "{ch}" at {self.line}:{self.col}')
