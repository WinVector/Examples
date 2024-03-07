import numbers
from typing import Iterable, Optional
from itertools import combinations, permutations, product
from sympy import (
    binomial,
    factorial,
    fraction,
    poly,
    Poly,
    symbols,
    Symbol,
    symmetrize,
)
from sympy.ntheory.continued_fraction import (
    continued_fraction_convergents,
    continued_fraction_iterator,
)
from sympy.solvers import solve
import pandas as pd
import numpy as np


def is_infinitesimal_poly(p, *, tol: float = 1e-8):
    """return true if poly is all small coefs"""
    if p == 0:
        return True
    if isinstance(p, float) or isinstance(p, int) or isinstance(p, numbers.Number):
        if abs(float(p)) <= tol:
            return True
        else:
            return False  # for breakpoints
    terms = poly(p).as_dict()
    max_abs_coef_diff = np.max(np.abs([v for v in terms.values()]))
    if max_abs_coef_diff <= tol:
        return True
    return False  # for breakpoint


def nearby_rational(x, *, tol=1e-8):
    """Find a rational number near a float"""
    if x == 0:
        return 0
    if isinstance(x, int):
        return x
    if abs(x) <= tol:
        return 0
    for est in continued_fraction_convergents(continued_fraction_iterator(x)):
        if np.abs(x - est) <= tol:
            return est


def _subsv(v, mp):
    """
    Substitute, but skip if already a number

    :param v: value to convert
    :param mp: variables to values substitution mapping
    """
    if v == 0:
        return 0
    if isinstance(v, float) or isinstance(v, int) or isinstance(v, numbers.Number):
        return v
    return v.subs(mp)


def sq_loss_polynomial(
    groups,
    *,
    use_variable_positions=None,
    effective_n_blocks: Optional[int] = None,
    effective_block_size: Optional[int] = None,
):
    """
    Build the polynomial representing square loss on y-variables grouped by groups.

    :param groups: iterable of a partition group variable names
    :return: polynomial, variables
    """
    result = 0
    p_vars = []
    variable_names = []
    groups = [g for g in groups if len(g) > 0]
    if len(groups) > 0:
        variable_names = sorted(set().union(*groups))
    n_variables = len(variable_names)
    if n_variables > 0:
        # confirm this is a partition
        seen = set()
        for group in groups:
            assert len(seen.intersection(group)) == 0
            seen.update(group)
        # do the work
        p_vars = list(symbols(" ".join([f"y_{i}" for i in variable_names])))
        if use_variable_positions is not None:
            for i, is_usable in enumerate(use_variable_positions):
                if not is_usable:
                    p_vars[i] = 0
        for group in groups:
            len_group = len(group)
            if len_group > 1:
                group_size = len_group
                if effective_block_size is not None:
                    group_size = effective_block_size
                sel_group = [p_vars[i] for i in group if p_vars[i] != 0]
                len_sel_group = len(sel_group)
                if len_sel_group > 0:
                    mean_i = sum(sel_group) / group_size
                    terms_i = (
                        (
                            sum([(pv - mean_i) ** 2 for pv in sel_group])
                            + (group_size - len_sel_group) * (0 - mean_i) ** 2
                        )
                        * group_size
                    ) / (group_size - 1)
                    result = result + terms_i
        n_singleton_groups = sum([len(group) == 1 for group in groups])
        effective_n_variables = n_variables
        if effective_n_blocks is not None:
            assert n_singleton_groups == 0
            effective_n_variables = effective_n_blocks * effective_block_size
        result = result / effective_n_variables
        if (
            (n_singleton_groups > 0)
            and (n_singleton_groups < n_variables)
            and (n_singleton_groups < len(groups))
        ):
            result = (result * n_variables) / (n_variables - n_singleton_groups)
    return result, p_vars


