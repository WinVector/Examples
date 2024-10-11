"""
Code for ["Catching the Mice"](catching_the_mice.ipynb)
"""

from typing import Optional, Tuple, Sequence
import functools
import numpy as np
import pandas as pd
import sympy as sp
from sympy.ntheory.modular import crt


# set up example
WHITE_MOUSE = "white mouse"


# compute where a play of the eating k mice game goes
def run_cat_process(*, start: int, advance: int, k: int) -> Tuple[int, ...]:
    """
    Work out what mice are eaten in k repetitions of advancing advance mice forward
    in  list (wrapping around) and then removing the mouse pointed to. Initial start
    is at start index.
    """
    eaten = []
    mice = [WHITE_MOUSE] + [f"black mouse {i+1}" for i in range(12)]
    p = start
    for _ in range(k):
        p = (p + advance) % len(mice)  # perform the move
        v = mice[p]  # get the label of the mouse now pointing at
        mice.remove(v)  # remove from the list (and shift remaining mice)
        eaten.append(v)  # add removed mouse to ordered removal list
    return tuple(eaten)


def check_soln(traj: Sequence[int]) -> bool:
    """return True if valid white mouse eaten on 3rd step solution"""
    return (
        (len(traj) == 3)
        and (len(set(traj)) == len(traj))
        and (traj[0] != WHITE_MOUSE)
        and (traj[1] != WHITE_MOUSE)
        and (traj[2] == WHITE_MOUSE)
    )


def create_mod_k_column(m_range: int, *, mod: int):
    """Write (i % mod) for i in range(m_range) without division or explicit remainders"""
    modulo_count = np.zeros(m_range, dtype=int)
    row_i = 0
    remainder = 0
    while row_i < m_range:
        modulo_count[row_i] = remainder
        # prepare for next pass
        row_i += 1
        remainder += 1
        if remainder >= mod:
            remainder = 0
    return modulo_count


def push_column_back(c, *, ub: int):
    """round a vector of non-negative integers into range [0, ub-1] with only subtractions."""
    c = c.copy()  # don't alter original
    while True:  # this loop will only execute one or twice for the range of numbers we are giving it
        overs = c >= ub
        if not np.any(overs):
            return c
        c[overs] -= ub


def sieve_solutions_11_12_13(m_range: int) -> pd.DataFrame:
    """
    Build up a sieving table for "catching the mice".
    The goal is to describe a method that would be effective with pencil and paper.
    The emphasis is on avoiding many steps and avoiding expensive steps.
    """
    sieve = {"advance": range(m_range)}
    for mod in (11, 12, 13):
        sieve[f"advance%{mod}"] = create_mod_k_column(m_range, mod=mod)
    # calculate derived check equation columns
    sieve["((advance % 13) + advance) % 12"] = push_column_back(
        sieve["advance%13"] + sieve["advance%12"], ub=12)
    sieve["(((advance % 13) + advance) % 12) + advance) % 11"] = push_column_back(
        sieve["((advance % 13) + advance) % 12"] + sieve["advance%11"], ub=11)
    sieve["is_sieve_solution"] = (
        (sieve["advance%13"] != 0)
        & (sieve["((advance % 13) + advance) % 12"] != 0)
        & (sieve["(((advance % 13) + advance) % 12) + advance) % 11"] == 0))
    return pd.DataFrame(sieve)


def push_number_back_into_range(v: int, *, modulus: int) -> int:
    """Push number back into range 0, modulus-1 by adding or subtracting modulus enough times"""
    n_shifts = 0
    while v < 0:
        v += modulus
        n_shifts += 1
    while v >= modulus:
        v -= modulus
        n_shifts -= 1
    return v, n_shifts


# mark text escape codes
found_prefix = "\u001b[1m"
found_suffix = "\u001b[0m"


def incremental_solution_(key, *, shared_modulus, d_vectors, solns):
    """Build a new solution from an old one by adding a d vector"""
    for pattern in d_vectors.keys():
        old_key = tuple([ki - pi for ki, pi in zip(key, pattern)])
        try:
            sum = solns[old_key] + d_vectors[pattern]
            soln, n_shifts = push_number_back_into_range(sum, modulus=shared_modulus)
            soln_str = f"{found_prefix}{soln}{found_suffix}"
            if n_shifts == 0:
                note = f"{key} -> {solns[old_key]} + {d_vectors[pattern]} = {soln_str}"
            else:
                note = f"{key} -> {solns[old_key]} + {d_vectors[pattern]} = {sum} =({n_shifts}*{shared_modulus})= {soln_str}"
            return soln, pattern, note
        except KeyError:
            pass
    raise KeyError(str(key))


