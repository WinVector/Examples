# Partial Pooling

<br/>[John Mount](https://win-vector.com/john-mount/)
<br/>[Win Vector LLC](https://win-vector.com) ([blog](https://win-vector.com/blog-2/))
<br/>4-2-2023


Much of data science is merely taking averages to estimate expected values. 

One can ask: are there better estimates for expected values than the obvious average of observations? One might think, in particular given the [Gauss Markov theorem](https://en.wikipedia.org/wiki/Gauss–Markov_theorem), the answer would have to be "no." Oddly enough, the answer is in fact "yes." One method to do this is called *partial pooling*, and we will describe this method here. There are even other methods, such as [James–Stein estimator](https://en.wikipedia.org/wiki/James–Stein_estimator) (which we do not go into here).

This note works an example of partial pooling from equation 12.1 of Gelman, Hill, "Data Analysis Using Regression and Multilevel/Hierarchical Models", Cambridge 2007. This is a bit of a magic trick, but we will show how it is done. I am not claiming this will revolutionize your data science projects, but it can be an improvement when you don't have a lot of data.

## Introduction

The topic of formula 12.1 is: how to partially pool data by hand, though this task is often handled by a hierarchical model solver. 

Take as our example problem: we want to estimate the ideal expected value of observed values from various locations. The optimal linear un-biased estimator is to just take the average of the observed values at each location, and hope this is close to the ideal unobserved generating process.

[Dr. Nina Zumel](https://win-vector.com/author/nzumel/) has two excellent articles on exactly this problem:

  * [Custom Level Coding in vtreat](https://win-vector.com/2017/09/25/custom-level-coding-in-vtreat/)
  * [Partial Pooling for Lower Variance Variable Encoding](https://win-vector.com/2017/09/28/partial-pooling-for-lower-variance-variable-encoding/)

These show how to use the right tools to perform and use the partial pooling analysis, largely in context of the `vtreat` data preparation system ([R version](https://CRAN.R-project.org/package=vtreat), [Python version](https://pypi.org/project/vtreat/)).

For this note, let's work on a formula and a synthetic example directly.

We will use `Python` and the `sympy` symbolic math package to work our examples. This is part of may "data for engineers" teaching effort, where we share code so people can try the methods. First we import our packages.


```python
# import packages
import sympy
from sympy.stats import E, Normal
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
```

Our problem set-up is:

  * Each location `j` has an unobserved expected value of examples drawn from this location, call this `LocationValue_j`.
  * The locations are related, in that the `LocationValue_j`s are all drawn from some common distribution. This is why we think pooling data could be useful, each location has a different value (but is telling us things about their common distribution).
  * Our observations are numbers drawn from a normal distribution around `LocationValue_j`. From these we hope to estimate `LocationValue_j`. The job is to try and remove the observation noise.
  * For a given location, we suspect that some combination of the observations from the location, *plus* observations from other locations may be a lower expected error estimate than can be found using only observations from the location. This is try to trade away some variance (the bane of small data situations) in place of accepting some bias in our procedures.

To execute this idea we need to define a great number of variables and their relations as follows.


```python
# define initial variables
TrueEffectCenter = sympy.Symbol("TrueEffectCenter")  # center of distribution generating locations, unobserved
BetweenLocationsSD = sympy.Symbol("BetweenLocationsSD")  # how individual locations very from each other in expected behavior, unobserved
EstimatedEffectCenter = sympy.Symbol("EstimatedEffectCenter")  # estimate of TrueEffectCenter, observed but some issues how to calculate
LocationValue_j = sympy.Symbol("LocationValue_j")  # actual expected behavior of a given location, unobserved and the goal to estimate
LocationDistFactor_j = Normal("LocationDistFactor_j", mean=0, std=BetweenLocationsSD)  # how locations differ from each other, unobserved
def_LocationValue_j = TrueEffectCenter + LocationDistFactor_j  #  generative definition of LocationDistFactor_j
PerObservationSD = sympy.Symbol("PerObservationSD", positive=True)  # sd of distribution generating observations per location, unobserved
n_j = sympy.Symbol("n_j", positive=True)  # number of observations at the j-th location, observed
LocationMean_j = sympy.Symbol("LocationMean_j", mean=LocationValue_j, std=PerObservationSD)  # mean of all observations at location j, observed
LocationCenterNoise_ji = Normal("LocationCenterNoise_ji", mean=0, std = PerObservationSD / sympy.sqrt(n_j))  # distribution of average seen at location j, unobserved
def_LocationMean_j = LocationValue_j + LocationCenterNoise_ji  # generative definition of LocationCenterNoise_ji
w = sympy.Symbol("w", positive=True)  # our weighting term picking how to pool specific and general observations, to solve for
estimate_j = sympy.Symbol("estimate_j")  # our estimate of the behavior of the j-th location, to solve for

```

These are a lot of terms, but most of them are merely placeholders for our calculations. The trickiest term is `LocationCenterNoise_ji` which is correct for independent observations. `LocationCenterNoise_ji` is founded on the fact that variance is additive for independent observations. The `Normal()` could be relaxed a bit, but it appears we must specify some specific distribution to use `sympy`'s expectation operators `E()`. If we can't use `E()` we could simulate it with more guided substitution steps. Throughout this analysis we are assuming our random variables are independent.

Our goal is to pick a `estimate_j` to minimize the expected square of the following expression.


```python
expected_error_term = LocationValue_j - estimate_j  # error of our estimate, to minimize square of

expected_error_term
```




$\displaystyle LocationValue_{j} - estimate_{j}$



Our plan is to re-factor this expression into independent expectation zero terms `A`, `B` and then use the fact that for such terms `E[(A - B_**2)] = E[A**2] + E[B**2]`. The goal is to derive relation 12.1 from Gelman and Hill:



<img src="IMG_1323.png">

This is a big equation with a "pooling strength" coefficient expanded into the expression. If we write the pooling coefficient as `w`, we can then re-write the above as the following.


```python
def_estimate_j = w * LocationMean_j + (1-w) * EstimatedEffectCenter  # definition of our estimate

def_estimate_j
```




$\displaystyle EstimatedEffectCenter \left(1 - w\right) + LocationMean_{j} w$



That is: our estimate is `w` times using the observed per-location mean (`LocationMean_j`, the obvious estimate) plus `(1-w)` times average expected behavior over all locations. Setting `w = 1` gives us the traditional "use only observations from the chosen location" solution. Setting `w = 0` gives us complete pooling, assuming there is no difference between locations. The trick is to find a `w` between `0` and `1` that might have lower expected square error. 

The 12.1 estimate is a solution that picks `w` as the following.


```python
neat_soln_approx = 1 / (1 + PerObservationSD**2 / (n_j * BetweenLocationsSD**2))

neat_soln_approx
```




$\displaystyle \frac{1}{1 + \frac{PerObservationSD^{2}}{BetweenLocationsSD^{2} n_{j}}}$



Some algebra shows this is the same as the Gelman and Hill citation (if we adopt the convention that `w = 0` when `n_j = 0`). We confirm that as follows.


```python
GH_soln =(n_j / PerObservationSD**2) / ( n_j / PerObservationSD**2 + 1 / BetweenLocationsSD**2)
assert (neat_soln_approx - GH_soln).together() == 0
```

This solution for `w` has some nice properties.

  * `w` goes to `1` (the standard simple solution) as `PerObservationSD` goes to zero. This can be read as: "there is no point in pooling of their is already little uncertainty in the obvious estimate.
  * `w` goes to `1` (the standard simple solution) as `n_j` goes to infinity. This can be read as: "there is no point in pooling if we already have a lot of data for the obvious estimate."
  * `w` goes to `0` (combining all the data) as `n_j` goes to zero (using the convention `1/infinity = 0`). This can be read as: "with no data for a new location, use the grand average."
  * `w` goes to `0` (combining all the data) as `PerObservationSD` goes to infinity. This can be read as: "combine all the data if the per-location uncertainty is very high."


Our goal is to derive this solution.


## Reproducing the Gelman and Hill citation

We can match the Gelman and Hill citation by, during the solving, replacing the visible `TrueEffectCenter` with our estimated `EstimatedEffectCenter` (ignoring an an assumed small difference between them).

When we solve in that manner we get the Gelman and Hill cited `w` as follows. Let's work on that error term, that we want to minimize the expected square of, for a bit.


```python
error_term_approx = (
    expected_error_term
        .subs(estimate_j, def_estimate_j)  # definition of estimate_j
        .subs(EstimatedEffectCenter, TrueEffectCenter)  # this step is an approximation, using the unobserved TrueEffectCenter as if it is the observed EstimatedEffectCenter
        .subs(LocationMean_j, def_LocationMean_j)  # generative definition of LocationMean_j
        .subs(LocationValue_j, def_LocationValue_j)   # generative definition of LocationValue_j
).expand().simplify()

error_term_approx
```




$\displaystyle - w LocationCenterNoise_{ji} - w LocationDistFactor_{j} + LocationDistFactor_{j}$



The simplifying substitution `MeanLocation` value for the `EstimatedEffectCenter` is an approximation, and is why the total number of observations is not present in this estimate. This substitution is ignoring the uncertainty in estimating the grand mean, which we assume is slightly easier than our overall task of estimating the conditional means. Or a different view would be: if we felt we knew `MeanLocation` this is how we would perform the estimate. For example in re-encoding variables (such as in `vtreat`) we know the overall `MeanLocation` is in fact zero by the structure of the application set-up.

There is in fact an issue in how to estimate `EstimatedEffectCenter` when different locations have very different numbers of observations. In this case an average where each observation contributes equally is sensitive to the between location variances, and an average where each location contributes equally is sensitive to per observation variances. What to put in for `EstimatedEffectCenter` is essentially the entire estimation problem started over again, so picking the data weighting cleverly probably is of some benefit.

Assuming we were happy with what we plugged in for `EstimatedEffectCenter` we can continue our calculation as follows.

We claim this error term is equal to `A - B`, for the following `A`, `B`.


```python
A = (1-w) * LocationDistFactor_j
B = w * LocationCenterNoise_ji
```

And we can confirm this claim as follows.


```python
assert (error_term_approx - (A - B)).simplify() == 0
assert E(A).expand() == 0
assert E(B).expand() == 0
```

We can expand the expected square error `E[(A - B)**2]` as `E[A**2] + E[B**2]` (using the independence of `A` and `B`, and that they are both expected value zero).

We expect the minimum to occur at either the bounds of our allowed values for `w` (`0` and `1`) or at a place where the derivative of our expected square error term with respect to `w` is zero. That solution is found as follows.


```python
soln_approx = sympy.solve(sympy.diff(E(A**2) + E(B**2), w), w)[0]

soln_approx
```




$\displaystyle \frac{BetweenLocationsSD^{2} n_{j}}{BetweenLocationsSD^{2} n_{j} + PerObservationSD^{2}}$



And we confirm this is (for non-zero quantities) equivalent to the earlier claimed solution.


```python
assert (soln_approx - neat_soln_approx).together().expand() == 0
```

And this, as promised, matches the text book. 

I am experimenting more and more with using `sympy` in place of hand-worked algebra in these sort of write-ups. My hope is that it allows me to spend more time on intent, and less time explaining steps (which often introduced yet more steps).

## Working an Example

Let's see the partial pooling inference in action. 

We will generate the synthetic example data according to the above hierarchical design. We will then see how a pooled estimate, itself using estimate parameters, can in fact improve estimation results. The advantage of synthetic data include: we can see how close the estimates come to the correct answers, and we can generate a favorable situation for demonstration.

We generate the not directly observable portion of our example as follows.


```python
# set state of pseudo random number generator for repeatability
rng = np.random.default_rng(2023)  
```


```python
# set parameters to specific values
example_between_locations_sd = 3.0
example_per_observations_sd = 10.0
n_locations = 10
n_obs_per_location = 3
```


```python
def generate_example_centers() -> pd.DataFrame:
    """generate the unobserved location values"""
    example_location_value_mean = rng.normal(loc=0, scale=15, size=1)
    example_locations = pd.DataFrame({
        "location_id": range(n_locations),
        "effect": rng.normal(
        loc=example_location_value_mean, 
        scale=example_between_locations_sd, 
        size=n_locations)
    })
    return example_locations
```


```python
example_locations = generate_example_centers()
```


```python
example_locations
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>location_id</th>
      <th>effect</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>12.480676</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>4.947432</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>9.691985</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>6.698217</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>11.451937</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>8.429935</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>4.289738</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>7.137952</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td>7.862549</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td>9.176378</td>
    </tr>
  </tbody>
</table>
</div>



And we can then generate observations as follows.


```python
def generate_observations(example_locations: pd.DataFrame)-> pd.DataFrame:
    """
    generate observed data

    :param example_locations: the (unobserved) ground truth to generate from
    :return: observed data
    """
    assert isinstance(example_locations, pd.DataFrame)
    observations = []
    for j in range(example_locations.shape[0]):
        obs_j = pd.DataFrame({
            "location_id": j,
            "observation": rng.normal(
            loc=example_locations.effect[j], 
            scale=example_per_observations_sd, 
            size=n_obs_per_location),
        })
        observations.append(obs_j)
    observations = pd.concat(observations, ignore_index=True)
    return observations

```


```python
observations = generate_observations(example_locations)
```


```python
observations
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>location_id</th>
      <th>observation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>3.410240</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>13.802057</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>26.529701</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>8.988453</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1</td>
      <td>-5.426702</td>
    </tr>
    <tr>
      <th>5</th>
      <td>1</td>
      <td>-2.470594</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2</td>
      <td>22.326980</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2</td>
      <td>2.798745</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2</td>
      <td>16.772133</td>
    </tr>
    <tr>
      <th>9</th>
      <td>3</td>
      <td>6.347742</td>
    </tr>
    <tr>
      <th>10</th>
      <td>3</td>
      <td>-1.679948</td>
    </tr>
    <tr>
      <th>11</th>
      <td>3</td>
      <td>-0.626963</td>
    </tr>
    <tr>
      <th>12</th>
      <td>4</td>
      <td>21.925762</td>
    </tr>
    <tr>
      <th>13</th>
      <td>4</td>
      <td>-2.786075</td>
    </tr>
    <tr>
      <th>14</th>
      <td>4</td>
      <td>24.992347</td>
    </tr>
    <tr>
      <th>15</th>
      <td>5</td>
      <td>4.479009</td>
    </tr>
    <tr>
      <th>16</th>
      <td>5</td>
      <td>-0.862222</td>
    </tr>
    <tr>
      <th>17</th>
      <td>5</td>
      <td>12.870562</td>
    </tr>
    <tr>
      <th>18</th>
      <td>6</td>
      <td>5.711914</td>
    </tr>
    <tr>
      <th>19</th>
      <td>6</td>
      <td>17.977145</td>
    </tr>
    <tr>
      <th>20</th>
      <td>6</td>
      <td>-0.697886</td>
    </tr>
    <tr>
      <th>21</th>
      <td>7</td>
      <td>6.395265</td>
    </tr>
    <tr>
      <th>22</th>
      <td>7</td>
      <td>16.531671</td>
    </tr>
    <tr>
      <th>23</th>
      <td>7</td>
      <td>0.876524</td>
    </tr>
    <tr>
      <th>24</th>
      <td>8</td>
      <td>-2.427039</td>
    </tr>
    <tr>
      <th>25</th>
      <td>8</td>
      <td>-13.467843</td>
    </tr>
    <tr>
      <th>26</th>
      <td>8</td>
      <td>16.906428</td>
    </tr>
    <tr>
      <th>27</th>
      <td>9</td>
      <td>-11.667661</td>
    </tr>
    <tr>
      <th>28</th>
      <td>9</td>
      <td>12.001735</td>
    </tr>
    <tr>
      <th>29</th>
      <td>9</td>
      <td>5.930353</td>
    </tr>
  </tbody>
</table>
</div>



Now we define the standard estimator, and code to evaluate how well it estimates the first group's expected value.


```python
# define the standard estimator
def standard_effect_estimate(observations: pd.DataFrame) -> pd.DataFrame:
    """
    Get the standard estimate of the effect at locations from observations.

    :param observations: the observations data frame
    :return: standard estimate of effect or mean by location
    """
    assert isinstance(observations, pd.DataFrame)
    means = (
        observations.loc[:, ["location_id", "observation"]]
            .reset_index(drop=True, inplace=False)
            .groupby(["location_id"])
            .mean()
            .reset_index(drop=False, inplace=False)
    )
    means.sort_values(["location_id"], inplace=True, ignore_index=True)
    means.rename(columns={"observation": "estimate"}, inplace=True)
    means["grand_mean"] = np.mean(observations["observation"])
    means["impact"] = means["estimate"] - means["grand_mean"]
    means.sort_values(["location_id"], inplace=True, ignore_index=True)
    return means
```

The standard estimate works as follows.


```python
standard_effect_estimate(observations)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>location_id</th>
      <th>estimate</th>
      <th>grand_mean</th>
      <th>impact</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>14.580666</td>
      <td>6.848728</td>
      <td>7.731938</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>0.363719</td>
      <td>6.848728</td>
      <td>-6.485009</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>13.965953</td>
      <td>6.848728</td>
      <td>7.117225</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>1.346944</td>
      <td>6.848728</td>
      <td>-5.501784</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>14.710678</td>
      <td>6.848728</td>
      <td>7.861950</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>5.495783</td>
      <td>6.848728</td>
      <td>-1.352945</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>7.663724</td>
      <td>6.848728</td>
      <td>0.814996</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>7.934487</td>
      <td>6.848728</td>
      <td>1.085759</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td>0.337182</td>
      <td>6.848728</td>
      <td>-6.511546</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td>2.088142</td>
      <td>6.848728</td>
      <td>-4.760585</td>
    </tr>
  </tbody>
</table>
</div>




```python
# estimate the quality of the standard estimator
def get_sq_error_loss_std_estimate(
        *, 
        location_id: int, example_locations: pd.DataFrame, observations: pd.DataFrame) -> float:
    """
    Show the square-error of estimate of the effect at location location_id from observations

    :parm location_id: which location to calculate for
    :param example_locations: the (unobserved) ground truth to compare to
    :param observations: the observations data frame
    :return: estimated square error of this estimation procedure
    """
    # get the standard estimates
    observed_means = standard_effect_estimate(observations=observations)
    # get the unobservable true effect for comparison
    true_effect = example_locations.loc[example_locations["location_id"] == location_id, "effect"].values[0]
    # calculate the square error of these estimates
    estimated_effect = observed_means.loc[observed_means["location_id"] == location_id, "estimate"].values[0]
    square_error = (estimated_effect - true_effect)**2
    return square_error

```

And we define the pooled estimator, and it's evaluation procedure.


```python
# define the pooled estimator
def pooled_effect_estimate(observations: pd.DataFrame) -> pd.DataFrame:
    """
    Get the pooled estimate of effect

    :param observations: the observations data frame, with columns location_id and observation
    :return: pooled estimates
    """
    assert isinstance(observations, pd.DataFrame)
    observations = observations.loc[:, ["location_id", "observation"]].reset_index(inplace=False, drop=True)
    # get the standard estimates
    estimated_centers = standard_effect_estimate(observations=observations)
    if estimated_centers.shape[0] <= 1:
        # no pooling possible
        return estimated_centers
    # get counts per group
    obs_count_frame = (
        pd.DataFrame({"location_id": observations["location_id"], "count": 1})
            .groupby(["location_id"])
            .sum()
            .reset_index(drop=False, inplace=False)
            .sort_values(["location_id"], inplace=False, ignore_index=True)
    )
    n_j = obs_count_frame["count"].values
    # get the observed variance for each item at for each location
    combined = (
        observations
            .merge(
                estimated_centers,
                on=["location_id"],
                how="left",
                )
            .merge(
                obs_count_frame,
                on=["location_id"],
                how="left",
                )
    )
    combined.sort_values(["location_id"], inplace=True, ignore_index=True)
    per_location_observation_var = (
        np.sum((combined["observation"] - combined["estimate"])**2) 
        / (combined.shape[0] - len(set(combined["location_id"])))
    )
    # get the observed variance between locations
    between_location_var = np.var(estimated_centers["estimate"], ddof=1)
    # get v, the pooling coefficient
    if between_location_var <= 0:
        v = 0
    elif per_location_observation_var <= 0:
        v = 1
    else:
        # as between_location_var > 0 and per_location_observation_var > 0 here
        # v will be in the range 0 to 1
        v = 1 / (1 + per_location_observation_var / (n_j * between_location_var))
    # our estimate of the overall shared effect
    # note we are using the mixing proportions suggested by the variance reduction ideas
    # simpler weightings include:
    #   combined["obs_weight"] = 1   # weights all observations equally
    #   combined["obs_weight"] = 1 / combined["count"]  # weights all locations equally
    # below, weights larger observations groups more, but with a diminishing return
    # this is an ad-hoc heuristic to try to reduce square error when the number of 
    # observations per location has a lot of variation
    combined["obs_weight"] = 1
    if (between_location_var > 0) and (per_location_observation_var > 0):
        combined["obs_weight"] = 1 / (1 + per_location_observation_var / (combined["count"] * between_location_var))
    # this quantity can be improved using knowledge of the variances
    grand_mean = np.sum(combined["observation"] * combined["obs_weight"]) / np.sum(combined["obs_weight"])
    # build the pooled estimate
    pooled_estimate = v * estimated_centers["estimate"] + (1 - v) * grand_mean
    return pd.DataFrame({
        "location_id": estimated_centers["location_id"],
        "estimate": pooled_estimate,
        "grand_mean": grand_mean,
        "impact": pooled_estimate - grand_mean,
    })
```

The pooled estimate works as follows.


```python
# show the estimate in action
pooled_effect_estimate(observations)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>location_id</th>
      <th>estimate</th>
      <th>grand_mean</th>
      <th>impact</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>10.557640</td>
      <td>6.848728</td>
      <td>3.708913</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>3.737951</td>
      <td>6.848728</td>
      <td>-3.110776</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>10.262770</td>
      <td>6.848728</td>
      <td>3.414043</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>4.209592</td>
      <td>6.848728</td>
      <td>-2.639136</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>10.620005</td>
      <td>6.848728</td>
      <td>3.771278</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>6.199737</td>
      <td>6.848728</td>
      <td>-0.648991</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>7.239671</td>
      <td>6.848728</td>
      <td>0.390943</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>7.369552</td>
      <td>6.848728</td>
      <td>0.520825</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td>3.725222</td>
      <td>6.848728</td>
      <td>-3.123506</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td>4.565135</td>
      <td>6.848728</td>
      <td>-2.283592</td>
    </tr>
  </tbody>
</table>
</div>




```python
# evaluate the pooled estimator quality
def get_sq_error_loss_pooled_estimate(
        *, 
        location_id: int, example_locations: pd.DataFrame, observations: pd.DataFrame) -> float:
    """
    Show the square error of partial pooled out estimates of the effect at location location_id from observations

    :parm location_id: which location to calculate for
    :param example_locations: the (unobserved) ground truth to compare to
    :param observations: the observations data frame
    :return: estimated square error of this estimation procedure
    """
    # get the estimates
    pooled_estimates = pooled_effect_estimate(observations=observations)
    # get the unobservable true effect for comparison
    true_effect = example_locations.loc[example_locations["location_id"] == location_id, "effect"].values[0]
    # calculate the square error of these estimates
    estimated_effect = pooled_estimates.loc[pooled_estimates["location_id"] == location_id, "estimate"].values[0]
    square_error = (estimated_effect - true_effect)**2
    return square_error
```

Now, let's try the estimators. In each case we the evaluation is returning square-error, so smaller is better.


```python
# run the experiment for the standard estimator
std_est_loss = get_sq_error_loss_std_estimate(
    location_id=0, 
    example_locations=example_locations, 
    observations=observations)

std_est_loss
```




    4.409957134811661




```python
# run the experiment for the pooled estimator
pooled_est_loss = get_sq_error_loss_pooled_estimate(
    location_id=0, 
    example_locations=example_locations, 
    observations=observations)

pooled_est_loss
```




    3.698066838111626




```python
assert pooled_est_loss < std_est_loss
```

We see, the pooled estimate has smaller expected square error loss that the standard estimate. That is: we have evidence the pooled estimate would be closer to new observations for a given location. We want to further confirm by repeating the experiment more times.


```python
# wrap our experiment in a repeatable function
def run_experiment() -> pd.DataFrame:
    example_locations = generate_example_centers()
    observations = generate_observations(example_locations)
    std_est_loss = get_sq_error_loss_std_estimate(
        location_id=0, 
        example_locations=example_locations, 
        observations=observations)
    pooled_est_loss = get_sq_error_loss_pooled_estimate(
        location_id=0, 
        example_locations=example_locations, 
        observations=observations)
    return pd.DataFrame({
        "std_loss": [std_est_loss],
        "pooled_loss": [pooled_est_loss],
    })
```


```python
# run the experiments
experiments = pd.concat([run_experiment() for i in range(1000)], ignore_index=True)
```


```python
# show the average loss of each method
experiments.mean()
```




    std_loss       31.652005
    pooled_loss    14.987383
    dtype: float64




```python
# show the median loss of each method
medians = experiments.median()
medians
```




    std_loss       13.859971
    pooled_loss     5.906482
    dtype: float64




```python
# show how each method's loss varies (standard deviation)
experiments.std()
```




    std_loss       46.143738
    pooled_loss    24.747940
    dtype: float64



Notice the pooled method, in this example, out-performs the standard method in all three of the above measurements. This is because the example is deliberately generating closely related data. 

We can also plot the distribution losses to get a bit more detail.


```python
# plot the experiments
plt_frame = pd.concat([
    pd.DataFrame({"estimate": "standard", "loss": experiments["std_loss"]}),
    pd.DataFrame({"estimate": "pooled", "loss": experiments["pooled_loss"]}),
    ], ignore_index=True)
palette = ["#d95f02", "#1b9e77"]
sns.kdeplot(
    data=plt_frame,
    x="loss",
    hue="estimate",
    hue_order=["standard", "pooled"],
    palette=palette,
    fill=True,
)
plt.title("distribution of square error losses by estimation method (lower better)\ndashed bars at medians")
plt.xlim(0, np.quantile(plt_frame["loss"], 0.95))
plt.axvline(x=medians["std_loss"], color=palette[0], linestyle="dashed")
plt.axvline(x=medians["pooled_loss"], color=palette[1], linestyle="dashed")
plt.show()
```


    
![png](PartialPooling_files/PartialPooling_56_0.png)
    


The method has been seen to work, even with estimated variances and grand means (instead of using the unobserved true generating parameters). This is evidence the method can be used in practice.

## Alternatives

One alternative method is to re-write the mixing estimate as `w = X / n_j`, where `X` is an unknown constant. We can then estimate an effective `X` by cross-validation, instead of using the theoretical value. That is: we use the functional form from the above theory, and instead of estimating the variances instead pick `X` directly from data.

Or, one can delegate the entire task to a hierarchical modeling tool. This allows specification of more detailed hierarchies, that can encode useful modeling assumptions.

# A note on hierarchical models

We've not really talked about the meaning of the term "hierarchical model."

Hierarchical models are the clear way to explain the how different data generation assumptions effect our modeling strategy. In this case, knowing how strongly different data is related allows us to implement a lower variance (though biased) estimate. This note is the direct re-implementation of a simple hierarchical model: using that locations come from a common distribution, and then later produce observations.

From Gelman and Hill section 11.3 we take that hierarchical models are an alternative to attempts to define *fixed effect* versus *random effect* modeling. We understand this is from Bayesian-friendly authors that don't particularly like the Frequentist terms *fixed effect* and *random effect*, but their advice seems sound:

> Our advice (elaborated upon in the rest of this book) is to *always* use multilevel modeling ("random effects"). Because of conflicting definitions and advice, we avoid the terms "fixed" and "random" entirely, and focus on the description of the model itself [...] with the understanding that batches of coefficients [...] will themselves be modeled.

(Ellipses meant to avoid some un-introduced detail, and not alter the meaning, context, or scope of the original statement. In this context "modeled" essentially means subject to distributional assumptions, be these assumptions priors or conditions relating groups of variables. This is quite normal for Bayesians. But needs to be mystified a bit when used by Frequentists, as this is something Frequentists claim not to do.)



## Conclusion

The partial pooling improvement for estimating an unseen value from noisy observations depends on a single parameter `PerObservationSD**2 / (n_j * BetweenLocationsSD**2)`. This parameter compares the uncertainty in the mean of the observations (`PerObservationSD**2 / n_j`, or standard error squared) for a single location, to the uncertainty between locations (`BetweenLocationsSD**2`, a standard deviation squared). When this ratio is small, we don't pool data, we just estimate the average value using data from one location. When this ratio is large, pooling is likely a useful variance reducing procedure. Of course, these values are not directly observed; and thus have to be themselves estimated.

Essentially the partial pooling method is trading away variance (due to having very few samples) for bias (due to including samples that don't match the target location). If the different locations are sufficiently related, this can be an improving trade off in terms of expected square error.

In practice, all of the above is typically ignored when there is a lot of data. And, the above inference is made inside a hierarchical model solver, not directly by a practitioner. However, it is good to see the actual form of the pooling strategy.
