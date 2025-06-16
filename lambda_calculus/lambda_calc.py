from dataclasses import dataclass
from functools import total_ordering
import re
from typing import FrozenSet, Iterable, List, Optional, Set, Tuple
import string
from abc import ABC, abstractmethod

import inspect
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from IPython.display import display, HTML

from TransitiveCache import TransitiveCache



string_repr_map = dict()
latex_repr_map = dict()


def _mk_abstraction(*, variable, term, eager: bool):
    assert isinstance(variable, _Variable)
    assert isinstance(term, Term)
    names = frozenset(variable.names.union(term.names))
    free_names = frozenset(term.free_names - variable.names)
    return _Abstraction(
        variable=variable,
        term=term,
        names=names,
        free_names=free_names,
        _hash_val=hash(variable) + 3 * hash(term) + 5 * hash(tuple(sorted(names))) + 7 * hash(tuple(sorted(free_names))),
        eager=eager,
    )


def _mk_composition(*, left, right):
    assert isinstance(left, Term)
    assert isinstance(right, Term)
    names = frozenset(left.names.union(right.names))
    free_names = frozenset(left.free_names.union(right.free_names))
    return _Composition(
        left=left,
        right=right,
        names=names,
        free_names=free_names,
        _hash_val=hash(left) + 3 * hash(right) + 5 * hash(tuple(sorted(names))) + 7 * hash(tuple(sorted(free_names))),
    )


@total_ordering
@dataclass(frozen=True, kw_only=True)
class Term(ABC):
    """Represent a term in a lambda calculus expression"""
    names: FrozenSet[str]
    free_names: FrozenSet[str]

    @abstractmethod
    def _capture_avoiding_substitution(
        self, *, var: "_Variable", t: "Term", new_name_source: "NewNameSource"
    ) -> "Term":
        """Apply capture avoiding substitution var replaced with t (renaming as needed, needs list of all names to avoid)"""

    @abstractmethod
    def _normal_order_beta_reduction(
        self, *, new_name_source: "NewNameSource", tc: TransitiveCache | None
    ) -> Tuple["Term", bool]:
        """internal method for reduction step, needs list of all names to avoid"""

    def r(self, *, n : int = 1, tc : TransitiveCache | None = None) -> "Term":
        """run n beta reduction step(s) in normal order (top left FIRST)"""
        assert isinstance(n, int)
        for i in range(n):
            red, _ = self._normal_order_beta_reduction(
                new_name_source=NewNameSource(self.names),
                tc=tc,
            )
        return red

    def nf(self, *, max_steps : int | None = None, tc : TransitiveCache | None = None) -> Tuple["Term", int]:
        """reduce to normal form"""
        assert isinstance(max_steps, int | None)
        steps = 0
        new_name_source = NewNameSource(self.names)
        seen = set()
        e = self
        while True:
            if e in seen:
                raise ValueError("cycle")
            seen.add(e)
            e, acted = e._normal_order_beta_reduction(new_name_source=new_name_source, tc=tc)
            if not acted:
                return e, steps
            steps = steps + 1
            if (max_steps is not None) and (steps > max_steps):
                raise ValueError("max_steps exceeded")

    @abstractmethod
    def to_latex(
        self, *, not_expanded: Set | None = None, top_level: bool = False
    ) -> str:
        """convert to to_latex, no substitutions for not_expanded set"""

    def _repr_latex_(self):
        """trigger pretty printing path in Jupyter"""
        return "$$" + self.to_latex(top_level=True) + "$$"

    def __or__(self, other) -> "Term":
        """concatenate/compose"""
        other = v(other)
        return _mk_composition(left=self, right=other)

    def __ror__(self, other) -> "Term":
        """concatenate/compose"""
        other = v(other)
        return _mk_composition(left=other, right=self)

    def __call__(self, *args) -> "_Composition":
        """concatenate/compose allows A(B) as an input for A B"""
        t = v(args)
        assert isinstance(t, Term)
        return _mk_composition(left=self, right=t)

    @abstractmethod
    def __eq__(self, other) -> bool:
        pass

    @abstractmethod
    def __lt__(self, other) -> bool:
        pass


