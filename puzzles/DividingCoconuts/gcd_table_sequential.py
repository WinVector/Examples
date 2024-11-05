from typing import Any, List, Optional
import numpy as np
import pandas as pd
from IPython.display import display


def _display_initial_forward_table(
        result: pd.DataFrame,
        *, 
        do_display: bool = True,
        row_count_hint: Optional[int] = None,
        captured_tables: Optional[List[Any]] = None,
        ) -> None:
    if not do_display:
        return
    result = result.reset_index(drop=True, inplace=False)  # copy to prevent interference
    if row_count_hint is not None:
        while result.shape[0] < row_count_hint:
            result.loc[result.shape[0]] = [None] * result.shape[1]
    def highlight_rowval(x):
        return ['background-color: yellow; font-weight: bold' if not pd.isna(cell) else '' for cell in x]
    result.attrs['note'] = "Initial table"
    styled_table = result.style.apply(highlight_rowval, axis=1).format(na_rep='')
    if captured_tables is not None:
        captured_tables.append(styled_table)
    display(styled_table.data.attrs['note'])
    display(styled_table)


def _display_intermediate_forward_table(
        result: List[pd.DataFrame],
        *, 
        do_display: bool = True,
        row_count_hint: Optional[int] = None,
        captured_tables: Optional[List[Any]] = None,
        ) -> None:
    if not do_display:
        return
    result = pd.concat(result, ignore_index=True)
    result = result.reset_index(drop=True, inplace=False)  # copy to prevent interference
    row_id = result.shape[0] - 1
    if row_count_hint is not None:
        while result.shape[0] < row_count_hint:
            result.loc[result.shape[0]] = [None] * result.shape[1]
    def highlight_rowval(x):
        if x.name == row_id:
            return ['background-color: yellow; font-weight: bold' if not pd.isna(cell) else '' for cell in x]
        if (x.name == row_id - 1) or (x.name == row_id - 2):
            return ['background-color: lightgreen' if col_name == 'r' else '' for col_name in x.index]
        return ['' for _ in x]
    if row_id <= 0:
        result.attrs['note'] = f"build row {row_id}: start (a >= b)"
    else:
        result.attrs['note'] = f"build row {row_id}: r[{row_id}] = r[{row_id-2}] % r[{row_id-1}], q[{row_id}] = r[{row_id-2}] // r[{row_id-1}]"
    styled_table = result.style.apply(highlight_rowval, axis=1).format(na_rep='')
    if captured_tables is not None:
        captured_tables.append(styled_table)
    display(styled_table.data.attrs['note'])
    display(styled_table)


def _display_backfill_step(
        result: pd.DataFrame, 
        *, i:int, 
        do_display: bool = True,
        captured_tables: Optional[List[Any]] = None,
        ) -> None:
    if not do_display:
        return
    result = result.reset_index(drop=True, inplace=False)  # copy to prevent interference
    if i == result.shape[0] - 1:
        result.attrs['note'] = f"fill row {i}: u[{i}]=1, v[{i}]=0"
    else:
        result.attrs['note'] = f"back fill row {i}: u[{i}]=v[{i+1}], v[{i}] = u[{i+1}] - q[{i+1}] * v[{i+1}]"
    def highlight_rowcol(x):
        res = ['' for _ in x]
        if (x.name == i):
            for col_i, col_name in enumerate(x.index):
                if col_name in ['u', 'v']:
                    res[col_i] = 'background-color: yellow; font-weight: bold'
        if (x.name == i+1):
            for col_i, col_name in enumerate(x.index):
                if col_name in ['q', 'u', 'v']:
                    res[col_i] = 'background-color: lightgreen'
        return res
    styled_table = result.style.apply(highlight_rowcol, axis=1).format(na_rep='')
    if captured_tables is not None:
        captured_tables.append(styled_table)
    display(styled_table.data.attrs['note'])
    display(styled_table)


def build_gcd_table(a: int, b: int, 
    *, 
    verbose: bool = False,
    record_q: bool = True,
    ) -> pd.DataFrame:
    """
    :param a: positive int
    :param b: non-negative int with b < a
    :return: extended GCD work table (not backfilled, see back_fill_gcd_table())
    Note: may swap a, b to establish entry invariant.
    """
    a, b = int(np.abs(a)), int(np.abs(b))
    if b > a:
        a, b = b, a
    assert (a >= b) and (b >= 0)
    row_count_hint = None
    if verbose:
        row_count_hint = build_gcd_table(a, b, record_q=False, verbose=False).shape[0]
    captured_tables = []
    start = pd.DataFrame({"r": [a, b]})
    if record_q:
        start["q"] = None
    result = [start]
    _display_initial_forward_table(
        start, do_display=verbose, row_count_hint=row_count_hint, captured_tables=captured_tables)
    while (b > 0) and (a > b):
        q = a // b  # quotient
        r = a - b * q  # remainder
        row = pd.DataFrame({"r": [r]})
        if record_q:
            row["q"] = q
        result.append(row)
        _display_intermediate_forward_table(
            result, do_display=verbose, row_count_hint=row_count_hint, captured_tables=captured_tables)
        # prepare for next step using gcd(a, b) = gcd(b, r)
        a, b = b, r
    gcd_table = pd.concat(result, ignore_index=True)
    gcd_table.attrs['captured_tables'] = captured_tables
    gcd_table.attrs['gcd'] = gcd_table.loc[gcd_table.shape[0] - 2, 'r']
    return gcd_table


def back_fill_gcd_table(result: pd.DataFrame, *, verbose: bool = False) -> None:
    """
    Back fill u, v into extended GCD table.
    See: build_gcd_table(), build_gcd_table_filled().
    """
    result["u"] = None
    result.loc[result.shape[0] - 1, "u"] = 1
    result["v"] = None
    result.loc[result.shape[0] - 1, "v"] = 0
    try:
        captured_tables = result.attrs['captured_tables']
    except KeyError:
        captured_tables = None
    _display_backfill_step(
        result, i=result.shape[0] - 1, do_display=verbose, captured_tables=captured_tables)
    for i in reversed(range(1, result.shape[0] - 1)):
        result.loc[i, "u"] = result.loc[i + 1, "v"]
        result.loc[i, "v"] = (result.loc[i + 1, "u"] 
                              - result.loc[i + 1, "q"] * result.loc[i + 1, "v"])
        _display_backfill_step(result, i=i, do_display=verbose, captured_tables=captured_tables)
    # save extended solution
    result.attrs['u'] = result.loc[1, 'u']
    result.attrs['v'] = result.loc[1, 'v']
    # check Bezout's identity
    gcd = result.loc[result.shape[0] - 2, 'r']
    lin_relns = [
        result.loc[i + 1, 'u'] * result.loc[i, 'r'] + result.loc[i + 1, 'v'] * result.loc[i + 1, 'r'] 
        for i in range(result.shape[0] - 1)]
    assert np.all(lin_relns == gcd)


def build_gcd_table_filled(a: int, b: int, *, verbose: bool = False) -> pd.DataFrame:
    """
    :param a: positive int
    :param b: non-negative int with b < a
    :return: extended GCD work table (backfilled)
    """
    result = build_gcd_table(a, b, record_q=True, verbose=verbose)
    back_fill_gcd_table(result, verbose=verbose)
    return result
