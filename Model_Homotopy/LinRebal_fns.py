
import functools
import sympy as sp
import numpy as np
import pandas as pd
from plotnine import *


def det_by_Laplace_expansion(X):
    """slow, but involves no divisions (otherwise just use sp.det())"""
    n = X.shape[0]
    if n <= 1:
        if len(X.shape) == 1:  # work around numpy bug
            return X[0]
        return X[0, 0]
    assert len(X.shape) == 2
    assert n == X.shape[1]
    # get the sign adjusted minors
    res = 0
    for i in range(n):
        minor = X[
                [x_i for x_i in range(n) if x_i != i],
                [x_j for x_j in range(n) if x_j != 0]
                ]
        term = X[i, 0] * det_by_Laplace_expansion(minor)
        if (i % 2) == 0:
            res = res + term
        else:
            res = res - term
    return res.expand()


def _det(X):
    # return sp.det(X)
    return det_by_Laplace_expansion(X)
    

def solve_by_Cramers_rule(
        XtX,
        Xty,
        *,
        normalize: bool = False,
):
    """solve b ~ (XtX)^(-1) Xty"""
    common_denom = _det(XtX)
    lc = sp.polys.polytools.LC(common_denom)
    if normalize:
        common_denom = common_denom / float(lc)
    soln_nums = sp.Matrix([0] * (XtX.shape[0]))
    for j in range(XtX.shape[0]):
        XtXc = XtX.copy()
        XtXc[:, j] = Xty
        if normalize:
            soln_nums[j] = _det(XtXc) / float(lc)
        else:
            soln_nums[j] = _det(XtXc)
    return sp.Matrix(soln_nums), common_denom


@functools.cache
def Chebyshev_first_kind(d: int, z: sp.Symbol):
    if d <= 0:
        return 1
    if d <= 1:
        return z
    return (2 * z * Chebyshev_first_kind(d-1, z) - Chebyshev_first_kind(d-2, z)).expand()


def solve_equality_near_target(
    *,
    X,
    p,
    y0,
):
    """
    Given: X (m row by n column matrix), y0 (n entry column vector), p (m entry column vector), m <= n.
    Find: y (n entry column vector)
    Minimizing t(y - y0) (y - y0), subject to X y = p

    Method: Lagrange multipliers
    L := t(y - y0) (y - y0) + t(lambda) (X y - p)
      dL/dy = 2 (y - y0) + t(X) lambda = 0   ->   y = y0  (1/2) t(X) lambda
    Subs y solution from above into X y = p equation
       X (y0 - (1/2) t(X) lambda) = p   ->   lambda = 2 inv(X t(X)) (X y0 - p)
       Then use y = y0 - (1/2) t(X) lambda

    # Example values for X, y, and m
    X = np.array([[1, 2, 3], [3, 4, 5]])
    p = np.array([5, 11])
    y0 = np.array([1, 1, 1])
    y = solve_equality_near_target(X=X, p=p, y0=y0)
    assert np.max(np.abs((X @ y) - p)) < 1e-8
    """
    X = np.array(X, dtype=float)
    y0 = np.array(y0, dtype=float)
    p = np.array(p, dtype=float)
    m, n = X.shape
    assert m <= n
    assert (n, ) == y0.shape
    assert (m, ) == p.shape
    lambda_ = 2 * np.linalg.solve(X @ X.T, (X @ y0) - p)
    y = y0 - (0.5 * X.T @ lambda_)
    assert np.max(np.abs((X @ y) - p)) < (1e-8 * np.max([1, np.mean(np.abs(p))]))
    return y


