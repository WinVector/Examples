# The Drunkard's Walk In Detail

## Introduction

I would like to spend some time on a simple random walk on the non-negative integers <code>0 ... k</code> called "the drunkard's walk"  A good amount of probabilistic intuition can be had by studying the this system. This note is a quick way to derive some of the observations used in ["A Slightly Unfair Game"](https://win-vector.com/2023/10/30/a-slightly-unfair-game/) and to set up some of the machinery used in Wald's "Sequential Analysis" (a relative of A/B testing).

This differs from many treatments of Markov chains in that we are analyzing an "absorbing chain" (instead of a "regular" or "ergodic" one, see Kemeny, Snell, *Finite Markov Chains*, 2nd Edition, 1976, Springer Verlag), and we are using bespoke recurrence arguments instead of the usual move to linear algebra. In fact I would like to prove a standard result that I think many will find unlikely or surprising: conditioning on where this Markov chain eventually will stop greatly changes the observed transition probabilities, yet does preserve the Markov property of independence from the past.


## The drunkard's walk

Pick an integer <code>k &gt; 0</code>. The states of our random process will be the integers <code>0</code> through <code>k</code>. The integers <code>0</code> and <code>k</code> are both "stop conditions" called "stop zero" and "stop non-zero". For an integer <code>i</code> strictly larger than <code>0</code> and strictly less than <code>k</code>, our random process is: pick the next integer to be either <code>i+1</code> (called moving up or moving right) or <code>i-1</code> (called moving down or moving left) with equal "50/50" probability. We stop the process when the state <code>i</code> is either <code>0</code> or <code>k</code>. This is called a "random walk" and is often known as "the drunkard's walk". Some variations have "stay probabilities" prior to stopping, but we will not need these here.

An example of this system "<code>P<sub>k</sub>[]</code> system" for <code>k = 4</code> is given below.

<img src="https://win-vector.com/wp-content/uploads/2023/11/chain50_50.png">

A lot can be directly seen for this walk. First we show the following.

<ol>
  <li>The drunkard's walk has the Markov property (and what that property is).</li>
  <li>The probability of a walk started in state-<code>i</code> "stopping non-zero" (first reaching <code>k</code>, with no prior visits to <code>0</code>) is <code>i/k</code>.</li>
  <li>The expected time of a walk started in state-<code>i</code> to hit either of the stopping conditions (reaching <code>0</code> or <code>k</code> for the first time) is <code>i * (k - i)</code>.</li>
</ol>


## The Markov property

The drunkard's walk is a famous example of a Markov chain, or a sequential random process with the Markov property.

The Markov property is when the relative probability of future states of a system depends *only* on the current state, and not on older details of history or how long a process has been running. The Markov property is *exactly* saying that we can make statements such as the "the probability of moving from state <code>2</code> to state <code>3</code> is <code>1/2</code>" *without* having to refer to the entire history of the random process prior to the state in question.


## Deriving the probability of "stopping non-zero"

Let <code>prob_pos<sub>k</sub>(i)</code> denote the probability that the drunkard's walk started at integer <code>i</code> (<code>0 &le; i &le; k</code>) stops at <code>k</code> before ever visiting <code>0</code>.

For any <code>i</code> with <code>0 &lt; i &lt; k</code> we can expand <code>prob_pos<sub>k</sub>(i)</code> by one walk step to get: 

<pre>
<code>
   prob_pos<sub>k</sub>(i) = (1/2) prob_pos<sub>k</sub>(i-1) + (1/2) prob_pos<sub>k</sub>(i+1)
</code>
</pre>

It is then a matter of algebra to check that <code>prob_pos<sub>k</sub>(i) = i/k</code> obeys this recurrence, and has the desired values for the boundary <code>i = 0, k</code>.

As a warm up we algebraically confirm the claim.



```python
import sympy
import numpy as np
rng = np.random.default_rng(2023)

```


```python
i, k = sympy.symbols("i k")

check = sympy.expand(
    ((1/2) * (i-1)/k + (1/2) * (i+1)/k) 
    - i/k
)

assert check == 0
print(check)

```

    0


## Deriving the probability of "stopping zero" for <code>p &ne; 1/2</code>

Let <code>prob_zero<sub>p,k</sub>(i)</code> denote the probability that an unfair drunkard's walk started at integer <code>i</code> (<code>0 &le; i &le; k</code>) stops at <code>0</code> before ever visiting <code>k</code> when the probability of increase state is <code>p</code> and decrease state is <code>1-p</code>.

For <code>k &gt; 1</code> can expand <code>prob_zero<sub>p,k</sub>(1)</code> by one walk step to get: 

<pre>
<code>
   prob_zero<sub>p,k</sub>(1) = 
     (1-p)   # visit zero in 1 step
     + p prob_zero<sub>p,k-1</sub>(1) prob_zero<sub>p,k</sub>(1)   # move up, return, and try again
</code>
</pre>

For <code>0 &lt; p &lt; 1</code> with <code>p &ne; 1/2</code> it is then a matter of algebra to check that  <code>prob_zero<sub>p,k</sub>(1) = ((p/(1-p))<sup>k-1</sup> – 1) / ((p/(1-p))<sup>k</sup> – 1)</code> obeys this recurrence and has boundary condition <code>prob_zero<sub>p,1</sub>(1) = 0</code>

We confirm the claim.


```python
i, k, p = sympy.symbols("i k p")

def f(k):
    return ((p/(1-p))**(k-1) - 1) / ((p/(1-p))**k - 1)

num, den = sympy.fraction((f(k) - (
    (1-p)
    + p * f(k-1) * f(k)
)).together())

print("numerator: " + str(num))
print("denominator: " + str(den))


```

    numerator: p*((p/(1 - p))**k - 1) - p*((p/(1 - p))**(k - 2) - 1) - (p/(1 - p))**k + (p/(1 - p))**(k - 1)
    denominator: (p/(1 - p))**k - 1



```python
# show numerator simplifies to zero (divide out common term)
check = (num / (p/(1-p))**(k-1)).expand().simplify()

assert check == 0
print(check)
```

    0



```python
# check boundary condition
assert f(1) == 0
```

Of special interest is the <code>p = 2/3</code> case, as it satisfies the limiting recurrence for <code>k = &#x221E;</code> with a "hit zero" probability of <code>1/2</code>

<pre>
<code>
   prob_zero<sub>2/3,&#x221E;</sub>(1) = 
     (1 - 2/3)
     + 2/3 prob_zero<sub>2/3,&#x221E;</sub>(1) prob_zero<sub>2/3,&#x221E;</sub>(1)
</code>
</pre>


```python
z = sympy.symbols('z')

soln = sympy.solve(
    z - ((1 - 2/3) + (2/3) * z * z),
    z
)

assert np.sum([zi == 1/2 for zi in soln]) > 0
soln
```




    [0.500000000000000, 1.00000000000000]



## Deriving the "expected time to stop"

Let <code>e_time<sub>k</sub>(i)</code> denote the expected number of steps the (fair) drunkard's walk started at integer <code>i</code> (<code>0 &le; i &le; k</code>) takes to reach *either* of <code>0</code> or <code>k</code> for the first time. We are not yet specifying *which one* is first reached.

For any <code>i</code> with <code>0 &lt; i &lt; k</code> we can expand <code>e_time<sub>k</sub>(i)</code> by one walk step to get: <code>e_time<sub>k</sub>(i) = 1 + (1/2) e_time<sub>k</sub>(i-1) + (1/2) e_time<sub>k</sub>(i+1)</code>. It is again, a matter of  algebra to check that <code>e_time<sub>k</sub>(i) = i * (k-i)</code> obeys this recurrence, and has the desired values on the boundary.

Let's confirm this claim.



```python
i, k = sympy.symbols("i k")

check = sympy.expand(
    (1 + (1/2) * (i-1) * (k-(i-1)) + (1/2) * (i+1) * (k-(i+1)))
    - i * (k-i)
)

assert check == 0
print(check)

```

    0


The above directly gives us the common "expected time to move distance <code>d</code> is around <code>d**2</code> steps" observation, without the usual appeal to linearity of expectation applied to independent variances.


## Basic probability notation

Define a legal or valid trajectory as a sequence of states <code>s = s<sub>0</sub></code>, <code>s<sub>1</sub></code>, ... . Where:

  * All the <code>s<sub>j</sub></code> are integers in the range <code>0</code> through <code>k</code>.
  * If <code>s<sub>j</sub></code> isn't <code>0</code> or <code>k</code>, then <code>|s<sub>j</sub> - s<sub>j+1</sub>| = 1</code> (the process has not yet stopped)
  * If <code>s<sub>j</sub></code> is <code>0</code> or <code>k</code>, then <code>s<sub>j+1</sub> = s<sub>j</sub></code> (the chain has "stopped").

Let <code>S<sub>k</sub>(i)</code> denote the set of all possible sequences <code>s</code> of integers obeying the above rules and where the first state <code>s<sub>1</sub> = i</code>.

In an appendix we define the probability measure <code>P<sub>k,i</sub>[s]</code> on <code>S<sub>k</sub>(i)</code> that tells us the probability of observing a given sequence <code>s</code> starting from state <code>i</code>. We have the extra parameter (<code>i</code>) in our notation to avoid having to assume an initial starting distribution.

Throughout this note we use <code>P[expression]</code> as shorthand for <code>sum<sub>s: expression(s)</sub> P[s]</code>. We also use <code>P[expression | condition]</code> as shorthand for <code>P[condition and expression] / P[condition]</code> (when <code>P[condition] &gt; 0</code>).


## Conditioning on the outcome

An interesting (and maybe even surprising) fact is: the following systems also have the Markov property and are therefore themselves Markov chains:

  * <code>S<sub>&lArr;,k</sub>(i)</code> defined as all the <code>s</code> in <code>S<sub>k</sub>(i)</code> that "eventually stopped at <code>0</code>", with the probability measure <code>P<sub>&lArr;,k,i</sub>[]</code> induced by restricting to <code>S<sub>&lArr;,k</sub>(i)</code>.
  * <code>S<sub>&rArr;,k</sub>(i)</code> defined as all the <code>s</code> in <code>S<sub>k</sub>(i)</code> that "eventually stopped at <code>k</code>", with the probability measure <code>P<sub>&rArr;,k,i</sub>[]</code> induced by restricting to <code>S<sub>&rArr;,k</sub>(i)</code>.

We can in fact establish that <code>P<sub>&lArr;,k</sub>[]</code> (and similarly <code>P<sub>&rArr;,k</sub>[]</code>) has the Markov property. The argument is in an appendix.


## Empirical conditional probabilities

We can show that the observed transition probabilities for <code>P<sub>&rArr;,k</sub>[]</code> are very different than the <code>1/2</code>s seen for <code>P<sub>k</sub>[]</code>.

Let's set up some code to estimate these transition probabilities from simulation.



```python
# our example k

k = 4

```


```python
# observe the empirical transition probabilities for right absorbed systems
observed = dict()
for start_i in range(1, k):
    downs = 0
    ups = 0
    for rep in range(1000000):
        first_up = 0
        first_down = 0
        state_i = start_i
        # run until we hit the stopping conditions
        while (state_i > 0) and (state_i < k):
            coin_flip = rng.binomial(n=1, p=0.5, size=1)[0]
            if coin_flip > 0.5:
                if (first_up + first_down) == 0:
                    first_up = 1
                state_i = state_i + 1
            else:
                if (first_up + first_down) == 0:
                    first_down = 1
                state_i = state_i - 1
        # only count right-absorbed paths
        if state_i == k:
            downs = downs + first_down
            ups = ups + first_up
    observed[f"probability of seeing {start_i} to {start_i+1}"] = ups / (ups + downs) 

observed

```




    {'probability of seeing 1 to 2': 1.0,
     'probability of seeing 2 to 3': 0.7505207655904511,
     'probability of seeing 3 to 4': 0.6665507149026005}



## The conditional transition probabilities

It is a fact that the <code>P<sub>k,i</sub>[]</code> probability system is Markov on <code>S<sub>k</sub>(i)</code> (see appendix). Given this, we can write transition probabilities independent of history (for not yet stopped sequences, i.e. <code>i &ne; 0, k</code>):

  * <code>prob_up<sub>k</sub>(i) = P<sub>k,i</sub>[s<sub>2</sub> = i+1 | s<sub>1</sub> = i] = 1/2</code>
  * <code>prob_down<sub>k</sub>(i) = P<sub>k,i</sub>[s<sub>2</sub> = i-1 | s<sub>1</sub> = i] = 1/2</code> 

where <code>P<sub>k,i</sub>[]</code> is the probability measure from the <code>S<sub>k</sub>(i)</code> system.

In an appendix we show the <code>P<sub>&lArr;,k</sub>[]</code> and <code>P<sub>&rArr;,k</sub>[]</code> probability measures are indeed Markov. This then allows us to define the following symbols for their transition probabilities (independent of earlier history):

  * <code>prob_up<sub>&lArr;,k</sub>(i) = P<sub>&lArr;,k,i</sub>[s<sub>2</sub> = i+1 | s<sub>1</sub> = i]</code>
  * <code>prob_down<sub>&lArr;,k</sub>(i) = P<sub>&lArr;,k,i</sub>[s<sub>2</sub> = i-1 | s<sub>1</sub> = i]</code> 
  * <code>prob_up<sub>&rArr;,k</sub>(i) = P<sub>&rArr;,k,i</sub>[s<sub>2</sub> = i+1 | s<sub>1</sub> = i]</code>
  * <code>prob_down<sub>&rArr;,k</sub>(i) = P<sub>&rArr;,k,i</sub>[s<sub>2</sub> = i-1 | s<sub>1</sub> = i]</code>

Where <code>P<sub>&lArr;,k,i</sub>[]</code> is the probability measure from the <code>S<sub>&lArr;,k</sub>(i)</code> system and <code>P<sub>&rArr;,k,i</sub>[]</code> is the probability measure from the <code>S<sub>&rArr;,k</sub>(i)</code> system.

We can show for <code>0 &lt; i &lt; k</code>:

  * <code>prob_up<sub>&rArr;,k</sub>(i) = (i+1)/(2*i)</code>
  * <code>prob_down<sub>&rArr;,k</sub>(i) = 1 - prob_up<sub>&rArr;,k</sub>(i)</code>

(and similar for <code>prob_up<sub>&lArr;,k</sub>(i)</code> and <code>prob_down<sub>&lArr;,k</sub>(i)</code>)


The <code>P<sub>&rArr;,k</sub>[]</code> system for <code>k = 4</code> with the above transition probabilities is portrayed below.



<img src="https://win-vector.com/wp-content/uploads/2023/11/chain_k.png">


This means the sequences that eventually stop at <code>k</code> actually *look* like they are attracted in that direction! An example of this are Dr. Zumel's animations in [A Slightly Unfair Game](https://win-vector.com/2023/10/30/a-slightly-unfair-game/).


The <code>P<sub>&lArr;,k</sub>[]</code> system for <code>k = 4</code> is as follows.

<img src="https://win-vector.com/wp-content/uploads/2023/11/chain_0.png">


The 50/50 system is a mixture of these two systems, *with the mixture proportions varying by state label*.


## Comparing observation to theory

Let's check our claimed theoretical transition probabilities in <code>S<sub>&rArr;,k</sub>(i)</code> are in fact close to our empirical estimates.



```python
# show the theoretical up transitions in absorbed systems
prob_up_given_stop_k = lambda *, k, i: 0 if (i<=0) or (i>=k) else (i+1)/(2*i)
prob_down_given_stop_k = lambda *, k, i: 0 if (i<=1) or (i>=k) else 1 - prob_up_given_stop_k(i)
prob_up_given_stop_0 = lambda *, k, i: 0 if (i<=0) or (i>=k-1) else prob_down_given_stop_k(k-i)
prob_down_given_stop_0 = lambda *, k, i: 0 if (i<=0) or (i>=k) else prob_up_given_stop_k(k-i)

```


```python
theoretical = {f"probability of seeing {i} to {i+1}": prob_up_given_stop_k(k=k, i=i) for i in range(1, k)}

theoretical

```




    {'probability of seeing 1 to 2': 1.0,
     'probability of seeing 2 to 3': 0.75,
     'probability of seeing 3 to 4': 0.6666666666666666}




```python
# confirm measurement matches theory
assert set(theoretical.keys()) == set(observed.keys())
for key, v_theoretical in theoretical.items():
    v_observed = observed[key]
    assert np.abs(v_theoretical - v_observed) < 1e-3

```

## Conclusion

The point of this note is to get some familiarity with deep facts about a specific random walk, before delegating to the usual general analysis tools.

We have derived quite a few results for the "half up, half down" bounded drunkard's walk that stops at <code>0</code> or <code>k</code> (<code>k &gt; 0</code>):

  * The probability of stopping at <code>k</code> after starting at <code>i</code> is <code>prob_pos<sub>k</sub>(i) = i/k</code>.
  * The expected number of steps to stop after starting at <code>i</code> is <code>e_time<sub>k</sub>(i) = i * (k-i)</code>. In particular for a start state <code>i ~ k/2</code> this is  <code>k/2 * (k - k/2) = k<sup>2</sup> / 4</code> expected run time.
  * The random process of looking only at sequences that stop at <code>0</code> is in fact itself a Markov chain.
  * The random process of looking only at sequences that stop at <code>k</code> is in fact itself a Markov chain.
  * If we condition on the walk stopping at <code>k</code>, then the probability of "stepping up" from state <code>i</code> (observing a <code>i</code> to <code>i+1</code> transition on a sequence that has not yet stopped) is <code>prob_up<sub>&rArr;,k</sub>(i) = (i+1)/(2*i)</code>.

The above is a bit more detail than one usually tolerates in analyzing a Markov chain. Showing that conditioning on *where* the Markov chain stops preserves the Markov property is of interest. Also deriving the expected quadratic run time directly is quite nice.

Thank you to Dr. Nina Zumel for comments and for preparing the diagrams.


## Appendices


### Probability notation in detail

Let's replace our informal probability measure with a strict measure on infinite sequences. Without a pre-defined probability space and measure, we are essentially making up probability statements as we go (instead of being able to derive them from a fixed base).

A run trajectory is a sequence of states <code>s = s<sub>0</sub></code>, <code>s<sub>1</sub></code>, ... . Where:

  * All the <code>s<sub>j</sub></code> are integers in the range <code>0</code> through <code>k</code>.
  * If <code>s<sub>j</sub></code> isn't <code>0</code> or <code>k</code>, then <code>|s<sub>j</sub> - s<sub>j+1</sub>| = 1</code> (the process has not stopped)
  * If <code>s<sub>j</sub></code> is <code>0</code> or <code>k</code>, then <code>s<sub>j+1</sub> = s<sub>j</sub></code> (the chain has "stopped").

Let <code>S<sub>k</sub>(i)</code> denote the set of all possible sequences <code>s</code> of integers obeying the above rules where the first state <code>s<sub>1</sub> = i</code>. Define <code>n_transition(s)</code> as the number of <code>j &gt; 1</code> such that <code>v<sub>j-1</sub> &ne; v<sub>j</sub></code>.

Define the probability measure <code>P<sub>k,i</sub>[]</code> of <code>s</code> in <code>S<sub>k</sub>(i)</code> assigning:

  * <code>P<sub>k,i</sub>[s] = &perp;</code> if <code>s</code> not in <code>S<sub>k</sub>(i)</code> (invalid trajectories, *not* part of the probability space, "<code>&perp;</code>" called "bottom" and representing an invalid state).
  * <code>P<sub>k,i</sub>[s] = 1</code>, if <code>s<sub>1</sub> = 0, k</code>. Call such <code>s</code> "stopped."
  * <code>P<sub>k,i</sub>[s] = 0</code>, when <code>n_transition(s)</code> is not finite. Call such <code>s</code> "never stopped."
  * <code>P<sub>k,i</sub>[s] = 1/2<sup>n_transition(s)</code>, when <code>n_transition(s)</code> is finite. Call such <code>s</code> "stopped" or "eventually."

We have the extra parameter (<code>i</code>) in our notation to avoid having to assume an initial starting distribution.

On can check that the <code>P<sub>k,i</sub>[s] &ge; 0</code> for all <code>s</code> in <code>S<sub>k</sub>(i)</code> and <code>sum<sub>s in S<sub>k</sub>(i)</sub> P<sub>k,i</sub>[s] = 1</code>. This meets the definition of a probability measure, so we can apply known probability theorems such as Bayes' law. The never stopped sequences have probability measure zero (so can be ignored in probability arguments; this is amusing, as this subset is the uncountable subset of the sequences).

The above random process <code>P[]</code> has "the Markov property" on <code>S<sub>k</sub>()</code>: history becomes irrelevant. That is we claim:

<pre>
<code>
   P<sub>k,v<sub>1</sub></sub>[s<sub>j+1</sub> = v | s<sub>1</sub>=v<sub>1</sub>, ..., s<sub>j</sub>=v<sub>j</sub>] = P<sub>k,v<sub>j</sub></sub>[s<sub>j+1</sub> = v | s<sub>j</sub>=v<sub>j</sub>]
</code>
</pre>

*when* <code>s<sub>1</sub>=v<sub>1</sub>, ..., s<sub>j</sub>=v<sub>j</sub>, s<sub>j+1</sub> = v</code> is a valid prefix of an <code>s</code> in <code>S<sub>k</sub>(v<sub>1</sub>)</code>.

Throughout this note we use <code>P[expression]</code> as shorthand for <code>sum<sub>s: expression(s)</sub> P[s]</code>. We also use <code>P[expression | condition]</code> as shorthand for <code>P[condition and expression] / P[condition]</code> (when <code>P[condition] &gt; 0</code>). For example <code>P<sub>k,i</sub>[s<sub>j+1</sub> = v | s<sub>j</sub>=v<sub>j</sub>]</code> denotes <code>(sum<sub>s in S<sub>k</sub>(i): (s<sub>j</sub>=v<sub>j</sub>) and (s<sub>j+1</sub> = v)</sub> P<sub>k,i</sub>[s]) / (sum<sub>s in S<sub>k</sub>(i): s<sub>j</sub>=v<sub>j</sub></sub> P<sub>k,i</sub>[s])</code>.

We often use the Markov property in analysis as follows: we can always pretend we are at the first move in a sequence! For <code>0 &lt; i &lt; k</code> we have <code>P<sub>k,i</sub>[s<sub>j+1</sub> = v<sub>2</sub> | s<sub>j</sub> = v<sub>1</sub>] = P<sub>k,v<sub>1</sub></sub>[s<sub>2</sub> = v<sub>2</sub> | s<sub>1</sub> = v<sub>1</sub>]</code> (for <code>s</code> in <code>S<sub>k</sub>(i)</code>).


### Appendix: <code>P<sub>k</sub>[]</code> has the Markov property

We sketch a rough outline of an argument why <code>P<sub>k</sub>[]</code> over <code>S<sub>k</sub>()</code> have the Markov property. This is an ugly proof of standard fact.

The Markov property itself is statements of the form:

<pre>
<code>
   P[s<sub>j+1</sub>=v | s<sub>j</sub>=v<sub>j</sub>, s<sub>j-1</sub>=v<sub>j-1</sub>] = P[s<sub>j+1</sub>=v | s<sub>j</sub>=v<sub>j</sub>]
</code>
</pre>

(when <code>P[s<sub>j+1</sub>=v | s<sub>j</sub>=v<sub>j</sub>, s<sub>j-1</sub>=v<sub>j-1</sub>]</code> is non-zero). I.e.: earlier history becomes irrelevant in conditional probabilities.

Call <code>(s<sub>1</sub>, ..., s<sub>j</sub>)</code> "<code>A(s)</code>" and <code>(s<sub>j</sub>, ...)</code> "<code>B(s)</code>". We have <code>n_transition(s) = n_transition(A(s)) + n_transition(B(s))</code>. So we can factor <code>P[]</code> as:

<pre>
<code>
  P<sub>k,i</sub>[f(A(s)) g(B(s))] = P<sub>k,s<sub>1</sub></sub>[f(A(s))] P<sub>k,s<sub>j</sub></sub>[f(B(s))]
</code>
</pre>

(for <code>s</code> in <code>S<sub>k</sub>(i)</code>).

The above follows from the usual factoring of sums of the form <code>sum<sub>a in A, b in B</sub> f(a) g(b)</code> as <code>(sum<sub>a in A</sub> f(a))(sum<sub>b in B</sub> g(b))</code>.

As we have the system is Markov over our states, it is justified to define <code>prob_up<sub>k</sub>(i)</code> as the probability the next state is <code>i+1</code>, given the next state is <code>i</code>.


### Appendix: the derived measures

We define derived probability measures (for each <code>i</code>):

  * <code>S<sub>&lArr;,k</sub>(i)</code> defined as all the <code>s</code> in <code>S<sub>k</sub>(i)</code> that "eventually stopped at <code>0</code>".
  * <code>P<sub>&lArr;,k,i</sub>[]</code> as: <code>P<sub>&lArr;,k,i</sub>[s] = &perp; if s not in S<sub>&lArr;,k</sub>(i) else P<sub>k,i</sub>[s] / (sum<sub>z in S<sub>&lArr;,k</sub>(i)</sub> P<sub>k,i</sub>[z])</code>.
  * <code>S<sub>&rArr;,k</sub>(i)</code> defined as all the <code>s</code> in <code>S<sub>k</sub>(i)</code> that "eventually stopped at <code>k</code>".
  * <code>P<sub>&rArr;,k,i</sub>[]</code> as: <code>P<sub>&rArr;,k,i</sub>[s] = &perp; if s not in S<sub>&rArr;,k</sub>(i) else P<sub>k,i</sub>[s] / (sum<sub>z in S<sub>&rArr;,k</sub>(i)</sub> P<sub>k,i</sub>[z])</code>.


### Appendix: <code>P<sub>&lArr;,k</sub>[]</code> and <code>P<sub>&rArr;,k</sub>[]</code> have the Markov property

Here we establish the Markov property for our conditioned measures and compute the new transition probabilities. This uses standard probability facts (such as Bayes' law) and the Markov property of <code>P<sub>k</sub>[]</code> (a standard fact, also established in an earlier appendix).

We will assume <code>k &gt; 1</code> and <code>0 &lt; v<sub>j</sub> &lt; k</code> for <code>j = 1...u</code> to avoid trivial corner cases. To check if <code>P<sub>&rArr;,k,v<sub>1</sub></sub>[v<sub>u+1</sub> = 1+v<sub>u</sub> | s<sub>1</sub>=v<sub>1</sub>, ..., s<sub>u</sub>=v<sub>u</sub>]</code> is Markov we need to show it equals <code>f(v<sub>u</sub>)</code> for some function <code>f()</code> independent of all state except <code>v<sub>u</sub></code> and <code>v<sub>u+1</sub></code>.

We have:

<pre>
<code>
P<sub>&rArr;,k,v<sub>1</sub></sub>[v<sub>u+1</sub> = 1+v<sub>u</sub> | s<sub>1</sub>=v<sub>1</sub>, ..., s<sub>u</sub>=v<sub>u</sub>]
  = P<sub>k,v<sub>1</sub></sub>[v<sub>u+1</sub> = 1+v<sub>u</sub> | s<sub>1</sub>=v<sub>1</sub>, ..., s<sub>u</sub>=v<sub>u</sub>, s stops at k]
  = P<sub>k,v<sub>1</sub></sub>[s stops at k | s<sub>1</sub>=v<sub>1</sub>, ..., s<sub>u</sub>=v<sub>u</sub>, v<sub>u+1</sub> = 1+v<sub>u</sub>] 
    * P<sub>k,v<sub>1</sub></sub>[v<sub>u+1</sub> = 1+v<sub>u</sub> | s<sub>1</sub>=v<sub>1</sub>, ..., s<sub>u</sub>=v<sub>u</sub>]
    / P<sub>k,v<sub>1</sub></sub>[stops at k | s<sub>1</sub>=v<sub>1</sub>, ..., s<sub>u</sub>=v<sub>u</sub>]
  = P<sub>k,1+v<sub>u</sub></sub>[s stops at k | s<sub>1</sub> = 1+v<sub>u</sub>] 
    * P<sub>k,v<sub>u</sub></sub>[v<sub>u+1</sub> = 1+v<sub>u</sub> | s<sub>1</sub>=v<sub>u</sub>]
    / P<sub>k,v<sub>u</sub></sub>[stops at k | s<sub>1</sub>=v<sub>u</sub>]
</code>
</pre>

At this point we have established the transition probabilities are Markov with respect to the state, as we now have terms involving only the most recent state.

In the above:

  * The first line is definitional.
  * The second line is an application of Bayes' Law <code>P[A|B] = P[B|A] P[A] / P[B]</code>, with <code>A = "v<sub>u+1</sub> = 1+v<sub>u</sub>"</code> and <code>B = "s stops at k"</code>.
  * The third line is the known Markov property of <code>P[]</code>.

We can now justify defining <code>prob_up<sub>&rArr;,k</sub>(i)</code> as the probability the next state is <code>i+1</code>, given the next state is <code>i</code> and given chain eventually stops and <code>k</code>.

We have proved the relation:

<pre>
<code>
prob_up<sub>&rArr;,k</sub>(i)
  = prob_up<sub>k</sub>(i) 
      * P<sub>k,1+i</sub>[s stops at k | s<sub>1</sub> = 1+i] 
      / P<sub>k,i</sub>[stops at k | s<sub>1</sub> = i]
</code>
</pre>

This relates a quantity we want to know (<code>prob_up<sub>&rArr;,k</sub>(i)</code>) about the chain known to halt and <code>k</code> to only known facts about the unconstrained Markov chain. Roughly we can think of this as saying <code>prob_up<sub>&rArr;,k</sub>(i)</code> is read off as what fraction of the unconstrained chain's positive stops are coming from a higher state.

To calculate the probability we can substitute in our known values for these probabilities.

<pre>
<code>
prob_up<sub>&rArr;,k</sub>(i)
  = prob_up<sub>k</sub>(i) 
      * P<sub>k,1+i</sub>[s stops at k | s<sub>1</sub> = 1+i] 
      / P<sub>k,i</sub>[stops at k | s<sub>1</sub> = i]
  = (1/2)
    * ((1+i)/k)
    / (i/k)
  = (i+1)/(2*i)
</code>
</pre>

In the above:

  * The second line is substituting in our previously calculated probabilities of "stopping non-zero", and the 1/2 transition probability under <code>P[]</code>.
  * The last step is algebra.

For <code>0 &lt; i &lt; k</code> we can write the transition probability (independent of older history) as:

  * <code>prob_up<sub>&rArr;,k</sub>(i) = (i+1)/(2*i)</code>
  * <code>prob_down<sub>&rArr;,k</sub>(i) = 1 - prob_up<sub>&rArr;,k</sub>(i)</code>

A similar argument establishes that <code>P<sub>&lArr;,k</sub>[]</code> is Markov on <code>S<sub>&lArr;,k</sub>()</code>. And we can get <code>prob_up<sub>&lArr;,k</sub></code> and <code>prob_down<sub>&lArr;,k</sub></code> by replacing <code>i</code> with <code>k-i</code> and also swapping the roles of up and down.

As a side note: the above work leads me wonder if "backward chain arguments" are perhaps being generalizations of Bayes' law. In particular I am anxious to re-read the brilliant "[coupling from the past](https://en.wikipedia.org/wiki/Coupling_from_the_past)" arguments in Propp, James Gary; Wilson, David Bruce, "Exact sampling with coupled Markov chains and applications to statistical mechanics", (1996), Proceedings of the Seventh International Conference on Random Structures and Algorithms (Atlanta, GA, 1995), pp. 223–252 [MR1611693](https://mathscinet.ams.org/mathscinet/relay-station?mr=1611693). Another way of looking at it: is we are using the original "fair" chain as a substitute system to analyze the "known to stop at <code>k</code>."



### Appendix: A non-Markov Conditioning

A bit of wisdom from Gian-Carlo Rota's "A Mathematician's Gossip":

> Some theorems aer hygienic prescriptions meant to guard us against potentially unpleasant complications. Authors of mathematics books frequently forget to give any hint as to what these complications would be. This omission makes their exposition incomprehensible.

Rota extends this by arguing statements such as "all extremely regular rings aer fully normal" should not be motivated by demonstrating examples of extremely regular rings. Instead one needs to motivate such statements by showing examples of the horror of non-extremely regular rings the in addition are not even fully normal.

So let's demonstrate an example of a future conditioning does not in fact leave the Markov property intact. This is why it is exciting that conditioning on outcome (also in the future) leaving the Markov property intact is something to celebrate.

Consider a Markov chain walking on the integers 0 through 4 (with 0 and 4 as stopping states). If we start the random walk at state 2 and condition on the chain stopping in exactly 4 steps. This is not Markov on the original states, as the transition probabilities of such conditioned chains no longer depends on state (independent of history or time).

There are exactly 4 sequences obeying the above conditioning:

  * <code>+-++</code>
  * <code>+---</code>
  * <code>-+++</code>
  * <code>-+--</code>

The non-Markov condition can be seen: the second move must always be in the opposite direction of the first and the fourth move must be in the same direction as the first. So transition probabilities are no longer a function of current state alone.
  
