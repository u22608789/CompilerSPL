# tests/test_lexer_basic.py
import pytest
from spl.tokens import T
from spl.lexer import Lexer


def toks(text):
    lx = Lexer(text)
    out = []
    while True:
        t = lx.next_token()
        out.append(t)
        if t.typ == T.EOF:
            break
    return out


def types(text):
    return [t.typ for t in toks(text)]


def lexemes(text):
    return [t.lexeme for t in toks(text)]


# 1) Keywords vs identifiers
def test_keywords_and_idents():
    ts = toks(
        "glob main var return if else while do until print halt neg not eq or and plus minus mult div >")
    # Just check the first few and the last operator
    assert ts[0].typ == T.GLOB
    assert ts[1].typ == T.MAIN
    assert ts[2].typ == T.VAR
    assert ts[3].typ == T.RETURN
    assert ts[-3].typ == T.DIV
    assert ts[-2].typ == T.GT
    assert ts[-1].typ == T.EOF

    # Identifier that looks similar but isn't a keyword
    ts2 = toks("globe var1 eqeq plus1")
    assert [t.typ for t in ts2[:4]] == [T.IDENT, T.IDENT, T.IDENT, T.IDENT]
    assert [t.lexeme for t in ts2[:4]] == ["globe", "var1", "eqeq", "plus1"]


# 2) Numbers (0 or nonzero start; no leading zeros like 01)
def test_numbers_valid_and_tokenization():
    ts = toks("0 7 42 999")
    assert [t.typ for t in ts[:4]] == [T.NUMBER, T.NUMBER, T.NUMBER, T.NUMBER]
    assert [t.lexeme for t in ts[:4]] == ["0", "7", "42", "999"]

    # "01" should be tokenized as NUMBER("0") then IDENT("1") won't match;
    # actually "1" starts a NUMBER, so you'll get NUMBER("0"), NUMBER("1")
    ts2 = toks("01")
    assert [t.typ for t in ts2[:2]] == [T.NUMBER, T.NUMBER]
    assert [t.lexeme for t in ts2[:2]] == ["0", "1"]


# 3) Strings (alnum only, max 15, must close)
def test_strings_valid():
    ts = toks('"OK" "abc123" "A1B2C3" ""')
    assert [t.typ for t in ts[:4]] == [T.STRING, T.STRING, T.STRING, T.STRING]
    assert [t.lexeme for t in ts[:4]] == ["OK", "abc123", "A1B2C3", ""]


def test_strings_invalid_non_alnum():
    with pytest.raises(ValueError):
        toks('"ab_cd"')   # underscore not allowed by spec
    with pytest.raises(ValueError):
        toks('"space here"')  # space not allowed


def test_strings_invalid_too_long():
    long15 = "A"*15
    ok = toks(f'"{long15}"')
    assert ok[0].typ == T.STRING and ok[0].lexeme == long15
    with pytest.raises(ValueError):
        toks('"ABCDEFGHIJKLMNOP"')  # 16 chars


def test_strings_unterminated():
    with pytest.raises(ValueError):
        toks('"unterminated')


# 4) Punctuation and single-char operators
def test_punct_and_ops():
    text = "{ } ( ) ; = >"
    tt = types(text)
    assert tt[:7] == [T.LBRACE, T.RBRACE,
                      T.LPAREN, T.RPAREN, T.SEMI, T.ASSIGN, T.GT]


# 5) Whitespace and positions (line/col)
def test_whitespace_and_positions():
    text = "glob  { \n  x   \n}\n"
    ts = toks(text)
    # glob at line 1, col 1
    assert ts[0].typ == T.GLOB and ts[0].line == 1 and ts[0].col == 1
    # { at line 1 (after spaces), col should be where '{' occurs (here: 7)
    assert ts[1].typ == T.LBRACE and ts[1].line == 1
    # x at line 2, after two spaces -> col 3
    assert ts[2].typ == T.IDENT and ts[2].lexeme == "x" and ts[2].line == 2 and ts[2].col == 3
    # } at line 3, col 1
    assert ts[3].typ == T.RBRACE and ts[3].line == 3 and ts[3].col == 1
    assert ts[-1].typ == T.EOF


# 6) Mini program smoke test
def test_mini_program_smoke():
    prog = """
glob { x y }
proc { p(x) { local { } halt } }
func { f(a b) { local { z } print "OK1" ; return a } }
main { var { t }
  print 0;
  t = ( (t plus 1) );
  if ( (t eq 0) ) { halt } else { print "X" }
}
"""
    tt = types(prog)
    assert T.GLOB in tt and T.MAIN in tt and T.PRINT in tt and T.HALT in tt
    assert tt[-1] == T.EOF
