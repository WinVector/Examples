import numpy as np
from Galvin import calculate_kernel, list_color_square, valid_coloring


def test_Dinitz_kernel_1():
    # Dinitz example
    #
    #     v0 v1 v2
    # h0   0  1  2
    # h1   1  2  0
    # h2   2  0  1
    #
    # point to bigger in rows
    # point to smaller in columns
    #
    # input:
    n = 3
    cells = [(0, 1), (1, 1), (1, 2)]
    res = calculate_kernel(n=n, cells=cells)
    expect = [(0, 1), (1, 2)]
    assert res == expect


def test_Dinitz_coloring_std_1():
    # standard Latin square
    n = 5
    sq = [[set(range(n)) for j in range(n)] for i in range(n)]
    res = list_color_square(sq)
    assert valid_coloring(sq=sq, coloring=res)


def test_Dinitz_coloring_1():
    # import numpy as np
    # k = 8
    # n = 5
    # rng = np.random.default_rng(2023)
    # sq = [[set(rng.choice(k, n, replace=False)) for j in range(n)] for i in range(n)]
    sq = [
        [
            {0, 1, 2, 5, 6},
            {0, 1, 2, 3, 6},
            {0, 1, 2, 3, 4},
            {0, 1, 2, 6, 7},
            {1, 4, 5, 6, 7},
        ],
        [
            {1, 2, 3, 4, 5},
            {1, 2, 4, 5, 7},
            {1, 3, 4, 5, 6},
            {0, 3, 4, 6, 7},
            {1, 3, 5, 6, 7},
        ],
        [
            {0, 1, 3, 4, 5},
            {0, 1, 4, 5, 6},
            {0, 3, 4, 5, 7},
            {0, 1, 3, 4, 7},
            {0, 1, 2, 4, 5},
        ],
        [
            {0, 1, 2, 5, 7},
            {0, 1, 2, 5, 6},
            {0, 1, 2, 3, 6},
            {1, 2, 4, 5, 6},
            {0, 1, 2, 3, 6},
        ],
        [
            {1, 2, 4, 6, 7},
            {0, 1, 2, 6, 7},
            {1, 2, 3, 4, 6},
            {0, 3, 4, 6, 7},
            {0, 1, 3, 5, 7},
        ],
    ]
    res = list_color_square(sq)
    assert valid_coloring(sq=sq, coloring=res)


def test_Dinitz_coloring_x():
    rng = np.random.default_rng(2023)

    def intset(v):
        """Make sure we don't have np.int64 contaimination."""
        return {int(vi) for vi in v}
    
    for n in range(1, 10):
        for k in range(n, n + 5):
            for rep in range(10):
                sq = [[intset(rng.choice(k, n, replace=False)) for j in range(n)] for i in range(n)]
                res = list_color_square(sq)
                assert valid_coloring(sq=sq, coloring=res)


def test_Dinitz_issue_1():
    # corner case we ran into
    sq = [[{0, 3}, {0, 2}], [{0, 1}, {1, 2}]]
    res = list_color_square(sq)
    assert valid_coloring(sq=sq, coloring=res)
