# Exact Sums Over a Group Action

## Introduction

In an older note ([Why No Exact Permutation Tests at Scale?](https://win-vector.com/2018/02/01/why-no-exact-permutation-tests-at-scale/)) we worked through why there can not be exact permutation tests for significance at large scale. The reason was: *if* one could efficiently perform such a test for the high degree polynomials used in exact significance calculations, then one could efficiently solve presumed hard problems such as calculating the permanent. We also recently illustrated the strength of the mean/variance characterization of the F-statistic here: [Illustrating the F-test in Action](https://github.com/WinVector/Examples/blob/main/analysis_of_variance/f_dist.ipynb). 

However, mean and variance are low degree [symmetric polynomials](https://en.wikipedia.org/wiki/Symmetric_polynomial). (A symmetric polynomial is a polynomial whose evaluation is not changed under re-ordering its variables.) Those should be *much* easier to deal with than general high degree polynomials.

One *can* design an efficient and exact calculation of both the mean and the variance of a quality evaluation of a data partition (or clustering) under a [group action](https://en.wikipedia.org/wiki/Group_action). A "group action" means a calculation over permutations of the values (which is a comparative tool to show what a summary looks like when there is no relation between the partition and the data). This procedure is called a ["permutation test"](https://en.wikipedia.org/wiki/Permutation_test), and is a standard method in machine learning (especially with Random Forests). (Note: calculating mean and variance are not in themselves a *fully exact test*, as we would need to assume a distribution to get higher order probabilities and significances.)

The goal is a dream of computer science: to identify an efficient calculation that exactly replicates the results of an expensive procedure. In this case we achieve the dream. We can exactly identify the mean and variance of such a permutation statistic, without explicitly running through all of the permutations of the data. 
Let's see this in action.


## Setting Up

First we import our packages.


```python
# import our modules/packages
from sympy import (
    factorial,
    init_printing,
    symbols,
)
import numpy as np
from itertools import permutations
from pprint import pprint

from sym_calc import (
    build_symmetric_to_moment_mapping,
    elementary_symmetric_polynomial,
    identify_variance_fn_regular_blocks_e,
    theoretical_sym_poly,
)
```


```python
def disp(v):
    display(v)
    # print(str(v))

# init_printing(pretty_print=False)
```

## Symmetric Polynomials

A symmetric polynomial is a polynomial whose value does not change when we permute or re-arrange the variables. Some example of symmetric polynomials (in variables `y_0, y_1, y_1`) are the following.

The elementary symmetric polynomials.


```python
for i in range(1, 4):
    disp(f"s{i}")
    disp(elementary_symmetric_polynomial(i, symbols("y_0 y_1 y_2")))

```


    's1'



$\displaystyle y_{0} + y_{1} + y_{2}$



    's2'



$\displaystyle y_{0} y_{1} + y_{0} y_{2} + y_{1} y_{2}$



    's3'



$\displaystyle y_{0} y_{1} y_{2}$


The symmetric moment polynomials.


```python
for i in range(1, 4):
    disp(f"m{i}")
    disp(sum([y**i for y in symbols("y_0 y_1 y_2")]))
```


    'm1'



$\displaystyle y_{0} + y_{1} + y_{2}$



    'm2'



$\displaystyle y_{0}^{2} + y_{1}^{2} + y_{2}^{2}$



    'm3'



$\displaystyle y_{0}^{3} + y_{1}^{3} + y_{2}^{3}$


For convenience we will write our desired results as polynomials in the symmetric moment polynomials (instead of directly in the original variables).

## An Example

Now we set up our problem. We want to exactly run a permutation test over the quality of a partition of data in 3 blocks each of size 17.


```python
n_blocks = 3
block_size = 17
```

We take as our example values just an increasing sequence of integers.


```python
values = np.asarray(range(n_blocks * block_size))

values
```




    array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16,
           17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33,
           34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50])



Our proposed split into blocks is 3 blocks in contiguous order.


```python
np.split(values, n_blocks)
```




    [array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15, 16]),
     array([17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33]),
     array([34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50])]



The point is: this partition is very informative for this data. The first block has a much lower mean than the last block. The blocks are in fact capturing as much information about the values in this data as can be done when only splitting the data into 3 groups. Typically we would have learned this split of these "outcome" or "y-values" using other explanatory variables (not shown here). And this illustration is what we would be checking in the case of a really good fit.



### Calculating the Loss

Let's define a loss function to show how bad a partition is with respect to outcome data.