def symmetrize_poly_by_summing_out_permutations(p, p_vars):
    """
    Symmetrize a polynomial by averaging it evaluated over all permutations of its variables.
    This works really well as any product of symmetric polynomials is invariant under
    this summation.

    :param p: polynomial
    :param p_vars: variables
    :return: polynomial
    """
    # subs doesn't work right if symbols on both sides
    # so reserve some intermediate symbols
    place_holders = symbols(" ".join([f"ph_{i}" for i in range(len(p_vars))]))
    assert len(set(p_vars).intersection(place_holders)) == 0
    sub_expr = _subsv(p, {orig: ph for orig, ph in zip(p_vars, place_holders)})
    sym_result = 0
    sym_count = 0
    for perm in permutations(p_vars):
        r_perm = _subsv(sub_expr, {ph: new for ph, new in zip(place_holders, perm)})
        sym_result = sym_result + r_perm
        sym_count = sym_count + 1
    return (sym_result / sym_count).expand()


def groups_from_partition(partition):
    """
    Build a grouping matching a given partition specification.
    """
    groups = []
    total = 0
    for pi in partition:
        groups.append(list(range(total, pi + total)))
        total = total + pi
    return groups


def calculate_symmetric_loss_poly_from_partition(part):
    """
    Return a row with the symmetrized loss function (expected square loss) and
    variance of that estimate.

    Used to debug and collect stats/examples.
    """
    n = sum(part)
    groups = groups_from_partition(part)
    loss_poly, p_vars = sq_loss_polynomial(groups)
    if loss_poly != 0:
        sym_loss_poly = symmetrize_poly_by_summing_out_permutations(loss_poly, p_vars)
        sym_loss_decomp = symmetrize(sym_loss_poly, formal=True)
        assert is_infinitesimal_poly(sym_loss_decomp[1])
        sym_loss_s = sym_loss_decomp[0]
        res = pd.DataFrame(
            {
                "n": [n],
                "partition": [part],
                "expected loss polynomial": [sym_loss_s],
            }
        )
        # calculate variance over full group
        sym_var_poly = symmetrize_poly_by_summing_out_permutations(
            (loss_poly - sym_loss_poly) ** 2, p_vars
        )
        sym_var_decomp = symmetrize(sym_var_poly, formal=True)
        assert is_infinitesimal_poly(sym_var_decomp[1])
        sym_var_s = sym_var_decomp[0]
        res["loss variance polynomial"] = [sym_var_s]
        return res
    return None


def theoretical_sym_poly(n: int):
    """
    Return the theoretical average of sq_loss_polynomial over all permutations.
    """
    s1, s2 = symbols("s1 s2")
    return (s1**2) / n - 2 * s2 / (n - 1)


def pair_poly(n: int):
    """
    Return the properly scaled all pairs difference polynomial.
    Matches sq_loss_polynomial[[range(n)]]
    """
    p_vars = symbols(" ".join([f"y_{i}" for i in range(n)]))
    result = 0
    for i in range(n):
        for j in range(i + 1, n):
            result = result + (p_vars[i] - p_vars[j]) ** 2
    return result / (n * (n - 1))


def partitions(n, m=None):
    """Partition n with a maximum part size of m. Yield non-increasing
    lists in decreasing lexicographic order. The default for m is
    effectively n, so the second argument is not needed to create the
    generator unless you do want to limit part sizes.
    https://stackoverflow.com/a/47848961
    """
    if m is None or m >= n:
        yield [n]
    for f in range(n - 1 if (m is None or m >= n) else m, 0, -1):
        for p in partitions(n - f, f):
            yield [f] + p


def elementary_symmetric_polynomial(i: int, p_vars):
    """build the i-th elementary symmetric polynomial on p_vars"""
    if i < 1:
        return 1
    p_vars = list(p_vars)
    res = 0
    for choice in combinations(p_vars, i):
        res = res + np.prod(choice)
    return res


