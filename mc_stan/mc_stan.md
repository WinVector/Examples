stan_ex
================
2025-08-23

Working the problem shared in: [J. Rickert, “Multistate Models for
Medical
Applications”](https://rviews.rstudio.com/2023/04/19/multistate-models-for-medical-applications/)

``` r
library(msm)
library(rstan)
library(cdata)
library(ggplot2)
```

``` r
cav = cav[order(cav$PTNUM, cav$years), , drop=FALSE]
cav$pt_idx = match(cav$PTNUM, unique(cav$PTNUM))
head(cav)
```

    ##    PTNUM      age    years dage sex pdiag cumrej state firstobs statemax pt_idx
    ## 1 100002 52.49589 0.000000   21   0   IHD      0     1        1        1      1
    ## 2 100002 53.49863 1.002740   21   0   IHD      2     1        0        1      1
    ## 3 100002 54.49863 2.002740   21   0   IHD      2     2        0        2      1
    ## 4 100002 55.58904 3.093151   21   0   IHD      2     2        0        2      1
    ## 5 100002 56.49589 4.000000   21   0   IHD      3     2        0        2      1
    ## 6 100002 57.49315 4.997260   21   0   IHD      3     3        0        3      1

``` r
statetable.msm(state = state, subject = PTNUM, data = cav)
```

    ##     to
    ## from    1    2    3    4
    ##    1 1367  204   44  148
    ##    2   46  134   54   48
    ##    3    4   13  107   55

Each row (except for the first) for each patient represents an observed
state transition. We confirm this by comparing the following counts.

``` r
sum(statetable.msm(state = state, subject = PTNUM, data = cav))
```

    ## [1] 2224

``` r
nrow(cav) - length(unique(cav$PTNUM))
```

    ## [1] 2224

We encode the transitions as an ad-hoc continuous time Markov chain
(time being given by “years”).

For this analysis we are going to assume the observation times are
independent of the states and that there are no unobserved transitions.
This is a strong assumption that the reporting intervals are triggers
are sufficiently sensitive. If this is not the case we need different
methods. We will also model state 4 as absorbing. We can perform the
analysis with different assumptions.

A number of lemmas allow us to represent a [continuous time Markov
chain](https://en.wikipedia.org/wiki/Continuous-time_Markov_chain) by
estimating exponential holding times at each state and the discrete jump
probabilities given a transition takes place.

The [exponential
distribution](https://en.wikipedia.org/wiki/Exponential_distribution) is
a probability distribution on the non-negative reals such that:

- The distribution has a single shape parameters $\lambda$.
- The density at $x$ is $\lambda e^{-\lambda x}$.
- The mean is $1 / \lambda$.
- The CDF or $\text{P}[X <= x]$ is $1 - e^{-\lambda x}$.
- $\text{P}[X >= x] =  e^{-\lambda x}$.
- The distribution is “memoryless” that is
  $\text{P}[X >= a + b \;|\; X >= b] = \text{P}[X >= a]$. Or: no matter
  how long you have waited, your remaining expected wait time remains
  the same. This property allows us to analyze the recorded data row by
  row.

In this formulation:the time spent at state $i$ is distributed
exponential with parameter $\lambda_{i} > 0$.

- The probability of observing a state $i$ to $i$ transition while
  waiting $t$ time units is given by how much mass of the exponential
  distribution is at least $t$. For the exponential distribution this is
  $\text{exp}(-\lambda_{i} t)$.
- The probability of observing a state $i$ to $j$ ($j$ different than
  $i$) transition at an unknown intermediate time $z$ such that
  $0 <= z <= t$ happens with probability given by waiting until time $z$
  in state $i$, jumping from $i$ to $j$ (itself with probability
  $\text{P}[i, j]$) and then waiting in state $j$ for time $t - z$. For
  a given $z$ this probability is
  $(\lambda_{i} \text{exp}(-\lambda_{i} z)) \text{P}[i, j] (\lambda_{j} \text{exp}(-\lambda_{j} (t - z)))$.
  As we don’t know $t$ we integrate it out. The solution in this case is
  (with the correct convention when $\lambda_i = \lambda_j$) then our
  solution is $\text{P}[i, j] I$ where:

$$
I = \int_{0}^{t} \bigl(\lambda_i e^{-\lambda_i z}\bigr) \bigl(\lambda_j e^{-\lambda_j (t-z)}\bigr) dz
$$

For $\lambda_i \neq \lambda_j$:

$$
I = \frac{\lambda_i \lambda_j}{\lambda_i - \lambda_j} \Bigl(e^{-\lambda_j t} - e^{-\lambda_i t}\Bigr).
$$

For $\lambda_i = \lambda_j = \lambda$ the above form is problematic, and
we switch to its limit:

$$
I = \lambda^{2} t e^{-\lambda t}.
$$

The switching is problematic (it destroys derivatives), but could be
softened by different interpolation ideas.

The argument that integrating out $z$ is a correct step is as follows:
we could put it in a model as an unobserved parameter of the model. Then
sampling the model would be picking viable values of $z$ uniformly,
which is numerically equivalent to integrating $z$ out. So either having
$z$ as an explicit unobserved parameter or integrating it out is a
correct inference method. When the math allows it we integrate out $z$,
when it does not we just add many $z$ as model parameters.

Given that we can copy these into Stan as distributional statements.

``` r
stan_src = "
data {
  int<lower=1> m_examples;
  int<lower=2> n_states;
  int<lower=1> n_patients;
  array[m_examples] int<lower=1, upper=n_patients> pt_idx;
  vector[m_examples] years;
  array[m_examples] int<lower=1, upper=n_states> state;
}
parameters {
   vector<lower=0>[n_states - 1] lambda;
   array[n_states - 1] simplex[n_states - 1] Pd;
}
model {
  for (i in 2:m_examples) {
     if ((pt_idx[i-1] == pt_idx[i]) && (state[i-1] < n_states)) {
       real t;
       real v;
       t = years[i] - years[i-1];
       if (state[i-1] == state[i]) {
          // stayed: 1 - CDF
          v = exp(-lambda[state[i-1]] * t);
       } else if (state[i] >= n_states) {
          // moved: CDF
          v = 1 - exp(-lambda[state[i-1]] * t);
       } else {
          if (abs(lambda[state[i]] - lambda[state[i-1]]) > 1e-5 ) { // depends on paramter inferences (ick)
            v = (
               lambda[state[i]] * lambda[state[i-1]] 
                 * (
                    exp(-lambda[state[i-1]] * t)
                    - exp(-lambda[state[i]] * t)
                 )
                 / (lambda[state[i]] - lambda[state[i-1]])
            );
          } else {
            v = (
               lambda[state[i]] * lambda[state[i-1]] 
                  * t 
                  * exp(-(lambda[state[i]] + lambda[state[i-1]]) * t / 2)
            );
          }
          if (state[i-1] < state[i]) {
             v = (v + 1e-6) * (Pd[state[i-1], state[i] - 1] + 1e-6);
          } else {
             v = (v + 1e-6) * (Pd[state[i-1], state[i]] + 1e-6);
          }
       }
       target += log(v);
     }
  }
}
"
```

The `Pd`s in this model do not encode self-transitions are in encoded as
follows:

- For $i > j$ $\text{Pd}[i, j]$ is the probability of moving from state
  $i$ to state $j$, given there was a transition.
- For $i < j$ $\text{Pd}[i, j - 1]$ is the probability of moving from
  state $i$ to state $j$, given there was a transition.

Notice there is no representation for a $i$ to $i$ transition. When we
unpack these results we will pad them out to get a more regular
$\text{P}[i, j]$ represents the $i$ to $j$ transition notation.

One can extend the model to parametric inference by writing `Pd` and
`lambda` as parametric functions of instance features.

Let’s use Stan to find a set of parameters for which the observations
are likely.

``` r
model = stan_model(
  model_code=stan_src
)
```

``` r
stan_data <- list(
  m_examples = nrow(cav),
  n_states = max(cav$state),
  n_patients = max(cav$pt_idx),
  pt_idx = array(cav$pt_idx, dim=nrow(cav)),
  years = array(cav$years, dim=nrow(cav)),
  state = array(cav$state, dim=nrow(cav))
)
```

``` r
res <- as.data.frame(sampling(
  model,
  data = stan_data,
  chains = 4,                 # number of Markov chains
  cores = 4,                  # number of cores (could use one per chain)
  warmup = 16000,              # number of warmup iterations per chain
  iter = 20000,                # total number of iterations per chain
  refresh = 0                # no progress shown
))
```

``` r
res = res[res$lp__ >= quantile(res$lp__, 0.9), , drop=FALSE]
res_row = colMeans(res)
```

``` r
head(res)
```

    ##    lambda[1] lambda[2] lambda[3]   Pd[1,1]   Pd[2,1]   Pd[3,1]   Pd[1,2]
    ## 1  0.1667267 0.9133397 0.7897752 0.7951012 0.5326352 0.2109809 0.2023738
    ## 5  0.1609505 0.9366243 0.8699767 0.7952534 0.4503686 0.2593287 0.1990042
    ## 6  0.1669464 0.9149762 0.6983760 0.8395679 0.4594418 0.2440368 0.1573581
    ## 10 0.1648138 0.8724636 0.7916135 0.7921049 0.4366527 0.3090811 0.2057875
    ## 12 0.1624818 0.9351874 0.7719916 0.8163519 0.5119756 0.1941504 0.1804917
    ## 13 0.1583559 0.9145563 0.7976539 0.7899196 0.4713240 0.2232464 0.2049640
    ##      Pd[2,2]   Pd[3,2]     Pd[1,3]     Pd[2,3]    Pd[3,3]      lp__
    ## 1  0.4584631 0.7309672 0.002524982 0.008901673 0.05805192 -2017.379
    ## 5  0.5316280 0.7045881 0.005742357 0.018003446 0.03608320 -2017.185
    ## 6  0.5371617 0.7131926 0.003074032 0.003396457 0.04277059 -2017.297
    ## 10 0.5552933 0.6524437 0.002107628 0.008053978 0.03847528 -2016.988
    ## 12 0.4815435 0.7522347 0.003156441 0.006480895 0.05361491 -2016.428
    ## 13 0.5161327 0.6868596 0.005116327 0.012543297 0.08989396 -2016.728

From our sample can extract the discrete step matrix, which encodes:
given one changed states what state did one change to?

``` r
n_states = max(cav$state)
step_matrix = matrix(0, nrow=n_states, ncol=n_states)
for (i in 1:(n_states - 1)) {
  for (j in 1:n_states) {
     if (i!=j) {
       js = j
       if (j > i) {
         js = j - 1
       }
       step_matrix[i, j] = as.numeric(res_row[paste0('Pd[', i, ',', js, ']')])
     }
  }
}

step_matrix
```

    ##           [,1]      [,2]      [,3]        [,4]
    ## [1,] 0.0000000 0.8174119 0.1786996 0.003888525
    ## [2,] 0.4576200 0.0000000 0.5328134 0.009566583
    ## [3,] 0.2511967 0.6986290 0.0000000 0.050174308
    ## [4,] 0.0000000 0.0000000 0.0000000 0.000000000

And it is then standard to combine this and the expected hold-times to
get the Q matrix.

``` r
Q = step_matrix
for (j in 1:(n_states - 1)) {
  # divide by expected hold time (1/lambda)
  Q[, j] = Q[, j] * res_row[paste0('lambda[', j, ']')]
}
diag = -rowSums(Q)
for (j in 1:(n_states - 1)) {
  Q[j, j] = diag[j]
}

Q
```

    ##             [,1]       [,2]       [,3]        [,4]
    ## [1,] -0.89893865  0.7558007  0.1392494 0.003888525
    ## [2,]  0.07503906 -0.4997938  0.4151881 0.009566583
    ## [3,]  0.04119043  0.6459709 -0.7373357 0.050174308
    ## [4,]  0.00000000  0.0000000  0.0000000 0.000000000

It is a standard argument that the probability of observing a patient
starting in state $i$ being in state $j$ at time $t$ is then
$\text{exp}(t Q)[i, j]$. An example of the `0.1` year situation is as
follows.

``` r
Matrix::expm(0.1 * Q)
```

    ## 4 x 4 Matrix of class "dgeMatrix"
    ##             [,1]       [,2]       [,3]         [,4]
    ## [1,] 0.914320342 0.07093754 0.01429996 0.0004421652
    ## [2,] 0.007081035 0.95278431 0.03909953 0.0010351182
    ## [3,] 0.004023400 0.06090234 0.93020466 0.0048696000
    ## [4,] 0.000000000 0.00000000 0.00000000 1.0000000000

As is usual with exponents, the `k* 0.1` year estimate is the `k'th`
power of the `0.1` year estimate.

``` r
Matrix::expm(3 * 0.1 * Q) - (Matrix::expm(0.1 * Q) %*% Matrix::expm(0.1 * Q) %*% Matrix::expm(0.1 * Q))
```

    ## 4 x 4 Matrix of class "dgeMatrix"
    ##              [,1]         [,2]          [,3]         [,4]
    ## [1,] 2.220446e-16 8.326673e-17  6.938894e-18 2.168404e-19
    ## [2,] 3.469447e-18 3.330669e-16  2.775558e-17 8.673617e-19
    ## [3,] 3.469447e-18 2.775558e-17 -2.220446e-16 1.734723e-18
    ## [4,] 0.000000e+00 0.000000e+00  0.000000e+00 0.000000e+00

Notice we have not referred to the [Kolmogorov
equations](https://en.wikipedia.org/wiki/Kolmogorov_equations#Continuous-time_Markov_chains),
instead attempting to infer parameters that entail a Q-matrix which we
can use to build detailed summaries.

``` r
time_frame = data.frame(
  year = seq(from=0, to=20, by=0.1),
  s1 = 0,
  s2 = 0,
  s3 = 0,
  s4 = 0
  )
for (i in 1:nrow(time_frame)) {
  d = Matrix::expm(max(1e-6, time_frame$year[i]) * Q)  # could also just power up exp(time[1] * Q)
  time_frame[i, 's1'] = d[1, 1]
  time_frame[i, 's2'] = d[1, 2]
  time_frame[i, 's3'] = d[1, 3]
  time_frame[i, 's4'] = d[1, 4]
}
plot_frame = pivot_to_blocks(
  time_frame, 
  nameForNewKeyColumn = 'state', 
  nameForNewValueColumn = 'probability', 
  columnsToTakeFrom = c('s1', 's2', 's3', 's4'))
(
  ggplot(
    data=plot_frame,
    mapping=aes(x=year, y=probability, color=state)
    )
  + geom_line()
  + ggtitle("probability of being in state-i starting from state-1 by year")
)
```

![](mc_stan_files/figure-gfm/unnamed-chunk-16-1.png)<!-- -->