def _eq_helper(a, b) -> bool:
    """See if equality can be resolved by type or hash, return None if same type and hash"""
    if id(a) == id(b):
        return True
    t_a = str(type(a))
    t_b = str(type(b))
    if t_a != t_b:
        return False
    h_a = hash(a)
    h_b = hash(b)
    if h_a != h_b:
        return False
    return None


def _lt_helper(a, b) -> bool:
    """See if order can be resolved by type or hash, return None if same type and hash"""
    if id(a) == id(b):
        return False
    t_a = str(type(a))
    t_b = str(type(b))
    if t_a != t_b:
        return t_a < t_b
    h_a = hash(a)
    h_b = hash(b)
    if h_a != h_b:
        return h_a < h_b
    return None


def _v(x) -> Term:
    """Collect structure to value (left associative)"""
    if x is None:
        raise ValueError("value should not be None")
    if isinstance(x, str):
        x = x.strip()
        return _mk_var(name=x)
    if isinstance(x, Term):
        return x
    # iterable cases
    res = None
    for xi in x:
        if xi is not None:
            xi = _v(xi)
            if res is None:
                res = xi
            else:
                res = _mk_composition(left=res, right=xi)
    if not isinstance(res, Term):
        raise ValueError("empty value list")
    return res


def v(*args) -> Term:
    """Collect structure to value (left associative)"""
    return _v(args)


def _vr(x) -> Term:
    """Collect structure to value (right associative)"""
    if x is None:
        raise ValueError("value should not be None")
    if isinstance(x, str):
        x = x.strip()
        return _mk_var(name=x)
    if isinstance(x, Term):
        return x
    # iterable cases
    res = None
    for xi in reversed(x):
        if xi is not None:
            xi = _vr(xi)
            if res is None:
                res = xi
            else:
                res = _mk_composition(left=xi, right=res)
    if not isinstance(res, Term):
        raise ValueError("empty value list")
    return res


def vr(*args) -> Term:
    """Collect structure to value (right associative)"""
    return _vr(args)


@total_ordering
@dataclass(frozen=True, kw_only=True)
class _Variable(Term):
    """represent a variable"""

    name: str

    def _capture_avoiding_substitution(
        self, *, var: "_Variable", t: "Term", new_name_source: "NewNameSource"
    ) -> "Term":
        assert isinstance(var, _Variable)
        assert isinstance(t, Term)
        if var == t:
            return self  # no op
        if var.name == self.name:
            return t
        return self

    def _normal_order_beta_reduction(
        self, *, new_name_source: "NewNameSource", tc: TransitiveCache | None
    ) -> Tuple["Term", bool]:
        return self, False

    def __eq__(self, other) -> bool:
        e_v = _eq_helper(self, other)
        if e_v is not None:
            return e_v
        # now know same type
        return self.name == other.name

    def __lt__(self, other) -> bool:
        l_v = _lt_helper(self, other)
        if l_v is not None:
            return l_v
        # now know same type
        return self.name < other.name

    def __hash__(self):
        return hash(
            "_Variable" + self.name
        )  # hash NULLed on derived classes that re-define __eq__()

    def __str__(self) -> str:
        return self.name

    def __repr__(self, *, need_v: bool = True) -> str:
        if need_v:
            return f"v('{self.name}')"
        return f"'{self.name}'"

    def to_latex(
        self, *, not_expanded: Set | None = None, top_level: bool = False
    ) -> str:
        return self.name.replace('_', '\\_')


def _mk_var(name: str) -> _Variable:
    assert isinstance(name, str)
    # not as strict as isidentifier()
    assert len(name) > 0
    assert not name.isdecimal()
    assert not any(char in string.whitespace for char in name)
    assert not any(char in "'\"().[];|+-*/%\\λΛε \n" for char in name)
    return _Variable(name=name, names=frozenset([name]), free_names=frozenset([name]))


class NewNameSource:
    """build a new name, disjoint from vars_seen"""

    names_to_avoid: Set[str]
    next_index: int
    prefix: str

    def __init__(
        self,
        nms: Iterable[str] | None = None,
        *,
        prefix: str = "v",
    ):
        assert isinstance(prefix, str)
        self.names_to_avoid = set()
        if nms is not None:
            self.names_to_avoid.update(nms)
        self.next_index = 0
        self.prefix = prefix

    def new_name(self):
        """buld a new name, disjoint from vars_seen"""
        while True:
            new_name = f"{self.prefix}{self.next_index}"
            if new_name not in self.names_to_avoid:
                self.names_to_avoid.add(new_name)
                return new_name
            self.next_index = self.next_index + 1