def _identify_variance_fn_through_sym(
    partition: Iterable[int],
    *,
    symmetry_fn,
    symmetry_args,
    detect_support: bool = True,
    effective_n_blocks: Optional[int] = None,
    effective_block_size: Optional[int] = None,
):
    """
    Identify the variance function by evaluating on a mostly zero example that
    is symmetrized on a set of states smaller than the full symmetric group.
    Works on a decomposition of the symmetry group into equal sized segments where the functions we are working over are constant
    (so it is enough to average over representatives.)

    :param partition: partition of group sizes to work with
    :param symmetry_fn: symmetry_fn(n=, values=, symmetry_args=symmetry_args) generates n-vectors working through symmetries we need to sum out
    :param symmetry_args: arguments to pass to symmetry_fn
    :param detect_support: if True try to remove non-supported variables (never set by symmetry_fn) from calculation.
    :return: variance polynomial as elementary symmetric polynomials (unless sizes are symbolic, then just return poly and place holder value list)
    """
    partition = list(partition)
    n = sum(partition)
    n_set_positions = 4
    if (effective_n_blocks is not None) or (effective_block_size is not None):
        effective_n = effective_n_blocks * effective_block_size
    else:
        effective_n = n
    # detect support
    saw_support = None
    if detect_support:
        saw_support = [False] * n
        for keyed_vec, wt in symmetry_fn(
            n=n, values=[1] * n_set_positions, symmetry_args=symmetry_args
        ):
            for i in keyed_vec.keys():
                saw_support[i] = True
    # build the initial loss polynomial, restricted to variables in action
    p, p_vars = sq_loss_polynomial(
        groups_from_partition(partition),
        effective_n_blocks=effective_n_blocks,
        effective_block_size=effective_block_size,
        use_variable_positions=saw_support,
    )
    # substitute out symmetric vars
    s_defs = [
        elementary_symmetric_polynomial(i, [v for v in p_vars if v != 0])
        for i in range(3)
    ]
    substitutions = {f"s{i}": s_defs[i] for i in range(1, len(s_defs))}
    # build the polynomial we wish to symmetrize over Sn
    eval_p = _subsv(p - theoretical_sym_poly(effective_n), substitutions) ** 2
    if isinstance(
        effective_n, numbers.Number
    ):  # if symbolic, leave as a general expression
        eval_p = poly(eval_p, domain="QQ")
    # evaluate over a group of sets where our functions are constant
    s_sum = 0
    s_wt = 0
    # as example_vec has only n_set_positions non-zero values it itself is
    # invariant over permutations of the zero positions.
    # so averaging over placement and arrangement of non-zero positions is the
    # same as averaging over Sn
    values = symbols(
        " ".join([f"ph_{i}" for i in range(n_set_positions)])
    )  # new variables disjoint from originals
    for keyed_vec, wt in symmetry_fn(n=n, values=values, symmetry_args=symmetry_args):
        s_sum = s_sum + wt * _subsv(
            eval_p, {p_vars[i]: value for i, value in keyed_vec.items()}
        )
        s_wt = s_wt + wt
    if not isinstance(effective_n, numbers.Number):
        # symbols in effective_n are not part of the symmetries
        return s_sum / s_wt, values
    # identify the symmetric function
    soln = symmetrize(s_sum / s_wt, formal=True)
    assert is_infinitesimal_poly(soln[1])  # confirm was actually symmetric
    return soln[0]


def _fill_in_generator_pick_k(
    *,
    n: int,
    values: Iterable,
    symmetry_args,
):
    """
    Produce a generator that returns n-vectors and weights with 4 filled in from values and zeros elsewhere.
    This treating factorial(n_cells) as binomial(n_cells, n_set_positions) * factorial(n_set_positions) segments of interest,
    (each of size factorial(n_cells - n_set_positions) and returning one representative vector for each set.

    :param n: vector dimension to form
    :param values: values to fill in
    :param symmetry_args: dictionary carrying "n_set_positions"]
    """
    n = int(n)
    n_set_positions = int(symmetry_args["n_set_positions"])
    values = list(values)
    assert len(values) >= n_set_positions
    assert n >= n_set_positions
    for combo in combinations(range(n), n_set_positions):
        for perm in permutations(combo):
            vec = [0] * n
            for value_i, vec_i in enumerate(perm):
                vec[vec_i] = values[value_i]
            yield (
                {i: vec[i] for i in range(n)},
                1,
            )  # must cary zero positions that sometimes carry non-zero data


