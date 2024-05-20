# Picking Vectors to Pack

<br/>John Mount
<br/>[Win-Vector LLC](https://www.win-vector.com)
<br/>5-23-2023

## Introduction

[Béla Bollobás *The Art of Mathematics*, Cambridge 2006](https://www.amazon.com/Art-Mathematics-Coffee-Time-Memphis/dp/0521693950/) has as problem 156: "Permutations of Vectors: Stienitz's Theorem."

This theorem states:

> Let <code>x<sub>1</sub></code>, ... <code>x<sub>n</sub></code> be vectors of norm at most <code>1</code> in a <code>d</code>-dimensional normed space such that <code>x<sub>1</sub> + ... + x<sub>n</sub> = 0</code>. Then there is a permutation <code>&#960; &#8712; S<sub>n</sub></code> such that <code>||x<sub>&#960;(1)</sub> + ... + x<sub>&#960;(k)</sub>|| &le; d</code> for every <code>k</code>.

The content of this is: if a sum if small departures ends at the origin, then we can re-order the sum so *all* partial sums are in a small ball.

For example, if we have <code>d=1</code>, <code>x<sub>1</sub>, ... x<sub>10</sub> = 1</code>, and <code>x<sub>11</sub>, ... x<sub>20</sub> = -1</code> we see <code>x<sub>1</sub> + ... + x<sub>10</sub> = 10</code> (which is big!), but the theorem states there is a re-ordering so that all the partial sums have norm no more than <code>1</code>.

Note, Bollobás states original proof of the theorem only established the weaker result <code>&le; 2 d</code>, and many papers gave even worse bounds (many exponential in the dimension!). Bollobás' presentation is derived from [Grinberg, Victor & Sevastyanov, Sergey. (1980) "Value of the Steinitz constant. Functional Analysis and Its Applications" - FUNCT ANAL APPL-ENGL TR. 14. 125-126. 10.1007/BF01086559](ValueoftheSteinitzconstantFunctionalanalysisanditsapplications1421980125-126.pdf
). My reading of the note is: the proof applies to all norms as long as the norm used to evaluate the vectors and the sum are the same norm. Essentially only scaling and the triangle inequality are central to the argument.

## An Example

In this note I'll give a very simple example where the sum has an asymptotic (or large <code>d</code>) growth rate of <code>sqrt(d / 5)</code> for the Euclidian norm. This shows there are vector sets where the sums must grow as a function of the dimension, no matter what the ordering. I.e., establishing there is in fact something to prove. Obviously this bound isn't tight, but it is picked for ease of calculation and explanation. Grinberg and Sevastyanov knock this example off in one line, but I feel it pays to slow down the exposition.

For our example we will take <code>d</code> even and <code>n = 2 * d</code>. We will define our vectors <code>x<sub>i</sub></code> as follows.

For <code>i = 1, ..., n/2</code> we define "type a" <code>x<sub>i, j</sub></code> as:

  * <code>1</code> if <code>j = i</code>
  * <code>0</code> otherwise.

For <code>i = n/2 + 1, ..., n</code> we define "type b" <code>x<sub>i, j</sub></code> as:

  * <code>-1 / d</code>.

It is easy to check these are norm no more than <code>1</code> vectors that sum to zero. We will also confirm a larger intermediate sum under any permutation of the summation order.

First let's import our packages.



```python
import sympy

```

Now define <code>d</code> and <code>n</code> as variables or symbols.



```python
d = sympy.var("d", positive=True)
n = 2 * d

```

We are going to examine all partial sums involving <code>n/2</code> of our <code>n</code> possible vectors.

Let <code>n<sub>a</sub></code> denote how many terms in our permutation are taken from the "type a" vectors, and <code>n<sub>b</sub></code> how many terms in our permutation are taken from "type b" vectors. For our example we have <code>n / 2 = n<sub>a</sub> + n<sub>b</sub></code>



```python
n_a = sympy.var("n_a")

```

Then the number of type b vectors in our sum is <code>n<sub>b</sub> := n/2 - n<sub>a</sub></code>.



```python
n_b = n / 2 - n_a

```

This example is designed so that the norm of one of our intermediate sums depends *only* on how many type a and type b vectors are present, and not on which ones.

The squared *Euclidian* norm of our sum in terms of <code>n<sub>a</sub></code> and <code>n<sub>b</sub></code> can be seen to be the following.



```python
normsq = (
    (n_a) *  (1 - n_b / n)**2  # coordinates with n_a effect
    + (d - n_a) * (- n_b / n)**2  # coordinates without n_a effect
)

```

This expands to the following.



```python
normsq = normsq.expand().together()

```


```python
normsq

```




$\displaystyle \frac{d^{2} - 2 d n_{a} + 5 n_{a}^{2}}{4 d}$



We expect the extreme values of this norm squared to occur at either the <code>n<sub>a</sub></code> boundaries (<code>0</code>, and <code>n/2</code>), or at some point where the derivative with respect to <code>n<sub>a</sub></code> is zero. Let's inspect all of those.



```python
deriv = sympy.diff(normsq, n_a)

```


```python
deriv

```




$\displaystyle \frac{- 2 d + 10 n_{a}}{4 d}$




```python
soln = sympy.solve(deriv, n_a)
assert len(soln) == 1
soln = soln[0]
soln

```




$\displaystyle \frac{d}{5}$




```python
[normsq.subs({n_a: v}) for v in [0, soln, n/2]]

```




    [d/4, d/5, d]



The minimum length <code>n/2</code> partial sum norm is at least the *minimum* of these three options, which in this case has a squared-norm of <code>d/5</code>, or a norm of <code>sqrt(d/5)</code>.


## The Correct Asymptotic Behavior

We have shown a sequence with a partial sum (for large <code>d</code>) at least <code>sqrt(d/5)</code>, as claimed.

Obviously, there is a large gap between <code>sqrt(d/5)</code> and <code>d</code>. However, it is known the correct bound for Euclidian norms is on the order of <code>sqrt(d)</code>: [Wojciech Banaszczyk, "A Beck-Fiala-type Theorem for Euclidean Norms", Europ. I.Combinatorics (1990) 11, pp. 497-500](82161243.pdf) as stronger results are possible when specializing to the Euclidian norm.

The above concerns and theory live on in many fields including [discrepancy theory](https://en.wikipedia.org/wiki/Discrepancy_theory).


## A Classic Signed Sum

A related, though less detailed, warm up problem is: 

Let <code>x<sub>1</sub></code>, ... <code>x<sub>n</sub></code> be vectors of Euclidian norm at most <code>1</code> in a <code>d</code>-dimensional space. Then there are signs <code>s &#8712; {-1, +1}<sup>n</sup></code> such that <code>||s<sub>1</sub> * x<sub>1</sub> + ... + s<sub>n</sub> * x<sub>n</sub>|| &le; sqrt(d)</code>.

Note this bound is independent of <code>n</code>. It is also tight if we take <code>x<sub>i</sub></code> as the <code>i</code>th orthogonal unit vector for <code>i = 1 ... d</code>.

Finding an optimal assignment of signs can be hard, as this is the the carpenter’s ruler folding problem, which is known to be NP-hard ([ref](https://www.msri.org/people/staff/levy/files/Book42/11cali.pdf)).

We can show this in two parts: a bound that depends on a the sum-length, and a method to eliminate most of the sum.

### The Sum-Length Dependent Bound

We first establish the following weaker result.

Let <code>x<sub>1</sub></code>, ... <code>x<sub>n</sub></code> be vectors of Euclidian norm at most <code>1</code> in a <code>d</code>-dimensional space. Then there are signs <code>s &#8712; {-1, +1}<sup>n</sup></code> such that <code>||s<sub>1</sub> * x<sub>1</sub> + ... + s<sub>n</sub> * x<sub>n</sub>|| &le; sqrt(n)</code>.

Notice this time the bound depends on the number of terms in the sum.  The above result can be obtained by observing the following.

<code>
<pre>
|| s<sub>1</sub> x<sub>1</sub> + s<sub>2</sub> x<sub>2</sub>  + ... + s<sub>n</sub> x<sub>n</sub> ||<sup>2</sup>
 = || x<sub>1</sub> ||<sup>2</sup> + || s<sub>2</sub> x<sub>2</sub>  + ... + s<sub>n</sub> x<sub>n</sub> ||<sup>2</sup> + s<sub>1</sub> 2 < x<sub>1</sub>,  s<sub>2</sub> x<sub>2</sub>  + ... + s<sub>n</sub> x<sub>n</sub>>
 &le; || x<sub>1</sub> ||<sup>2</sup> + || s<sub>2</sub> x<sub>2</sub>  + ... + s<sub>n</sub> x<sub>n</sub> ||<sup>2</sup>   # (for some s<sub>1</sub> in {-1, +1})
</pre>
</code>

Applying induction on the above gives us, for some choice of signs <code>s</code>:

<code>
<pre>
|| s<sub>1</sub> x<sub>1</sub> + s<sub>2</sub> x<sub>2</sub>  + ... + s<sub>n</sub> x<sub>n</sub> ||<sup>2</sup> 
  &le; || x<sub>1</sub> ||<sup>2</sup> + ... + || x<sub>n</sub> ||<sup>2</sup>
  &le; n
</pre>
</code>

### The Length Independent Bound

Consider the polytope given by:

<code>
<pre>
u<sub>1</sub> x<sub>1</sub> + ... + u<sub>n</sub> x<sub>n</sub> = 0
</pre>
</code>

where <code>-1 &le; u<sub>i</sub> &le; 1</code> for all <code>i</code>.

This is a bounded feasible linear program with <code>d</code> equality constraints and <code>n</code> variables (the <code>u<sub>i</sub></code>). Therefore there is a vertex solution where at least <code>n - d</code> of the inequality constraints are tight.  This lets us re-write the solution as the following.

<code>
<pre>
s<sub>1</sub> x<sub>1</sub> + ... + s<sub>n</sub> x<sub>n</sub> = sum<sub>j = 1 ... d</sub> s<sub>v(j)</sub> e<sub>v(j)</sub> x<sub>v(j)</sub>
</pre>
</code>

Where <code>s<sub>1</sub> &#8712; {-1, +1}</code> (most copied from <code>u<sub>i</code></code>s), <code>v(j)</code> is the vector of indices covering all <code>u<sub>i</code></code> not in <code>{-1, +1}</code>, and all <code>|e<sub>i</sub>| &lt; 1</code>.

By our earlier lemma we know <code>||sum<sub>j = 1 ... d</sub> s<sub>v(j)</sub> e<sub>v(j)</sub> x<sub>v(j)</sub>|| &le; sqrt(d)</code> for some choice of the <code>s<sub>v(j)</sub></code> in <code>{-1, +1}<sup>d</sup></code>. Therefore (by the above equality) we also have <code>||s<sub>1</sub> x<sub>1</sub> + ... + s<sub>n</sub> x<sub>n</sub>|| &le; sqrt(d)</code> (combining the <code>s<sub>i</sub></code> fixed by the <code>n-d</code> extremal <code>u<sub>i</sub></code> with the <code>d</code> more choices of sign in the "left over" sum), giving us the desired sum-length independent bound.


## Back to the Sum Prefix Theorem

Returning to the issue of bounding all partial <code>0/1</code> sums. The proof technique is similar to the last section.

The proof ideas are as follows.

  * Replace the norm-bound with an exact equality for a linear program over continuous variables.
  * Pick an extremal solution, and use it to identify the next term to place in the sum.

Frankly, one doesn't really understand a proof until one attempts to write it back out. That is what I am doing, for myself, here. To have understood this proof the reader would likely have to write it out once again.

We want to show:

> Let <code>x<sub>1</sub></code>, ... <code>x<sub>n</sub></code> be vectors of norm at most <code>1</code> in a <code>d</code>-dimensional normed space such that <code>x<sub>1</sub> + ... + x<sub>n</sub> = 0</code>. Then there is a permutation <code>&#960; &#8712; S<sub>n</sub></code> such that <code>||x<sub>&#960;(1)</sub> + ... + x<sub>&#960;(k)</sub>|| &le; d</code> for every <code>k</code>.

There is nothing to check if <code>k &le; d</code> (as these cases follow from the triangle inequality) or <code>k = n</code> (as this sum is assumed to be zero). What we will do is prove a stronger theorem for the intermediate cases.

For <code>x<sub>1</sub> ... x<sub>n</sub></code> <code>d</code>-dimensional vectors of norm no more than <code>1</code>. We do not assume anything about the sum of the <code>x<sub>i</sub></code>. Let <code>x = sum<sub>i = 1...n</sub> x<sub>i</sub> / n</code>. 

We will show the stronger result, that for all <code>k</code> with <code>d &lt; k &le; n</code>: <code>||sum<sub>i=1,...,k</sub> x<sub>&#960;(i)</sub> - (k-d) x|| &le; d</code>. This is enough to establish the original claim.

<code>A[k]</code> will be a constructed subset of the integers <code>{1...n}</code> such that <code>|A[k]| = k</code>. For <code>k &ge; d</code>, <code>&lambda;<sub>k</sub></code> will be a constructed <code>n</code>-vector such that <code>&lambda;<sub>k,i</sub> = 0</code> if <code>i not in A[k]</code>, <code>0 &le; &lambda;<sub>k,i</sub> &le; 1</code>, and

<code>
<pre>
sum<sub>i &#8712; A[k]</sub> &lambda;<sub>k,i</sub> = k - d          # our scalar or total constraint
sum<sub>i &#8712; A[k]</sub> &lambda;<sub>k,i</sub> x<sub>i</sub> = (k - d) x.  # our vector constraint
</pre>
</code>


For <code>k = n</code> we have <code>A[n] = {1,...,n}</code> and the choice of <code>&lambda;<sub>n</sub> = (n - d)/n</code> works.

We will try to establish this for more <code>k</code>.

For <code>k</code> such that <code>n &gt; k &gt; d</code> we induct down, assuming we have already solved for <code>A[k+1]</code> and <code>&lambda;<sub>k+1</sub></code>.

We solve the following to find <code>A[k]</code> and <code>&lambda;<sub>k</sub></code> as follows.

<code>
<pre>
u<sub>i</sub> = 0 for i where i not in A[k+1]  # (consider these <em>not</em> to be actual variables)
0 &le; u<sub>i</sub> &le; 1 where i in A[k+1]        # (consider these to be the actual variables)
sum<sub>i &#8712; A[k+1]</sub> u<sub>i</sub> = k - d
sum<sub>i &#8712; A[k+1]</sub> u<sub>i</sub> x<sub>i</sub> = (k - d) x.
</pre>
</code>

Call this <code>program(k)</code>. 

<code>program(k)</code> is feasible as <code>&lambda;<sub>k+1</sub>(k-d)/(k+1-d)</code> gives us an initial feasible solution. This is a feasible linear program over <code>k+1</code> variables with <code>d+1</code> equality constraints. So there is an extremal solution least <code>(k+1) - (d+1)</code> of them hit their <code>{0,1}</code> inequality constraints. If all <code>k-d</code> of them were <code>1</code>, the additional fractional coordinates would violate the sum bound. So there is a solution <code>&lambda;<sub>k,i</code></code> that is zero for some <code>i</code> in <code>A[k+1]</code>. Pick <code>A[k] = A[k+1] - {i}</code> where <code>&lambda;<sub>k,i</sub> = 0</code> and <code>i in A[k+1]</code>.

For <code>k = d</code> we can take <code>A[k] = A[k+1] - {i}</code> where <code>i</code> is an arbitrary <code>i in A[k+1]</code>, and <code>&lambda;<sub>k</sub> = 0</code>.

For <code>k = d-1, ..., 0</code> define <code>A[k] = A[k+1] - {i}</code> where <code>i</code> is an arbitrary <code>i in A[k+1]</code>.

Now consider the sequence <code>&#960;(i)</code> picked such that:

  * <code>&#960;(k) = A[k] - A[k-1]</code> for <code>k = 1,...,n</code>

The claim is: <code>&#960;()</code> is a permutation with the desired small partial sums. 

For <code>k</code> such that <code>d &le; k &le; n</code> we have the following (as mentioned, we don't need this result for other <code>k</code>):

<code>
<pre>
||sum<sub>i=1...k</sub> x<sub>&#960;(i)</sub> - (k-d) x||                   # what we are checking
= ||sum<sub>i in A[k]</sub> x<sub>i</sub> - (k-d) x||                  # definition of &#960;(i)
= ||sum<sub>i in A[k]</sub> x<sub>i</sub> - sum<sub>i in A[k]</sub> &lambda;<sub>k,i</sub> x<sub>i</sub>||       # our vector equality!
= ||sum<sub>i in A[k]</sub> (1 - &lambda;<sub>k,i</sub>) x<sub>i</sub>||                  # collecting terms
&le; sum<sub>i in A[k]</sub> (1 - &lambda;<sub>k,i</sub>)                        # triangle inequality
= sum<sub>i in A[k]</sub> 1 - sum<sub>i in A[k]</sub> &lambda;<sub>k,i</sub>               # expanding terms
= k - (k - d)                                  # our scalar equality!!!
= d                                            # that which was to be shown
</pre>
</code>

The cleverness of the proof is picking what equalities to replace the norm constraint with.


## Conclusion

[Once again](https://win-vector.com/2015/05/06/proof-style-in-the-erdos-ko-rado-theorem/) Bollobás' work brings great vacation joy. Working though some of the argumentation can sharpen one's own approach to proofs and calculation.