@total_ordering
@dataclass(frozen=True, kw_only=True)
class _Abstraction(Term):
    """represent (λ(variable).term)"""

    _hash_val: int
    variable: _Variable
    term: Term
    eager: bool

    def __post_init__(self):
        assert isinstance(self.variable, _Variable)
        assert isinstance(self.term, Term)
        assert isinstance(self.eager, bool)

    def _capture_avoiding_substitution(
        self, *, var: "_Variable", t: "Term", new_name_source: "NewNameSource"
    ) -> "Term":
        assert isinstance(var, _Variable)
        assert isinstance(t, Term)
        if var == t:
            return self  # no op
        if var.name == self.variable.name:
            return self  # variable isn't free
        if var.name not in self.term.names:
            return self  # symbol not present, no substitution needed; some speedup and safety
        if self.variable.name in t.free_names:  # freshness condition violation
            new_var = _mk_var(name=new_name_source.new_name())  # establish freshness
            nt = _mk_abstraction(
                variable=new_var,
                term=self.term._capture_avoiding_substitution(
                    var=self.variable, t=new_var, new_name_source=new_name_source
                ),
                eager=self.eager,
            )
        else:
            nt = self
        return _mk_abstraction(
            variable=nt.variable,
            term=nt.term._capture_avoiding_substitution(
                var=var, t=t, new_name_source=new_name_source
            ),
            eager=self.eager,
        )
    
    def _normal_order_beta_reduction(
        self, *, new_name_source: "NewNameSource", tc: TransitiveCache | None
    ) -> Tuple["Term", bool]:
        # try cached
        if (tc is not None) and (self in tc):
            res = tc.lookup_result(self)
            assert res is not None
            return res, res!=self
        # needed for SUCC | N(0) == N(1)
        sub, acted = self.term._normal_order_beta_reduction(
            new_name_source=new_name_source,
            tc=tc
        )
        if not acted:
            if tc is not None:
                tc.store_absorbing(self)
            return self, False
        result = _mk_abstraction(variable=self.variable, term=sub, eager=self.eager)
        assert result != self
        if tc is not None:
            tc.store_transition(self, result)
        return result, True

    def __eq__(self, other) -> bool:
        e_v = _eq_helper(self, other)
        if e_v is not None:
            return e_v
        # now know same type
        if self.variable != other.variable:
            return False
        if self.eager != other.eager:
            return False
        return self.term == other.term

    def __lt__(self, other) -> bool:
        l_v = _lt_helper(self, other)
        if l_v is not None:
            return l_v
        if self.variable != other.variable:
            return self.variable < other.variable
        if self.eager != other.eager:
            return self.eager < other.eager
        return self.term < other.term

    def __hash__(self):
        return self._hash_val  # hash NULLed on derived classes that re-define __eq__()

    def _get_value_seq(self) -> Optional[List[Term]]:
        """Forms like (PAIR | 'x' | 'y') -> λ['f']('f', 'x', 'y')"""
        val = self.term
        values = []
        while True:
            if isinstance(val, _Variable) and (val == self.variable):
                return list(reversed(values))
            if isinstance(val, _Composition):
                values.append(val.right)
                val = val.left
            else:
                return None
            
    def __str__(self) -> str:
        try:
            return string_repr_map[self]
        except KeyError:
            pass
        values = self._get_value_seq()
        if values is not None:
            return "[" + ", ".join([str(vi) for vi in values]) + "]"
        symbol = "λ"
        if self.eager:
            symbol = "Λ"
        if self.variable.name == "":
            return "(" + symbol + " " + str(self.term) + ")"
        return "(" + symbol + str(self.variable) + " . " + str(self.term) + ")"
    
    def __repr__(self, *, need_v: bool = True) -> str:
        symbol = "λ"
        if self.eager:
            symbol = "Λ"
        if self.variable.name == "":
            return f"{symbol}({self.term.__repr__(need_v=False)})"
        return f"{symbol}[{self.variable.__repr__(need_v=False)}]({self.term.__repr__(need_v=False)})"

    def to_latex(
        self, *, not_expanded: Set | None = None, top_level: bool = False
    ) -> str:
        if (not_expanded is None) or (self not in not_expanded):
            try:
                return latex_repr_map[self]
            except KeyError:
                pass
            values = self._get_value_seq()
            if values is not None:
                return "[" + ", ".join([vi.to_latex(not_expanded=not_expanded, top_level=False) for vi in values]) + "]"
        s1 = self.variable.to_latex(not_expanded=not_expanded, top_level=False)
        s2 = self.term.to_latex(not_expanded=not_expanded, top_level=False)
        symbol = "\\lambda"
        if self.eager:
            symbol = "\\Lambda"
        if self.variable.name == "":
            res = f"{symbol} \\; {s2}"
        else:
            res = f"{symbol} \\; {s1} \\;.\\; {s2}"
        if not top_level:
            res = "( " + res + " )"
        return res