def identify_variance_fn(partition: Iterable[int]):
    """
    Identify the variance function by evaluating on a mostly zero example that
    is symmetrized on a set of states smaller than the full symmetric group.
    Works on a factorial(n_cells) = binomial(n_cells, 4) * factorial(4) * factorial(n_cells - 4) decomposition.

    :param partition: partition of group sizes to work with
    :return: variance polynomial as elementary symmetric polynomials
    """
    partition = list(partition)
    # eliminate some special cases to establish n is at least 4 for the n pick 4 methods
    if len(partition) <= 1:
        # special case: one group- so estimate constant over all permutations
        return 0
    if np.max(partition) <= 1:
        return 0
    if (partition == [2, 1]) or (partition == [1, 2]):
        # this and the above special case solve all partitions up through 4 symbols
        # s1**4/18 - s1**2*s2/3 + s2**2/2
        s = symbols(" ".join([f"s{i}" for i in range(3)]))
        return s[1] ** 4 / 18 - s[1] ** 2 * s[2] / 3 + s[2] ** 2 / 2
    n = sum(partition)
    assert n >= 4
    return _identify_variance_fn_through_sym(
        partition,
        symmetry_fn=_fill_in_generator_pick_k,
        symmetry_args={"n_set_positions": 4},
        detect_support=False,
    )


def s_binomial(n, k: int):
    """
    Return polynomial form of n choose k.
    :param n: value or symbol
    :param k: int
    """
    k = int(k)
    if k <= 0:
        return 1
    if k <= 1:
        return n
    if isinstance(n, numbers.Number):
        return binomial(n, k)
    return np.prod([n - i for i in range(k)]) / factorial(k)


def _fill_in_list_regular_blocks(*, n: int, values: Iterable, symmetry_args):
    """
    Produce a generator that returns n-vectors with 4 filled in from values and zeros elsewhere.
    This is assuming that all blocks of the partition are of size block_size.

    :param n: vector dimension to form
    :param values: values to fill in
    :param symmetry_args: dictionary carrying "effective_n_blocks", "effective_block_size" parameters
    """
    n = int(n)
    n_set_positions = int(symmetry_args["n_set_positions"])
    block_size = int(symmetry_args["block_size"])
    assert n_set_positions == 4
    values = list(values)
    assert len(values) == n_set_positions
    assert n >= n_set_positions
    assert block_size >= 4
    assert block_size <= n
    assert block_size >= 4  # could relax this
    assert (n % block_size) == 0
    n_blocks = int(n / block_size)
    assert n_blocks >= 2
    effective_n_blocks = symmetry_args.get("effective_n_blocks", n_blocks)
    effective_block_size = symmetry_args.get("effective_block_size", block_size)

    def new_keyed_vec():
        # must cary zero positions that sometimes carry non-zero data
        v = {}
        v[0] = 0
        v[1] = 0
        v[2] = 0
        v[3] = 0
        v[block_size] = 0
        v[block_size + 1] = 0
        if n_blocks > 2:
            v[2 * block_size] = 0
            if n_blocks > 3:
                v[3 * block_size] = 0
        return v

    keyed_vecs = []
    for perm in permutations(values):
        # 4
        v = new_keyed_vec()
        v[0] = perm[0]
        v[1] = perm[1]
        v[2] = perm[2]
        v[3] = perm[3]
        keyed_vecs.append(
            (v, s_binomial(effective_n_blocks, 1) * s_binomial(effective_block_size, 4))
        )
        # 2,2
        v = new_keyed_vec()
        v[0] = perm[0]
        v[1] = perm[1]
        v[block_size] = perm[2]
        v[block_size + 1] = perm[3]
        keyed_vecs.append(
            (
                v,
                s_binomial(effective_n_blocks, 2)
                * s_binomial(effective_block_size, 2) ** 2,
            )
        )
        # 3, 1
        v = new_keyed_vec()
        v[0] = perm[0]
        v[1] = perm[1]
        v[2] = perm[2]
        v[block_size] = perm[3]
        keyed_vecs.append(
            (
                v,
                s_binomial(effective_n_blocks, 1)
                * s_binomial(effective_block_size, 3)
                * s_binomial(effective_n_blocks - 1, 1)
                * s_binomial(effective_block_size, 1),
            )
        )
        if n_blocks > 2:
            # 2,1,1
            v = new_keyed_vec()
            v[0] = perm[0]
            v[1] = perm[1]
            v[block_size] = perm[2]
            v[2 * block_size] = perm[3]
            keyed_vecs.append(
                (
                    v,
                    s_binomial(effective_n_blocks, 1)
                    * s_binomial(effective_block_size, 2)
                    * s_binomial(effective_n_blocks - 1, 2)
                    * s_binomial(effective_block_size, 1) ** 2,
                )
            )
            if n_blocks > 3:
                # 1,1,1,1
                v = new_keyed_vec()
                v[0] = perm[0]
                v[block_size] = perm[1]
                v[2 * block_size] = perm[2]
                v[3 * block_size] = perm[3]
                keyed_vecs.append(
                    (
                        v,
                        s_binomial(effective_n_blocks, 4)
                        * s_binomial(effective_block_size, 1) ** 4,
                    )
                )
    return keyed_vecs


