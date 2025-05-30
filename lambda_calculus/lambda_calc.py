from dataclasses import dataclass
from functools import total_ordering
import re
from typing import Iterable, List, Set, Tuple
import string
from abc import ABC, abstractmethod

import inspect
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from IPython.display import display, HTML, Math, Markdown


string_repr_map = dict()
latex_repr_map = dict()


def _combine_hash(a, b) -> int:
    return hash(str(hash(a)) + "," + str(hash(b)))


def _mk_abstraction(*, variable, term):
    assert isinstance(variable, Variable)
    assert isinstance(term, Term)
    return _Abstraction(
        variable=variable,
        term=term,
        _hash_val=_combine_hash(variable, term),
    )


def _mk_composition(*, left, right):
    assert isinstance(left, Term)
    assert isinstance(right, Term)
    return _Composition(
        left=left,
        right=right,
        _hash_val=_combine_hash(left, right),
    )


@dataclass(frozen=True)
class Term(ABC):
    """Represent a term in a lambda calculus expression"""

    @abstractmethod
    def has_name(self, name: str):
        """Check if name occurs in sub-tree"""
        pass

    @abstractmethod
    def has_free_name(self, name: str):
        """Check if name occurs free in sub-tree"""
        pass

    @abstractmethod
    def _capture_avoiding_substitution(
        self, *, var: "Variable", t: "Term", new_name_source: "NewNameSource"
    ) -> "Term":
        """Apply capture avoiding substitution var replaced with t (renaming as needed, needs list of all names to avoid)"""
        pass

    @abstractmethod
    def _normal_order_beta_reduction(
        self, *, new_name_source: "NewNameSource"
    ) -> Tuple["Term", bool]:
        """internal method for reduction step, needs list of all names to avoid"""
        pass

    def r(self) -> "Term":
        """run one beta reduction step in normal order (top left first)"""
        red, _ = self._normal_order_beta_reduction(
            new_name_source=NewNameSource(root_node=self)
        )
        return red

    def nf(self) -> Tuple["Term", int]:
        """reduce to normal form"""
        steps = 0
        new_name_source = NewNameSource(root_node=self)
        e = self
        while True:
            e, acted = e._normal_order_beta_reduction(new_name_source=new_name_source)
            if not acted:
                return e, steps
            else:
                steps = steps + 1

    @abstractmethod
    def to_latex(
        self, *, not_expanded: Set | None = None, top_level: bool = False
    ) -> str:
        """convert to to_latex, no substitutions for not_expanded set"""
        pass

    def _repr_latex_(self):
        """trigger pretty printing path in Jupyter"""
        return "$$" + self.to_latex(top_level=True) + "$$"

    def __or__(self, other) -> "Term":
        """concatenate/compose"""
        other = v(other)
        if (self is None) or isinstance(self, _Empty):
            return other
        if isinstance(other, _Empty):
            return self
        return _mk_composition(left=self, right=other)

    def __ror__(self, other) -> "Term":
        """concatenate/compose"""
        other = v(other)
        if (self is None) or isinstance(self, _Empty):
            return other
        if isinstance(other, _Empty):
            return self
        return _mk_composition(left=other, right=self)

    def __call__(self, *args) -> "_Composition":
        """concatenate/compose"""
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
    t_a = str(type(a))
    t_b = str(type(b))
    if t_a != t_b:
        return t_a < t_b
    h_a = hash(a)
    h_b = hash(b)
    if h_a != h_b:
        return h_a < h_b
    return None


@total_ordering
@dataclass(frozen=True)
class _Empty(Term):
    """represent empty expression"""

    def has_name(self, name: str):
        """Check if name occurs in sub-tree"""
        assert isinstance(name, str)
        return False

    def has_free_name(self, name: str):
        """Check if name occurs free in sub-tree"""
        assert isinstance(name, str)
        return False

    def _normal_order_beta_reduction(
        self, *, new_name_source: "NewNameSource"
    ) -> Tuple["Term", bool]:
        return self, False

    def _capture_avoiding_substitution(
        self, *, var: "Variable", t: "Term", new_name_source: "NewNameSource"
    ) -> "Term":
        assert isinstance(var, Variable)
        assert isinstance(t, Term)
        return self

    def __eq__(self, other) -> bool:
        e_v = _eq_helper(self, other)
        if e_v is not None:
            return e_v
        # now know same type
        return True

    def __lt__(self, other) -> bool:
        l_v = _lt_helper(self, other)
        if l_v is not None:
            return l_v
        # now know same type
        return False

    def __hash__(self):
        return 9859541  # hash NULLed on derived classes that re-define __eq__()

    def __str__(self) -> str:
        return "ε"

    def __repr__(self, *, need_v: bool = True) -> str:
        return "v(None)"

    def to_latex(
        self, *, not_expanded: Set | None = None, top_level: bool = False
    ) -> str:
        return "\\mathbb{\\epsilon}"


