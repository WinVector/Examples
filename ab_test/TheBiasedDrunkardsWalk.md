# The Biased Drunkard's Walk

  * John Mount, [Win Vector LLC](https://win-vector.com)
  * Nina Zumel, [Win Vector LLC](https://win-vector.com)
  * December 4, 2023

## Introduction

This note is a deep dive into the biased drunkard's walk, and its application in what I will define as "first to win <code>w</code> tournaments." This is anticipation of reexamining [Wald's Sequential Analysis](https://win-vector.com/2015/12/10/sequential-analysis/) (a variation of A/B testing with a correct early stopping procedure!).

Our previous note (["The Drunkard's Walk In Detail"](https://github.com/WinVector/Examples/blob/main/ab_test/drunkards_walk.ipynb)) demonstrated a lot of properties of the unbiased drunkards walk (the walk with equal probabilities of increasing or decreasing the recorded state). In this note we will concentrate on a biased drunkard's walk where the probability of decreasing our state is <code>p</code> and the probability of increasing state is <code>1-p</code>. We are again working with absorbing Marko chains, and not the usual regular, ergodic, or "time reversible" Markov chains. 

This note is part of our "check a lot of things by running Python examples" math series.


## The drunkard's walk again

As in ["The Drunkard's Walk In Detail"](https://github.com/WinVector/Examples/blob/main/ab_test/drunkards_walk.ipynb) we take the non-negative integers <code>0</code> through <code>k &gt; 0</code> as our states. States <code>0</code> and <code>k</code> are "stopping" or "absorbing" states. Once one of these states is hit the walk is stopped, or over. States <code>1, ..., k-1</code> are continuation states where with probability <code>p</code> we move from state <code>i</code> to state <code>i-1</code>, and otherwise we move from state <code>i</code> to state <code>i+1</code>.


### Notation and Definitions

Pick <code>k</code> a positive even integer, and set <code>n = k-1</code> and <code>w = (n+1)/2 = k/2</code>.

We will try to be somewhat consistent with variable names:

  * <code>k (= n+1)</code>, <code>n = k-1</code>, and <code>w = (n+1)/2 = k/2</code> are positive integers describing the size of the random walk region.
    * The states <code>1, ..., n</code> are the "continuation" or "non-stopping" states.
    * The states <code>0, k</code> are the "stopping" or "boundary" states.
    * The state <code>w</code> is the middle or "start state".
  * <code>i</code> is used for state labels.
  * <code>j</code> is used for step number or number of steps, meaning "time."
  * <code>p</code> is used for probability; throughout we will assume <code>0 &lt; p &lt; 1</code>. By symmetry we will only need estimates and arguments for <code>p &ge; 1/2</code>.
  * <code>&lambda;</code> is used for eigenvalues.
  * <code>x</code> is used for eigenvectors.
  * <code>v</code> is used for a vector whose values represent the probability of being in each modeled state.
  * <code>e<sub>i</sub></code> is the probability vector with <code>i</code>-th position equal to <code>1</code>, and zeroes elsewhere.


We will track the probability of being in any of the continuation states <code>1, ..., n</code> using a vector <code>v</code> in <code>R<sup>n</sup></code>. <code>v<sub>i</sub></code> is our modeled probability of the random process being in state <code>i</code>. As an example distribution vector, define <code>e<sub>i</sub></code> as the vector that has a <code>1</code> in the <code>i</code>-th position and zeroes everywhere else. We modeled "stopped probability" simply as missing mass. For us, probability vectors are non-negative and sum to no more than <code>1</code>. For a such a vector <code>v &ge; 0 </code>, the probability of already of having hit one of the halting states is <code>1 - |v|<sub>1</sub></code> (where <code>||<sub>1</sub></code> is the usual L1-norm).


## First to win <code>w</code> Tournaments

Consider recording the win/loss outcomes of a sequence of games between two players "Z" (zero) and "P" (positive). We decrement a count when "Z" wins, and increment otherwise. Further suppose "Z" has an (unknown) independent probability <code>p</code> of winning any individual game. We want to determine if <code>p &gt; 1/2</code> or not. We start our walk at state <code>i = w</code>, and stop the walk once the state reaches <code>0</code> or <code>k</code>. 

<img style="display:block; margin-left:auto; margin-right:auto;" src="https://win-vector.com/wp-content/uploads/2023/12/unnamed-chunk-3-1.png" alt="Unnamed chunk 3 1" title="unnamed-chunk-3-1.png" border="0" width="672" height="480" />

We call this arrangement a "first to win <code>w</code> tournament", as the distance to each boundary is <code>w</code> from the start. Our procedure is to say that we think <code>p &gt; 1/2</code> if the walk stops at <code>0</code>.

The utility of a tournament is that for large <code>w</code>, running a tournament greatly increases our probability of correctly identifying the better player from observed outcomes.


## Tournament odds as a function of <code>w</code>

There is a standard trick argument to calculate the probability that a player of skill <code>p</code> wins a "first to win <code>w</code> tournament."

The argument depends on symmetry, so only works for <code>n</code> odd and <code>w = (n+1)/2 = k/2</code>.  Consider the set of <code>S<sub>P</sub></code> of all trajectories that first stop at <code>k</code> and the set <code>S<sub>Z</sub></code> of all trajectories that first stop at <code>0</code>. By symmetry these paths are in 1 to 1 correspondence by just reversing the moves.

For a trajectory <code>t<sub>Z</sub> in S<sub>Z</sub></code> that ends on the <code>j</code>-th step we must have: the trajectory took <code>w</code> more "down/left" steps than "up/right" steps. So the relative probability of this trajectory is <code>p<sup>r+w</sup> (1-p)<sup>r</sup></code>, where <code>r</code> is the non-negative integer such that <code>j = 2 r + w</code>. Another way of saying is this is to observe that if `Z` won the tournament after `j` games, then `P` won `r` games, and `Z` won `r + w`. This trajectory has a matching trajectory <code>t<sub>P</sub> in S<sub>P</sub></code> defined by reversing all the moves. <code>t<sub>P</sub></code> has relative probability <code>p<sup>r</sup> (1-p)<sup>r+w</sup></code>. The ratio of these two quantities is <code>(p/(1-p))<sup>w</sup></code> independent of <code>r</code>. Since this ratio is constant for all matched pairs of stopped trajectories, the ratio <code>P[S<sub>Z</sub>] / P[S<sub>P</sub>]</code> is also <code>(p/(1-p))<sup>w</sup></code>.

The above argument shows how a first to win <code>w</code> tournament greatly amplifies the observed probability of the more skilled player prevailing.


## Expected Tournament Length

We will use linear algebra (in particular eigenvectors and properties of Toeplitz matrices) to characterize the behavior of the drunkard's walk. In [our earlier note](https://github.com/WinVector/Examples/blob/main/ab_test/drunkards_walk.ipynb) we proved a good number of things about the drunkard's walk directly, without resorting to the linear algebra "hammers" often used in reasoning about Markov chains. In this note we bring out a *big* such hammer.

<a href="https://www.worldhistory.org/image/17048/nasmyths-steam-hammer/">
<img src="https://win-vector.com/wp-content/uploads/2023/11/nasmyths-steam-hammer-17048.png">
<br>1871 oil painting of a steam hammer invented by James Nasmyth
</a>


## The Toeplitz matrix formulation

In general our "drunkard's walk" can be represented by the <code>n</code> by <code>n</code> tri-diagonal Toeplitz matrix <code>T</code> such that:

<ul>
<li><code>T<sub>i,i-1</sub> = 1-p</code> (probability of a <code>i-1</code> to <code>i</code> transition)</li>
<li><code>T<sub>i,i+1</sub> = p</code> (probability of a <code>i+1</code> to <code>i</code> transition)</li>
<li><code>0</code> otherwise</li>
</ul>

Some details on the above notation:

  * In this set-up the row of the matrix (which by convention is the first index) is the future state, and the column (which by convention is the second index) is the current state. So <code>T<sub>b,a</sub></code> represents the probability of seeing state <code>b</code> immediately after state <code>a</code> (called "<code>a &rightarrow; b</code>" transition).
  * This implies <code>T v</code> is the vector of probabilities one step after <code>v</code>. This "operator matrix on the left" notation is consistent with linear algebra practice. Unfortunately Markov chain literature, uses a reverse convention; putting the operator on the right. Not checking which convention is being used is a great source of confusion and errors.
  * In particular the column <code>T[?, i] = T e<sub>i</sub></code>. So we see the operator as operating on columns by evolving the modeled probability distribution forward one step.

As an example, for <code>n = 5</code> we have:

<pre>
<code>
       [  0 ,  p ,  0 ,  0 ,  0 ]
       [ 1-p,  0 ,  p ,  0 ,  0 ]
T(5) = [  0 , 1-p,  0 ,  p ,  0 ]
       [  0 ,  0 , 1-p,  0 ,  p ]
       [  0 ,  0 ,  0 , 1-p,  0 ]
</code>
</pre>


The matrix describes how probabilities evolve forward. So facts about this matrix give us facts about the random walk. Our goal is to use this formulation to show when <code>p &ne; 1/2</code> this walk halts faster than what we would expect in the <code>p = 1/2</code> case. We will only argue the <code>p &ge; 1/2</code>, and note the <code>p &le; 1/2</code> case follows from reversing the roles of the two players. From now on: assume <code>1/2 &le; p &lt; 1</code>.


### The Toeplitz eigenvalues and eigenvectors

It is a standard fact that a Toeplitz matrix <code>T</code> has the eigenvalues:

<pre>
<code>
   &lambda;<sub>h</sub> = 2 sqrt(p (1-p)) cos(h &pi; / k),  h = 1...n
</code>
</pre>


<img style="display:block; margin-left:auto; margin-right:auto;" src="https://win-vector.com/wp-content/uploads/2023/12/unnamed-chunk-4-1.png" alt="Unnamed chunk 4 1" title="unnamed-chunk-4-1.png" border="0" width="599" height="428" />


The (not normalized) eigenvectors <code>x<sub>1</sub>, ..., x<sub>n</sub></code> are known to be:

<pre>
<code>
   x<sub>h,j</sub> = ((1-p)/p)<sup>j/2</sup> sin(h j &pi; / k),  h = 1...n, j = 1...n
</code>
</pre>

Good references for this include: [Silvia Noschese, Lionello Pasquini, and Lothar Reichel, "Tridiagonal Toeplitz Matrices: Properties and Novel Applications"](https://www.math.kent.edu/~reichel/publications/toep3.pdf), [Gene H. Golub, "CME 302: NUMERICAL LINEAR ALGEBRA"](http://www2.stat.duke.edu/~sayan/Lek-Heng/Golub_notes/notes14.pdf), and [stack exchange](https://math.stackexchange.com/questions/955168/how-to-find-the-eigenvalues-of-tridiagonal-toeplitz-matrix). We directly confirm the eigenvectors and eigenvalues in an appendix.

## Using the Toeplitz formulation


### Sizing the eigenvalues

An eigenvalue of largest absolute value of our Toeplitz matrix representing our (possibly unfair) drunkards walk is <code>&lambda;<sub>1</sub> = 2 sqrt(p (1-p)) cos(&pi; / k)</code>. 

We will use a couple of estimates (both gotten by Taylor series expansion):

  * For large <code>n</code> we have <code>cos(&pi; / k) ~ 1 - &pi;<sup>2</sup> / (2 k<sup>2</sup>)</code>.
  * For positive <code>&epsilon;</code> near zero: <code>(1 - &epsilon;) ~ e<sup>-&epsilon;</sup></code>.

We show, for any eigenvalue <code>&lambda;</code> of <code>T</code>:

<pre>
<code>
  |&lambda;|
    &le; &lambda;<sub>1</sub>
    = 2 sqrt(p (1-p)) cos(&pi; / k)
    ~ 2 sqrt(p (1-p)) (1 - &pi;<sup>2</sup> / (2 k<sup>2</sup>))
    ~ 2 sqrt(p (1-p)) e<sup>-&pi;<sup>2</sup> / (2 k<sup>2</sup>)</sup>
</code>
</pre>

Thus we know (for large <code>n</code>):

<pre>
  For any <code>&lambda;</code> eigenvalue of <code>T</code>:
    <code>|&lambda;|</code> can't be much bigger than <code>2 sqrt(p (1-p)) exp(- &pi;<sup>2</sup> / (2 k<sup>2</sup>))</code>
</pre>

We are excited about the case where <code>p &ne; 1/2</code> as then <code>2 sqrt(p (1-p))</code> is strictly below <code>1</code>.


### Picking a start vector

We are going to start our walk with the probability distribution vector:

<pre>
  <code>e<sub>mid</sub></code> defined as <code>e<sub>mid,i</sub> = 1 if i = w, 0 otherwise</code>
</pre>

In linear algebra it is easier to prove facts about eigenvectors than for general vectors. So instead of proving facts about the probability vector <code>e<sub>mid</sub></code>, we will prove facts about a general non-negative vector (not representing probabilities!) called <code>s</code>.  Define:

<pre>
  <code>s = c * x<sub>1</sub> </code>, where <code>c = (p/(1-p))<sup>w/2</sup></code>
</pre>

where <code>x<sub>1</sub></code> is the eigenvector with eigenvalue equal to <code>&lambda;<sub>1</sub></code>.
  
We will confirm in an appendix that:

  * <code>s &ge; 0</code>
  * <code>s<sub>w</sub> &ge; 1</code>


<img style="display:block; margin-left:auto; margin-right:auto;" src="https://win-vector.com/wp-content/uploads/2023/12/unnamed-chunk-16-1.png" alt="Unnamed chunk 16 1" title="unnamed-chunk-16-1.png" border="0" width="672" height="480" />

This is enough to show:

  * <code>e<sub>mid</sub> &le; s</code>
  * <code>T<sup>2 j</sup> e<sub>mid</sub> &le; T<sup>2 j</sup> s</code> for all non-negative integers <code>j</code> (follows from the fact none of <code>T</code>, <code>e<sub>mid</sub></code>, or <code>s</code> have negative entries).


<img style="display:block; margin-left:auto; margin-right:auto;" src="https://win-vector.com/wp-content/uploads/2023/12/unnamed-chunk-18-1.png" alt="Unnamed chunk 18 1" title="unnamed-chunk-18-1.png" border="0" width="672" height="480" />

We will also use the fact that <code>&lambda;<sub>1</sub><sup>2 j</sup> = &lambda;<sub>n</sub><sup>2 j</sup></code>, and these are the two eigenvalues with largest absolute value.


### Showing the action on <code>s</code>

Let's look at the result of applying <code>T</code> to <code>s</code> as many as <code>2 j</code> times.

<pre>
<code>
  T<sup>2 j</sup> s
    = T<sup>2 j</sup> c x<sub>1</sub>
    =  c T<sup>2 j</sup> x<sub>1</sub> 
    =  c &lambda;<sub>1</sub><sup>2 j</sup> x<sub>1</sub>
    =  &lambda;<sub>1</sub><sup>2 j</sup> c x<sub>1</sub>
    =  &lambda;<sub>1</sub><sup>2 j</sup> s
</code>
</pre>

So <code>|T<sup>2 j</sup> s|<sub>1</sub> = &lambda;<sub>1</sub><sup>2 j</sup> |s|<sub>1</sub></code>. Or, <code>s</code> is proportional to an eigenvector of <code>T<sup>2</sup></code>.

When <code>p &ge; 1/2</code> we have:

  * By the triangle inequality: <code>|s|<sub>1</sub> &le; c * |x<sub>1</sub>|<sub>1</sub></code>.  For <code>p &ge; 1/2</code> we have <code>|x<sub>i</sub>|<sub>1</sub> &le; n</code>. So <code>|s|<sub>1</sub> &le; n c = n (p/(1-p))<sup>w/2</sup></code>.
  * Substituting this into the earlier derivation, we have <code>|T<sup>2 j</sup> s|<sub>1</sub> &le; &lambda;<sub>1</sub><sup>2 j</sup> n (p/(1-p))<sup>w/2</sup></code>.
  * <code>&lambda;<sub>1</sub><sup>2 j</sup> &le; (2 sqrt(p (1-p)))<sup>2 j</sup> = (4 p (1-p))<sup>j</sup></code> (and <code>(4 p (1-p)) &lt; 1</code>).

Putting all of the above together gives us:

<pre>
<code>
  |T<sup>2 j</sup> e<sub>mid</sub>|<sub>1</sub> &le; A * B * C
</code>
</pre>

With:

  * <code>A = n (p/(1-p))<sup>w/2</sup></code> is from the initial norm bound on <code>s</code>. It is a large quantity that we have to get rid of.
  * <code>B = exp(- 2 j &pi;<sup>2</sup> / (2 k<sup>2</sup>))</code> is related to how fast the fair (<code>p = 1/2</code>) drunkard's walk moves to the halting states. We see the expected <code>O(1/n<sup>2</sup>)</code> decrease rate, showing how slow this sort of escape is.
  * <code>C = (4 p (1-p))<sup>j</sup></code> is the exciting bit! When <code>p &ne; 1/2</code> we have <code>4 p (1-p)</code> is less than one and therefore the walk is escaping the non-stopping states exponentially fast in time <code>j</code>.

While <code>|T<sup>2 j</sup> s|<sub>1</sub> &ge; 1</code> the above bounds tell us nothing of interest. 

However, once <code>|T<sup>2 j</sup> s|<sub>1</sub> &le; 1 - f</code> we know also <code>|T<sup>2 j</sup> e<sub>mid</sub>|<sub>1</sub> &le; 1 - f</code>, which means the tournament has a probability of at least <code>f</code> of being complete by time <code>2 j</code>.


<img style="display:block; margin-left:auto; margin-right:auto;" src="https://win-vector.com/wp-content/uploads/2023/12/unnamed-chunk-20-1.gif" alt="Unnamed chunk 20 1" title="unnamed-chunk-20-1.gif" border="0" width="672" height="480" />

We now have what we want: when <code>p &ne; 1/2</code> the drunkard's walk can be expected to halt in time proportional to <code>n</code>, and not the much larger time proportional to <code>n<sup>2</sup></code> (as we saw in the <code>p = 1/2</code> case [here](https://github.com/WinVector/Examples/blob/main/ab_test/drunkards_walk.ipynb)).


<img style="display:block; margin-left:auto; margin-right:auto;" src="https://win-vector.com/wp-content/uploads/2023/12/unnamed-chunk-23-1.png" alt="Unnamed chunk 23 1" title="unnamed-chunk-23-1.png" border="0" width="672" height="480" />


## Conclusion

We were able to show when <code>p &ne; 1/2</code>:

  * First to win <code>w</code> tournaments greatly amplify the reliability of measurements.
  * The amount of non-stopped mass in the first to win <code>w</code> tournament is decreasing exponentially fast as a function of time (and not the much slower "as a function of sqrt-time")
  * The initial bounding mass is not too large, so the decrease rate is enough to move it to small values quickly.

Determining where the biased drunkard's walk stops and how long it takes to do so is the key component of [Wald's sequential analysis](https://win-vector.com/2015/12/10/walds-sequential-analysis-technique/). Wald's sequential analysis is a relative of A/B testing that is designed to allow controlled early stopping of experiments, while avoiding the errors introduced by improper early peeking.

The benefit of moving to linear algebra arguments include: 

  * they are exactly the tool for solving linear recurrences
  * we can move from probability vectors to general non-negative vectors (given more freedom in the analysis)
  * they supply more detailed conjectures (that turn out to be easier to confirm).

The argument style substituting in an upper bound we can prove more about is particularly satisfying.


## Appendices


### Appendix: Confirming the Eigenvectors and Eigenvalues of the tri-diagonal Toeplitz matrix

In mathematics, one shouldn't derive everything. But one *has* to check most everything used (else often a mis-read, typo, or unexpected variation in reference notation can spoil the work). The idea is: we *are* going to have typos, misunderstandings, and mistakes, but we work to ensure they are not critical. Derivations and examples help ensure surviving errors are not critical.

Let's confirm the claimed eigenvalues and eigenvectors. In the end we are still just checking linear recurrence relations. What the linear algebra formulation brings us the very detailed eigenvectors, which make confirming the eigenvalues and behavior easier.

Note: in Python vectors are indexed from <code>0</code>, not <code>1</code> so Python indices will be one smaller than formal indices we discuss in the mathematical sections.



```python
import numpy as np
import sympy

```


```python
p = sympy.symbols("p", positive = True, real = True)
a, h, j, w, n = sympy.symbols("a h j w n", positive = True, real = True, integer=True)

# eigenvalues: h numbered from 1 through n
def l(h):
    return (
        sympy.Integer(2) * sympy.sqrt(p * (sympy.Integer(1) - p))
        * sympy.cos(h * sympy.pi / (n + sympy.Integer(1)))
    )


# eigenvectors: h, j numbered from 1 through n
def x(h, j):
    return (
        ((sympy.Integer(1) - p)/p)**(j / sympy.Integer(2))
        * sympy.sin(h * j * sympy.pi / (n + sympy.Integer(1)))
    )

```


```python
# define example
p_example = 2/3
n_example = 5

```


```python
# confirm meet conditions
assert isinstance(p_example, float) and (p_example >= 1/2) and (p_example < 1)
assert isinstance(n_example, int) and (n_example >= 2) and (n_example % 2 != 0)

```


```python
# show eigenvalues
eigen_values = [
    float(l(h_i).subs({p: p_example, n: n_example}))
    for h_i in range(1, n_example + 1)]
assert len(list(eigen_values)) == len(set(eigen_values))

eigen_values

```




    [0.8164965809277261,
     0.47140452079103173,
     0.0,
     -0.47140452079103173,
     -0.8164965809277261]




```python
# show eigenvectors (as columns)
eigen_vector_list = [
    np.array([float(x(h_i, j_i).subs({p: p_example, n: n_example})) 
              for j_i in range(1, n_example + 1)])
    for h_i in range(1, n_example + 1)
    ]
# note: not a symmetric matrix so eigenvectors not orthogonal
# also note unit norm in this formulation
eigen_vectors = np.transpose(np.array(eigen_vector_list))  # write as columns

eigen_vectors

```




    array([[ 0.35355339,  0.61237244,  0.70710678,  0.61237244,  0.35355339],
           [ 0.4330127 ,  0.4330127 ,  0.        , -0.4330127 , -0.4330127 ],
           [ 0.35355339,  0.        , -0.35355339,  0.        ,  0.35355339],
           [ 0.21650635, -0.21650635,  0.        ,  0.21650635, -0.21650635],
           [ 0.08838835, -0.15309311,  0.1767767 , -0.15309311,  0.08838835]])



We have to take care. The above eigenvectors are not norm-1, and they are not orthogonal as our matrix was not symmetric.



```python
# show structure of eigenvectors
np.matmul(np.transpose(eigen_vectors), eigen_vectors)

```




    array([[0.4921875 , 0.3435997 , 0.140625  , 0.0623497 , 0.0234375 ],
           [0.3435997 , 0.6328125 , 0.40594941, 0.1640625 , 0.0623497 ],
           [0.140625  , 0.40594941, 0.65625   , 0.40594941, 0.140625  ],
           [0.0623497 , 0.1640625 , 0.40594941, 0.6328125 , 0.3435997 ],
           [0.0234375 , 0.0623497 , 0.140625  , 0.3435997 , 0.4921875 ]])



We can confirm these are (up to proportionality) the eigenvectors corresponding to the claimed eigenvalues. The proof technique uses [trigonometric identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities#Angle_sum_and_difference_identities). The idea is: the proposed eigenvectors and eigenvalues have <code>sin()</code> and <code>cos()</code> terms laid out in a regular spacing spacing. Then, when we expand out the matrix operating on one of the proposed eigenvectors this produces relations such as <code>sin(a + b) = sin(a) cos(b) + cos(a) sin(b)</code> that cancel things out. This is one of those "mechanically confirm an amazing guess" situations, so let's move on to checking.

Let's look first at the Toeplitz matrix for our specific numeric example.



```python
# example Toeplitz operator
T_example = np.zeros((n_example, n_example), dtype=float)
for i in range(n_example-1):
    T_example[i, i+1] = p_example
    T_example[i+1, i] = 1 - p_example

T_example

```




    array([[0.        , 0.66666667, 0.        , 0.        , 0.        ],
           [0.33333333, 0.        , 0.66666667, 0.        , 0.        ],
           [0.        , 0.33333333, 0.        , 0.66666667, 0.        ],
           [0.        , 0.        , 0.33333333, 0.        , 0.66666667],
           [0.        , 0.        , 0.        , 0.33333333, 0.        ]])




```python
# confirm eigenvectors
for i in range(0, n_example):
    matrix_result = np.matmul(T_example, eigen_vectors[:, i])
    scalar_result = eigen_values[i] * eigen_vectors[:, i]
    assert np.max(np.abs(scalar_result - matrix_result)) < 1e-10

```

Now let's look at the general case using algebra.

In general we need to check the recurrences encoded in the matrix:

  * <code>p * x(h, 2) = l(h) * x(h, 1)</code> (left boundary condition)
  * <code>(1-p) * x(h, n-1) = l(h) * x(h, n)</code> (right boundary condition)
  * <code>(1-p) * x(h, a-1) + p * x(h, a+1) = l(h) * x(h, a)</code> for <code>1 &lt; a &lt; n</code> (general interior condition).

The left-hand sides are how the linear operator <code>T</code> evolves forward our claimed eigenvector <code>x(h,)</code>, and the right hand side is how the claimed eigenvalue <code>l(h)</code> evolves forward <code>x(h,)</code>. For correct eigenvectors and eigenvalues, the two ways of stepping forward are identical (by definition). We are confirming these equations hold for our *proposed* eigenvectors and eigenvalues.

This is a bit of an algebra nightmare, but can be machine checked.


#### Confirming <code>p * x(h, 2) = l(h) * x(h, 1)</code>.

Let's take a look at <code>p * x(h, 2) - l(h) * x(h, 1)</code>.



```python
expr = p * x(h, 2) - l(h) * x(h, 1)

expr

```




$\displaystyle - 2 \cdot \left(1 - p\right) \sin{\left(\frac{\pi h}{n + 1} \right)} \cos{\left(\frac{\pi h}{n + 1} \right)} + \left(1 - p\right) \sin{\left(\frac{2 \pi h}{n + 1} \right)}$



We can confirm this is uniformly zero.



```python
expr = expr.simplify().radsimp()
assert expr == 0

expr

```




$\displaystyle 0$



#### Confirming <code>(1-p) * x(h, n-1) = l(h) * x(h, n)</code>. 

Let's look at <code>(1-p) * x(h, n-1) - l(h) * x(h, n)</code>.



```python
expr = (1-p) * x(h, n-1) - l(h) * x(h, n)

expr

```




$\displaystyle - 2 \sqrt{p} \left(\frac{1 - p}{p}\right)^{\frac{n}{2}} \sqrt{1 - p} \sin{\left(\frac{\pi h n}{n + 1} \right)} \cos{\left(\frac{\pi h}{n + 1} \right)} + \left(\frac{1 - p}{p}\right)^{\frac{n}{2} - \frac{1}{2}} \cdot \left(1 - p\right) \sin{\left(\frac{\pi h \left(n - 1\right)}{n + 1} \right)}$



This can be confirmed to be zero.



```python
expr = expr.subs({n: 2*w - 1})
expr = expr.simplify().radsimp()
assert expr == 0

expr

```




$\displaystyle 0$



#### Confirming <code>(1-p) * x(h, a-1) + p * x(h, a+1) = l(h) * x(h, a)</code>



```python
expr = ((1-p) * x(h, a-1) + p * x(h, a+1)) - l(h) * x(h, a)

expr

```




$\displaystyle - 2 \sqrt{p} \left(\frac{1 - p}{p}\right)^{\frac{a}{2}} \sqrt{1 - p} \sin{\left(\frac{\pi a h}{n + 1} \right)} \cos{\left(\frac{\pi h}{n + 1} \right)} + p \left(\frac{1 - p}{p}\right)^{\frac{a}{2} + \frac{1}{2}} \sin{\left(\frac{\pi h \left(a + 1\right)}{n + 1} \right)} + \left(\frac{1 - p}{p}\right)^{\frac{a}{2} - \frac{1}{2}} \cdot \left(1 - p\right) \sin{\left(\frac{\pi h \left(a - 1\right)}{n + 1} \right)}$




```python
check = expr.simplify()

assert check==0
check

```




$\displaystyle 0$



And that confirms our last claim.

We have delegated some ugly work to the sympy symbolic algebra system.


### Appendix: Confirming the start properties


For odd integer <code>n</code> define:

<pre>
  <code>s = c * x<sub>1</sub></code>, where <code>c = (p/(1-p))<sup>w/2</sup></code>
</pre>

We must show:

  * <code>s &ge; 0</code>
  * <code>s<sub>w</sub> &ge; 1</code>

Recall: 
<pre>
<code>
   x<sub>1,j</sub> = ((1-p)/p)<sup>j/2</sup> sin(j &pi; / k),  j = 1...n
</code>
</pre>


#### Confirming <code>s &ge; 0</code>

This reduces to a matter of checking if <code>sin(j &pi; / k) &ge; 0</code> for <code>j = 1 ... n = k-1</code>, which is in fact true.



#### Confirming <code>s<sub>w</sub> &ge; 1</code>

This reduces to a matter of checking if <code>sin(w &pi; / k) &ge; 1</code>.  As <code>sin(w &pi; / k) = sin(pi/2) = 1</code>, this is confirmed.

Note: for a larger <code>c<sup>'</sup></code> such as <code>c<sup>'</sup> = (p/(1-p))<sup>n/2</sup> / sin(&pi;/k) ~ (p/(1-p))<sup>n/2</sup> k / &pi;</code> we would have <code>s<sup>'</sup> = c<sup>'</sup> x<sub>1</sub> &ge; 1</code>, which would bound all possible starting distributions simultaneously.

