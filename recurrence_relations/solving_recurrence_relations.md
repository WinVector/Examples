# Solving Recurrence Relations

## Introduction

A neat bit of "engineering mathematics" is solving [recurrence relations](https://en.wikipedia.org/wiki/Recurrence_relation). The solution method falls out of the notation itself, and harkens back to a time where formal sums were often used in place of vector subscript notation.

Unfortunately the variety of such solutions is small enough to allow teaching by memorization. In this note I try to avoid memorization, and motivate the methodology. I feel this is facilitated by separating a number of often smeared together representations (formulas, sequences, vectors, linear checks, characteristic polynomial, and polynomial check families) into distinct realizations. We are also going to emphasize calculating and confirming claims in Python.

## The problem

A simple form of the recurrence problem is to write down a general solution for a subscripted family of linear equations such as the following

<code>
F<sub>n+2</sub> = F<sub>n+1</sub> + F<sub>n</sub>
</code>

where <code>n</code> is a subscript varying over all positive integers.

Such a relation or equation can arise in number of situations or applications:

  * [Time series analysis](https://win-vector.com/2023/05/25/some-of-the-perils-of-time-series-forecasting/).
  * Estimating run times of algorithms.
  * Combinatorics.

The above example is in fact [the Fibonacci sequence](https://en.wikipedia.org/wiki/Fibonacci_sequence).

The question is: if we are given initial conditions <code>F<sub>1</sub> = 1</code> and <code>F<sub>2</sub> = 1</code>, what is <code>F<sub>n</sub></code> (for general non-negative integer <code>n</code>)?

In this case the [Wikipedia solution](https://en.wikipedia.org/wiki/Fibonacci_sequence) is <code>F<sub>n</sub> = (r<sub>1</sub><sup>n</sup> - r<sub>2</sub><sup>n</sup>)/sqrt(5)</code> where:

  * <code>r<sub>1</sub> = (1 + sqrt(5))/2</code>
  * <code>r<sub>2</sub> = (1 - sqrt(5))/2</code>

Natural questions include:

  * Why is the solution in this form?
  * How do you find <code>r<sub>1</sub></code> and <code>r<sub>2</sub></code>?

We will set up some notation and then solve a few examples.

## The Solution

 


### Vector space notation

Let's formalize our notation a bit.

First let's settle on working over the [vector space](https://en.wikipedia.org/wiki/Vector_space) of all infinite sequences of real numbers with non-negative subscripts. This is just saying we consider the infinite sequence <code>F = (F<sub>1</sub>, F<sub>2</sub>, F<sub>3</sub>, ...)</code> we are solving for as one of many possible sequences. We can use "<code>R[Z+]</code>" as the [group-ring](https://en.wikipedia.org/wiki/Group_ring) style naming of this vector space.  Now consider any such vector <code>v</code> that obeys the recurrence equations:

<code>
v<sub>n+2</sub> = v<sub>n+1</sub> + v<sub>n</sub> for n = 1, 2, ...
</code>

Let "<code>S</code>" denote the subset of <code>R[Z+]</code> that obey all of the above linear recurrence checks. We claim a few things about <code>S</code> (the set of solutions to our current example system):

  * The all zeroes vector is in <code>S</code>. So <code>S</code> is non-empty.
  * If <code>v</code> obeys all of the above constraints then so does <code>c v</code> for any constant c.
  * If <code>u</code> and <code>v</code> obey all of the above constraints then so does <code>u + v</code>.
  * By induction, all <code>v<sub>n</sub></code> are completely determined by the values <code>v<sub>1</sub></code> and <code>v<sub>2</sub></code>.

The first three observations tell us <code>S</code> is a vector subspace of <code>R[Z+]</code>. The fourth observation tells us this vector subspace is 2 dimensional, so any solution can be written as the linear combination of two basis solutions.

For notational convenience we will associate functions with vectors in <code>R[Z+]</code>. For a function <code>f()</code> let <code>[f(n) | n = 1, 2, ...]</code> denote the graph or vector <code>(f(1), f(2), f(3), ...)</code>. In particular we are interested in the vectors <code>[r<sub>1</sub><sup>n</sup> | n = 1, 2, ...] = (r<sub>1</sub>, r<sub>1</sub><sup>2</sup>, r<sub>1</sub><sup>3</sup>, ...)</code> and <code>[r<sub>2</sub><sup>n</sup> | n = 1, 2, ...] = (r<sub>2</sub>, r<sub>2</sub><sup>2</sup>, r<sub>2</sub><sup>3</sup>, ...)</code> (for the previously defined <code>r<sub>1</sub></code> and <code>r<sub>2</sub></code>). We claim <code>[r<sub>1</sub><sup>n</sup> | n = 1, 2, ...]</code> and <code>[r<sub>2</sub><sup>n</sup> | n = 1, 2, ...]</code> both obey the above linear check conditions.


### Inspecting the claimed Fibonacci solution

Let's confirm both <code>[r<sub>1</sub><sup>n</sup> | n = 1, 2, ...]</code> and <code>[r<sub>2</sub><sup>n</sup> | n = 1, 2, ...]</code> both obey the linear check conditions. In my opinion one doesn't truly learn the math without working at least a few concrete examples.


```python
# define [r1**n | n = 1, 2, ...] = f_r_1
import numpy as np

r_1 = (1 + np.sqrt(5))/2

f_r_1 = np.asarray([r_1**n for n in range(1, 11)])

f_r_1
```




    array([  1.61803399,   2.61803399,   4.23606798,   6.85410197,
            11.09016994,  17.94427191,  29.03444185,  46.97871376,
            76.01315562, 122.99186938])




```python
# check f_r_1 obeys specified  Fibonacci relations
assert np.all([
    np.abs(f_r_1[n+2] - (f_r_1[n+1] + f_r_1[n])) < 1e-8
    for n in range(2, len(f_r_1) - 2)
])
```


```python
# define [r2**n | n = 1, 2, ...] = f_r_2

r_2 = (1 - np.sqrt(5))/2

f_r_2 = np.asarray([r_2**n for n in range(1, 11)])

f_r_2
```




    array([-0.61803399,  0.38196601, -0.23606798,  0.14589803, -0.09016994,
            0.05572809, -0.03444185,  0.02128624, -0.01315562,  0.00813062])




```python
# check f_r_2 obeys specified  Fibonacci relations
assert np.all([
    np.abs(f_r_2[n+2] - (f_r_2[n+1] + f_r_2[n])) < 1e-8
    for n in range(2, len(f_r_2) - 2)
])
```


```python
# generate a bit of the Fibonacci sequence using 
# the definitional recurrence F[n+2] = F[n+1] + F[n]
f = [1, 1]
for i in range(8):
    n = len(f) - 2
    f.append(f[n + 1] + f[n])

f

```




    [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]




```python
# Wikipedia claimed solution
prediction = (f_r_1 - f_r_2) / np.sqrt(5)

prediction
```




    array([ 1.,  1.,  2.,  3.,  5.,  8., 13., 21., 34., 55.])




```python
# confirm claimed combination matches Fibonacci sequence
assert np.max(np.abs(
        np.asarray(f) - prediction
    )) < 1e-8
```


```python
# we can also solve for the mixture coefficients by
# treating our sequences as column vectors and asking
# a solver how to write the vector f as a linear
# combination of the vectors f_r_1 and f_r_2.
#
# As a linear system in the first 2 terms this looks like:
#
# f[0] = soln[0] * f_r_1[0]  +  soln[1] * f_r_1[0]
# f[1] = soln[0] * f_r_1[1]  +  soln[1] * f_r_1[1]
#
# And such a linear system is translated into 
# matrix notation as follows:
soln = np.linalg.solve(
    np.asarray([
        [f_r_1[0], f_r_2[0]],
        [f_r_1[1], f_r_2[1]],
    ]),
    [
        f[0],
        f[1],
    ]
)

soln

```




    array([ 0.4472136, -0.4472136])




```python
# our (identical) derived solution
prediction2 = (
    soln[0] * f_r_1 
    + soln[1] * f_r_2
)

prediction2
```




    array([ 1.,  1.,  2.,  3.,  5.,  8., 13., 21., 34., 55.])




```python
# confirm claimed combination matches Fibonacci sequence
assert np.max(np.abs(
        np.asarray(f) - prediction2
    )) < 1e-8
```


### The neat trick

The core of the solution follows from a neat trick: replace the subscripts with superscripts. This is *very* powerful trick. Let's see that in action.

We gamble and hope some of the solutions are of the following simple form: <code>[r<sup>n</sup> | n = 1, 2, ...] = (r, r<sup>2</sup>, r<sup>3</sup>, ...)</code>, where <code>r</code> is a to be determined (possibly [complex](https://en.wikipedia.org/wiki/Complex_number)) number. 

Our claim is: *if* the number <code>r</code> is a solution to the polynomial equation (in <code>x</code>)

<code>
x<sup>2</sup> = x + 1
</code>

*then* <code>v = [r<sup>n</sup> | n = 1, 2, ...]</code> satisfies

<code>
v<sub>n+2</sub> = v<sub>n+1</sub> + v<sub>n</sub> for n = 1, 2, ...
</code>.

The polynomial is called "the characteristic polynomial" of the linear recurrence checks.

The "trick" to this is: if <code>x = r</code> is a root of, or satisfies, <code>x<sup>2</sup> = x + 1</code>, then it also satisfies <code>x<sup>n+2</sup> = x<sup>n+1</sup> + x<sup>n</sub></code> (which is equivalent to <code>x<sup>n</sup> x<sup>2</sup> = x<sup>n</sup> x + x<sup>n</sup> 1</code>) for *all* <code>n &ge; 0 </code>. So <code>r<sup>n+2</sup> = r<sup>n+1</sup> + r<sup>n</sub></code> for *all* <code>n &ge; 0 </code> which is exactly the claim <code>v = [r<sup>n</sup> | n = 1, 2, ...]</code> is a solution to all of the subscripted <code>v</code>-checks. It pays to think of the characteristic polynomial <code>p(x)</code> as shorthand for the family of "check polynomials" <code>x<sup>n</sup> p(x) for n = 0, 1, 2, ...</code>. However, for some problems we will need to appeal directly to the family of check polynomials.

In our case, the roots, or solutions, to this polynomial equation are the roots <code>x<sup>2</sup> - x - 1 = 0</code>. By the [quadratic formula](https://en.wikipedia.org/wiki/Quadratic_formula):

  * <code>r<sub>1</sub> = (1 + sqrt(5))/2</code>
  * <code>r<sub>2</sub> = (1 - sqrt(5))/2</code>

This gives us two linearly independent solutions to the recurrence check equations: <code>[r<sub>1</sub><sup>n</sup> | n = 1, 2, ...]</code> and <code>[r<sub>2</sub><sup>n</sup> | n = 1, 2, ...]</code>. These solutions are enough to form a basis for the solution space <code>S</code>, so we know <code>F</code> is some linear combination of <code>[r<sub>1</sub><sup>n</sup> | n = 1, 2, ...]</code> and <code>[r<sub>2</sub><sup>n</sup> | n = 1, 2, ...]</code>. And we have already showed how to find the linear combination by setting up linear equations to match the first two entries of the vector.


## A harder example

Suppose we want to solve the recurrence:

<code>
W<sub>n+2</sub> = 6 W<sub>n+1</sub> - 9 W<sub>n</sub>  for n = 1, 2, ...
</code>

The above are the "<code>W</code> checks" we now want to satisfy. A solution to these is a specific vector of values we can substitute in for the <code>W</code>'s, such that none of the equations are false.

We will try the earlier solution strategy. We are then interested in roots of the corresponding characteristic polynomial:

<code>
x<sup>2</sup> - 6 x + 9  = 0
</code>

The above polynomial factors into <code>(x - 3)<sup>2</sup></code>. So <code>r<sub>1</sub> = r<sub>2</sub> = 3</code>. So we know <code>[3<sup>n</sup> | n = 1, 2, ...]</code> is a solution to the <code>W</code> checks.

The space of solutions is again 2 dimensional. So to parameterize over all the possible solutions, we need a second linear independent solution. The question then is: how do we find a second linear independent solution?


### Dealing with repeated roots

When our characteristic polynomial <code>p(x)</code> has repeated roots, the characteristic polynomial is not expressive enough to represent some solutions. However, *the corresponding family of check polynomials* <code>x<sup>n</sup> p(x) for n = 0, 1, ...</code> *are* rich enough to find the extra solutions. We will use that when a polynomial <code>p(x)</code> has a repeated root (that is: for some number <code>r</code>, the fact that <code>(x-r)<sup>2</sup></code> divides into <code>p(x)</code> with no remainder), then <code>p(x)</code> shares that root with <code>p'(x)</code> (where <code>p'(x)</code> is the derivative of <code>p(x)</code> with respect to <code>x</code>).

Take the earlier "<code>W</code> check" polynomials <code>p(x) = x<sup>n+2</sup> - 6 x<sup>n+1</sup> + 9 x<sup>n</sup></code>. Define the polynomial <code>y(x) = x p'(x) = (n+2) x<sup>n+2</sup> - 6 (n+1) x<sup>n+1</sup> + 9 n x<sup>n</sup></code>. <code>y(x)</code> itself is (by inspection) the check polynomials corresponding to the following (new) linear recurrence checks:

<code>
(n+2) Y<sub>n+2</sub> = 6 (n+1) Y<sub>n+1</sub> - 9 (n) Y<sub>n</sub> for n = 1, 2, ...
</code>

As <code>y(3) = 0</code> (true because <code>3</code> is a double root of <code>p(x)</code>) we know <code>[3<sup>n</sup> | n = 1, 2, ...]</code> *is* a solution to the new <code>Y</code> linear recurrence checks. Substitute this valid <code>Y</code> solution <code>[3<sup>n</sup> | n = 1, 2, ...]</code> into the <code>Y</code> checks to derive the following family of (true or valid) equations.

<code>
((n+2) 3<sup>n+2</sup>) = 6 ((n+1) 3<sup>n+1</sup>) - 9 ((n) 3<sup>n</sup>)   for n = 1, 2, ...
</code>

Notice the above is saying <code>[n 3<sup>n</sup> | n = 1, 2, ...]</code> obeys the earlier <code>W</code> linear recurrence problem. We have our desired additional solution.

#### Confirming the last claim

Frankly, this sort of argument doesn't fully sink in until one confirms some examples and calculations. The derivation is a bit of "proof by change of notation", which is *never* very satisfying.

So: let's confirm some calculations claimed in the example to try to build some familiarity with the items discussed.



```python
# show down p(x) zeros out at x=3
r = 3
evals_p = [
    r**(n+2) - 6 * r**(n+1) + 9 * r**n 
    for n in range(10)]

evals_p


```




    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]




```python
assert np.all(np.abs(evals_p)) < 1e-8
```


```python
# show down y(x) = x p'(x) zeros out at x=3
r = 3
evals_y = [
    r * ((n+2) * r**(n+1) - 6 * (n+1) * r**(n) + 9 * n * r**(n-1)) 
    for n in range(10)]

evals_y
```




    [0.0, 0, 0, 0, 0, 0, 0, 0, 0, 0]




```python
assert np.all(np.abs(evals_y)) < 1e-8
```


```python
# write down the first p = [3**n | n = 1, 2, ...] solution
p = np.asarray([
    r**n for n in range(1, 11)
    ])

p
```




    array([    3,     9,    27,    81,   243,   729,  2187,  6561, 19683,
           59049])




```python
# confirm W checks on p'
assert np.all([
    p[n+2] - 6 * p[n+1] + 9 * p[n] == 0 
    for n in range(1, len(p) - 2)])
```


```python
# confirm Y checks on p
# this works as W is the "Y" checks for p'
assert np.all([
    (n+2) * p[n+2] - 6 * (n+1) * p[n+1] + 9 * n * p[n] == 0 
    for n in range(1, len(p) - 2)])
```

### Back to the example

As we now have the required number of linearly independent solutions (2 solutions: <code>[3<sup>n</sup> | n = 1, 2, ...]</code> and <code>[n 3<sup>n</sup> | n = 1, 2, ...]</code>), we can solve for any specified initial conditions (as demonstrated earlier).

Believe it or not, we are done.

## In general

The general solution strategy is as follows.

For a general homogeneous linear recurrence of the form:

<code>
v<sub>n+k</sub> = c<sub>k-1</sub> v<sub>n+k-1</sub> + ... + c<sub>0</sub> v<sub>n</sub>
</code>

Move to the characteristic polynomial equation:

<code>
x<sup>k</sup> = c<sub>k-1</sub> x<sup>k-1</sup> + ... + c<sub>0</sub>
</code>

We can generate a basis for all solutions as <code>v = [ n<sup>k</sup> r<sup>n</sup> | n = 1, 2, ...]</code> where <code>r</code> is a root of the characteristic polynomial, and <code>k</code> is a non-negative integer smaller than the degree of multiplicity of the root <code>r</code>. Once we have enough linear independent solutions, we can write any other solution as a linear combination of what we have.

We call all of the above the "swap subscripts (general and powerful) to powers (specific and weak)" strategy (though there are obviously a few more steps and details to the method).


## Conclusion

Our solution strategy was exchanging powerful subscripts (which can implement any integer keyed lookup table) with less powerful superscripts (that can only express powers). We can lift any solution found in the weaker world (power series) to the more general one (subscripted sequences). We don't always find enough power series solutions, and in that case we transform the problem to find more solutions to modified polynomials. The trick is to track the details of how the transforms operate on both our vector solutions and check polynomials.

The above system is general, it can solve a lot of problems. We concentrated on calculating over vector values. Related methods include [the umbral calculus](https://en.wikipedia.org/wiki/Umbral_calculus), the study of [shift operators](https://en.wikipedia.org/wiki/Shift_operator), and the [Laplace transform](https://en.wikipedia.org/wiki/Laplace_transform).

(The source code for this worksheet can be found [here](https://github.com/WinVector/Examples/blob/main/recurrence_relations/solving_recurrence_relations.ipynb))