# canonical empty term, may not need at user level
ε = _Empty()


def _v(x) -> Term:
    """Collect structure to value (left associative)"""
    if x is None:
        return ε
    if isinstance(x, str):
        return Variable(name=x)
    if isinstance(x, Term):
        return x
    # iterable cases
    res = None
    for xi in x:
        if xi is not None:
            xi = _v(xi)
            if not isinstance(xi, _Empty):
                if res is None:
                    res = xi
                else:
                    res = _mk_composition(left=res, right=xi)
    if res is None:
        return ε
    assert isinstance(res, Term)
    return res


def v(*args) -> Term:
    """Collect structure to value (left associative)"""
    return _v(args)


def _vr(x) -> Term:
    """Collect structure to value (right associative)"""
    if x is None:
        return ε
    if isinstance(x, str):
        return Variable(name=x)
    if isinstance(x, Term):
        return x
    # iterable cases
    res = None
    for xi in reversed(x):
        if xi is not None:
            xi = _vr(xi)
            if not isinstance(xi, _Empty):
                if res is None:
                    res = xi
                else:
                    res = _mk_composition(left=xi, right=res)
    if res is None:
        return ε
    assert isinstance(res, Term)
    return res


def vr(*args) -> Term:
    """Collect structure to value (right associative)"""
    return _vr(args)


@total_ordering
@dataclass(frozen=True)
class Variable(Term):
    """represent a variable"""

    name: str

    def __post_init__(self):
        assert isinstance(self.name, str)
        # not as string as isidentifier()
        assert len(self.name) > 0
        assert not any(char in string.whitespace for char in self.name)
        assert not any(char in "'\"().[];|+-*/%\\λΛε \n" for char in self.name)

    def has_name(self, name: str):
        """Check if name occurs in sub-tree"""
        assert isinstance(name, str)
        return name == self.name

    def has_free_name(self, name: str):
        """Check if name occurs free in sub-tree"""
        assert isinstance(name, str)
        return name == self.name

    def _normal_order_beta_reduction(
        self, *, new_name_source: "NewNameSource"
    ) -> Tuple["Term", bool]:
        return self, False

    def _capture_avoiding_substitution(
        self, *, var: "Variable", t: "Term", new_name_source: "NewNameSource"
    ) -> "Term":
        assert isinstance(var, Variable)
        assert isinstance(t, Term)
        if var == t:
            return self  # no op
        if var.name == self.name:
            return t
        return self

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
            "Variable" + self.name
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
        return self.name


class NewNameSource:
    """build a new name, disjoint from vars"""

    root_node: Term
    addnl_terms: Set[str]
    next_index: int
    prefix: str

    def __init__(
        self,
        *,
        root_node: Term | None = None,
        nms: Iterable[str] | None = None,
        prefix: str = "v",
    ):
        if root_node is not None:
            assert isinstance(root_node, Term)
        assert isinstance(prefix, str)
        self.root_node = root_node
        self.addnl_terms = set()
        if nms is not None:
            self.addnl_terms.update(nms)
        self.next_index = 0
        self.prefix = prefix

    def new_name(self):
        """buld a new name, disjoint from vars"""
        while True:
            new_name = f"{self.prefix}{self.next_index}"
            if (new_name not in self.addnl_terms) and (
                (self.root_node is None) or (not self.root_node.has_name(new_name))
            ):
                self.addnl_terms.add(new_name)
                return new_name
            self.next_index = self.next_index + 1


