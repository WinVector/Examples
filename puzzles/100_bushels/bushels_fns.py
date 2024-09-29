

from typing import Tuple

import numpy as np
import sympy as sp

import smithnormalform
import smithnormalform.matrix
import smithnormalform.z
import smithnormalform.snfproblem


def is_integers(v) -> bool:
    """Check that a sympy matrix is all ingegers"""
    for i in range(v.shape[0]):
        for j in range(v.shape[1]):
            if v[i, j] != int(v[i, j]):
                return False
    return True


def is_non_neg(v) -> bool:
    """Check that a sympy matrix is non-negative"""
    for i in range(v.shape[0]):
        for j in range(v.shape[1]):
            if v[i, j] < 0:
                return False
    return True


def to_sympy_int_Matrix_(v) -> sp.Matrix:
    """convert from smithnormalform matrix to sympy matrix"""
    h : int = v.h
    w : int = v.w
    return sp.Matrix([
        [int(str(v.get(row_i, col_j))) for col_j in range(w)] 
        for row_i in range(h)
    ])


def right_pseudo_inverse_of_Smith_normal_form(j: sp.Matrix) -> sp.Matrix:
    """build right pseudo inverse of j"""
    jp = j[range(j.shape[0]), range(j.shape[0])].inv()
    for insert_position in range(j.shape[0], j.shape[1]):
        jp = jp.row_insert(insert_position, sp.Matrix([0] * j.shape[0]).T)
    # confirm on the right inverse
    assert j * jp == sp.Matrix.eye(j.shape[0])
    return jp


def smith_normal_form(a: sp.Matrix) -> Tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    """
    Write s * a * t = j
    where j is in Smith normal form, and S, T unimodular
    uses: https://pypi.org/project/smithnormalform/
    (sympy Smith normal form doesn't return transform matrices)
    """

    assert is_integers(a)
    # convert to Smith normal form data type
    av_elements = sum([
        [a[row_i, col_j] for col_j in range(a.shape[1])] 
        for row_i in range(a.shape[0])], start=[])
    asnf = smithnormalform.matrix.Matrix(
        a.shape[0], 
        a.shape[1],
        [smithnormalform.z.Z(int(v)) for v in av_elements])
    # solve
    prob = smithnormalform.snfproblem.SNFProblem(asnf)
    prob.computeSNF()
    # confirm solution
    assert prob.isValid()
    assert prob.S * prob.A * prob.T == prob.J
    # pull into sympy representation
    s = to_sympy_int_Matrix_(prob.S)
    t = to_sympy_int_Matrix_(prob.T)
    j = to_sympy_int_Matrix_(prob.J)
    # confirm solution
    assert s * a * t == j
    # standardize signs
    for i in range(j.shape[0]):
        if j[i, i] < 0:
            j[:, i] = -j[:, i]
            s[i, :] = -s[i, :]
    assert s * a * t == j
    assert is_integers(s)
    assert is_integers(t)
    assert is_integers(j)
    s_det = s.det()
    assert (s_det == 1) or (s_det == -1)
    t_det = t.det()
    assert (t_det == 1) or (t_det == -1)
    return s, t, j
