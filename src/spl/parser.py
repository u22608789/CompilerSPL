# parser.py
from .tokens import T, Token
from .astnodes import *
from .lexer import Lexer

# Tokens that can begin an instruction
INSTR_START = {T.HALT, T.PRINT, T.IDENT, T.WHILE, T.DO, T.IF}


class Parser:
    def __init__(self, text: str):
        self.lexer = Lexer(text)
        # prime 2-token lookahead
        self.cur = self.lexer.next_token()
        self.nxt = self.lexer.next_token()

    # --- low-level token helpers -------------------------------------------------

    def _advance(self):
        self.cur = self.nxt
        self.nxt = self.lexer.next_token()

    def _eat(self, typ: T) -> Token:
        if self.cur.typ != typ:
            raise SyntaxError(
                f'expected {typ.name}, found {self.cur.typ.name} at {self.cur.line}:{self.cur.col}'
            )
        tok = self.cur
        self._advance()
        return tok

    def _match(self, typ: T) -> bool:
        if self.cur.typ == typ:
            self._advance()
            return True
        return False

    # --- entrypoint --------------------------------------------------------------

    def parse(self) -> Program:
        # SPL_PROG ::= glob { VARIABLES } proc { PROCDEFS } func { FUNCDEFS } main { MAINPROG }
        self._eat(T.GLOB)
        self._eat(T.LBRACE)
        globals_ = self._variables()
        self._eat(T.RBRACE)

        self._eat(T.PROC)
        self._eat(T.LBRACE)
        procs = self._procdefs()
        self._eat(T.RBRACE)

        self._eat(T.FUNC)
        self._eat(T.LBRACE)
        funcs = self._funcdefs()
        self._eat(T.RBRACE)

        self._eat(T.MAIN)
        self._eat(T.LBRACE)
        main = self._mainprog()
        self._eat(T.RBRACE)

        self._eat(T.EOF)
        return Program(globals_, procs, funcs, main)

    # --- small list helpers ------------------------------------------------------

    # VARIABLES -> (VAR)*
    def _variables(self) -> list[str]:
        names = []
        while self.cur.typ == T.IDENT:  # VAR ::= user-defined-name (lexer ensures not keyword)
            names.append(self._eat(T.IDENT).lexeme)
        return names

    # PROCDEFS -> (PDEF)*
    def _procdefs(self) -> list[ProcDef]:
        acc = []
        while self.cur.typ == T.IDENT:
            acc.append(self._pdef())
        return acc

    def _pdef(self) -> ProcDef:
        name = self._eat(T.IDENT).lexeme
        self._eat(T.LPAREN)
        params = self._param()
        self._eat(T.RPAREN)
        self._eat(T.LBRACE)
        body = self._body()
        self._eat(T.RBRACE)
        return ProcDef(name, params, body)

    # FUNCDEFS -> (FDEF)*
    def _funcdefs(self) -> list[FuncDef]:
        acc = []
        while self.cur.typ == T.IDENT:
            acc.append(self._fdef())
        return acc

    def _fdef(self) -> FuncDef:
        name = self._eat(T.IDENT).lexeme
        self._eat(T.LPAREN)
        params = self._param()
        self._eat(T.RPAREN)
        self._eat(T.LBRACE)
        body = self._body()
        self._eat(T.SEMI)          # the ';' that precedes 'return'
        self._eat(T.RETURN)
        ret = self._atom()
        self._eat(T.RBRACE)
        return FuncDef(name, params, body, ret)

    def _body(self) -> Body:
        self._eat(T.LOCAL)
        self._eat(T.LBRACE)
        locals_ = self._maxthree_vars()
        self._eat(T.RBRACE)
        algo = self._algo()
        return Body(locals_, algo)

    def _param(self) -> list[str]:
        return self._maxthree_vars()

    # MAXTHREE -> (VAR (VAR (VAR)?)?)?
    def _maxthree_vars(self) -> list[str]:
        names = []
        for _ in range(3):
            if self.cur.typ == T.IDENT:
                names.append(self._eat(T.IDENT).lexeme)
            else:
                break
        return names

    def _mainprog(self) -> Main:
        self._eat(T.VAR)
        self._eat(T.LBRACE)
        locals_ = self._variables()
        self._eat(T.RBRACE)
        algo = self._algo()
        return Main(locals_, algo)

    # --- ALGO / INSTR ------------------------------------------------------------

    # ALGO -> INSTR (';' INSTR)*
    # Guard the repetition so we don't steal the ';' that belongs to ' ; return ' in FDEF.
    def _algo(self) -> Algo:
        instrs = [self._instr()]
        while self.cur.typ == T.SEMI and self.nxt.typ in INSTR_START:
            self._eat(T.SEMI)
            instrs.append(self._instr())
        return Algo(instrs)

    def _instr(self):
        t = self.cur.typ

        if t == T.HALT:
            self._eat(T.HALT)
            return Halt()

        if t == T.PRINT:
            self._eat(T.PRINT)
            out = self._output()
            return Print(out)

        if t == T.IDENT:
            # Could be:
            #   NAME '(' INPUT ')'                 (proc call)
            #   VAR '=' NAME '(' INPUT ')'         (assign func call)
            #   VAR '=' TERM                       (assign general term)
            name = self._eat(T.IDENT).lexeme

            if self.cur.typ == T.LPAREN:
                # proc call: NAME '(' INPUT ')'
                self._eat(T.LPAREN)
                args = self._input_atoms()
                self._eat(T.RPAREN)
                return Call(name, args)

            if self.cur.typ == T.ASSIGN:
                # assignment: VAR '=' ...
                self._eat(T.ASSIGN)

                # After '=', three shapes are possible:
                # 1) '(' ... ')'         -> TERM (parenthesized unary/binary/term)
                # 2) IDENT '(' ... ')'   -> function call on RHS
                # 3) IDENT or NUMBER     -> ATOM (plain term)
                if self.cur.typ == T.LPAREN:
                    rhs = self._term()
                    return Assign(var=name, rhs=rhs)

                if self.cur.typ == T.IDENT:
                    fname = self._eat(T.IDENT).lexeme
                    if self.cur.typ == T.LPAREN:
                        self._eat(T.LPAREN)
                        args = self._input_atoms()
                        self._eat(T.RPAREN)
                        return Assign(var=name, rhs=Call(fname, args))
                    else:
                        return Assign(var=name, rhs=TermAtom(VarRef(fname)))

                if self.cur.typ == T.NUMBER:
                    num = int(self._eat(T.NUMBER).lexeme)
                    return Assign(var=name, rhs=TermAtom(NumberLit(num)))

                # Anything else after '=': delegate to term parser (will raise if invalid)
                rhs = self._term()
                return Assign(var=name, rhs=rhs)

            # IDENT not followed by '(' or '=' is invalid as a statement
            raise SyntaxError(
                f'unexpected IDENT in statement at {self.cur.line}:{self.cur.col}'
            )

        if t == T.WHILE:
            self._eat(T.WHILE)
            cond = self._term()
            self._eat(T.LBRACE)
            body = self._algo()
            self._eat(T.RBRACE)
            return LoopWhile(cond, body)

        if t == T.DO:
            self._eat(T.DO)
            self._eat(T.LBRACE)
            body = self._algo()
            self._eat(T.RBRACE)
            self._eat(T.UNTIL)
            cond = self._term()
            return LoopDoUntil(body, cond)

        if t == T.IF:
            self._eat(T.IF)
            cond = self._term()
            self._eat(T.LBRACE)
            then = self._algo()
            self._eat(T.RBRACE)
            if self._match(T.ELSE):
                self._eat(T.LBRACE)
                els = self._algo()
                self._eat(T.RBRACE)
                return BranchIf(cond, then, els)
            return BranchIf(cond, then, None)

        raise SyntaxError(
            f'unexpected token {t.name} at {self.cur.line}:{self.cur.col}'
        )

    # --- small nonterminals ------------------------------------------------------

    # OUTPUT -> ATOM | STRING
    def _output(self):
        if self.cur.typ == T.STRING:
            s = self.cur.lexeme
            self._eat(T.STRING)
            return StringLit(s)
        return self._atom()

    # INPUT -> 0..3 ATOM (bounded list)
    def _input_atoms(self) -> list[Atom]:
        args = []
        for _ in range(3):
            if self.cur.typ in (T.IDENT, T.NUMBER):
                args.append(self._atom())
            else:
                break
        return args

    # TERM -> ATOM | '(' UNOP TERM ')' | '(' TERM BINOP TERM ')'
    def _term(self):
        if self.cur.typ in (T.IDENT, T.NUMBER):
            return TermAtom(self._atom())

        self._eat(T.LPAREN)

        if self.cur.typ in (T.NEG, T.NOT):
            op = self.cur.lexeme
            self._eat(self.cur.typ)
            t = self._term()
            self._eat(T.RPAREN)
            return TermUn(op, t)

        # ( TERM BINOP TERM )
        left = self._term()
        op_tok = self.cur  # eq, >, or, and, plus, minus, mult, div
        if op_tok.typ not in (T.EQ, T.GT, T.OR, T.AND, T.PLUS, T.MINUS, T.MULT, T.DIV):
            raise SyntaxError(f'expected binary op at {op_tok.line}:{op_tok.col}')
        op = op_tok.lexeme
        self._eat(op_tok.typ)
        right = self._term()
        self._eat(T.RPAREN)
        return TermBin(left, op, right)

    def _atom(self):
        if self.cur.typ == T.IDENT:
            return VarRef(self._eat(T.IDENT).lexeme)
        if self.cur.typ == T.NUMBER:
            return NumberLit(int(self._eat(T.NUMBER).lexeme))
        raise SyntaxError(f'expected ATOM at {self.cur.line}:{self.cur.col}')
