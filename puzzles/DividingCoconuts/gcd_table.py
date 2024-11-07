from typing import Any, List, Optional
import numpy as np
import pandas as pd


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
        if x.name == row_id - 1:
            return ['background-color: lightgreen' if col_name in ['b', 'a%b'] else '' for col_name in x.index]
        return ['' for _ in x]
    if row_id <= 0:
        result.attrs['note'] = f"build row {row_id}: start (a >= b)"
    else:
        result.attrs['note'] = f"build row {row_id}: a[{row_id}]=b[{row_id-1}], b[{row_id}]=(a%b)[{row_id-1}]"
    styled_table = (
        result.style
            .set_properties(**{'min-width': '100px'})
            .apply(highlight_rowval, axis=1)
            .format(na_rep='')
    )
    if captured_tables is not None:
        captured_tables.append(styled_table)


def _display_final_forward_table(
        result: pd.DataFrame, 
        *, 
        do_display: bool = True,
        captured_tables: Optional[List[Any]] = None,
        ) -> None:
    if not do_display:
        return
    result = result.reset_index(drop=True, inplace=False)  # copy to prevent interference
    row_id = result.shape[0] - 1
    def highlight_rowcol(x):
        res = ['background-color: yellow; font-weight: bold' if col_name == 'GCD(a, b)' else '' for col_name in x.index]
        if x.name == result.shape[0] - 1:
            for i in range(len(x)):
                res[i] = 'background-color: yellow; font-weight: bold'
        if x.name == result.shape[0] - 2:
            for i, col_name in enumerate(x.index):
                if col_name in ['b', 'a%b']:
                    res[i] = 'background-color: lightgreen'
        return res
    result.attrs['note'] = f"finish with row {result.shape[0] - 1}: a[{row_id}]=b[{row_id-1}], b[{row_id}]=(a%b)[{row_id-1}], GCD= a[{row_id}]"
    styled_table = (
        result.style
            .set_properties(**{'min-width': '100px'})
            .apply(highlight_rowcol, axis=1)
            .format(na_rep='')
    )
    if captured_tables is not None:
        captured_tables.append(styled_table)


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
        result.attrs['note'] = f"back fill row {i}: u[{i}]=1, v[{i}]=0"
    else:
        result.attrs['note'] = f"back fill row {i}: u[{i}]=v[{i+1}], v[{i}] = u[{i+1}] - (a//b)[{i}] * v[{i+1}]"
    def highlight_rowcol(x):
        res = ['' for _ in x]
        if (x.name == i):
            for col_i, col_name in enumerate(x.index):
                if col_name in ['u', 'v']:
                    res[col_i] = 'background-color: yellow; font-weight: bold'
                elif (col_name == 'a//b') and (i < result.shape[0] - 1):
                    res[col_i] = 'background-color: lightgreen'
        if (x.name == i+1):
            for col_i, col_name in enumerate(x.index):
                if col_name in ['u', 'v']:
                    res[col_i] = 'background-color: lightgreen'
        return res
    styled_table = (
        result.style
            .set_properties(**{'min-width': '100px'})
            .apply(highlight_rowcol, axis=1)
            .format(na_rep='')
    )
    if captured_tables is not None:
        captured_tables.append(styled_table)


def build_gcd_table(a: int, b: int, 
    *, 
    verbose: bool = False) -> pd.DataFrame:
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
        row_count_hint = build_gcd_table(a, b, verbose=False).shape[0]
    captured_tables = []
    result = []
    while (b > 0) and (a > b):
        q = a // b  # quotient
        r = a - b * q  # remainder
        row = pd.DataFrame({"a": [a], "b": [b], "a%b": [r], "a//b": [q], "GCD(a, b)": None})
        result.append(row)
        _display_intermediate_forward_table(
            result, do_display=verbose, row_count_hint=row_count_hint, captured_tables=captured_tables)
        # prepare for next step using gcd(a, b) = gcd(b, r)
        a, b = b, r
    row = pd.DataFrame({"a": [a], "b": [b], "a%b": ["N/A"], "a//b": ["N/A"], "GCD(a, b)": None})
    result.append(row)
    gcd_table = pd.concat(result, ignore_index=True)
    gcd_table["GCD(a, b)"] = a
    _display_final_forward_table(gcd_table, do_display=verbose, captured_tables=captured_tables)
    gcd_table.attrs['captured_tables'] = captured_tables
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
    for i in reversed(range(result.shape[0] - 1)):
        result.loc[i, "u"] = result.loc[i + 1, "v"]
        result.loc[i, "v"] = (result.loc[i + 1, "u"] 
                              - result.loc[i, "a//b"] * result.loc[i + 1, "v"])
        _display_backfill_step(result, i=i, do_display=verbose, captured_tables=captured_tables)
    assert np.all(result["u"] * result["a"] + result["v"] * result["b"] == result["GCD(a, b)"])


def build_gcd_table_filled(a: int, b: int, *, verbose: bool = False) -> pd.DataFrame:
    """
    :param a: positive int
    :param b: non-negative int with b < a
    :return: extended GCD work table (backfilled)
    """
    result = build_gcd_table(a, b, verbose=verbose)
    back_fill_gcd_table(result, verbose=verbose)
    return result