@total_ordering
@dataclass(frozen=True)
class _Abstraction(Term):
    """represent (λ(variable).term)"""

    _hash_val: int
    variable: Variable
    term: Term

    def __post_init__(self):
        assert isinstance(self.variable, Variable)
        assert isinstance(self.term, Term)

    def has_name(self, name: str):
        """Check if name occurs in sub-tree"""
        assert isinstance(name, str)
        if self.variable.has_name(name):
            return True
        return self.term.has_name(name)

    def has_free_name(self, name: str):
        """Check if name occurs free in sub-tree"""
        assert isinstance(name, str)
        if self.variable.has_free_name(name):
            return False  # shields name
        return self.term.has_free_name(name)

    def _normal_order_beta_reduction(
        self, *, new_name_source: "NewNameSource"
    ) -> Tuple["Term", bool]:
        # needed for SUCC | N(0) == N(1)
        sub, acted = self.term._normal_order_beta_reduction(
            new_name_source=new_name_source
        )
        if not acted:
            return self, False
        return _mk_abstraction(variable=self.variable, term=sub), True

    def _capture_avoiding_substitution(
        self, *, var: "Variable", t: "Term", new_name_source: "NewNameSource"
    ) -> "Term":
        assert isinstance(var, Variable)
        assert isinstance(t, Term)
        if var == t:
            return self  # no op
        if var.name == self.variable.name:
            return self  # variable isn't free
        if not self.term.has_name(var.name):
            return self  # symbol not present, no substitution needed; some speedup and
        if t.has_free_name(self.variable.name):  # freshness condition violation
            new_var = Variable(name=new_name_source.new_name())  # establish freshness
            nt = _mk_abstraction(
                variable=new_var,
                term=self.term._capture_avoiding_substitution(
                    var=self.variable, t=new_var, new_name_source=new_name_source
                ),
            )
        else:
            nt = self
        return _mk_abstraction(
            variable=nt.variable,
            term=nt.term._capture_avoiding_substitution(
                var=var, t=t, new_name_source=new_name_source
            ),
        )

    def _beta_reduce(self, right, *, new_name_source: "NewNameSource") -> Term:
        right = v(right)
        assert isinstance(right, Term)
        return self.term._capture_avoiding_substitution(
            var=self.variable, t=right, new_name_source=new_name_source
        )

    def __eq__(self, other) -> bool:
        e_v = _eq_helper(self, other)
        if e_v is not None:
            return e_v
        # now know same type
        if self.variable != other.variable:
            return False
        return self.term == other.term

    def __lt__(self, other) -> bool:
        l_v = _lt_helper(self, other)
        if l_v is not None:
            return l_v
        if self.variable != other.variable:
            return self.variable < other.variable
        return self.term < other.term

    def __hash__(self):
        return self._hash_val  # hash NULLed on derived classes that re-define __eq__()

    def __str__(self) -> str:
        try:
            return string_repr_map[self]
        except KeyError:
            pass
        return "(λ" + str(self.variable) + " . " + str(self.term) + ")"

    def __repr__(self, *, need_v: bool = True) -> str:
        return f"λ[{self.variable.__repr__(need_v=False)}]({self.term.__repr__(need_v=False)})"

    def to_latex(
        self, *, not_expanded: Set | None = None, top_level: bool = False
    ) -> str:
        if (not_expanded is None) or (self not in not_expanded):
            try:
                return latex_repr_map[self]
            except KeyError:
                pass
        s1 = self.variable.to_latex(not_expanded=not_expanded, top_level=False)
        s2 = self.term.to_latex(not_expanded=not_expanded, top_level=False)
        if top_level:
            return f"\\lambda \\; {s1} \\;.\\; {s2}"
        return f"( \\lambda \\; {s1} \\;.\\; {s2} )"


@dataclass(frozen=True)
class _AbstractionFactory:
    """internal class, build abstractions factories with λ['v']"""

    vars: Tuple[Variable, ...]

    def __post_init__(self):
        assert isinstance(self.vars, Tuple)
        assert len(self.vars) > 0
        names = set()
        for v in self.vars:
            assert isinstance(v, Term)
            names.add(v.name)
        assert len(names) == len(self.vars)

    def __call__(self, *args) -> "_Abstraction":
        t = v(args)
        assert isinstance(t, Term)
        res = None
        for var in reversed(self.vars):
            if res is None:
                res = _mk_abstraction(variable=var, term=t)
            else:
                res = _mk_abstraction(variable=var, term=res)
        assert isinstance(res, Term)
        return res