@dataclass(frozen=True)
class _AbstractionFactory:
    """internal class, build abstractions factories with λ['v']"""

    vars_seen: Tuple[_Variable, ...]
    eager: bool

    def __post_init__(self):
        assert isinstance(self.vars_seen, Tuple)
        assert len(self.vars_seen) > 0
        assert isinstance(self.eager, bool)
        names = set()
        for val in self.vars_seen:
            assert isinstance(val, Term)
            names.add(val.name)
        assert len(names) == len(self.vars_seen)

    def __call__(self, *args) -> "_Abstraction":
        """support λ['v'](B) notation"""
        t = v(args)
        assert isinstance(t, Term)
        res = None
        for var in reversed(self.vars_seen):
            if res is None:
                res = _mk_abstraction(variable=var, term=t, eager=self.eager)
            else:
                res = _mk_abstraction(variable=var, term=res, eager=self.eager)
        assert isinstance(res, Term)
        return res


@dataclass(frozen=True, kw_only=True)
class _AbstractionFactoryFactory:
    """build abstractions with λ['v']('t')"""

    eager: bool

    def __getitem__(self, index):
        """Support λ['x']('x') notation for lambda calculus abstraction"""
        if isinstance(index, str) or isinstance(index, _Variable):
            vars_seen = [v(index)]
        else:
            vars_seen = [v(val) for val in index]
        vars_seen = tuple(vars_seen)
        names = set()
        for val in vars_seen:
            assert isinstance(val, _Variable)
            names.add(val.name)
        assert len(vars_seen) == len(names)
        return _AbstractionFactory(vars_seen, eager=self.eager)

    def __str__(self) -> str:
        return "λ"

    def __repr__(self, *, need_v: bool = True) -> str:
        return "λ"


# expose factory factories
λ = _AbstractionFactoryFactory(eager=False)
Λ = _AbstractionFactoryFactory(eager=True)


