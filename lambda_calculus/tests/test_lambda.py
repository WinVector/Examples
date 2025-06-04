import pytest
from lambda_calc import *
from lambda_calc import _r_convert_deBruijn_codes, _DeBruijnIndex, _Variable


def check_expr(expr: Term, *, expect: str | Term | None = None):
    """expect str built by repr(), expect None means don't check expect"""
    assert isinstance(expr, Term)
    assert expr == expr
    assert not expr < expr
    assert expr != expr | v("a")
    source = repr(expr)
    parsed = parse_l(source)
    assert isinstance(parsed, Term)
    assert expr == parsed
    str1 = str(expr)
    str2 = str(parsed)
    assert str1 == str2
    if expect is not None:
        if isinstance(expect, str):
            expect = parse_l(expect)
        check_expr(expect)
        assert expr == expect
        assert repr(expr) == repr(expect)


def test_atoms():
    with pytest.raises(ValueError):
        v(None)
    with pytest.raises(ValueError):
        v(())
    assert isinstance(v("x"), _Variable)
    assert isinstance(v(1), _DeBruijnIndex)


def test_bar_parens():
    check_expr(v(("a")), expect=v("a"))
    check_expr(v(("a", "b")), expect=v("a", "b"))
    check_expr(v("a") | "b", expect=v("a", "b"))
    check_expr(v(("a", "b", "c")), expect=v("a", "b", "c"))
    check_expr(v("a") | "b" | "c", expect=v("a", "b", "c"))


def test_lc():
    check_expr(
        v([f"a_{i}" for i in range(5)]),
        expect="v((((('a_0', 'a_1'), 'a_2'), 'a_3'), 'a_4'))",
    )


def test_call():
    check_expr(
        λ["x"]("x")("a", "b", "c"), expect=λ["x"]("x") | (v("a") | v("b") | v("c"))
    )
    assert λ["x"]("x")("a", "b", "c") != λ["x"]("x") | v("a") | v("b") | v("c")


def test_rc():
    check_expr(
        vr([f"a_{i}" for i in range(5)]),
        expect="v(('a_0', ('a_1', ('a_2', ('a_3', 'a_4')))))",
    )


def test_subst():
    new_name_source = NewNameSource(nms=("x", "y", "y", "v"))
    check_expr(
        (λ["x"]("x") | "y" | "x")._capture_avoiding_substitution(
            var=v("x"), t=v("h"), new_name_source=new_name_source
        ),
        expect=λ["x"]("x") | "y" | "h",
    )
    check_expr(
        λ["x"]("y")._capture_avoiding_substitution(
            var=v("x"), t=v("y"), new_name_source=new_name_source
        ),
        expect=λ["x"]("y"),
    )
    check_expr(
        λ["x"]("y")._capture_avoiding_substitution(
            var=v("x"), t=v("x"), new_name_source=new_name_source
        ),
        expect=λ["x"]("y"),
    )
    check_expr(
        λ["x"]("y")._capture_avoiding_substitution(
            var=v("y"), t=v("x"), new_name_source=new_name_source
        ),
        expect=λ["v0"]("x"),  # saw name change
    )


def test_beta():
    check_expr(
        ((λ["x"](λ["x"]("x") | "q" | "y" | "x")) | "N").nf()[0],
        expect=v((("q", "y"), "N")),
    )


def test_cn():
    check_expr(N(0), expect=λ["f"](λ["x"]("x")))
    check_expr(N(1), expect=λ["f"](λ["x"]("f", "x")))
    check_expr(N(2), expect=λ["f"](λ["x"]("f", ("f", "x"))))
    check_expr(N(3), expect=λ["f"](λ["x"]("f", ("f", ("f", "x")))))
    for i in range(11):
        check_expr(N(i))
        check_expr(N(i).nf()[0], expect=N(i))


def test_successor():
    for i in range(11):
        check_expr((SUCC | N(i)).nf()[0], expect=N(i + 1))


def test_addition():
    for i in range(10):
        for j in range(10):
            check_expr(
                v([PLUS, N(i), N(j)]).nf()[0],
                expect=N(i + j),
            )


def test_predecessor():
    check_expr((PRED | N(0)).nf()[0], expect=N(0))
    for i in range(11):
        check_expr((PRED | N(i + 1)).nf()[0], expect=N(i))


def test_subtraction():
    for i in range(10):
        for j in range(10):
            check_expr(
                v([SUB, N(i), N(j)]).nf()[0],
                expect=N(max(0, i - j)),
            )