@dataclass(frozen=True)
class _AbstractionFactoryFactory:
    """build abstractions with λ['v']('t')"""

    def __getitem__(self, index):
        """Support λ['x']('x') notation for lambda calculus abstraction"""
        if isinstance(index, str) or isinstance(index, Variable):
            vars = [v(index)]
        else:
            vars = [v(val) for val in index]
        vars = tuple(vars)
        names = set()
        for val in vars:
            assert isinstance(val, Variable)
            names.add(val.name)
        assert len(vars) == len(names)
        return _AbstractionFactory(vars)

    def __str__(self) -> str:
        return "λ"

    def __repr__(self, *, need_v: bool = True) -> str:
        return "λ"


# expose factory factories
λ = _AbstractionFactoryFactory()


@total_ordering
@dataclass(frozen=True)
class _Composition(Term):
    """define concatenate expression: left right"""

    _hash_val: int
    left: Term
    right: Term

    def __post_init__(self):
        assert isinstance(self.left, Term)
        assert isinstance(self.right, Term)
        # insure we are not collecting invisible cruft
        assert not isinstance(self.left, _Empty)
        assert not isinstance(self.right, _Empty)

    def has_name(self, name: str):
        """Check if name occurs in sub-tree"""
        assert isinstance(name, str)
        if self.left.has_name(name):
            return True
        return self.right.has_name(name)

    def has_free_name(self, name: str):
        """Check if name occurs free in sub-tree"""
        assert isinstance(name, str)
        if self.left.has_free_name(name):
            return True
        return self.right.has_free_name(name)

    def _normal_order_beta_reduction(
        self, *, new_name_source: "NewNameSource"
    ) -> Tuple["Term", bool]:
        if isinstance(self.left, _Abstraction):
            res = self.left._beta_reduce(self.right, new_name_source=new_name_source)
            return res, res != self
        else:
            left, left_triggered = self.left._normal_order_beta_reduction(
                new_name_source=new_name_source
            )
            if left_triggered:
                right, right_triggered = self.right, False
            else:
                right, right_triggered = self.right._normal_order_beta_reduction(
                    new_name_source=new_name_source
                )
            if not (left_triggered or right_triggered):
                return self, False
            if isinstance(left, _Empty):
                return right, True
            if isinstance(right, _Empty):
                return left, True
            return _mk_composition(left=left, right=right), True

    def _capture_avoiding_substitution(
        self, *, var: "Variable", t: "Term", new_name_source: "NewNameSource"
    ) -> "Term":
        assert isinstance(var, Variable)
        assert isinstance(t, Term)
        if var == t:
            return self  # no op
        left = self.left._capture_avoiding_substitution(
            var=var, t=t, new_name_source=new_name_source
        )
        right = self.right._capture_avoiding_substitution(
            var=var, t=t, new_name_source=new_name_source
        )
        if isinstance(left, _Empty):
            return right
        if isinstance(right, _Empty):
            return left
        return _mk_composition(left=left, right=right)

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
SUCC = λ["n"](λ["f"](λ["x"]("f", ("n", "f", "x"))))
# PLUS
PLUS = λ["m"](λ["n"]("n", SUCC, "m"))
# predecessor
PRED = λ["n"](
    λ["f"](λ["x"](("n", λ["g"](λ["h"]("h", ("g", "f")))), λ["u"]("x"), λ["u"]("u")))
)
# SUB
SUB = λ["m"](λ["n"]("n", PRED, "m"))
# MULT
MULT = λ["m"](λ["n"](λ["f"](λ["x"]("m", ("n", "f"), "x"))))

# https://en.wikipedia.org/wiki/Fixed-point_combinator
Y = λ["f"](
    λ["x"]("f", ("x", "x")),
    λ["x"]("f", ("x", "x")),
)

# Theta combinator
# https://www.pls-lab.org/en/Theta_combinator
# Θ≜(λxy.y(xxy))(λxy.y(xxy))
Θ = λ["x"](λ["y"]("y", ("x", "x", "y"))) | λ["x"](λ["y"]("y", ("x", "x", "y")))

# https://en.wikipedia.org/wiki/Church_encoding#Church_pairs
pair = λ["x"](λ["y"](λ["z"]("z", "x", "y")))
first = λ["p"]("p", λ["x"](λ["y"]("x")))
second = λ["p"]("p", λ["x"](λ["y"]("y")))