The function is breaking the supplied values into consecutive groups, and then calculating the square difference between items in the groups and the mean for the group.


```python
def sq_loss_fn(values, *, n_blocks: int, block_size: int):
    values = np.asarray(values)
    assert values.shape == (n_blocks * block_size, )
    return (
        np.sum([(block - np.mean(block))**2 for block in np.split(values, n_blocks)]) 
        / ((block_size - 1) * n_blocks))
```

Now we apply this loss to our data to measure how much our partition misses. We would like this value to be small, or even zero.


```python
observed_loss = sq_loss_fn(values, n_blocks=n_blocks, block_size=block_size)

observed_loss
```




    25.5



For a random arrangement (that the partition isn't good at grouping) we see a larger loss. This is evidence the original loss is small, and the partition was aware of the original data ordering.


```python
permuted_values = np.random.default_rng(25235).permutation(values)

permuted_values
```




    array([42, 37, 28, 44, 26, 30, 15,  6, 29, 41,  3, 50, 47, 48,  5, 11, 14,
            1, 25, 17, 23, 21, 46, 10, 35,  0, 33, 22, 49, 40, 18, 19,  8, 34,
            2, 27, 16, 12, 36,  7,  4, 13, 38, 39, 32, 24, 31, 43,  9, 45, 20])




```python
np.split(permuted_values, n_blocks)
```




    [array([42, 37, 28, 44, 26, 30, 15,  6, 29, 41,  3, 50, 47, 48,  5, 11, 14]),
     array([ 1, 25, 17, 23, 21, 46, 10, 35,  0, 33, 22, 49, 40, 18, 19,  8, 34]),
     array([ 2, 27, 16, 12, 36,  7,  4, 13, 38, 39, 32, 24, 31, 43,  9, 45, 20])]




```python
sq_loss_fn(permuted_values, n_blocks=n_blocks, block_size=block_size)
```




    225.42156862745097



We see a much larger loss. This is evidence our first arrangement was good. Unfortunately, this exact value of this large comparison loss depends on what particular permutation of the data we used. To eliminate this dependency it is traditional to average over all possible permutations. This is whole methodology is called a [permutation test](https://en.wikipedia.org/wiki/Permutation_test).

### Estimating the Mean Loss

Let's use a permutation test to see if this loss is small (which would be great) or large compared to a random loss.

In this case, we can't try all of the permutations directly to get the exact expected loss, as there are rather a lot of permutations to check.


```python
number_of_permutations = factorial(n_blocks * block_size)

number_of_permutations
```




$\displaystyle 1551118753287382280224243016469303211063259720016986112000000000000$




```python
float(number_of_permutations)
```




    1.5511187532873822e+66



Let's now compute the expected loss of permuted data over a uniform sample of the permutations.



```python

# define permutation generator
def permutation_generator(
        values, 
        *, 
        max_samples: int = 100000,
        rng_seed: int = 364636,
        ):
    """Generate a sequence of uniformly likely permutations of values."""
    number_of_permutations = factorial(len(values))
    if number_of_permutations > max_samples:
        # sample
        rng = np.random.default_rng(rng_seed)
        for i in range(max_samples):
            yield rng.permutation(values)
    else:
        # all
        for perm in permutations(values):
            yield perm


```


```python
mean_loss = np.mean([
    sq_loss_fn(permuted_values, n_blocks=n_blocks, block_size=block_size) 
    for permuted_values in permutation_generator(values)
])

mean_loss
```




    221.0366338235294



This says the mean-loss is probably about 221, which is much larger than our observed loss of 25.5. This is strong evidence the partition we started with *does* in fact know something about the order of the values. And we have now eliminated the dependence on choice of comparison.




The question is: can we compute the expected loss *exactly* and *without* trying to evaluate our loss function over `1.5 * 10**66` permutations?



### Calculating the Exact Mean Loss

We now want to calculate the expected value of our loss function over all possible permutations of the data. In theory we would do this by evaluating the loss function for every permuted value of the data. This shows our original arrangement in comparison to every possible arrangement, which lets us determine scale. The magic is: we are going to calculate the exact value without performing that many steps. We will compare this to a sampled value as part of the demonstration.

We can show:

  * The loss polynomial summed over all permutations must be a degree 2 homogeneous [symmetric polynomial](https://en.wikipedia.org/wiki/Symmetric_polynomial). 
  * *There are not a lot of degree 2 homogeneous symmetric polynomials*. In fact they are at most a rank 2 vector space.
  * By the above: the exact polynomial that is the sum of a given loss polynomial over all permutations can be quickly identified.
  * [Bessel corrections](https://en.wikipedia.org/wiki/Bessel%27s_correction) (including a not shown correction for size-1 groups) ensure that the symmetrized loss polynomial depends only on the number of datums, and not the block structure!

The solution in terms of symmetric moment polynomials is given below.


```python
mean_of_loss_symmetric_polynomial = theoretical_sym_poly(n_blocks * block_size)
symmetric_to_moments_map = build_symmetric_to_moment_mapping()
mean_of_loss_as_moments = mean_of_loss_symmetric_polynomial.subs(symmetric_to_moments_map).simplify()

mean_of_loss_as_moments
```




$\displaystyle - \frac{m_{1}^{2}}{2550} + \frac{m_{2}}{50}$



Let's plug values into the `mean_of_loss_as_moments` polynomial to get the exact expected loss.


```python
m1 = np.sum(values)
m2 = np.sum(values**2)
symbolic_mean_loss = mean_of_loss_as_moments.subs(
    {'m1': m1, 'm2': m2})

symbolic_mean_loss
```




$\displaystyle 221$



We can confirm the earlier empirical `mean_loss` is in fact quite close to this idea value.


```python
def rel_abs_error(a, b):
    a = float(a)
    b = float(b)
    if a==b:
        return 0
    if (a==0) or (b==0):
        return 1
    return np.abs(a - b) / np.min([np.abs(a), np.abs(b)])
```


```python
assert rel_abs_error(mean_loss, symbolic_mean_loss) < 1e-2
```

### Estimating the Variance of the Loss

To take procedure a step further: let's get the variance of the loss function over the permutations. Knowing the variance will pretty much complete our characterization of the permutation test.

We again start with an empirical sampling based estimate.


```python
loss_variance = np.mean([
    (sq_loss_fn(permuted_values, n_blocks=n_blocks, block_size=block_size) - mean_loss)**2 
    for permuted_values in permutation_generator(values)
])

loss_variance
```




    79.45291694978158



### Calculating the Exact Variance of the Loss

Now we identify the homogeneous degree 4 symmetric polynomial that will read off the exact answer.


```python

variance_of_loss_symmetric_polynomial = identify_variance_fn_regular_blocks_e(
    n_blocks=n_blocks, block_size=block_size)
variance_of_loss_as_moments = variance_of_loss_symmetric_polynomial.subs(symmetric_to_moments_map).simplify()

variance_of_loss_as_moments
```




$\displaystyle \frac{m_{1}^{4}}{3598560000} - \frac{m_{1}^{2} m_{2}}{35280000} + \frac{m_{1} m_{3}}{17992800} + \frac{817 m_{2}^{2}}{1199520000} - \frac{m_{4}}{1411200}$



And we substitute in the evaluations of the moment polynomials to get a numeric answer.


```python
m3 = np.sum(values**3)
m4 = np.sum(values**4)
symbolic_variance = variance_of_loss_as_moments.subs(
    {'m1': m1, 'm2': m2, 'm3': m3, 'm4': m4})

symbolic_variance
```




$\displaystyle \frac{6409}{80}$



Again, our previous empirical estimate is very close to the ideal answer.


```python
float(symbolic_variance)
```




    80.1125




```python
assert rel_abs_error(loss_variance, symbolic_variance) < 1e-2
```

## Conclusion/Discussion

  * We have demonstrated exact calculation of low degree summary statistics (such as mean and variance of low degree polynomial loss function) averaged over all permutations of data. Exact mean and variance characterizations can drive powerful statistical tests. Permutations are one way to simulate a system with no useful signal (itself important for calibration).
  * The method uses the fact that the sum of a polynomial over all permutations, must itself be a symmetric polynomial (itself immune to permutations of variables). This allows us to use elements of the theory of symmetric polynomials to complete the derivations.
  * For a computer scientist, computing the necessary outcome of a procedure *without* actually running the original explicit defining procedure is a big deal. In this note we have computed what the average of a function over all permutations of the data would be, without explicitly running through all of the permutations.
  * The structure of the result looks a lot like what is seen in [Polya enumeration](https://en.wikipedia.org/wiki/Pólya_enumeration_theorem) (where one writes down polynomials over moments) or discrepancy-theory/pseudo-random methods (which sometimes also break error into a structural polynomial over separately calculated moments).


All the code for this article can be found [here](https://github.com/WinVector/Examples/tree/main/group_action).
 


