```python
import itertools
from typing import Dict, Hashable, Iterable, List, Set, Tuple
import numpy as np
from Galvin import list_color_square, valid_coloring
from pprint import pprint


def count_solutions(
        sq: List[List[Set[int]]],
        *,
        verbose: bool = False) -> int:
    """
    Count number of valid solutions to sq, by brute force.

    :param sq: list colorable Latin square specification
    :param verbose: if True print solutions.
    :return: number of valid fill-ins
    """
    n = len(sq)
    # flatten into list of value lists
    lists = []
    for vi in sq:
        for vij in vi:
            lists.append(list(vij))
    # try every combination
    n_valid = 0
    #for v in itertools.product(list(range(n)), repeat=n*n):
    for v in itertools.product(*lists):
        v = [v.tolist() for v in np.split(np.array(v, dtype=int), n)]
        is_valid = valid_coloring(sq=sq, coloring=v)
        if is_valid:
            n_valid = n_valid + 1
            if verbose:
                pprint(v)
    return n_valid
```


```python
print(count_solutions([
    [{0, 1}, {0, 1}], 
    [{0, 1}, {0, 1}],
]))

```

    2



```python
print(count_solutions([
    [{0, 1}, {0, 1}],
    [{0, 2}, {1, 2}],
], verbose=True))

```

    [[1, 0], [0, 1]]
    [[1, 0], [0, 2]]
    [[1, 0], [2, 1]]
    3



```python
print(count_solutions([
    [{0, 2}, {0, 1}],
    [{0, 2}, {1, 2}],
], verbose=True))
```

    [[2, 0], [0, 1]]
    [[2, 0], [0, 2]]
    [[2, 1], [0, 2]]
    3



```python
print(count_solutions([
    [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}],
    [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}],
    [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}],
]))
```

    12



```python
print(count_solutions([
    [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}],
    [{0, 1, 3}, {1, 2, 3}, {1, 2, 3}],
    [{0, 1, 3}, {1, 2, 3}, {1, 2, 3}],
]))
```

    28



```python
def solve_and_check(sq):
    """solve list coloring for Latin square, confirm and return answer"""
    soln = list_color_square(sq)
    assert valid_coloring(sq=sq, coloring=soln)
    return soln
```


```python
pprint(solve_and_check([
    [{0, 1}, {0, 1}], 
    [{0, 1}, {0, 1}],
]))
```

    [[1, 0], [0, 1]]



```python
pprint(solve_and_check([
    [{0, 2}, {0, 1}],
    [{0, 2}, {1, 2}],
]))
```

    [[2, 0], [0, 1]]



```python
pprint(solve_and_check([
    [{0, 2}, {0, 1}],
    [{0, 2}, {1, 2}],
]))
```

    [[2, 0], [0, 1]]



```python
pprint(solve_and_check([
    [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}],
    [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}],
    [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}],
]))
```

    [[2, 1, 0], [1, 0, 2], [0, 2, 1]]



```python
pprint(solve_and_check([
    [{0, 1, 2}, {0, 1, 2}, {0, 1, 2}],
    [{0, 1, 3}, {1, 2, 3}, {1, 2, 3}],
    [{0, 1, 3}, {1, 2, 3}, {1, 2, 3}],
]))
```

    [[2, 0, 1], [1, 2, 3], [0, 1, 2]]