# https://jwodder.freeshell.org/lambda.html
# great ref!
# TRUE = λxy. x ≡ K
TRUE = λ["x", "y"]("x")
# FALSE = λxy. y ≡ 0 ≡ λx. I ≡ K I ≡ S K ≡ X (X X)
FALSE = λ["x", "y"]("y")
AND = λ["p", "q"]("p", "q", "p")
OR = λ["p", "q"]("p", "p", "q")
NOT = λ["p", "a", "b"]("p", "b", "a")
XOR = λ["p", "q"]("p", (NOT, "q"), "q")
# ISZERO = λn. n (λx. FALSE) TRUE
ISZERO = λ["n"]("n", λ["x"](FALSE), TRUE)
# Less than or equal to:
LEQ = λ["m", "n"](ISZERO, (SUB, "m", "n"))
# Less than:
LT = λ["a", "b"](NOT, (LEQ, "b", "a"))
# Equal to:
EQ = λ["m", "n"](AND, (LEQ, "m", "n"), (LEQ, "n", "m"))
# Not equal to:
NEQ = λ["a", "b"](OR, (NOT, (LEQ, "a", "b")), (NOT, (LEQ, "b", "a")))
# Greater than or equal to:
GEQ = λ["a", "b"](LEQ, "b", "a")
# Greater than:
GT = λ["a", "b"](NOT, (LEQ, "a", "b"))
# PAIR x y — create a pair with a car of x and a cdr of y; also called CONS:
PAIR = λ["x", "y", "f"]("f", "x", "y")
# CAR p — get the car of pair p; also called FIRST or HEAD:
CAR = λ["p"]("p", TRUE)
# CDR p — get the cdr of pair p; also called SECOND, TAIL, or REST:
CDR = λ["p"]("p", FALSE)
# The empty list:
NIL = λ["x"](TRUE)
# NULL p — evaluates to TRUE if p is NIL or to FALSE if p is a normal pair (all other types are undefined):
isNULL = λ["p"]("p", (λ["x", "y"](FALSE)))
# Division — DIV a b evaluates to a pair of two numbers, a idiv b and a mod b:
DIV = Y(
    λ["g", "q", "a", "b"](
        LT, "a", "b", (PAIR, "q", "a"), ("g", (SUCC, "q"), (SUB, "a", "b"), "b")
    )
) | N(0)
MOD = λ["a", "b"](CDR, (DIV, "a", "b"))
GCD = λ["g", "m", "n"](LEQ, "m", "n", ("g", "n", "m"), ("g", "m", "n")) | (
    Y,
    λ["g", "x", "y"](ISZERO, "y", "x", ("g", "y", (MOD, "x", "y"))),
)


# FACTORIAL	=	Y (λgx. ISZERO x 1 (MULT x (g (PRED x))))
FACTORIALstep = λ["g", "x"](ISZERO, "x", N(1), (MULT, "x", ("g", (PRED, "x"))))


# define a number of presentation aliases

text_aliases = dict()


def def_text_symbol(t: Term, s: str):
    global string_repr_map
    global latex_repr_map
    global text_aliases
    assert isinstance(t, Term)
    assert isinstance(s, str)
    latex_repr_map[t] = "\\textbf{" + s + "}"
    string_repr_map[t] = s
    # make available to parser
    if s.isidentifier():
        text_aliases[s] = t


def def_math_symbol(t: Term, s: str, m: str):
    global string_repr_map
    global latex_repr_map
    assert isinstance(t, Term)
    assert isinstance(s, str)
    assert isinstance(m, str)
    latex_repr_map[t] = "\\mathbf{" + m + "}"
    string_repr_map[t] = s


