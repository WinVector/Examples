# When Profitable Betting Systems are not Possible

## Introduction

In this note I would like to demonstrate the impossibility of
a profitable betting system for fair coin flip style games.

This is in contrast to the case of card-dealing games, which
can often have profitable betting systems. The most famous betting
system is [Thorp](https://en.wikipedia.org/wiki/Edward_O._Thorp)'s card counting strategies for [blackjack or 21](https://en.wikipedia.org/wiki/Blackjack), in turn based on [Kelly's
criterion](https://en.wikipedia.org/wiki/Kelly_criterion). We demonstrate an
example of a working card counting strategy (with code!) for the simple game of guessing whether the next
card dealt is red or black can be found [here](https://win-vector.com/2021/02/25/kelly-thorp-betting/).

### Betting Systems

I find many non-mathematicians are completely unsatisfied with
the claim that there cannot be a winning betting system for fair coin flip style games.
They have a valid point; the result ([Doob's optional
stopping theorem](https://en.wikipedia.org/wiki/Optional_stopping_theorem)) is very close to the definitions. 
So the usual proof doesn't have a lot of
content, and the audience usually doesn't have ready access to correct and concise
statements of the appropriate probability definitions to start from.

I would like to state some very simple *software engineering* definitions, that are sufficient
to rigorously calculate the expected or average value of a betting system over a [martingale](https://en.wikipedia.org/wiki/Martingale_(probability_theory)) (the proper name for the class of random processes that include what I
have been calling "fair coin flip").
We will then show that the expected change in stake is zero with
respect to any implementable betting system.

Proving that a betting system for cards exists is easy: it is enough
to propose one and see it work, as we do [here](https://win-vector.com/2021/02/25/kelly-thorp-betting/). Proving a betting system
for fair coin flips can not exist is in principle harder, as we
are not saying only one system doesn't work- but asserting no system would.

To appreciate this, the reader will have to accept two things.

  * Our clunky stand-in notation for probability theory captures
    a little bit of the intuition of probabilities.
  * That some things can be shown to be impossible. We are not using
    the informal definition of impossible as "very difficult" which
    allows phrases such as
    Charles Alexandre de Calonne's "Madame, si c'est possible, c'est fait;
    impossible? cela se fera."
    Or the WW2 US Army's "The difficult we do immediately, the impossible takes a
    little longer."
    
Luckily we don't really have to show anything is impossible. All we have to do 
is show the expected net-change in stake for any fair coin betting system is zero.
That isn't to say there are not wild high-variance betting systems, it is just
they all share the same expected change in stake: zero.

So we are actually faced with a positive calculation.

## Definitions

We are going to work over a large table data structure for this entire
note. This data structure is not powerful enough or graceful enough
to represent all of the ideas of mathematical probability. However,
it is just enough to precisely define our terms
(including "expected value") and calculate that the expected value of
betting in a martingale is zero.

### Our event data table

We are going to organize or betting situation and simulatons into
$N$ rounds. For each round we generate:

  * The last coin flip outcome "$+1$" (heads)
    or "$-1$" (tails). Call this $C[t]$.
  * A "random number" the betting algorithm can use, if desired, to 
    simulate randomized behavior. This is always an integer in the
    range $0 \cdots M$. Call this $U[t]$.
    
The entire trajectory or history of a possible play is stored
in two vectors $(C, U)$. Where $C[t]$ is the $t$-th coin flip
and $U[t]$ is the $t$-th bit of user randomness.
There are exactly $2 M$ values for each round, so there are
$2^N M^N$ possible distinct records $(C, U)$.
We assume a notional table that has each possible record exactly once,
hence holding $2^N M^N$ records.

We are betting for exactly $N$ rounds. The game ends at time $N$, or
earlier (betting zero is the same as not playing). All algorithms
are going to be deterministic, aside from the random numbers we supply.
With this crude finitist setup we avoid having to discuss many issues
of measure theory.

Our gambling simulation works as follows:

  * A single record $(C, U)$ is drawn from our table, with each of the
    $2^N M^N$ records being equally likely. This is the only
    place we use probability in these arguments.
  * We then simulate the gambling game by saying the
    values $C_1, \cdots, C_{t-1}$ and $U_1, \cdots U_t$ are "what is
    seen at time $t$." Or, the record observable at time $t$ is
    $(C[1:(t-1)], U[1:t])$.

Our entire appeal to the theory of distributions is: repeated plays
of the game approach the expected value of summing over all rows
in the above table. Thus, if we calculate the expected value
of this table we have the expected value of repeated play.

The trick of pretending all of the random
selections have happened before we start is one of the most
powerful in reasoning about probabilistic systems. It is perhaps
most famous in its use in Doob's exposure martingale. The idea
being: we pretend all random events are written down
before we start, and we merely expose them in time order.

Let's realize an example of this data structure in `Python`. Some indexing will be from zero, not
1 as Python and mathematics conventions differ.

Let's define an example record table with no user-random numbers $U$.


```python
import numpy
import collections
import itertools

record = collections.namedtuple('record', 'C U')

def mk_record_table(*, N, M):
    Ms = [v for v in range(M)]
    Cs = [v for v in itertools.product((+1, -1), repeat=N)]
    Us = [v for v in itertools.product(Ms, repeat=N)]
    return([record(v[0], v[1]) 
            for v in itertools.product(Cs, Us)])

record_table = mk_record_table(N=3, M=1)
record_table
```




    [record(C=(1, 1, 1), U=(0, 0, 0)),
     record(C=(1, 1, -1), U=(0, 0, 0)),
     record(C=(1, -1, 1), U=(0, 0, 0)),
     record(C=(1, -1, -1), U=(0, 0, 0)),
     record(C=(-1, 1, 1), U=(0, 0, 0)),
     record(C=(-1, 1, -1), U=(0, 0, 0)),
     record(C=(-1, -1, 1), U=(0, 0, 0)),
     record(C=(-1, -1, -1), U=(0, 0, 0))]



### A betting strategy

A betting strategy is a
function $\text{betfn}(\text{stake}, t, (C'[1:(t-1), U'[1:t]))$ that takes
as arguments:

  * $\text{stake}$: the current complete holdings. For simplicity we assume
    the initial holdings or stake is $1$, and fractional bets are allowed.
  * $t$: the current time or stage.
  * $(C[1:(t-1)], U[1:t])$: the observed coin flip outcomes prior to now,
    and the user-random helper data up to now.

If the function $\text{betfn}$ returns a valid floating point number in the range
$[-1, +1]$, in no more than $W$ seconds (say $W = 120$),
without throwing an exception, or abnormally exiting, then the
stage-$t$ bet $b(t)$ is the returned value times the current holding or stake.
Otherwise the bet $b(t) = 0$. The bet function is putting on "heads" with positive returns,
and "tails" tails with negative returns.

Let's define our example betting strategy.


```python
def record_up_to_time(*, rec, t):
    return(record([rec.C[i] for i in range(t-1)], 
                  [rec.U[i] for i in range(t)]))

partial_record = record_up_to_time(rec=record_table[2], t=2)
partial_record
```




    record(C=[1], U=[0, 0])




```python
def betfn(*, stake, t, rec):
    # bet mean flip outcome seen up to now
    if len(rec.C) <= 0:
        return 0
    return(0.5 * numpy.mean(rec.C))

betfn(stake = 1, t = 2, rec=partial_record)
```




    0.5



### Valuing a betting trajectory

For any single complete record $(C, U)$ we can define the value of
a $\text{betfn}()$ trajectory,
written as $\text{value}(\text{betfn}, (C, U))$ as follows.

  * $\text{stake}(1) = 1$ is the original stake or amount of money held.
  * $\text{stake}(t+1) = \text{stake}(t) + C[t] \; \text{bet}(t) \; \text{stake}(t)$, where
    $bet(t) = \text{betfn}(\text{stake}, t, (C[1:(t-1)], U[1:t]))$.
    This encodes: the bet is calculated by $\text{betfn}()$, and the sign of
    the bet is a prediction of the sign of $C[t]$. We get our bet
    paid out if $\text{sign}(C[t]) == \text{sign}(bet(t))$ and we lose our bet
    if $\text{sign}(C[t]) \neq \text{sign}(bet(t))$.
  * We apply the above rules inductively to find the final holdings
    $\text{stake}(N+1)$. We call $\text{stake}(N+1)$ the
    final value of
    $\text{betfn}()$ for the record $(C, U)$. This is written as:
    $\text{value}(\text{betfn}, (C, U))$.

It takes a while, but by working all the cases one can conclude that the
$\text{stake}(t+1) = \text{stake}(t) + C[t] \; \text{bet}(t) \; \text{stake}(t)$
pays off when the sign of the stake and bet are the same and takes money
away when they are opposite. I find the expression slightly nicer than
the equivalent `if/else` code.

Let's build code to value our betting function.


```python
def value_fn(*, betfn, rec, verbose=False):
    if verbose:
        print(rec)
    stake = 1.0
    for t in range(len(rec.C)):
        if verbose:
            print('time: ' + str(t))
        bet = betfn(
            stake=stake, 
            t=t, 
            rec=record_up_to_time(rec=rec, t=t+1))
        if verbose:
            print('   bet fraction: ' + str(bet))
            print('   bet quantity: ' + str(bet * stake))
        assert bet >= -1
        assert bet <= 1
        new_stake = stake + rec.C[t] * bet * stake
        if verbose:
            print('   outcome: ' + str(rec.C[t]))
            print('   stake: ' + str(stake) 
                  + ' -> ' + str(new_stake))
        stake = new_stake
    return(stake)

value_fn(betfn=betfn, rec=record_table[0], verbose=True)
```

    record(C=(1, 1, 1), U=(0, 0, 0))
    time: 0
       bet fraction: 0
       bet quantity: 0.0
       outcome: 1
       stake: 1.0 -> 1.0
    time: 1
       bet fraction: 0.5
       bet quantity: 0.5
       outcome: 1
       stake: 1.0 -> 1.5
    time: 2
       bet fraction: 0.5
       bet quantity: 0.75
       outcome: 1
       stake: 1.5 -> 2.25





    2.25



In the above trajectory we converted our initial stake of $1$ to $2.25$, for a net-profit of $1.25$.

Let's try another example.


```python
value_fn(betfn=betfn, rec=record_table[1], verbose=True)
```

    record(C=(1, 1, -1), U=(0, 0, 0))
    time: 0
       bet fraction: 0
       bet quantity: 0.0
       outcome: 1
       stake: 1.0 -> 1.0
    time: 1
       bet fraction: 0.5
       bet quantity: 0.5
       outcome: 1
       stake: 1.0 -> 1.5
    time: 2
       bet fraction: 0.5
       bet quantity: 0.75
       outcome: -1
       stake: 1.5 -> 0.75





    0.75



This time we ended with a stake of $0.75$, for a net-loss of $0.25$.

### Valuing a betting strategy

To value a betting strategy we compute the expected value against our
table of all possible $(C, U)$ records.

For this writeup define the conditional expected value of a function $\text{betfn}()$
as:

$\text{E}_{(C', U')}[\text{betfn}() | (C[1:(t-1)], U[1:t])] = \frac{
\sum_{(C', U') s.t. C'[1:(t-1)] = C[1:(t-1)], U'[1:t] = U[1:t]} \text{value}(\text{betfn}, (C', U'))}{
\sum_{(C', U') s.t. C'[1:(t-1)] = C[1:(t-1)], U'[1:t] = U[1:t]} 1}$.

That is: on average
how does the bet function perform, conditioned what we know up to now.
$(C', U')$ are taken from all rows of our table that agree with $(C, U)$ "up to time $t$."
This definition is in fact an [expectation](https://en.wikipedia.org/wiki/Expected_value), but not as versatile as the more general definitions.

When $t$ is $0$ we shorten the notation $\text{E}_{(C', U')}[\text{betfn}() | ()]$ to $\text{E}_{(C', U')}[\text{betfn}()]$.

The formula can be translated to code as follows.


```python
# define our conditional expectation function
# (designed to transparently match definitions, not for speed)
def E(*, betfn, condition=None, verbose=False):
    numerator = 0
    denominator = 0
    for rec in record_table:
        if ((condition is None) or 
            (record_up_to_time(rec=rec, t=len(condition.U)) == condition)):
            vi = value_fn(betfn=betfn, rec=rec)
            numerator = numerator + vi
            denominator = denominator + 1
            if verbose:
                print(" match " + str(rec) + ", value = " + str(vi))
        else:
            if verbose:
                print(" no-match " + str(rec))
    return(numerator / denominator)

# compute an unconditional expected value
E(betfn=betfn, verbose=True)
```

     match record(C=(1, 1, 1), U=(0, 0, 0)), value = 2.25
     match record(C=(1, 1, -1), U=(0, 0, 0)), value = 0.75
     match record(C=(1, -1, 1), U=(0, 0, 0)), value = 0.5
     match record(C=(1, -1, -1), U=(0, 0, 0)), value = 0.5
     match record(C=(-1, 1, 1), U=(0, 0, 0)), value = 0.5
     match record(C=(-1, 1, -1), U=(0, 0, 0)), value = 0.5
     match record(C=(-1, -1, 1), U=(0, 0, 0)), value = 0.75
     match record(C=(-1, -1, -1), U=(0, 0, 0)), value = 2.25





    1.0



Notice the calculated value of $\text{betfn}()$ is exactly `1`, or the initial stake. Expectation appears to be behaving as claimed.

We can also use the same code to continue the game from an initial conditioning state.


```python
# Let's add some conditioning
partial_record
```




    record(C=[1], U=[0, 0])




```python
# compute a conditional expected value
E(betfn=betfn, condition=partial_record, verbose=True)
```

     match record(C=(1, 1, 1), U=(0, 0, 0)), value = 2.25
     match record(C=(1, 1, -1), U=(0, 0, 0)), value = 0.75
     match record(C=(1, -1, 1), U=(0, 0, 0)), value = 0.5
     match record(C=(1, -1, -1), U=(0, 0, 0)), value = 0.5
     no-match record(C=(-1, 1, 1), U=(0, 0, 0))
     no-match record(C=(-1, 1, -1), U=(0, 0, 0))
     no-match record(C=(-1, -1, 1), U=(0, 0, 0))
     no-match record(C=(-1, -1, -1), U=(0, 0, 0))





    1.0



We start this game later into the sequence with a stake of `1` at that time. 

Notice in both cases the expected value of the final stake is exactly the initial stake value 1!

To calculate we will need some standard fact about expectations. I'll list them here
so they seem a bit less like cheating when we appeal to them. Items written as functions
(with trailing parenthesis) are functions of $(C', U')$. Items without parenthesis are constants
independent of $(C', U')$. We are not stating things in full generality, but in simplest terms
that allow a complete calculation to be demonstrated. $Z()$ is a placeholder for any conditioning
information.

  * Expected value of a constant:
    $\text{E}_{(C', U')}[a | Z()] = a$. When $a$ is a value not varying as a function of $(C', U')$ we can simplify by dropping
    the expectation notation.
  * Linearity of expectation:
    $\text{E}_{(C', U')}[A() + B() | Z()] = \text{E}_{(C', U')}[A() | Z()] + \text{E}_{(C', U')}[B() | Z()]$. This is one of the most important
    facts about expected values, and follows as expectations are just adding things up.
  * Scaling of expectation:
    $\text{E}_{(C', U')}[a \; B() | Z()] = a \; \text{E}_{(C', U')}[B() | Z()]$, where $a$ is a constant. This is a much weaker version
    of the general fact that expectations of independent products are products of expectations. For this note we only need
    this weaker form that expected values scale with constants.

The above are true in general for expectations, and can be explicitly confirmed for
our formulation.

## The claim

Now that we have precise definitions we can make our claim.
We are going to definitions so we are all using the same
translation from English to mathematics and algorithms in this
discussion.

> Claim: For any $\text{betfn}()$ defined as
> above we have the expected value $\text{E}_{(C', U')}[\text{betfn}()]$
> is $\text{stake}(1)$.
> Or, informally, $\text{E}_{(C', U')}[\text{stake}(N+1)] = \text{stake}(1)$.

That is: there is no betting strategy that is reliable in making,
or even losing money. It is an important point to consider: if we could design a strategy
that reliably lost money, we could build a profitable one by
simply reversing its bets.

This is what we mean when saying a successful betting system on a fair coin is
impossible. All such betting systems have the same expected delta value: zero.

Let's try another betting strategy before we prove the theorem. In this case let's try
the small martingale always betting on positive. This is a classic gambler's fallacy:
bet on plus. If we win walk away with a profit. If we lose roughly double the bet
to try to make up the loss and win. This strategy wins on every sequence except one:
the all minus draw.


```python
# the classic: double when I lose, quit when ahead strategy
# in this case always betting on +1
def small_martingale(*, stake, t, rec, fraction=1/8):
    if stake > 1:
        return(0) # we are ahead, quit betting
    if stake == 1:
        return(fraction) # first bet, fraction of our holdings
    # stake < 1, we are behind! bet on + enough to try and finish game
    return(min(1, (1 + fraction)/stake -1))

value_fn(betfn=small_martingale, rec=record_table[6], verbose=True)
```

    record(C=(-1, -1, 1), U=(0, 0, 0))
    time: 0
       bet fraction: 0.125
       bet quantity: 0.125
       outcome: -1
       stake: 1.0 -> 0.875
    time: 1
       bet fraction: 0.2857142857142858
       bet quantity: 0.2500000000000001
       outcome: -1
       stake: 0.875 -> 0.6249999999999999
    time: 2
       bet fraction: 0.8000000000000003
       bet quantity: 0.5000000000000001
       outcome: 1
       stake: 0.6249999999999999 -> 1.125





    1.125



The problem is: the strategy loses so much money in the minus situation it eats up
all the winnings in all the other alternatives. And the expected value is again
exactly the initial stakes: 1. For larger $N$ and smaller initial bets relative to the total
stake one can make ruin arbitrarily unlikely. But the ruin still happens, and always loses
exactly the amount of money to erase all the winnings.


```python
E(betfn=small_martingale, verbose=True)
```

     match record(C=(1, 1, 1), U=(0, 0, 0)), value = 1.125
     match record(C=(1, 1, -1), U=(0, 0, 0)), value = 1.125
     match record(C=(1, -1, 1), U=(0, 0, 0)), value = 1.125
     match record(C=(1, -1, -1), U=(0, 0, 0)), value = 1.125
     match record(C=(-1, 1, 1), U=(0, 0, 0)), value = 1.125
     match record(C=(-1, 1, -1), U=(0, 0, 0)), value = 1.125
     match record(C=(-1, -1, 1), U=(0, 0, 0)), value = 1.125
     match record(C=(-1, -1, -1), U=(0, 0, 0)), value = 0.12499999999999978





    1.0



Let's try a more conservative strategy: bet on positive, and stop on first time tails comes up. This strategy
has the "stopping" spirit, it is always betting the same amount until it decides to leave the game (by betting zero from that point on).


```python
def stop_on_first_tails(*, stake, t, rec, fraction=1/8):
    # see if tails ever came up, 
    # if so we wrong as we always bet on heads
    if any([ct < 0 for ct in rec.C]):
        return(0) # stop betting forever
    return(1 / stake) # bet constant amount (divide out stake)

value_fn(betfn=stop_on_first_tails, rec=record_table[1], verbose=True)
```

    record(C=(1, 1, -1), U=(0, 0, 0))
    time: 0
       bet fraction: 1.0
       bet quantity: 1.0
       outcome: 1
       stake: 1.0 -> 2.0
    time: 1
       bet fraction: 0.5
       bet quantity: 1.0
       outcome: 1
       stake: 2.0 -> 3.0
    time: 2
       bet fraction: 0.3333333333333333
       bet quantity: 1.0
       outcome: -1
       stake: 3.0 -> 2.0





    2.0



In the above example we see a net-win of $1$. However, as always, this doesn't hold on average.


```python
E(betfn=stop_on_first_tails, verbose=True)
```

     match record(C=(1, 1, 1), U=(0, 0, 0)), value = 4.0
     match record(C=(1, 1, -1), U=(0, 0, 0)), value = 2.0
     match record(C=(1, -1, 1), U=(0, 0, 0)), value = 1.0
     match record(C=(1, -1, -1), U=(0, 0, 0)), value = 1.0
     match record(C=(-1, 1, 1), U=(0, 0, 0)), value = 0.0
     match record(C=(-1, 1, -1), U=(0, 0, 0)), value = 0.0
     match record(C=(-1, -1, 1), U=(0, 0, 0)), value = 0.0
     match record(C=(-1, -1, -1), U=(0, 0, 0)), value = 0.0





    1.0



We now see the content of the claim: one can not write a betting function that
makes or even loses money in expected value. As long as the function is deterministic in its inputs, doesn't "snoop the future, returns valid values in the range `[-1, 1]`, we don't experience numeric errors in tracking the stake, and we don't throw an exception the expected value calculation above will *always* return 1.

One should really try coding up a few betting strategies to test the limits of the above claim!

With such a theorem in hand "I don't need to hear the details of your betting system to know it doesn't work." Or more politely: a fair coin (or martingale) evaluation is designed to exactly not allow any betting
working betting system. Trying variations of the above code is a safe way to get experience with betting systems.

## The proof


As we have precise definitions, we can actually work a specific proof of our claim.
It is in two parts:

  * These betting systems are martingales.
  * Martingales don't allow profits.

This sort of mathematical proof isn't so much convincing, but showing a calculation
dragged through all the steps yields the claimed result. We are intentionally belaboring the
obvious, to try and make the "obvious" visible.

The guiding principle is: a betting system like the above is called
a martingale. The definition of a martingale is: for any step in time we
have the expected value: 

> $\text{E}_{(C', U')}[\text{stake}(t+1)] = \text{stake}(t)$

Our setup is designed to represent a system with the martingale property: that a single bet doesn't know
anything about the future. What we are trying to prove is: when this
is the case, then even a sequence of bets can't predict the future. This is also called [Doob's optional stopping theorem](https://en.wikipedia.org/wiki/Optional_stopping_theorem).

### Establishing the martingale property

Let's first confirm the martingale property is present in our formulation. We are going
to compute expectations of the form $\text{E}_{(C', U')}[\text{...} | (C[1:(t-1)], U[1:t])]$. For conciseness
let's write this as $\text{E}[\text{...} | Z]$ for the next few equations. Also, most of the items
in this expectation are functions of $(C', U')$, but we are not adding such subscripts for legibility.

$\begin{align*}
 \text{E}[\text{stake}(t+1) | Z] &= \\
 &\#\; \text{by our payoff definition}  \\
 &= \text{E}[\text{stake}(t) + C'[t] \; \text{bet}(t) \; \text{stake}(t) | Z] \\
 &\#\; \text{by linearity of expectation}  \\
 &= \text{E}[\text{stake}(t) | Z] + \text{E}[C'[t] \; \text{bet}(t) \; \text{stake}(t) | Z] \\
 &\#\; \text{bet}(t) \; \text{and} \; \text{stake}(t) \; \text{are constant given} \; Z  \\
 &= \text{E}[\text{stake}(t) | Z] + \text{E}[C'[t] | Z] \; \text{bet}(t) \; \text{stake}(t)  \\
 &\#\; \text{substitute in} \; \text{E}[C'[t] | Z] = 0 \; \text{the fair coin flip} \\
 &= \text{E}[\text{stake}(t) | Z] + 0 \; \text{bet}(t) \; \text{stake}(t) \\
 &\#\; \text{simplify}  \\
 &= \text{E}[\text{stake}(t) | Z] \\
 &\#\;\text{equals our desired conclusion}  \\
 &= \text{stake}(t) 
\end{align*}$

We are using $\text{E}[C'[t] | Z] = 0$ as it is $+1$ and $-1$ each exactly half the time
in the set of records we are using (those meeting the $Z$ condition). We are only using a very
weak form of independence as $\text{bet}(t) \; \text{stake}(t)$ is the same
constant for all records meeting our $Z$ condition, as they all have the exact same history up to this time.
This confirms the martingale condition is present in our formulation.

We have essentially shown the martingale property: 1 round or single period fair coin flip games have expected value
equal to the initial stake.
All that remains to be shown is: even betting over multiple periods and
picking when to stop betting doesn't make a difference.

The experienced probabilist would not bother with the above.
For them it is obvious that the system we are talking about has
the martingale property:
$\text{E}_{(C', U')}[\text{stake}(t+1)] = \text{stake}(t)$.


### Proving the general theorem

We know:

$\text{E}_{(C', U')}[\text{stake}(t+1)] = \text{stake}(t)$

The full optional stopping theorem would be establishing one of the following (both are true):

  * $\text{E}_{(C', U')}[\text{stake}(t)] = \text{stake}(1)$
  * $\text{E}[\text{stake}(t+1)] = \text{E}[\text{stake}(t)]$

And we could prove either of these by more of the brutal symbol pushing we did earlier.
Let's instead use a more fluid proof by contradiction. We want to reduce
estimating $E[\text{stake}_{\text{betfn}()}(N+1)]- E[\text{stake}_{\text{betfn}()}(N)]$ to
estimating $E[\text{stake}_{\text{betfn}()}(N+1)] - \text{stake}_{\text{betfn}()}(N)$ by constraining
$\text{stake}_{\text{betfn}()}(N)$ to be a constant.

Suppose there was a betting system specified by $M$, $N$, $\text{betfn}()$ such that $\text{E}_{(C', U')}[\text{betfn}()] \neq \text{stake}(1)$.
Further suppose this betting system has minimal play length $N$ for all such betting systems.

This means:

  * $\text{E}_{(C', U')}[\text{stake}_{\text{betfn}()}(N)] = \text{stake}(1)$.
  * $\text{E}_{(C', U')}[\text{stake}_{\text{betfn}()}(N+1)] \neq \text{stake}(1)$.
  * So $\text{E}_{(C', U')}[\text{stake}_{\text{betfn}()}(N+1) - \text{stake}_{\text{betfn}()}(N)] \neq 0$

So the magic, if any, is in the last stage. However, this can not be.

The issue is: $\text{stake}_{\text{betfn}()}(N)$ is a constant when conditioned on $(C[1:n-1], U[1:n])$.
So this expression is exactly in the martingale
form, $\text{E}_{(C', U')}[\text{stake}_{\text{betfn}()}(N+1) | (C[1:n-1], U[1:n])] - \text{stake}_{\text{betfn}()}(N)$.
We have constrained our game enough so the margingale lemma directly applies.

The martingale property says this last difference must be zero, contradicting our claim that
it was not zero. Thus such a betting system having a expectation different than its starting 
stake leads to a contradiction. We then say this means there are no such betting systems,
completing the proof.

## Conclusion

Many card games have winning betting systems, as knowledge of the cards
draw is knowledge about the cards remaining to be dealt. Fair coin flipping games tend to be martingales: where the expected value of
each step is just the actual value of the step before. In the martingale
case we can make an inductive argument that if no step is on average profitable, then the sequence cannot on average not be profitable (or even unprofitable!). Our tools for making this argument are a bit clumsy as they involve
uninteresting calculations very close to the starting definitions.
The conclusion, however, is very important whether you consider this
obvious or subtle. The result is commonly called Doob's optional stopping theorem.
In probability our ability to calculate rapidly out-performs our
intuition of what is or is not obvious, so for safety we tend to depend on calculation, despite the opaqueness this can introduce.


```python

```
