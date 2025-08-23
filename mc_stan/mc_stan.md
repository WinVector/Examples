stan_ex
================
2025-08-23

Working the problem shared in: [J. Rickert, “Multistate Models for
Medical
Applications”](https://rviews.rstudio.com/2023/04/19/multistate-models-for-medical-applications/)

``` r
library(msm)
library(rstan)
```

    ## Loading required package: StanHeaders

    ## 
    ## rstan version 2.32.6 (Stan version 2.32.2)

    ## For execution on a local, multicore CPU with excess RAM we recommend calling
    ## options(mc.cores = parallel::detectCores()).
    ## To avoid recompilation of unchanged Stan programs, we recommend calling
    ## rstan_options(auto_write = TRUE)
    ## For within-chain threading using `reduce_sum()` or `map_rect()` Stan functions,
    ## change `threads_per_chain` option:
    ## rstan_options(threads_per_chain = 1)

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

``` r
unique(cav$state)
```

    ## [1] 1 2 3 4

For this analysis we are going to assume the observation times are
independent of the states and that there are no unobserved transitions.
We will also model state 4 as absorbing. We can perform the analysis
with different assumptions.

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
  how long you have waited, your remaining expected wait time remans the
  same. This property allows us to analyze the recorded data row by row.

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
     if ((pt_idx[i-1] == pt_idx[i]) && (state[i] < n_states)) {
       real t;
       real v;
       t = years[i] - years[i-1];
       if (state[i-1] == state[i]) {
          v = exp(-lambda[state[i]] * t);
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

- For $i > j$ $Pd[i, j]$ is the probability of moving from state $i$ to
  state $j$.
- For $i < j$ $Pd[i, j - 1]$ is the probability of moving from state $i$
  to state $j$.

Notice there is no representation for a $i$ to $i$ transition. When we
unpack these results we will pad them out to get a more regular
$\text{P}[i, j]$ represents the $i$ to $j$ transition notation.

One can extend the model to parametric inference by writing `Pd` and
`lambda` as parametric functions of instance features.

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
    ## 3  0.1074034 0.9088712 0.6321297 0.8145221 0.4453542 0.1572724 0.1812960
    ## 5  0.1198312 0.8417540 0.5548391 0.8219302 0.4933370 0.2675063 0.1725522
    ## 7  0.1104179 0.9192706 0.6008022 0.8266347 0.4432129 0.2448043 0.1717263
    ## 15 0.1118236 0.7980800 0.6252320 0.8303443 0.5082514 0.2977180 0.1681083
    ## 48 0.1106810 0.8096113 0.6069468 0.8284002 0.4352925 0.2976471 0.1682989
    ## 54 0.1113944 0.8704110 0.6522751 0.8270936 0.4906704 0.2785500 0.1718146
    ##      Pd[2,2]   Pd[3,2]     Pd[1,3]     Pd[2,3]    Pd[3,3]      lp__
    ## 3  0.5516441 0.7867152 0.004181854 0.003001639 0.05601243 -1588.817
    ## 5  0.4991948 0.6899790 0.005517592 0.007468172 0.04251464 -1588.143
    ## 7  0.5506678 0.7319331 0.001639054 0.006119337 0.02326263 -1588.194
    ## 15 0.4852536 0.6542650 0.001547408 0.006495010 0.04801696 -1588.944
    ## 48 0.5623052 0.6266280 0.003300924 0.002402319 0.07572494 -1588.764
    ## 54 0.5073506 0.6624982 0.001091804 0.001978967 0.05895183 -1588.740

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
    ## [1,] 0.0000000 0.8172666 0.1786737 0.004059779
    ## [2,] 0.4565648 0.0000000 0.5337538 0.009681476
    ## [3,] 0.2492002 0.7015638 0.0000000 0.049236040
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
    ## [1,] -0.82415307  0.7099574  0.1101359 0.004059779
    ## [2,]  0.05238696 -0.3910786  0.3290101 0.009681476
    ## [3,]  0.02859362  0.6094467 -0.6872764 0.049236040
    ## [4,]  0.00000000  0.0000000  0.0000000 0.000000000

It is a standard argument that the probability of observing a patient
starting in state $i$ being in state $j$ at time $t$ is then
$\text{exp}(t Q)[i, j]$.
