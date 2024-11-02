
import numpy as np
import pandas as pd


def build_gcd_table(a: int, b: int) -> pd.DataFrame:
    """
    :param a: positive int
    :param b: non-negative int with b < a
    :return: extended GCD work table
    """
    a = int(np.abs(a))
    b = int(np.abs(b))
    if b > a:
        a, b = b, a
    assert (a >= b) and (b >= 0)
    result = None
    while True:
        if (b <= 0) or (a <= b):
            result = pd.concat(
                [
                    result,
                    pd.DataFrame(
                        {  # base case
                            "a": [a],
                            "b": [b],
                            "a%b": ["N/A"],
                            "u": [1],
                            "a//b": ["N/A"],
                            "v": [0],
                            "GCD(a, b)": [a],
                        }
                    ),
                ],
                ignore_index=True,
            )
            result["GCD(a, b)"] = a
            # back-fill u, v
            for i in reversed(range(result.shape[0] - 1)):
                result.loc[i, "u"] = result.loc[i + 1, "v"]
                result.loc[i, "v"] = (
                    result.loc[i + 1, "u"]
                    - result.loc[i, "a//b"] * result.loc[i + 1, "v"]
                )
            assert np.all(
                result["u"] * result["a"] + result["v"] * result["b"]
                == result["GCD(a, b)"]
            )
            return result
        d = a // b  # quotient
        r = a - b * d  # remainder
        result = pd.concat(
            [
                result,
                pd.DataFrame(
                    {
                        "a": [a],
                        "b": [b],
                        "a%b": [r],
                        "u": [None],
                        "a//b": [d],
                        "v": [None],
                        "GCD(a, b)": [None],
                    }
                ),
            ],
            ignore_index=True,
        )
        # prepare for next step using gcd(a, b) = gcd(b, r)
        a, b = b, r