@total_ordering
@dataclass(frozen=True, kw_only=True)
class _Composition(Term):
    """define concatenate expression: left right"""

    _hash_val: int
    left: Term
    right: Term

    def __post_init__(self):
        assert isinstance(self.left, Term)
        assert isinstance(self.right, Term)
    
    def _capture_avoiding_substitution(
        self, *, var: "_Variable", t: "Term", new_name_source: "NewNameSource"
    ) -> "Term":
        assert isinstance(var, _Variable)
        assert isinstance(t, Term)
        if var == t:
            return self  # no op
        if var.name not in self.names:
            return self  # symbol not present, no substitution needed; some speedup and safety
        left = self.left._capture_avoiding_substitution(
            var=var, t=t, new_name_source=new_name_source
        )
        right = self.right._capture_avoiding_substitution(
            var=var, t=t, new_name_source=new_name_source
        )
        return _mk_composition(left=left, right=right)

    def _normal_order_beta_reduction(
        self, *, new_name_source: "NewNameSource", tc: TransitiveCache | None
    ) -> Tuple["Term", bool]:
        # try cached
        if (tc is not None) and (self in tc):
            res = tc.lookup_result(self)
            assert res is not None
            return res, res!=self
        # first try top most application
        if isinstance(self.left, _Abstraction):
            assert self.left.variable.name != ""
            right = self.right
            if self.left.eager:
                right = right.nf(tc=tc)[0]
            res = self.left.term._capture_avoiding_substitution(
                var=self.left.variable, t=right, new_name_source=new_name_source
            )
            if res != self:
                if tc is not None:
                    tc.store_transition(self, res)
                return res, True
        # now try left to right application
        left, left_triggered = self.left._normal_order_beta_reduction(
            new_name_source=new_name_source,
            tc=tc
        )
        if left_triggered:
            # don't apply to right, already have a transform on left
            right, right_triggered = self.right, False
        else:
            right, right_triggered = self.right._normal_order_beta_reduction(
                new_name_source=new_name_source,
                tc=tc
            )
        if not (left_triggered or right_triggered):
            if tc is not None:
                tc.store_absorbing(self)
            return self, False
        res = _mk_composition(left=left, right=right)
        assert res != self
        if tc is not None:
            tc.store_transition(self, res)
        return res, True

    def __eq__(self, other) -> bool:
        e_v = _eq_helper(self, other)
        if e_v is not None:
            return e_v
        # now know same type
        if self.left != other.left:
            return False
        return self.right == other.right

    def __lt__(self, other) -> bool:
        l_v = _lt_helper(self, other)
        if l_v is not None:
            return l_v
        # now know same type
        if self.left != other.left:
            return self.left < other.left
        return self.right < other.right

    def __hash__(self):
        return self._hash_val  # hash NULLed on derived classes that re-define __eq__()

    def __str__(self) -> str:
        try:
            return string_repr_map[self]
        except KeyError:
            pass
        r_str = str(self.right)
        if isinstance(self.right, _Composition):
            r_str = "(" + r_str + ")"
        return str(self.left) + " " + r_str

    def __repr__(self, *, need_v: bool = True) -> str:
        l_str = self.left.__repr__(need_v=False)
        r_str = self.right.__repr__(need_v=False)
        if isinstance(self.left, _Composition):
            l_str = "(" + l_str + ")"
        if isinstance(self.right, _Composition):
            r_str = "(" + r_str + ")"
        if need_v:
            return f"v({l_str}, {r_str})"
        return f"{l_str}, {r_str}"

    def to_latex(
        self, *, not_expanded: Set | None = None, top_level: bool = False
    ) -> str:
        if (not_expanded is None) or (self not in not_expanded):
            try:
                return latex_repr_map[self]
            except KeyError:
                pass
        r_str = self.right.to_latex(not_expanded=not_expanded)
        if isinstance(self.right, _Composition):
            r_str = "(" + r_str + ")"
        return self.left.to_latex(not_expanded=not_expanded) + " \\; " + r_str


# https://en.wikipedia.org/wiki/Church_encoding#Church_numerals
def N(k: int) -> Term:
    """represent non-negative integer using Church numerals"""
    assert k >= 0
    return λ["f"](λ["x"](vr(["f"] * k + ["x"])))


def pretty_print_function(func):
    """format a function from reference"""
    source_code = inspect.getsource(func)
    highlighted_code = highlight(source_code, PythonLexer(), HtmlFormatter())
    display(
        HTML(
            f"<style>{HtmlFormatter().get_style_defs('.highlight')}</style>{highlighted_code}"
        )
    )


# define a number of useful lambda expressions

# https://en.wikipedia.org/wiki/Church_encoding#Table_of_functions_on_Church_numerals
# successor = λn.λf.λx. f (n f x)
SUCC = Λ["n"](λ["f"](λ["x"]("f", ("n", "f", "x"))))
# PLUS
PLUS = Λ["m"](Λ["n"]("n", SUCC, "m"))
# predecessor
PRED = Λ["n"](
    λ["f"](λ["x"](("n", λ["g"](λ["h"]("h", ("g", "f")))), λ["u"]("x"), λ["u"]("u")))
)
# SUB
SUB = Λ["m"](Λ["n"]("n", PRED, "m"))
# MULT
MULT = Λ["m"](Λ["n"](λ["f"](λ["x"]("m", ("n", "f"), "x"))))

# https://en.wikipedia.org/wiki/Fixed-point_combinator
Y = λ["f"](
    λ["x"]("f", ("x", "x")),
    λ["x"]("f", ("x", "x")),
)