def identify_variance_fn_regular_blocks(
    *,
    n_blocks: int,
    block_size: int,
    detect_support: bool = True,
):
    """
    Identify the variance function by evaluating on a mostly zero example that
    is symmetrized on a set of states smaller than the full symmetric group.
    Works on a factorial(n_cells) = binomial(n_cells, 4) * factorial(4) * factorial(n_cells - 4) decomposition.

    :param n_blocks: number of blocks
    :param block_size: size of each block
    :param detect_support: if True try to remove non-supported variables (never set by symmetry_fn) from calculation.
    :return: variance polynomial as elementary symmetric polynomials
    """
    if (n_blocks <= 1) or (block_size <= 1):
        return 0
    return _identify_variance_fn_through_sym(
        [block_size] * n_blocks,
        symmetry_fn=_fill_in_list_regular_blocks,
        symmetry_args={"n_set_positions": 4, "block_size": block_size},
        detect_support=detect_support,
    )


def identify_variance_fn_regular_blocks_e(
    *,
    n_blocks,
    block_size,
    detect_support: bool = True,
):
    """
    Identify the variance function by working on a 4,4 system and substituting in different counts

    :param n_blocks: number of blocks
    :param block_size: size of each block >=4 or variable
    :param detect_support: if True try to remove non-supported variables (never set by symmetry_fn) from calculation.
    :return: variance polynomial as elementary symmetric polynomials
    """
    driver_pattern = [4] * 4
    if isinstance(n_blocks, numbers.Number):
        if n_blocks <= 1:
            return 0
        driver_pattern = [4] * min(4, n_blocks)
    if isinstance(block_size, numbers.Number):
        if block_size <= 1:
            return 0
        assert block_size >= 4
    return _identify_variance_fn_through_sym(
        driver_pattern,
        symmetry_fn=_fill_in_list_regular_blocks,
        symmetry_args={
            "n_set_positions": 4,
            "block_size": 4,
            "effective_n_blocks": n_blocks,
            "effective_block_size": block_size,
        },
        detect_support=detect_support,
        effective_n_blocks=n_blocks,
        effective_block_size=block_size,
    )


def build_symmetric_to_moment_mapping(deg_bound: int = 5):
    """
    Build mapping from elementary symmetric polynomials (non-central) moment polynomials.
    (Uses solve instead of explicit Newton identities.)

    :param degree_bound: degree bound of polynomials (exclusive)
    :return: s1 written as a formula of moments
    """
    y_vars = symbols(" ".join([f"y{i}" for i in range(deg_bound)]))
    m_vars = symbols(" ".join([f"m{i}" for i in range(deg_bound)]))
    s_vars = symbols(" ".join([f"s{i}" for i in range(deg_bound)]))
    m_polys = [sum([v**i for v in y_vars]) for i in range(deg_bound)]
    m_syms = []
    for mi in m_polys:
        si = symmetrize(mi, formal=True)
        assert si[1] == 0
        m_syms.append(si[0])
    s_solns = solve(
        [m_var - m_sym for m_var, m_sym in zip(m_vars[1:], m_syms[1:])], s_vars[1:]
    )[0]
    soln = {s: m for s, m in zip(s_vars[1:], s_solns)}
    return soln


