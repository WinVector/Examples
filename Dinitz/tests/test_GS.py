from GS import match_Gale_Shapley


def test_GS_1():
    res = match_Gale_Shapley(
        left_preferences={
            1: ["b", "a", "c"],
            2: ["c", "b", "a"],
            3: ["a", "b", "c"],
        },
        right_preferences={
            "a": [3, 2, 1],
            "b": [2, 3, 1],
            "c": [1, 2, 3],
        },
    )
    expect = [(1, "c"), (2, "b"), (3, "a")]
    assert res == expect


def test_GS_2():
    # from a Latin square
    res = match_Gale_Shapley(
        left_preferences={
            1: ["a", "b", "c"],
            2: ["b", "c", "a"],
            3: ["c", "a", "b"],
        },
        right_preferences={
            "a": [2, 3, 1],
            "b": [3, 1, 2],
            "c": [1, 2, 3],
        },
    )
    expect = [(1, "c"), (2, "a"), (3, "b")]
    assert res == expect


def test_GS_issue_1():
    # corner case we ran into
    res = match_Gale_Shapley(
        left_preferences={1: [1, 0]},
        right_preferences={0: [1], 1: [1]}
    )