# https://en.wikipedia.org/wiki/Fixed-point_combinator
Z = λ["f"](
    λ["x"]("f", λ["v"]("x", "x", "v")),
    λ["x"]("f", λ["v"]("x", "x", "v")),
)

# Theta combinator
# https://www.pls-lab.org/en/Theta_combinator
# Θ≜(λxy.y(xxy))(λxy.y(xxy))
Θ = λ["x"](λ["y"]("y", ("x", "x", "y"))) | λ["x"](λ["y"]("y", ("x", "x", "y")))

# https://en.wikipedia.org/wiki/Church_encoding#Church_pairs
PAIR = λ["x"](λ["y"](λ["z"]("z", "x", "y")))
FIRST = λ["p"]("p", λ["x"](λ["y"]("x")))
SECOND = λ["p"]("p", λ["x"](λ["y"]("y")))

# https://jwodder.freeshell.org/lambda.html
# great ref!
# TRUE = λxy. x ≡ K
TRUE = λ["x", "y"]("x")
# FALSE = λxy. y ≡ 0 ≡ λx. I ≡ K I ≡ S K ≡ X (X X)
FALSE = λ["x", "y"]("y")
AND = λ["p", "q"]("p", "q", "p")
OR = λ["p", "q"]("p", "p", "q")
NOT = λ["p", "a", "b"]("p", "b", "a")
IFTHENELSE = Λ["p"](λ["a", "b"]("p", "a", "b"))
XOR = Λ["p", "q"]("p", (NOT, "q"), "q")
# isZERO = λn. n (λx. FALSE) TRUE
isZERO = Λ["n"]("n", λ["x"](FALSE), TRUE)
# Less than or equal to:
LEQ = Λ["m", "n"](isZERO, (SUB, "m", "n"))
# Less than:
LT = Λ["a", "b"](NOT, (LEQ, "b", "a"))
# Equal to:
EQ = Λ["m", "n"](AND, (LEQ, "m", "n"), (LEQ, "n", "m"))
# Not equal to:
NEQ = Λ["a", "b"](OR, (NOT, (LEQ, "a", "b")), (NOT, (LEQ, "b", "a")))
# Greater than or equal to:
GEQ = Λ["a", "b"](LEQ, "b", "a")
# Greater than:
GT = Λ["a", "b"](NOT, (LEQ, "a", "b"))
# PAIR x y — create a PAIR with a car of x and a cdr of y; also called CONS:
PAIR = λ["x", "y", "f"]("f", "x", "y")
# CAR p — get the car of PAIR p; also called FIRST or HEAD:
CAR = λ["p"]("p", TRUE)
# CDR p — get the cdr of PAIR p; also called SECOND, TAIL, or REST:
CDR = λ["p"]("p", FALSE)
# The empty list:
NIL = λ["x"](TRUE)
# NULL p — evaluates to TRUE if p is NIL or to FALSE if p is a normal PAIR (all other types are undefined):
isNULL = λ["p"]("p", (λ["x", "y"](FALSE)))
# Division — DIV a b evaluates to a PAIR of two numbers, a idiv b and a mod b:
DIV = Y(
    λ["g", "q", "a", "b"](
        LT, "a", "b", (PAIR, "q", "a"), ("g", (SUCC, "q"), (SUB, "a", "b"), "b")
    )
) | N(0)
MOD = Λ["a", "b"](CDR, (DIV, "a", "b"))
GCD = λ["g", "m", "n"](LEQ, "m", "n", ("g", "n", "m"), ("g", "m", "n")) | (
    Y,
    λ["g", "x", "y"](isZERO, "y", "x", ("g", "y", (MOD, "x", "y"))),
)


# FACTORIAL	=	Y (λgx. isZERO x 1 (MULT x (g (PRED x))))
FACTORIALstep = λ["g"](Λ["x"](isZERO, "x", N(1), (MULT, "x", ("g", (PRED, "x")))))


# define a number of presentation aliases

text_aliases = dict()