def split_polynomial_on_symbols(p: Poly, syms: Iterable[Symbol]):
    """
    Split a polynomial on a variable.
    Same effect can be had by listing the non-polynomial variables as being in the domain (i.e. "Q[a, b]").

    :param p: polynomial to split
    :param syms: symbols to grade by
    :return: list of tuples (k, a, b) such that (poly(sum([cl[1] * cl[2] for cl in result])) - p) == 0, a only symbols from syms, b s-free
    """
    assert isinstance(p, Poly)
    syms = list(syms)
    assert len(syms) > 0
    assert np.all([isinstance(s, Symbol) for s in syms])
    sym_strs = set([str(s) for s in syms])
    poly_vars = tuple(p.gens)
    symbol_indices = set([i for i, pv in enumerate(poly_vars) if str(pv) in sym_strs])
    new_terms = [
        (
            tuple([v for i, v in enumerate(term[0]) if i in symbol_indices]),
            np.prod(
                [
                    poly_vars[i] ** v
                    for i, v in enumerate(term[0])
                    if i in symbol_indices
                ]
            ),
            term[1]
            * np.prod(
                [
                    poly_vars[i] ** v
                    for i, v in enumerate(term[0])
                    if i not in symbol_indices
                ]
            ),
        )
        for term in p.terms()
    ]
    # sort into powers of symbol
    keys = sorted(set(nt[0] for nt in new_terms))
    kv = {}
    collected = {k: 0 for k in keys}
    for nt in new_terms:
        collected[nt[0]] = collected[nt[0]] + nt[2]
        kv[nt[0]] = nt[1]
    result = tuple([(k, kv[k], collected[k]) for k in keys])
    assert (poly(sum([cl[1] * cl[2] for cl in result])) - p) == 0
    return result


def solve_for_block_size_poly(n_blocks: int):
    """
    Solve for the symmetric polynomial yielding the symmetric fn
    in s for the n_blocks, by block_size=s variance function.
    """
    n_blocks = int(n_blocks)
    block_size = symbols("b")
    vp = identify_variance_fn_regular_blocks_e(n_blocks=n_blocks, block_size=block_size)
    num, den = fraction(vp[0].expand().together())
    num = poly(num)
    den = poly(den)
    res = split_polynomial_on_symbols(num, [block_size])
    new_poly = 0
    for ri in res:
        si = symmetrize(ri[2], formal=True)
        assert si[1] == 0
        new_poly = new_poly + ri[1] * si[0]
    return (new_poly.expand() / den).simplify()


def symmetrize_poly_by_summing_out_selections(p, p_vars):
    """
    Symmetrize a polynomial by averaging it evaluated over all selections (bootstrap style).
    Note if B = symmetrize_poly_by_summing_out_selections.
    We do not have B(p1 * p2) = B(p1) * B(p2) (use p1 = p2 = s1 as counter example),
    do not have B(B(p)) = B(p) (use p=s2 as counter example),
    and do not have B(si) = si for i>1.
    Do have B(sum_i y_i**k) = sum_i y_i**k

    :param p: polynomial
    :param p_vars: variables
    :return: polynomial
    """
    # subs doesn't work right if symbols on both sides
    # so reserve some intermediate symbols
    place_holders = symbols(" ".join([f"ph_{i}" for i in range(len(p_vars))]))
    assert len(set(p_vars).intersection(place_holders)) == 0
    sub_expr = _subsv(p, {orig: ph for orig, ph in zip(p_vars, place_holders)})
    sym_result = 0
    sym_count = 0
    for perm in product(p_vars, repeat=len(p_vars)):
        r_sample = _subsv(sub_expr, {ph: new for ph, new in zip(place_holders, perm)})
        sym_result = sym_result + r_sample
        sym_count = sym_count + 1
    return (sym_result / sym_count).expand()