def load_common_aliases():
    def_math_symbol(PLUS, "+", "+")
    def_math_symbol(SUB, "-", "-")
    def_math_symbol(MULT, "*", "\\times")
    def_math_symbol(Θ, "Θ", "\\theta")
    def_math_symbol(ε, "ε", "\\epsilon")
    def_text_symbol(SUCC, "SUCC")
    def_text_symbol(PRED, "PRED")
    def_text_symbol(Y, "Y")
    def_text_symbol(pair, "pair")
    def_text_symbol(first, "1st")
    def_text_symbol(second, "2nd")
    def_text_symbol(TRUE, "TRUE")
    def_text_symbol(FALSE, "FALSE")
    def_text_symbol(AND, "AND")
    def_text_symbol(OR, "OR")
    def_text_symbol(NOT, "NOT")
    def_text_symbol(XOR, "XOR")
    def_text_symbol(ISZERO, "ISZERO")
    def_text_symbol(LEQ, "LEQ")
    def_text_symbol(LT, "LT")
    def_text_symbol(EQ, "EQ")
    def_text_symbol(NEQ, "NEQ")
    def_text_symbol(GEQ, "GEQ")
    def_text_symbol(GT, "GT")
    def_text_symbol(PAIR, "PAIR")
    def_text_symbol(CAR, "CAR")
    def_text_symbol(CDR, "CDR")
    def_text_symbol(NIL, "NIL")
    def_text_symbol(isNULL, "isNULL")
    def_text_symbol(FACTORIALstep, "!step")
    def_text_symbol(DIV, "DIV")
    def_text_symbol(MOD, "MOD")
    def_text_symbol(GCD, "GCD")
    for ii in range(1000):
        def_math_symbol(N(ii), f"N({ii})", f"{ii}")


def parse_l(src: str) -> Term:
    """Parse a lambda calculus expression from string (warning: uses Python eval)"""
    global text_aliases
    assert isinstance(src, str)
    restricted_globals = {
        "__builtins__": {
            "ε": ε,
            "λ": λ,
            "v": v,
            "vr": vr,
        },
    }  # Disable built-in functions and supply some definitions
    for key, val in text_aliases.items():
        restricted_globals[key] = val
    restricted_locals = {}
    res = eval(src, restricted_globals, restricted_locals)
    assert isinstance(res, Term)
    return res


def r_convert_deBuijn_codes(e: Term, *, variables: List[Variable]) -> Term:
    assert isinstance(e, Term)
    result = None
    if isinstance(e, _Abstraction):
        variables.append(e.variable)
        result = _mk_abstraction(
            variable=e.variable,
            term=r_convert_deBuijn_codes(e.term, variables=variables),
        )
        variables.pop()
    elif isinstance(e, Variable):
        dbcode = int(re.sub(r"\D", "", e.name))
        idx = len(variables) - dbcode
        assert (idx >= 0) and (idx < len(variables))
        result = variables[idx]
    elif isinstance(e, _Empty):
        result = e
    elif isinstance(e, _Composition):
        result = _mk_composition(
            left=r_convert_deBuijn_codes(e.left, variables=variables),
            right=r_convert_deBuijn_codes(e.right, variables=variables),
        )
    else:
        raise ValueError("unexpected type")
    if result is None:
        result = ε
    assert isinstance(result, Term)
    return result


def read_zero_one_code(code: str) -> Term:
    """
    Read 0/1 encoding of lambda expression
    https://tromp.github.io/cl/Binary_lambda_calculus.html#binary_io
        blc(λM) = 00 blc(M)
        blc(M N) = 01 blc(M) blc(N)
        blc(i) = [1]*i0   ( De Bruijn indices )
    """
    code = re.sub(r"[^01]", "", code)
    overall_result = None
    next_index = 0
    next_name_index = 0
    assert len(code) >= 2
    assert [c in ("0", "1") for c in code]  # double check

    def consume_term() -> Term:
        nonlocal next_index
        nonlocal next_name_index
        nonlocal code
        assert next_index <= len(code) - 2
        if code[next_index] == "0":
            c = code[next_index + 1]
            next_index = next_index + 2
            if c == "0":
                var = Variable(name=f"x{next_name_index}")
                next_name_index = next_name_index + 1
                term = consume_term()
                result = _mk_abstraction(variable=var, term=term)
            else:
                left = consume_term()
                right = consume_term()
                result = _mk_composition(left=left, right=right)
        else:
            depth_count = 0
            while code[next_index] == "1":
                depth_count = depth_count + 1
                next_index = next_index + 1
            next_index = next_index + 1
            result = Variable(name=f"b{depth_count}")
        return result

    while next_index < len(code):
        term = consume_term()
        if overall_result is None:
            overall_result = term
        else:
            overall_result = _mk_composition(left=overall_result, right=term)
    assert next_index == len(code)
    assert isinstance(overall_result, Term)
    converted = r_convert_deBuijn_codes(overall_result, variables=[])
    return converted
