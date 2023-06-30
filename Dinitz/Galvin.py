import ast
import sys
from pprint import pprint
from typing import Dict, Hashable, Iterable, List, Set, Tuple
from GS import match_Gale_Shapley


def _sort_prefs(
    *, n: int, k: int, prefs_k: Iterable[int], reverse: bool = False
) -> List[int]:
    """
    Sort items according to (i + j) % n Latin square ordering.

    :param n: order of latin square.
    :param k: row or column we are in
    :param prefs_k: matched items
    :param reverse: if True reverse sorting.
    """
    prefs_k = {(k + v) % n: v for v in prefs_k}
    prefs_k = [prefs_k[k] for k in sorted(prefs_k.keys(), reverse=reverse)]
    return prefs_k


def _partially_confirm_kernel(
    kernel: Iterable[Tuple[int, int]],
    *,
    n: int,
    cells: Iterable[Tuple[int, int]],
) -> bool:
    """
    Confirm kernel is a non-empty subset of cells with no row or column used twice.
    This is only a partial confirm of the kernel, as we are not
    checking order relations.

    :param kernel: (i, j) pairs forming a kernel for cells
    :param n: order of latin square.
    :param cells: (i, j) pairs we want a stable marriage over (not empty)
    :return: True if kernel is valid
    """
    n = int(n)
    cells = list(cells)
    kernel = list(kernel)
    assert len(kernel) > 0
    kernel_set = set(kernel)
    left_set = set()
    right_set = set()
    for c in kernel:
        assert c in kernel_set
        assert c[0] not in left_set
        assert c[1] not in right_set
        left_set.add(c[0])
        right_set.add(c[1])


def calculate_kernel(n: int, cells: Iterable[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Compute a graph kernel for cells using a Latin square order relation.
    A kernel of cells is a subset of cells that is a subset of cells,
    idependent (no two cells with same row or column order), and dominating
    (each cell skipped is either pointed to by a lessor cell in row or points
    to a grear cell in column for some Latin square ordering).

    :param n: order of latin square.
    :param cells: (i, j) pairs we want a stable marriage over (not empty)
    :return: subset of cells that is a graph kernel.
    """
    n = int(n)
    cells = list(cells)
    assert n > 0
    # re-pack cells into preference lists (not yet ordered)
    left_preferences = {i: set() for i in range(n)}
    right_preferences = {i: set() for i in range(n)}
    for hi, vi in cells:
        left_preferences[hi].add(vi)
        right_preferences[vi].add(hi)
    left_preferences = {
        k: _sort_prefs(n=n, k=k, prefs_k=prefs_k, reverse=False)
        for k, prefs_k in left_preferences.items()
        if len(prefs_k) > 0
    }
    right_preferences = {
        k: _sort_prefs(n=n, k=k, prefs_k=prefs_k, reverse=True)
        for k, prefs_k in right_preferences.items()
        if len(prefs_k) > 0
    }
    res = match_Gale_Shapley(
        left_preferences=left_preferences, right_preferences=right_preferences
    )
    _partially_confirm_kernel(res, n=n, cells=cells)
    return res


def _free_squares_with_color(
    *, sq: List[List[Set[int]]], color: int, coloring: List[List[int]]
) -> List[Tuple[int, int]]:
    """
    Return list of all free squares with a given color available.

    :param sq: grid of color set squares
    :param color: color we are looking for
    :param coloring: coloring we are checking against
    """
    n = len(sq)
    cells = []
    for i in range(n):
        for j in range(n):
            if (coloring[i][j] is None) and (color in sq[i][j]):
                cells.append((i, j))
    return cells


def list_color_square(sq: List[List[Set[int]]]) -> List[List[int]]:
    """
    List-color a square where each color is used at most once per
    row or column, and colors are chosen from the sets specifed.
    Array should be square, and each set should have cardinality at
    least n.

    :param sq: n by n array of sets of allowed colors (non-empty, ints)
    :return: coloring
    """
    # get dimensions
    n = len(sq)
    assert n >= 0
    # check expected properties
    for vi in sq:
        assert isinstance(vi, list)
        assert len(vi) == n
        for vij in vi:
            assert isinstance(vij, set)
            assert len(vij) >= n
            for vijv in vij:
                assert isinstance(vijv, int)
    # get color set
    colors = set()
    for vi in sq:
        for vij in vi:
            colors.update(vij)
    # start coloring
    coloring = [[None] * n for i in range(n)]
    n_blank = n * n
    for color in colors:
        cells = _free_squares_with_color(sq=sq, color=color, coloring=coloring)
        if len(cells) < 1:
            continue
        kernel = calculate_kernel(n=n, cells=cells)
        for i, j in kernel:
            if coloring[i][j] is None:
                coloring[i][j] = color
                n_blank = n_blank - 1
        if n_blank <= 0:
            break
    assert n_blank == 0
    return coloring


def valid_coloring(*, sq: List[List[Set[int]]], coloring: List[List[int]]) -> bool:
    """
    Check if coloring is valid. coloring selects allowed color
    for each cell with no dupicates in row or column.

    :param sq: list colorable grid (non empty)
    :param coloring: proposed coloring
    :return: True if coloring is valid.
    """
    # get dimensions
    n = len(sq)
    assert n >= 0
    # check basic types and dimensions
    if not isinstance(coloring, list):
        return False
    if len(coloring) != n:
        return False
    for vi in coloring:
        if not isinstance(vi, list):
            return False
        if len(vi) != n:
            return False
        for vij in vi:
            if not isinstance(vij, int):
                return False
    # check valid colors chosen
    for i in range(n):
        for j in range(n):
            if coloring[i][j] not in sq[i][j]:
                return False
    # check no color is used twice in a row or column
    row_obs = [set() for i in range(n)]
    col_obs = [set() for i in range(n)]
    for i in range(n):
        for j in range(n):
            c_ij = coloring[i][j]
            if c_ij in row_obs[i]:
                return False
            row_obs[i].add(c_ij)
            if c_ij in col_obs[j]:
                return False
            col_obs[j].add(c_ij)
    return True


# Compute list coloring for input square.
# Example:
# echo '[[{0, 3}, {0, 2}], [{0, 1}, {1, 2}]]' | python Galvin.py
if __name__ == '__main__':
    input_text = sys.stdin.read()
    sq = ast.literal_eval(input_text)
    res = list_color_square(sq)
    assert valid_coloring(sq=sq, coloring=res)
    pprint(res)
