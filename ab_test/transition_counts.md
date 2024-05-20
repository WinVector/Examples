# Conditioning on the Future

In both [A Slightly Unfair Game](https://win-vector.com/2023/10/30/a-slightly-unfair-game/) and [The Drunkard's Walk In Detail](https://github.com/WinVector/Examples/blob/main/ab_test/drunkards_walk.ipynb) we showed a fair random walk that moved up or down with 50/50 probability. Some of these walks stopped when they were absorbed at zero, and some stopped when the were absorbed at a positive boundary.

Here is an example of 20 such walks.

<img src="https://i0.wp.com/win-vector.com/wp-content/uploads/2023/10/unnamed-chunk-4-1.gif" />

In [The Drunkard's Walk In Detail](https://github.com/WinVector/Examples/blob/main/ab_test/drunkards_walk.ipynb) we proved that the set of all walks that get absorbed at a specified boundary have two seemingly competing properties:

  * Their transition behavior is radically changed by conditioning on the eventual outcome.
  * The conditioned walks are still Markov chains on the same state.

That is: rows 2 and 16 above (which get absorbed on the right boundary) *are* a posteriori moving with different transition probabilities than the other rows, *and* these transition probabilities depend only on the state-id (nothing more from the random process past, this is called the Markov property for this choice of state). Similarly all the chains eventually absorbed ast zero are moving with transition probabilities different than the original 50/50. Prior to being conditioned on where the row-process ended all games in the tournament share the same 50/50 transition odds. After conditioning (or selection) on eventual outcome: they remain Markov chains on the state, but have different transition probabilities.

For those more comfortable with empirical confirmation than proofs, we take a look at these Markov chains again through simulation.


```python
# import our packages
from collections import namedtuple
import numpy as np
rng = np.random.default_rng(2023)
```


```python
# specify positive stop state
k = 4

```


```python
# define simulation function
WalkResult = namedtuple("WalkResult", "n_up n state")

def run_walk(start: int) -> WalkResult:
    assert isinstance(start, int)
    assert (start > 0) and (start <= k)
    n = np.zeros(k+1)
    n_up = np.zeros(k+1)
    state = start
    while (state > 0) and (state < k):
        n[state] = n[state] + 1
        move_up = rng.binomial(n=1, p=0.5, size=1)[0] >= 0.5
        if move_up:
            n_up[state] = n_up[state] + 1
            state = state + 1
        else:
            state = state - 1
    return WalkResult(
        n_up=n_up,
        n=n,
        state=state,
        )
```

The above code is a simulation realization of the following Markov chain.

<img src="https://win-vector.com/wp-content/uploads/2023/11/chain50_50.png">


```python
# define function running many simulations
SimulationResult = namedtuple(
    "SimulationResult", 
    "n_stopped_positive n_up_given_stopped_positive n_given_stopped_positive" 
    " n_stopped_zero n_up_given_stopped_zero n_given_stopped_zero")

def run_many_simulations(
        start: int,
        *,
        n_repetitions: int = 100000,
):
    n_stopped_positive = 0
    n_up_given_stopped_positive = np.zeros(k+1)
    n_given_stopped_positive = np.zeros(k+1)
    n_stopped_zero = 0
    n_up_given_stopped_zero = np.zeros(k+1)
    n_given_stopped_zero = np.zeros(k+1)
    for rep in range(n_repetitions):
        wr = run_walk(start)
        if wr.state > 0:
            n_stopped_positive = n_stopped_positive + 1
            n_up_given_stopped_positive = n_up_given_stopped_positive + wr.n_up
            n_given_stopped_positive = n_given_stopped_positive + wr.n
        else:
            n_stopped_zero = n_stopped_zero + 1
            n_up_given_stopped_zero = n_up_given_stopped_zero + wr.n_up
            n_given_stopped_zero = n_given_stopped_zero + wr.n
    return SimulationResult(
        n_stopped_positive=n_stopped_positive, 
        n_up_given_stopped_positive=n_up_given_stopped_positive, 
        n_given_stopped_positive=n_given_stopped_positive, 
        n_stopped_zero=n_stopped_zero, 
        n_up_given_stopped_zero=n_up_given_stopped_zero, 
        n_given_stopped_zero=n_given_stopped_zero,
        )
```


```python
s2 = run_many_simulations(start=2)
```


```python
s2.n_stopped_zero
```




    50001




```python
s2.n_stopped_positive
```




    49999




```python
assert np.abs(s2.n_stopped_zero - s2.n_stopped_positive) / (s2.n_stopped_zero + s2.n_stopped_positive) < 1e-2
```


```python
with np.errstate(invalid='ignore'):
    p_up_given_stopped_zero_2 = s2.n_up_given_stopped_zero / s2.n_given_stopped_zero

p_up_given_stopped_zero_2
```




    array([       nan, 0.33477463, 0.25207718, 0.        ,        nan])



These up-transitions for the chains absorbed at zero are as predicted:

<img src="https://win-vector.com/wp-content/uploads/2023/11/chain_0.png">


```python
def prob_up_right_k(i: int) -> float:
    """ https://github.com/WinVector/Examples/blob/main/ab_test/drunkards_walk.ipynb """
    if (i<=0) or (i>=k):
        return np.nan
    return (i+1)/(2*i)

theoretical = [1 - prob_up_right_k(k-i) for i in range(k+1)]

theoretical
```




    [nan, 0.33333333333333337, 0.25, 0.0, nan]




```python
assert ((s2.n_stopped_zero / (s2.n_stopped_zero + s2.n_stopped_positive)) - 0.5) < 1e-2
```

Some care must be taken, in the above we are keeping only per-state records. Such record keeping can never detect any variation that depends on more than the last state. However, we already have proven the frequencies being estimated do only depend on the last state (see [The Drunkard's Walk In Detail](https://github.com/WinVector/Examples/blob/main/ab_test/drunkards_walk.ipynb)). So, in this case, the record keeping is correct. The simulation confirms the predicted transition probabilities, but does depend on the Markov property for correctness.

We can simulate from a different start position, which does give us a look at different conditioning.


```python
s1 = run_many_simulations(start=1)
```


```python
s1.n_stopped_zero
```




    75033




```python
s1.n_stopped_positive
```




    24967



Notice now the absorbing probabilities are no longer nearly equal (due to the unfair start).



```python
assert ((s1.n_stopped_zero / (s1.n_stopped_zero + s1.n_stopped_positive)) - 0.75) < 1e-2
```


However, the observed transition probabilities are the same as before.


```python
with np.errstate(invalid='ignore'):
    p_up_given_stopped_zero_1 = s1.n_up_given_stopped_zero / s1.n_given_stopped_zero

p_up_given_stopped_zero_1
```




    array([       nan, 0.33138778, 0.24759747, 0.        ,        nan])




```python
assert np.nanmax(np.abs(p_up_given_stopped_zero_2 - p_up_given_stopped_zero_1)) < 1e-2
```

And that is the absorbing Markov chain again, this time as an empirical example.

Please checkout more of our series on Markov chains:

  * [A Slightly Unfair Game](https://win-vector.com/2023/10/30/a-slightly-unfair-game/) (the original coin flipping game demo)
  * [The Drunkard’s Walk In Detail](https://github.com/WinVector/Examples/blob/main/ab_test/drunkards_walk.ipynb) (proving the Markov property for outcome conditioned walks)
  * [The Biased Drunkard’s Walk](https://win-vector.com/2023/12/04/the-biased-drunkards-walk/) (proving stopping time bounds)
  * [Conditioning on the Future](https://github.com/WinVector/Examples/blob/main/ab_test/transition_counts.ipynb) (this note, demonstrating the condition transition probabilities)