def test_pairs():
    check_expr(v((FIRST, v((PAIR, "aaa", "bbb")))).nf()[0], expect=v("aaa"))
    check_expr(v((SECOND, v((PAIR, "aaa", "bbb")))).nf()[0], expect=v("bbb"))


def test_avoid_name_collision():
    # a harder example
    assert "v0" not in repr(FACTORIALstep)
    fnf = FACTORIALstep.nf()[0]
    assert "v0" in repr(fnf)
    check_expr(fnf.nf()[0], expect=fnf)


def test_nf():
    # value style items should be in normal form, same for conditionals
    for expr in [TRUE, FALSE, isZERO]:
        check_expr(expr.nf()[0], expect=expr)


def test_db_decoding():
    # https://en.wikipedia.org/wiki/De_Bruijn_index
    example = λ(λ(1, λ(1)), λ(2, 1))
    check_expr(
        _r_convert_deBruijn_codes(example, variables=[], next_variable_index=[1]),
        expect=λ["x1"](λ["x2"]("x2", λ["x3"]("x3")), λ["x4"]("x1", "x4")),
    )


def test_binary_parse():
    # https://tromp.github.io/cl/Binary_lambda_calculus.html#binary_io
    example = "00 00 00 01 01 10 1110 110"
    parsed = read_zero_one_code(example)
    check_expr(parsed, expect=λ["x1"](λ["x2"](λ["x3"](("x3", "x1"), "x2"))))


def test_nf_identity():
    # u has a beta reduction, but it takes u to u
    u = λ["x"]("x", "x") | λ["x"]("x", "x")
    nf, steps = u.nf()
    check_expr(u, expect=nf)


def test_skip_identity_transform():
    # skip past trivial beta reduction to on later term
    u = λ["z"](λ["x"]("x", "x") | λ["x"]("x", "x") | (λ["x"]("x") | "q"))
    nf, steps = u.nf()
    check_expr(nf, expect=λ["z"]((λ["x"]("x", "x"), λ["x"]("x", "x")), "q"))


def test_binary_parse_u():
    # https://tromp.github.io/cl/Binary_lambda_calculus.html#universality
    machine_U = """
0101000110100000000101011000000000011110000101111110011110
0001011100111100000011110000101101101110011111000011111000
0101111010011101001011001110000110110000101111100001111100
0011100110111101111100111101110110000110010001101000011010
"""
    p = read_zero_one_code(machine_U)
    check_expr(p)


def test_binary_parse_lambda():
    # https://esolangs.org/wiki/Binary_lambda_calculus#self-interpreter
    # self-iterpreter
    self_interpreter = """
  01010001
   10100000
    00010101
     10000000
      00011110
       00010111
        11100111
         10000101
          11001111
          000000111
         10000101101
        1011100111110
       000111110000101
      11101001 11010010
     11001110   00011011
    00001011     11100001
   11110000       11100110
  11110111         11001111
 01110110           00011001
00011010             00011010
"""
    p = read_zero_one_code(self_interpreter)
    check_expr(p)


def test_binary_parse_prime():
    # https://esolangs.org/wiki/Binary_lambda_calculus#self-interpreter
    prime_sieve = """
000100011001100101000110100
 000000101100000100100010101
 11110111          101001000
 11010000          111001101
 000000000010110111001110011
 11111011110000000011111001
 10111000
 00010110
0000110110
"""
    p = read_zero_one_code(prime_sieve)
    check_expr(p)


def test_blinker():
    a = λ["x", "y"]("y", "x", "y")
    blinker = a | a | a
    assert blinker != blinker.r()
    check_expr(blinker.r().r(), expect=blinker)


def test_eself():
    a = λ["x"]("x", "x")
    eself = a | a
    assert eself == eself.r()
    assert eself.nf()[0] == eself  # show application does not prevent finding normal form


def test_div():
    dividend = N(14)
    divisor = N(3)
    expr = DIV | dividend | divisor
    res = expr.nf()[0]
    quotient = (CAR | res).nf()[0]
    assert quotient == N(4)
    remainder = (CDR | res).nf()[0]
    assert remainder == N(2)
    check = (PLUS | (MULT | quotient | divisor) | remainder).nf()[0]
    assert check == dividend


def test_gcd():
    expr = GCD | N(6) | N(9)
    result, _ = expr.nf()
    assert result == N(3)
    expr = GCD | N(9) | N(6)
    result, _ = expr.nf()
    assert result == N(3)
