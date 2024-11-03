from typing import List, Optional
import numpy as np
import pandas as pd
from IPython.display import display


captured_tables = []


def _display_intermediate_forward_table(
        result: List[pd.DataFrame],
        *, 
        do_display: bool = True,
        row_count_hint: Optional[int] = None) -> None:
    global captured_tables
    if not do_display:
        return
    result = pd.concat(result, ignore_index=True)
    result = result.reset_index(drop=True, inplace=False)  # copy to prevent interference
    row_id = result.shape[0] - 1
    if row_count_hint is not None:
        while result.shape[0] < row_count_hint:
            result.loc[result.shape[0]] = [None] * result.shape[1]
    def highlight_rowval(x):
        return ['background-color: yellow; font-weight: bold' if (x.name == row_id) and (not pd.isna(cell)) else '' for cell in x]
    display(f"build row {row_id}")
    styled_table = result.style.apply(highlight_rowval, axis=1).format(na_rep='')
    captured_tables.append(styled_table)
    display(styled_table)


def _display_final_forward_table(result: pd.DataFrame, *, do_display: bool = True) -> None:
    global captured_tables
    if not do_display:
        return
    result = result.reset_index(drop=True, inplace=False)  # copy to prevent interference
    def highlight_rowcol(x):
        return ['background-color: yellow; font-weight: bold' if (x.name == result.shape[0] - 1) or (col_name == 'GCD(a, b)') else '' for col_name in x.index]
    display(f"finish with row {result.shape[0] - 1}")
    styled_table = result.style.apply(highlight_rowcol, axis=1).format(na_rep='')
    captured_tables.append(styled_table)
    display(styled_table)


def _display_backfill_step(result: pd.DataFrame, *, i:int, do_display: bool = True) -> None:
    global captured_tables
    if not do_display:
        return
    result = result.reset_index(drop=True, inplace=False)  # copy to prevent interference
    display(f"back fill row {i}")
    def highlight_rowcol(x):
       return ['background-color: yellow; font-weight: bold' if (x.name == i) and (col_name in ['u', 'v']) else '' for col_name in x.index]
    styled_table = result.style.apply(highlight_rowcol, axis=1).format(na_rep='')
    captured_tables.append(styled_table)
    display(styled_table)


def build_gcd_table(a: int, b: int, 
    *, 
    add_quotients: bool = True,
    verbose: bool = False) -> pd.DataFrame:
    """
    :param a: positive int
    :param b: non-negative int with b < a
    :return: extended GCD work table (not backfilled, see back_fill_gcd_table())
    Note: may swap a, b to establish entry invariant.
    """
    global captured_tables
    a, b = int(np.abs(a)), int(np.abs(b))
    if b > a:
        a, b = b, a
    assert (a >= b) and (b >= 0)
    row_count_hint = None
    if verbose:
        row_count_hint = build_gcd_table(a, b, verbose=False).shape[0]
        captured_tables.clear()
    result = []
    while (b > 0) and (a > b):
        q = a // b  # quotient
        r = a - b * q  # remainder
        row = pd.DataFrame({"a": [a], "b": [b], "a%b": [r]})
        if add_quotients:
            row["a//b"] = q
        result.append(row)
        _display_intermediate_forward_table(result, do_display=verbose, row_count_hint=row_count_hint)
        # prepare for next step using gcd(a, b) = gcd(b, r)
        a, b = b, r
    row = pd.DataFrame({"a": [a], "b": [b], "a%b": ["N/A"]})
    if add_quotients:
        row["a//b"] = "N/A"
    result.append(row)
    gcd_table = pd.concat(result, ignore_index=True)
    gcd_table["GCD(a, b)"] = a
    _display_final_forward_table(gcd_table, do_display=verbose)
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
    _display_backfill_step(result, i=result.shape[0] - 1, do_display=verbose)
    for i in reversed(range(result.shape[0] - 1)):
        result.loc[i, "u"] = result.loc[i + 1, "v"]
        result.loc[i, "v"] = (result.loc[i + 1, "u"] 
                              - result.loc[i, "a//b"] * result.loc[i + 1, "v"])
        _display_backfill_step(result, i=i, do_display=verbose)
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
