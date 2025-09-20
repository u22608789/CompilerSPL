# lexer.py
import re
from .tokens import T, Token, KEYWORDS

IDENT_RE  = re.compile(r'[a-z][a-z0-9]*') # match user defined name - lower-case only
NUM_RE    = re.compile(r'(0|[1-9][0-9]*)') #match number - either a 0 or number not starting with zero 
STR_RE    = re.compile(r'"([A-Za-z0-9]{0,15})"')  # match string literal of max 15 alphanumerical chars  

PUNCT = {'{':T.LBRACE,'}':T.RBRACE,'(':T.LPAREN,')':T.RPAREN,';':T.SEMI,'=':T.ASSIGN,'>':T.GT} #map punctuation

class Lexer:
    def __init__(self, text:str):
        self.s=text; # input text
        self.i=0; # current index 
        self.line=1; # to track position for error message
        self.col=1; # to track position for error message
        self.n=len(text) #total length

    def _peek(self): 
        return self.s[self.i] if self.i<self.n else '\0' #return current character without consuming it. Return \0 if past end. 
    
    def _adv(self, k=1): #advance by k characters 
        for _ in range(k):
            if self.i<self.n:
                ch=self.s[self.i]; self.i+=1
                if ch=='\n': self.line+=1; self.col=1 # move to next line and reset column 
                else: self.col+=1 # move to next column 

    # skip white space (spaces, tabs, newlines)
    def _skip_ws(self):
        while self.i<self.n and self._peek().isspace():
            self._adv()

    # go to next token 
    def next_token(self)->Token:
        self._skip_ws() #skip white space 
        if self.i>=self.n: return Token(T.EOF,'',self.line,self.col) # if at end of input, return EOF token

        ch=self._peek() #look at next character to decide what token type it starts 

        # punctuators ({ } ( ) ; = >)
        if ch in PUNCT:
            t=PUNCT[ch]; 
            tok=Token(t,ch,self.line,self.col); self._adv(); 
            return tok

        # string
        if ch=='"':
            m=STR_RE.match(self.s, self.i) # try match full string literal 
            if not m: #if no match (unterminated, too long, invalid chars)
                raise ValueError(f'Invalid string at {self.line}:{self.col} (only alnum, ≤15, closed with ")')
            lex=m.group(0)
            val=m.group(1) #remove quotes
            tok=Token(T.STRING,val,self.line,self.col); self._adv(len(lex)) # emit string token with no quotes and advance by length of string
            return tok

        # number
        m=NUM_RE.match(self.s, self.i) #try match a number
        if m: # if match 
            lex=m.group(0)
            tok=Token(T.NUMBER,lex,self.line,self.col); self._adv(len(lex)) #emit number token and advance by length
            return tok

        # identifier / keyword
        m=IDENT_RE.match(self.s, self.i) #try to match a user defined name 
        if m: #if match 
            lex=m.group(0)
            if lex in KEYWORDS: # if its a keyword 
                tok=Token(KEYWORDS[lex],lex,self.line,self.col) # emit that keyword token
            else: 
                tok=Token(T.IDENT,lex,self.line,self.col) # otherwise emit as a user defined name / identifier
            self._adv(len(lex)) #advance by length of of match
            return tok

        #if no rule matches
        raise ValueError(f'Unknown character "{ch}" at {self.line}:{self.col}')
