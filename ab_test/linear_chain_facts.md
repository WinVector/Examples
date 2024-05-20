# Linear Markov Chain Facts

I want to collect some "great things to know about linear Markov chains."

For this note we are working with a [Markov chain](https://en.wikipedia.org/wiki/Markov_chain) on states that are the integers `0` through `k` (`k > 0`). A Markov chain is an iterative random process with time tracked as an increasing integer `t`, and the next state of the chain depending only on the current (soon to be previous) state. For our linear Markov chain the only possible next states from state `i` are: `i` (called a "self loop" when present), `i+1` (called up or right), and `i-1` (called down or left). In no case does the chain progress below `0` or above `k`.

There are two important variations of this Markov chain:

  * The absorbing one, where the exit probabilities of states `0` and `k` are both zero. All other up/right probabilities are `p` and all other down/left probabilities are `1-p`.
  * The stationary one, where all up/right probabilities are `p/2` and all down/left probabilities are `(1-p)/2` (the rest of the time taking self loops). "Stationary" in this case means the behavior of the chain is approaching a single limiting or stationary behavior (compared to the absorbing chains which have two different absorbing states).

The absorbing chain is illustrated below.

<img src="https://win-vector.com/wp-content/uploads/2023/12/p_walk.png">

The stationary chain is similar.

For this sort of Markov chain one can directly solve for most of the important behaviors. This is a bit under-taught, and good to keep as a reference.

If `p = 1/2` then:

  * On the absorbing chain the probability of stopping at state `k`, given one starts at state `i` is: `i/k`.
  * On the absorbing chain the probability of stopping at state `0`, given one starts at state `i` is: `1 - i/k`.
  * On the absorbing chain the expected time to first stop at either of state `0` or `k`, given one starts at state `i` is: `i * (k - i)`.
  * On the stationary chain the steady-state probability of seeing the chain in state `i` is: `1/(k+1)`.

If `0 < p < 1` and `p != 1/2`, set `z = p/(1-p)` (the odds) then:

  * On the absorbing chain the probability of stopping at state `k`, given one starts at state `i` is: `(z**k - z**(k-i)) / (z**k - 1)`.
  * On the absorbing chain the probability of stopping at state `0`, given one starts at state `i` is: `(z**(k-i) - 1) / (z**k - 1)`.
  * On the absorbing chain the expected time to first stop at either of state `0` or `k`, given one starts at state `i` is: `((z+1)/(z-1)) * (k * (z**k - z**(k-i)) / (z**k - 1) - i)`.
  * On the stationary chain the steady-state probability of seeing the chain in state `i` is: `z**i * (z - 1) / (z**(k+1) - 1)`.


We also have an explicit bound on the probability of the absorbing chain running past a given time [here](https://github.com/WinVector/Examples/blob/main/ab_test/TheBiasedDrunkardsWalk.ipynb) (though one can get similar by arguing the run time shouldn't be too far from its expected value that often and attempting to apply a [concentration inequality](https://en.wikipedia.org/wiki/Concentration_inequality)).

Please check out more of our series on Markov chains:

<ul>
<li><a href="https://win-vector.com/2023/10/30/a-slightly-unfair-game/">A Slightly Unfair Game</a> (the original coin flipping game demo)</li>
<li><a href="https://github.com/WinVector/Examples/blob/main/ab_test/drunkards_walk.ipynb">The Drunkard’s Walk In Detail</a> (proving the Markov property for outcome conditioned walks)</li>
<li><a href="https://win-vector.com/2023/12/04/the-biased-drunkards-walk/">The Biased Drunkard’s Walk</a> (proving stopping time bounds)</li>
<li><a href="https://github.com/WinVector/Examples/blob/main/ab_test/transition_counts.ipynb">Conditioning on the Future</a> demonstrating the condition transition probabilities</li>
<li><a href="https://github.com/WinVector/Examples/blob/main/ab_test/linear_chain_facts.ipynb">Linear Chain Facts</a> this note, quick derivations of probabilities and expected wait times.</li>
</ul>


## Appendices

### Appendix: The Derivation Outline

All of the above is derived by writing down solutions that obey various linear recurrences:

  * For stop probability: `P[stop at k | state = i] = (1-p) P[stop at k | state = i-1] + p P[stop at k | state = i+1]`.
  * For expected stop time: `E[stop time | state = i] = 1 + (1-p) E[stop time | state = i-1] + p E[stop time | state = i+1]`.
  * For stationary distribution: `P[state = i] P[next state = i+1 | state = i] = P[state = i+1] P[next state = i | state = i+1]` (this is called "[detailed balance](https://en.wikipedia.org/wiki/Detailed_balance)").

The first two solutions can be found by the well known theory of linear recurrences. In sketch form we do the following.

We want to solve for `f()` in the linear recurrence `a f(n+2) + b f(n+1) + c f(n) = d`. 

  * The solution is: `f(n) = A (r1)**n + B (r2)**n + C(n)` where `r1`, `r2` are roots of the characteristic polynomial `a x**2 + b x + c = 0`.
  * In our case we had `r1 = 1`, `r2 = (1-p)/p`. 
  * Then solve for `A`, `B`, `C()` are solved for by matching the equation to known values or boundary conditions (in our case `f(0)` and `f(k)`). 
  * `C()` is typically a low degree polynomial, and `0` when `d = 0`.

Realizing the above is just a fairly long mechanical application of algebra.

The stationary distribution is found by noticing the detailed balance conditions imply `P[state = i+1] / P[state = i] = p / (1-p)` and then enforcing the sum of all state probabilities must equal `1`.

The detailed balance conditions are usually an additional assumption imposed to restrict to nice or time-reversible Markov chains. In the case of linear chains (where all edges are graph separating cuts): then the detailed balance condition follows from (already specified) conservation of probability (and is not in fact an additional assumption in this case). This is the usual mathematical attempt to cary a property from simpler systems to more complex ones.


### Appendix: demonstrate the above claims in Python


```python
# import our packages
import numpy as np
# configure
np.set_printoptions(linewidth=300)
dtype = np.float64
```


```python
# set some example parameters
k = 6
p = 2/3

```


```python
# numeric check tolerance
epsilon = 1e-8
```

Note: in all matrices here `M[a][b]` is the probability of moving form `b` to `a`. This transpose notation allows us to write operators on the left (as is traditional in linear algebra).


```python
# transition matrix for absorbing chain
tm_stop = np.zeros(
    shape=(k+1, k+1),
    dtype=dtype)
tm_stop[0, 0] = 1
tm_stop[k, k] = 1
for i in range(1, k):
    tm_stop[i-1, i] = 1-p
    tm_stop[i+1, i] = p
ones_col = np.zeros(
    shape=(1, k+1), 
    dtype=dtype) + 1
assert np.min(tm_stop) >= 0
assert np.max(np.abs(np.matmul(ones_col, tm_stop) - ones_col)) < epsilon

tm_stop
```




    array([[1.        , 0.33333333, 0.        , 0.        , 0.        , 0.        , 0.        ],
           [0.        , 0.        , 0.33333333, 0.        , 0.        , 0.        , 0.        ],
           [0.        , 0.66666667, 0.        , 0.33333333, 0.        , 0.        , 0.        ],
           [0.        , 0.        , 0.66666667, 0.        , 0.33333333, 0.        , 0.        ],
           [0.        , 0.        , 0.        , 0.66666667, 0.        , 0.33333333, 0.        ],
           [0.        , 0.        , 0.        , 0.        , 0.66666667, 0.        , 0.        ],
           [0.        , 0.        , 0.        , 0.        , 0.        , 0.66666667, 1.        ]])



#### Confirming probability of stopping right/positive.


```python
# solve for right-stop probabilities
# could also use left eigenvalue solver, but as we know eigenvalue is 1 simple linear algebra will do
tts = tm_stop.T
c1_0 = np.zeros((1, k+1))
c1_0[0][0] = 1
c0_1 = np.zeros((1, k+1))
c0_1[0][k] = 1
a = np.concatenate([
    tts - np.identity(k+1, dtype=dtype), 
    c1_0, 
    c0_1,
    ])
b = np.zeros((k+3, 1))
b[k+2] = 1
stop_soln = np.linalg.solve(
    np.matmul(a.T, a),
    np.matmul(a.T, b)
)

stop_soln
```




    array([[-1.63890066e-17],
           [ 5.07936508e-01],
           [ 7.61904762e-01],
           [ 8.88888889e-01],
           [ 9.52380952e-01],
           [ 9.84126984e-01],
           [ 1.00000000e+00]])




```python
# confirm expected properties of stop_soln
assert np.abs(stop_soln[0] - 0) < epsilon
assert np.abs(stop_soln[k] - 1) < epsilon
assert np.min(stop_soln) > -epsilon
assert (np.max(stop_soln) - 1) < epsilon
assert np.max(np.abs(np.matmul(tts, stop_soln) - stop_soln)) < epsilon
for i in range(1, k+1):
    assert stop_soln[i-1] < stop_soln[i]
```


```python
def p_stop_positive_from_i(i:int, *, k:int, p:float) -> float:
    """
    Compute the probability of stopping at k when starting at state i on the
    "probability up = p" 
    Markov chain with states integers 0 through k (inclusive, k>0; states 0, k absorbing).
    """
    assert isinstance(i, int)
    assert isinstance(k, int)
    assert k > 0
    assert (i>=0) and (i<=k)
    assert (p>0) and (p<1)
    z = p/(1-p)
    if p==1/2:
        return i/k
    return (z**k - z**(k-i)) / (z**k - 1)
```


```python
stop_i_res = np.array([p_stop_positive_from_i(i, k=k, p=p) for i in range(k+1)], dtype=dtype).reshape((k+1, 1))
stop_i_res
```




    array([[0.        ],
           [0.50793651],
           [0.76190476],
           [0.88888889],
           [0.95238095],
           [0.98412698],
           [1.        ]])



Show numeric solution matches theoretical solution.


```python
max_diff_stop = np.max(np.abs(stop_soln - stop_i_res))

max_diff_stop
```




    2.220446049250313e-15




```python
assert max_diff_stop < epsilon
```

#### Confirming expected stop time


```python
def expected_stop_time_i(i:int, *, k:int, p: float) -> float:
  """
  Compute the expected stop time starting state i on the
  up with probability p 
  Markov chain with states integers 0 through k (inclusive, k>0; states 0, k absorbing).
  """
  assert isinstance(i, int)
  assert isinstance(k, int)
  assert k > 0
  assert (i>=0) and (i<=k)
  assert (p>0) and (p<1)
  z = p/(1-p)
  if p==1/2:
    return i * (k - i)
  return ((z+1)/(z-1)) * (k * (z**k - z**(k-i)) / (z**k - 1) - i)
```


```python
expected_times = np.array([expected_stop_time_i(i, k=k, p=p) for i in range(k+1)], dtype=dtype).reshape((k+1, 1))

expected_times
```




    array([[0.00000000e+00],
           [6.14285714e+00],
           [7.71428571e+00],
           [7.00000000e+00],
           [5.14285714e+00],
           [2.71428571e+00],
           [2.66453526e-15]])




```python
# check expected properties
assert np.min(expected_times) > -epsilon
assert np.abs(expected_times[0] - 0) < epsilon
assert np.abs(expected_times[k] - 0) < epsilon
check_times = np.zeros((k+1, 1), dtype=dtype)
for i in range(1, k):
    check_times[i][0] = (1-p)*expected_times[i-1][0] + p*expected_times[i+1][0] + 1
```

Confirm the expected times obey the defining invariance.


```python
check_times
```




    array([[0.        ],
           [6.14285714],
           [7.71428571],
           [7.        ],
           [5.14285714],
           [2.71428571],
           [0.        ]])




```python
check_error = np.max(np.abs(check_times - expected_times))

check_error
```




    2.6645352591003765e-15




```python
assert check_error < epsilon
```

#### Confirming stationary distribution


```python
# transition matrix for absorbing chain
tm_stationary = np.identity(k+1, dtype=dtype) / 2
for i in range(k+1):
    if i > 0:
        tm_stationary[i-1, i] = (1-p)/2
    if i < k:
        tm_stationary[i+1, i] = p/2
tm_stationary[0, 0] = 1 - tm_stationary[1, 0]
tm_stationary[k, k] = 1 - tm_stationary[k-1, k]
assert np.min(tm_stationary) >= 0
assert np.max(np.abs(np.matmul(ones_col, tm_stationary) - ones_col)) < epsilon

tm_stationary
```




    array([[0.66666667, 0.16666667, 0.        , 0.        , 0.        , 0.        , 0.        ],
           [0.33333333, 0.5       , 0.16666667, 0.        , 0.        , 0.        , 0.        ],
           [0.        , 0.33333333, 0.5       , 0.16666667, 0.        , 0.        , 0.        ],
           [0.        , 0.        , 0.33333333, 0.5       , 0.16666667, 0.        , 0.        ],
           [0.        , 0.        , 0.        , 0.33333333, 0.5       , 0.16666667, 0.        ],
           [0.        , 0.        , 0.        , 0.        , 0.33333333, 0.5       , 0.16666667],
           [0.        , 0.        , 0.        , 0.        , 0.        , 0.33333333, 0.83333333]])




```python
# solve for stationary distribution
# could also use right eigenvalue solver, but as we know eigenvalue is 1 simple linear algebra will do
a_stationary = np.concatenate([
    tm_stationary - np.identity(k+1, dtype=dtype), 
    np.zeros((1, k+1), dtype=dtype) + 1,
    ])
b_stationary = np.zeros((k+2, 1), dtype=dtype)
b_stationary[k+1] = 1
stationary_soln = np.linalg.solve(
    np.matmul(a_stationary.T, a_stationary),
    np.matmul(a_stationary.T, b_stationary))

stationary_soln
```




    array([[0.00787402],
           [0.01574803],
           [0.03149606],
           [0.06299213],
           [0.12598425],
           [0.2519685 ],
           [0.50393701]])




```python
# confirm expected properties of stationary solution
assert np.min(stationary_soln) > -epsilon
assert np.abs(np.sum(stationary_soln) - 1) < epsilon
assert np.max(np.abs(stationary_soln - np.matmul(tm_stationary, stationary_soln))) < epsilon
```


```python
def stationary_p_i(i:int, *, k:int, p: float) -> float:
  """
  Compute the stationary probability of state i on the
  "hold probability = 1/2, probability up = p/2, down = (1-p)/2" 
  Markov chain with states integers 0 through k (inclusive, k>0; states 0, k reflecting).
  """
  assert isinstance(i, int)
  assert isinstance(k, int)
  assert k > 0
  assert (i>=0) and (i<=k)
  assert (p>0) and (p<1)
  z = p/(1-p)
  if p==1/2:
    return 1/(k+1)
  return z**i * (z - 1) / (z**(k+1) - 1)

```

Confirm the theoretical solution matches the numeric solution.


```python
stationary_i_res = np.array([stationary_p_i(i, k=k, p=p) for i in range(k+1)], dtype=dtype).reshape((k+1, 1))
stationary_i_res
```




    array([[0.00787402],
           [0.01574803],
           [0.03149606],
           [0.06299213],
           [0.12598425],
           [0.2519685 ],
           [0.50393701]])




```python
max_diff_stationary = np.max(np.abs(stationary_soln - stationary_i_res))

max_diff_stationary
```




    1.6542323066914832e-14




```python
assert max_diff_stationary < epsilon
```

One can build confidence in the correctness of the formulas by trying more example `p`s and `k`s.