def mk_c_11_if_valid_(*, target: int, c_12: int, c_13: int) -> Optional[int]:
    """Return c_11 implied by c_12, c_13 if (c_11, c_12, c_13) is a valid solution, else return None"""
    c_11 = target - (c_12 + c_13)
    if (
        (c_11 >= 0)
        and (c_12 >= 0)
        and (c_13 >= 0)  # non-negativity
        and (c_11 < 11)
        and (c_12 < 12)
        and (c_13 < 13)  # range conditions
        and (c_13 != 0)  # don't eat white mouse on 1st step
    ):
        return c_11
    else:
        return None


def check_mice_equations(advance: int) -> bool:
    """confirm advance length matches catch the mice check equations"""
    return (
        ((advance % 13) != 0)
        and (((advance % 13) + advance) % 12 != 0)
        and ((((advance % 13) + advance) % 12 + advance) % 11 == 0)
    )


def find_candidates_11_12_13(target: int, *, d_vectors):
    """
    Find all the candidates for a given target k, return vetted solutions
    A human readable realization of the whole procedure is as follows.

    <blockquote>
    Complete the ledger below using the following rules. Note: we are only using `% 1716` (modulo) to explain what is wanted, we should calculate this with just a few subtractions or additions.<p/>

    * Let `target` be a fixed positive integer.
    * Run through every non-negative integer from `0` through `min(11, target)` inclusive as the value `c_12` in increasing order. End the procedure when there are not more valid `c_12`.
    * For each such value of `c_12`, find the largest integer `c_13` (if any) such that there is a `c_11 = target - (c_12 + c_13)` and `c_11, c_12, c_13` meets all of our puzzle check conditions (sign, `c_i < i`, and not eating the white mouse in the first or second step). If there are no such solutions go back to the next `c_12` step.
    * If this is the first time we got to this step:
        * Solve for `v` by CRT such that `v % 11 = c_11`, `v % 12 = c_12`, and `v % 13 = c_13`, and write down "start: `(c_11, c_12, c_13) = v`".
        * Otherwise, calculate `v` using the relation `v = f(c_11 - d_11, c_12 - d_12, c_12 - d_13) + d_vectors[(d_11, d_12, d_13)]` where we already know the value for `(c_11 - d_11, c_12 - d_12, c_12 - d_13)`, and `(d_11, d_12, d_13)` is one of the keys to our `d_vectors` table.
    * Write down "step: `(c_11, c_12, c_13) = v`".
    * For this value `v` calculate `(v + 12 * k) % 1716` for all integers `k` such that `(c_11 + k, c_12, c_13 - k)` meet all of our puzzle check conditions. List these in an additional indented "more candidates:" row in the ledger.
    * Return back to the pick next `c_12` step.
    </blockquote>
    """
    print(
        f"solutions to ((x%13 + x)%12 + x)%11 = 0 such that (x%13) + (x%12) + (x%11) = {target}"
    )
    print("vector notation: (soln % 11, soln % 12, soln % 13)")
    moduli = (11, 12, 13)
    shared_modulus = functools.reduce(sp.lcm, moduli)
    solns = []
    previous_solution = None
    for c_12 in range(0, min(11, target) + 1):  # obvious c_12 values
        c_13 = min(12, target - c_12)  # largest obvious c_13 attempt
        # walk up to first valid selection, if any
        while c_13 >= 0:
            c_11 = mk_c_11_if_valid_(target=target, c_12=c_12, c_13=c_13)
            if c_11 is not None:
                break
            # next pass
            c_13 -= 1
        if c_11 is None:
            continue  # no valid selection, try next pass
        # do the work
        if previous_solution is None:
            # full cost calculation only once
            v = int(crt(moduli, (c_11, c_12, c_13))[0])
            if not check_mice_equations(
                v
            ):  # use would not have to do this, just double checking
                raise ValueError(
                    f"start: {(c_11, c_12, c_13)} -> {v}, not a valid problem solution"
                )
            soln_str = f"{found_prefix}{v}{found_suffix}"
            print(f"start: {(c_11, c_12, c_13)} -> {soln_str}")
        else:
            v, pattern, note = incremental_solution_(
                (c_11, c_12, c_13),
                shared_modulus=shared_modulus,
                d_vectors=d_vectors,
                solns=previous_solution,
            )
            print("step: " + note)
        previous_solution = {(c_11, c_12, c_13): v}
        solns.append(v)
        # pick up more solution(s)
        c_13 -= 1
        note_i = []
        while c_13 >= 0:
            c_11 = mk_c_11_if_valid_(target=target, c_12=c_12, c_13=c_13)
            if c_11 is not None:
                v = push_number_back_into_range(v + 12, modulus=shared_modulus)[0]
                solns.append(v)
                note_i.append(found_prefix + str(v) + found_suffix)
            # next pass
            c_13 -= 1
        if len(note_i) > 0:
            print("  more solution(s) (by +12 rule): " + ", ".join(note_i))
    return solns