def engineer_new_ys(
    *,
    X1,
    y1,
    X2,
    y2,
    target_j: int,
    z,
    target_poly,
):
    XtX = ((1-z) * sp.Matrix(X1.T @ X1)) + (z * sp.Matrix(X2.T @ X2))
    # get the sign adjusted minors
    signed_minors = sp.Matrix([0] * (XtX.shape[0]))
    for i in range(XtX.shape[0]):
        minor = XtX[
                [x_i for x_i in range(XtX.shape[0]) if x_i != i], 
                [x_j for x_j in range(XtX.shape[1]) if x_j != target_j]
                ]
        signed_minors[i] = (-1)**(i + target_j) * _det(minor)
    # confirm signed minor expansion
    dXtX = _det(XtX)
    minor_check = (
        np.sum([XtX[x_i, target_j] * signed_minors[x_i] for x_i in range(XtX.shape[0])]).expand()
        - dXtX)
    assert np.max(np.abs(sp.Poly(minor_check).coeffs())) < 1e-8 * np.max([1, np.mean(np.abs(sp.Poly(dXtX).coeffs()))])
    # get the polynomial coefs
    def get_coef_vector(p):
        vec = [0] * XtX.shape[0]
        terms = sp.Poly(p).terms()
        for pwr, coef in terms:
            vec[pwr[0]] = float(coef)
        return vec

    vecs = [get_coef_vector(sm) for sm in signed_minors]
    vecs = np.array(vecs)
    target_vec = get_coef_vector(target_poly.expand())
    mixing_soln = np.linalg.lstsq(vecs.T, target_vec, rcond=None)[0]
    # confirm mixing soln yields target vector
    assert np.max(np.abs(
        np.array(get_coef_vector(np.sum([mixing_soln[j] * signed_minors[j] 
                                         for j in range(len(signed_minors))]).expand()))
        - np.array(target_vec))) < 1e-8 * np.max([1, np.mean(np.abs(target_vec))])
    # want ((1-z) * sp.Matrix(X1.T @ ys1)) + (z * sp.Matrix(X2.T @ ys2)) == mixing solution
    # so solve X1.T @ ys1 = mixing_soln and X2.T @ ys2 = mixing_soln
    # ys1 = np.linalg.lstsq(X1.T, mixing_soln, rcond=None)[0]
    # ys2 = np.linalg.lstsq(X2.T, mixing_soln, rcond=None)[0]
    ys1 = solve_equality_near_target(X=X1.T, p=mixing_soln, y0=y1)
    ys2 = solve_equality_near_target(X=X2.T, p=mixing_soln, y0=y2)
    scale = np.mean(np.abs(ys1)) + np.mean(np.abs(ys2))
    return 1e+6 * ys1 / scale, 1e+6 * ys2 / scale


colors = [  # https://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=8
    '#1b9e77', '#d95f02', '#7570b3',
    '#e7298a', '#66a61e', '#e6ab02',
    '#a6761d', '#666666']


def plot_linear_diagram(
    evals_ends_plot
):
    return (
        ggplot(
            data=evals_ends_plot,
            mapping=aes(
                x='z', 
                y='value', 
                color='coefficient')
        )
        + geom_line(size=1, alpha=0.8, linetype="dashed")
        + geom_point(size=3, alpha=0.8)
        + scale_color_manual(colors)
        + geom_vline(xintercept=0.0, alpha=0.8, linetype="dashdot")
        + geom_vline(xintercept=0.50, alpha=0.8, linetype="dashdot")
        + geom_vline(xintercept=1, alpha=0.2, linetype="dashdot")
        + ggtitle("a naive imagining of how coefficients move as a function of data mixture")
    )


def plot_coefficient_curves(
    evals,
    *,
    evals_ends_plot=None,
    title: str,
):
    evals_plot = evals.melt(
        id_vars=['z'], 
        var_name='coefficient', 
        value_name='value')
    res = (
        ggplot(
            data=evals_plot,
            mapping=aes(
                x='z', 
                y='value', 
                color='coefficient')
        )
        + geom_line(size=1, alpha=0.8)

        + scale_color_manual(colors)
        + geom_vline(xintercept=0.0, alpha=0.8, linetype="dashdot")
        + geom_vline(xintercept=0.50, alpha=0.8, linetype="dashdot")
        + geom_vline(xintercept=1, alpha=0.2, linetype="dashdot")
        + ggtitle(title)
    )
    if evals_ends_plot is not None:
        res = (
            res
                + geom_point(data=evals_ends_plot,
                    size=3, alpha=0.8)
        )
    return res


def plot_single_curve(
    evals,
    *,
    target_j: int,
    title: str,
):
    return (
        ggplot()
        + geom_line(
            data=evals,
            mapping=aes(x='z', y=f'b[{target_j}]'),
            color = colors[target_j],
            size=2,
        )
        + ggtitle(title)
    )


def plot_poly_curve(
    target_evals,
    *,
    all_target_roots,
    target_j: int,
):
    return (
        ggplot()
        + geom_line(
            data=target_evals,
            mapping=aes(x='z', y='target_polynomial'),
            color = colors[target_j],
            size=2,
            linetype="dashed",
        )
        + geom_point(
            data=all_target_roots,
            mapping=aes(x='root', y='crossing'),
            color='blue',
            size=5,
            alpha=0.5,
        )
        + geom_hline(yintercept=0, linetype="dashdot", alpha=0.5)
        + ggtitle("designed zero crossings for new example")
    )


def plot_curve_annotated(
    eval_eng_direct,
    *,
    all_target_roots,
    target_j: int,
):
    return (
        ggplot(
        )
        + geom_line(
            data=eval_eng_direct,
            mapping=aes(x='z', y=f'b[{target_j}]'),
            color = colors[target_j],
            size=2,
        )
        + geom_point(
            data=all_target_roots,
            mapping=aes(x='root', y='crossing'),
            color='blue',
            size=5,
            alpha=0.5,
        )
        + geom_hline(yintercept=0, linetype="dashdot", alpha=0.5)
        + ggtitle(f"""fit coefficient b[{target_j}] as a function of data mixture
direct sklearn.linear_model.LinearRegression fits
(difference in shape is common solution denominator)""")
    )
