
import numpy as np
import pandas as pd
from IPython.display import display


def _display_intermediate_forward_table(result: pd.DataFrame, *, do_display: bool = True) -> None:
    if not do_display:
        return
    def highlight_rowval(x):
        return ['background-color: yellow; font-weight: bold' if (x.name == result.shape[0] - 1) and (not pd.isna(cell)) else '' for cell in x]
    display(f"build row {result.shape[0] - 1}")
    display(result.style.apply(highlight_rowval, axis=1).format(na_rep=''))


def _display_final_forward_table(result: pd.DataFrame, *, do_display: bool = True) -> None:
    if not do_display:
        return
    def highlight_rowcol(x):
        return ['background-color: yellow; font-weight: bold' if (x.name == result.shape[0] - 1) or (col_name == 'GCD(a, b)') else '' for col_name in x.index]
    display(f"finish with row {result.shape[0] - 1}")
    display(result.style.apply(highlight_rowcol, axis=1).format(na_rep=''))


def _display_backfill_step(result: pd.DataFrame, *, i:int, do_display: bool = True) -> None:
    if not do_display:
        return
    display(f"back fill row {i}")
    def highlight_rowcol(x):
       return ['background-color: yellow; font-weight: bold' if (x.name == i) and (col_name in ['u', 'v']) else '' for col_name in x.index]
    display(result.style.apply(highlight_rowcol, axis=1).format(na_rep=''))


def build_gcd_table(a: int, b: int, *, verbose: bool = False) -> pd.DataFrame:
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
    result = None
    while (b > 0) and (a > b):
        d = a // b  # quotient
        r = a - b * d  # remainder
        result = pd.concat([
                result,
                pd.DataFrame({
                    "a": [a], "b": [b], "a%b": [r], "a//b": [d]}),
            ],
            ignore_index=True)
        _display_intermediate_forward_table(result, do_display=verbose)
        # prepare for next step using gcd(a, b) = gcd(b, r)
        a, b = b, r
    result = pd.concat([
            result,
            pd.DataFrame({
                "a": [a], "b": [b], "a%b": ["N/A"], "a//b": ["N/A"]}),
        ],
        ignore_index=True)
    result["GCD(a, b)"] = a
    _display_final_forward_table(result, do_display=verbose)
    return result


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