def def_text_symbol(t: Term, s: str, *, add_reps: bool):
    assert isinstance(t, Term)
    assert isinstance(s, str)
    if add_reps:
        latex_repr_map[t] = "\\textbf{" + s + "}"
        string_repr_map[t] = s
    else:
        # make available to parser
        if s.isidentifier():
            text_aliases[s] = t


def def_math_symbol(t: Term, s: str, m: str, *, add_reps: bool):
    assert isinstance(t, Term)
    assert isinstance(s, str)
    assert isinstance(m, str)
    if add_reps:
        latex_repr_map[t] = "\\mathbf{" + m + "}"
        string_repr_map[t] = s
    else:
        # make available to parser
        if s.isidentifier():
            text_aliases[s] = t


def load_common_aliases(add_reps: bool = True):
    def_math_symbol(PLUS, "PLUS", "+", add_reps=add_reps)
    def_math_symbol(SUB, "SUB", "-", add_reps=add_reps)
    def_math_symbol(MULT, "MULT", "\\times", add_reps=add_reps)
    def_math_symbol(Θ, "Θ", "\\theta", add_reps=add_reps)
    def_text_symbol(SUCC, "SUCC", add_reps=add_reps)
    def_text_symbol(PRED, "PRED", add_reps=add_reps)
    def_text_symbol(Y, "Y", add_reps=add_reps)
    def_text_symbol(Z, "Z", add_reps=add_reps)
    def_text_symbol(FIRST, "FIRST", add_reps=add_reps)
    def_text_symbol(SECOND, "SECOND", add_reps=add_reps)
    def_text_symbol(TRUE, "TRUE", add_reps=add_reps)
    def_text_symbol(FALSE, "FALSE", add_reps=add_reps)
    def_text_symbol(AND, "AND", add_reps=add_reps)
    def_text_symbol(OR, "OR", add_reps=add_reps)
    def_text_symbol(NOT, "NOT", add_reps=add_reps)
    def_text_symbol(IFTHENELSE, "IFTHENELSE", add_reps=add_reps)
    def_text_symbol(XOR, "XOR", add_reps=add_reps)
    def_text_symbol(isZERO, "isZERO", add_reps=add_reps)
    def_text_symbol(LEQ, "LEQ", add_reps=add_reps)
    def_text_symbol(LT, "LT", add_reps=add_reps)
    def_text_symbol(EQ, "EQ", add_reps=add_reps)
    def_text_symbol(NEQ, "NEQ", add_reps=add_reps)
    def_text_symbol(GEQ, "GEQ", add_reps=add_reps)
    def_text_symbol(GT, "GT", add_reps=add_reps)
    def_text_symbol(PAIR, "PAIR", add_reps=add_reps)
    def_text_symbol(CAR, "CAR", add_reps=add_reps)
    def_text_symbol(CDR, "CDR", add_reps=add_reps)
    def_text_symbol(NIL, "NIL", add_reps=add_reps)
    def_text_symbol(isNULL, "isNULL", add_reps=add_reps)
    def_text_symbol(FACTORIALstep, "FACTORIALstep", add_reps=add_reps)
    def_text_symbol(DIV, "DIV", add_reps=add_reps)
    def_text_symbol(MOD, "MOD", add_reps=add_reps)
    def_text_symbol(GCD, "GCD", add_reps=add_reps)
    if add_reps:
        for ii in range(1000):
            def_math_symbol(N(ii), f"N({ii})", f"{ii}", add_reps=True)


load_common_aliases(add_reps=False)


def parse_l(src: str) -> Term:
    """Parse a lambda calculus expression from string (warning: uses Python eval)"""
    assert isinstance(src, str)
    restricted_globals = {
        "__builtins__": {
            "λ": λ,
            "Λ": Λ,
            "v": v,
            "vr": vr,
            "N": N,
        },
    }  # Disable built-in functions and supply some definitions
    for key, val in text_aliases.items():
        restricted_globals[key] = val
    restricted_locals = {}
    res = eval(src, restricted_globals, restricted_locals)
    assert isinstance(res, Term)
    return res


def ifthenelse(condition, then, otherwise):
    """alias for IFTHENELSE | (condition) | (then) | (otherwise)"""
    return IFTHENELSE | condition | then | otherwise


def let(terms, *, be, within):
    """alias for λ[terms](within) | be"""
    return λ[terms](within) | be
