stan_ex
================
2025-08-23

[J. Rickert, “Multistate Models for Medical
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

We encode the transitions as an ad-hoc continuous time Markov chain.

``` r
unique(cav$state)
```

    ## [1] 1 2 3 4

For this analysis we are going to assume the observation times are
independent of the states and that there are no unobserved transitions.
We can perform the analysis with different assumptions.

One can characterize a [continuous time Markov
chain](https://en.wikipedia.org/wiki/Continuous-time_Markov_chain) by
estimating exponential holding times at each state and the discrete jump
probabilities given a transition takes place. We will use the
memorylessness of the exponential distribution to allow us to analyze
the recorded data row by row,

In this formulation:the time spent at state $i$ is distributed
exponential with parameter $\lambda_{i} > 0$.

- Observing a state $i$ to $i$ transition while waiting $t$ time units
  is given by how much mass of the exponential distribution is at least
  $t$. For the [exponential
  distribution](https://en.wikipedia.org/wiki/Exponential_distribution)
  this is $exp(-\lambda_{i} t)$.
- Observing a state $i$ to $j$ ($j$ different than $i$) transition at an
  unknown intermediate time $z$ such that $0 <= z <= t$ happens with
  probability given by waiting until time $z$ in state $i$, jumping from
  $i$ to $j$ (itself with probability $P[i, j]$) and then waiting in
  state $j$ for time $t - z$. For a given $z$ this probability is
  $(\lambda_{i} exp(-\lambda_{i} z)) P[i, j] (\lambda_{j} exp(-\lambda_{j} (t - z)))$.
  As we don’t know $t$ we integrate it out. The solution in this case is
  (with the correct convention when $\lambda_i = \lambda_j$) then our
  solution is $P[i, j] I$ where:

$$
I(t)=\int_{0}^{t}\bigl(\lambda_i e^{-\lambda_i z}\bigr)\bigl(\lambda_j e^{-\lambda_j (t-z)}\bigr)\,dz
$$

For $\lambda_i \neq \lambda_j$, $$
I(t) = \frac{\lambda_i \lambda_j}{\lambda_i - \lambda_j}\,\Bigl(e^{-\lambda_j t} - e^{-\lambda_i t}\Bigr).
$$

For the equal–rate case $\lambda_i = \lambda_j = \lambda$, $$
I(t) = \lambda^{2} t e^{-\lambda t}.
$$

It is a bit delicate to argue why integrating out is a correct step. But
assuming that let’s proceed.

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
   array[n_states - 1] simplex[n_states - 1] P;
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
          if (abs(lambda[state[i]] - lambda[state[i-1]]) > 1e-5 ) {
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
             v = (v + 1e-6) * (P[state[i-1], state[i] - 1] + 1e-6);
          } else {
             v = (v + 1e-6) * (P[state[i-1], state[i]] + 1e-6);
          }
       }
       target += log(v);
     }
  }
}
"
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
model = stan_model(
  model_code=stan_src
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

    ##     lambda[1] lambda[2] lambda[3]    P[1,1]    P[2,1]    P[3,1]    P[1,2]
    ## 1   0.1112005 0.8253202 0.5958462 0.8247118 0.4635543 0.1229196 0.1723421
    ## 15  0.1158650 0.8190166 0.6244339 0.8180139 0.4332962 0.2656353 0.1806127
    ## 62  0.1093429 0.8361757 0.6039513 0.8213030 0.4394677 0.1933338 0.1760160
    ## 82  0.1184011 0.8868717 0.6121329 0.8123223 0.4354987 0.3389126 0.1812193
    ## 83  0.1172491 0.8818320 0.5526092 0.8073599 0.4171884 0.3176605 0.1845978
    ## 110 0.1145118 0.8629383 0.5904544 0.8266976 0.4734864 0.1795991 0.1726539
    ##        P[2,2]    P[3,2]       P[1,3]      P[2,3]     P[3,3]      lp__
    ## 1   0.5261660 0.8337668 0.0029461263 0.010279601 0.04331364 -1588.651
    ## 15  0.5652688 0.6609091 0.0013734682 0.001435062 0.07345554 -1588.938
    ## 62  0.5556556 0.7279863 0.0026809532 0.004876699 0.07867999 -1587.946
    ## 82  0.5555539 0.5258112 0.0064584010 0.008947387 0.13527624 -1588.696
    ## 83  0.5720959 0.5940018 0.0080422367 0.010715687 0.08833766 -1588.672
    ## 110 0.5049176 0.7314418 0.0006485391 0.021595946 0.08895905 -1588.885

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
       step_matrix[i, j] = as.numeric(res_row[paste0('P[', i, ',', js, ']')])
     }
  }
}

step_matrix
```

    ##           [,1]      [,2]      [,3]        [,4]
    ## [1,] 0.0000000 0.8162774 0.1796438 0.004078781
    ## [2,] 0.4553225 0.0000000 0.5350999 0.009577607
    ## [3,] 0.2496014 0.7001581 0.0000000 0.050240517
    ## [4,] 0.0000000 0.0000000 0.0000000 0.000000000

``` r
q_matrix = step_matrix
for (j in 1:(n_states - 1)) {
  # divide by expected hold time (1/lambda)
  q_matrix[, j] = q_matrix[, j] * res_row[paste0('lambda[', j, ']')]
}
diag = -rowSums(q_matrix)
for (j in 1:(n_states - 1)) {
  q_matrix[j, j] = diag[j]
}

q_matrix
```

    ##             [,1]       [,2]       [,3]        [,4]
    ## [1,] -0.82235760  0.7075297  0.1107491 0.004078781
    ## [2,]  0.05219068 -0.3916535  0.3298852 0.009577607
    ## [3,]  0.02861020  0.6068803 -0.6857310 0.050240517
    ## [4,]  0.00000000  0.0000000  0.0000000 0.000000000
