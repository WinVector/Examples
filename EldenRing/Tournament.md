# Some Math Inspired by Losing in Elden Ring

I've been playing a bit of [Elden Ring](https://en.wikipedia.org/wiki/Elden_Ring) lately. While taking a break from being "one-shotted" (avatar being killed in one strike), I got to thinking about the math behind Elden Ring's combat style.

I thought I would use this an excuse to work out some of the mathematics of tournaments. This is just a small transition to some math, for some actual useful game advice and calculators I suggest [FExtraLife](https://eldenring.wiki.fextralife.com/Elden+Ring+Wiki).

The content of my thought was as follows.

  * Many games set up combat as you and the enemy being capable of taking off similar small fractions of each other's health. First one with health exhausted is the loser. This style of combat *amplifies* skill difference. If fighting the enemy is a sum of small independent increments slightly in your favor, then you can win with very high probability. This is due to our great friend: [the law of large numbers](https://en.wikipedia.org/wiki/Law_of_large_numbers).
  * In Elden Ring, many of the enemies (especially in the beginning) are pretty much capable of one-shotting the player. Mess up an engagement, so they hit you instead of you hitting them, and you lose. This favors powering up and/or "getting good" over repeating the attempt. Any small increase in the moment to moment odds makes a large change in the probability of overall victory. In the extreme: it isn't enough to perform slightly better, one must perform flawlessly. One must hit the enemy `n` times in a row without being hit.

Both of these play styles are examples of tournaments. Tournaments are a tool of converting a series of games into declaring a winner. They are tools that tend to measure relative performance more reliably than single games. An example of a fair tournament design are "first to 3" (first to win 3 encounters is the winner). Often the Elden Ring tournament is: hit the enemy `n` times before they hit you `1` time.

That got me to thinking: given a (possibly unfair) tournament where it takes us `n_to_win` wins to win, but we lose if we lose `n_to_lose` times, how do we calculate the probability of winning the tournament (assuming an independent probability of winning each engagement of `p_single_win`)? It is such a fundamental combinatorial question, that there must be a standard answer. In this note I will work out the solution in Python in terms of what are called "special functions."


```python
# get Python ready, import packages
import numpy as np
from scipy.special import betainc
```

I want to work on the problem of calculating the probability of winning where we need to win `n_to_win` games before losing `n_to_lose` games, where we have an independent chance of winning each individual game played. That is, we play an unknown number of independent games, stopping the tournament at the first moment we have either won a total of `n_to_win`, or lost a total of `n_to_lose`.  We want to see how the tournament structure converts an assumed independent chance `p_single_win` of wining individual games into a chance of winning the tournament.

This can be solved with tabular bookkeeping (a simple form of [dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming)) where we vary `n_to_win` and `n_to_lose`. To do this we define a table `v[,]`, where we use `v[n_to_win, n_to_lose]` to denote the probability of winning a tournament with tournament win conditions: `n_to_win` and `n_to_lose`.

Some values of `v[,]` can be derived from a direct argument:

  * `v[n_to_win, 1]` is `p_single_win ** n_to_win`, for `n_to_win >= 1` (only way to achieve this is to win all games).
  * `v[1, n_to_lose]` is `1 - (1 - p_single_win) ** n_to_lose`, for `n_to_lose >= 1` (only way to not achieve this is to lose all games).

Notice the above two equations claim the same result `p_single_win` for `v[1, 1]`.

Now we look at how to build later values of `v[,]` from earlier ones. We will use a common trick in calculating probabilities: argue how the underlying game is structured, which implies a similar structure in the values.

Consider if we win or lose the first game of a `v[n_to_win + 1, n_to_lose + 1]` tournament. If we win the first game the we need to complete a `v[n_to_win, n_to_lose + 1]` tournament to win overall. If we lose the first game we have to complete a `v[n_to_win + 1, n_to_lose]` tournament to win overall. This lets us claim the recurrence:

  * `v[n_to_win + 1, n_to_lose + 1] = p_single_win * v[n_to_win, n_to_lose + 1] + (1 - p_single_win) * v[n_to_win + 1, n_to_lose]`.

If we use the convention that `v[n_to_win, 0] = 0` for `n_to_win > 0` and `v[0, n_to_lose] = 1` for `n_to_lose > 0` this recurrence also generates the two boundary cases we started with.

So, we can fill in `v[,]` starting with our boundary conditions and using the recurrence to complete the table.

Let's instantiate this strategy as a non-optimized Python function.


```python
# define our calculate probability of winning tournament function
def p_win_tournament(
    n_to_win: int, n_to_lose: int, p_single_win: float) -> float:
    """
    Brute force dynamic programming solution to computing the 
    probability of winning a tournament where we need to win 
    n_to_win games before losing n_to_lose games, assuming we 
    have an independent chance of p_single_win of winning each
    individual game played.

    :param n_to_win: number of games we must with to win tournament > 0.
    :param n_to_lose: number of games we must lose to lose tournament > 0.
    :param p_single_win: assumed independent probability of winning each game.
    :return: probability of winning the tournament.
    """
    assert n_to_win > 0
    assert n_to_lose > 0
    assert p_single_win >= 0
    assert p_single_win <= 1
    # init dynamic programming table
    v = np.zeros((n_to_win + 1, n_to_lose + 1))
    v[:, :] = np.nan  # unmark entries as unknown
    v[:, 0] = 0  # mark losing states
    v[0, :] = 1  # mark winning states
    v[0, 0] = np.nan  # unmark ambiguous unreachable state
    # fill in unknown (nan) cells from known cells
    for n_win in range(v.shape[0] - 1):
        for n_lose in range(v.shape[1] - 1):
            v[n_win + 1, n_lose + 1] = (
                p_single_win * v[n_win, n_lose + 1] 
                + (1 - p_single_win) * v[n_win + 1, n_lose] )
    # return answer
    return v[n_to_win, n_to_lose]
```

We can then compute the win probabilty of a simple example as follows.


```python
calc_1 = p_win_tournament(n_to_win=3, n_to_lose=1, p_single_win=0.9)

calc_1
```




    0.7290000000000001



For this sort of tournament we must win 3 games in a row, and take no losses. This means we have a tournament win probability of `p_single_win ** 3`.  In our case this is `0.9 ** 3`. We can see our function computed the correct probability as follows.




```python
direct_1 = 0.9 ** 3

direct_1
```




    0.7290000000000001




```python
assert abs(calc_1 - direct_1) < 1e-6
```

Now let's link this to known results. The most common probability distribution associated with measuring how long it takes to see a number of outcomes is the [negative binomial distribution](https://en.wikipedia.org/wiki/Negative_binomial_distribution). This distribution reads off the chance of needing a given number of trials to see a specified number of outcomes. We want the sum of a number of such outcomes.  Such sums are called "cumulative distribution functions", or CDFs. The CDF for the negative binomial distribution is (from our reference) a function called the [regularized incomplete beta function](https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function). We haven't put all the pieces together just yet, but this loose chain is strong evidence the regularized incomplete beta function may calculate our tournament probabilities.

In Python the regularized incomplete beta function can be written as `scipy.special.betainc()`. From the [the Wikipedia](https://en.wikipedia.org/wiki/Beta_function#Incomplete_beta_function) we see `betainc()` has the following properties (for `n_to_win`, `n_to_lose` integers greater than `1`, and `0 < p_single_win < 1`).

  * `betainc(n_to_win, 1, p_single_win)` is `p_single_win ** n_to_win`.
  * `betainc(1, n_to_lose, p_single_win)` is `1 - (1 - p_single_win)**n_to_lose`.

This exactly matches our tournament calculations when one of `n_to_win` or `n_to_lose` is `1`.

Let's confirm this.



```python
assert abs(betainc(1, 1, 0.3) - 0.3) < 1e-6
assert abs(betainc(1, 1, 0.3) - p_win_tournament(1, 1, 0.3)) < 1e-6
```


```python
assert abs(betainc(5, 1, 0.3) - 0.3 ** 5) < 1e-6
assert abs(betainc(5, 1, 0.3) - p_win_tournament(5, 1, 0.3)) < 1e-6
```


```python
assert abs(betainc(1, 5, 0.3) - (1 - (1 - 0.3) ** 5)) < 1e-6
assert abs(betainc(1, 5, 0.3) - p_win_tournament(1, 5, 0.3)) < 1e-6
```


And it turns out the recurrence relation we used to calculate the tournament win probability also holds for `betainc()`. From equation 8.17.12 of [NIST Digital Library of Mathematical Functions](https://dlmf.nist.gov/8.17) we have:

  * `betainc(n_win + 1, n_lose + 1, p_single_win) = p_single_win * betainc(n_win, n_lose + 1, p_single_win) + (1 - p_single_win) * betainc(n_win + 1, n_lose, p_single_win)` 

So `betainc()` and `p_win_tournament()` agree on corner cases and obey the same recurrence for values of interest. Thus we can be assured `betainc()` and `p_win_tournament()` must agree for all examples of interest. (Other "check first" references would include[Abramowitz and Stegun](https://en.wikipedia.org/wiki/Abramowitz_and_Stegun) and [Gradshteyn and Ryzhik](https://en.wikipedia.org/wiki/Gradshteyn_and_Ryzhik). Alternately one can derive this sort of equation from the chain rule or integration by parts.)

Let's check an example to confirm.


```python
p_win_v = p_win_tournament(n_to_win=5, n_to_lose=3, p_single_win=0.8)

p_win_v
```




    0.8519680000000002




```python
p_beta_v = betainc(5, 3, 0.8)

p_beta_v
```




    0.8519680000000001




```python
assert abs(p_win_v - p_beta_v) < 1e-6
```

And we have `p_win_tournament(n_to_win, n_to_lose, p_single_win) == betainc(n_to_win, n_to_lose, p_single_win)` for our values of interest (essentially by an implicit [proof by induction](https://en.wikipedia.org/wiki/Mathematical_induction)). So we don't need the `p_win_tournament()` implementation. It isn't a surprise that such an simple problem matches the identities and symmetries of a known special function.
