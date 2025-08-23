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

For $\lambda_i \neq \lambda_j$,

$$
I(t) = \frac{\lambda_i \lambda_j}{\lambda_i - \lambda_j}\,\Bigl(e^{-\lambda_j t} - e^{-\lambda_i t}\Bigr).
$$

For the equal–rate case $\lambda_i = \lambda_j = \lambda$,

$$
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

    ##    lambda[1] lambda[2] lambda[3]    P[1,1]    P[2,1]    P[3,1]    P[1,2]
    ## 7  0.1123928 0.8107043 0.5702379 0.8213162 0.4920084 0.2146823 0.1775270
    ## 28 0.1092454 0.8688491 0.5751543 0.8374736 0.4708126 0.2244265 0.1576518
    ## 55 0.1119164 0.8015940 0.6516123 0.8096482 0.4021262 0.2441190 0.1825884
    ## 58 0.1159888 0.8752488 0.6418255 0.8422126 0.4230694 0.2340259 0.1540897
    ## 65 0.1140669 0.8004209 0.5787513 0.8122135 0.4540259 0.2804119 0.1846411
    ## 66 0.1124174 0.8693859 0.6179292 0.8284956 0.5318478 0.2312035 0.1693184
    ##       P[2,2]    P[3,2]      P[1,3]      P[2,3]     P[3,3]      lp__
    ## 7  0.4987629 0.7288027 0.001156786 0.009228682 0.05651496 -1588.638
    ## 28 0.5157689 0.6609712 0.004874563 0.013418447 0.11460227 -1588.443
    ## 55 0.5829153 0.6702733 0.007763368 0.014958524 0.08560772 -1588.992
    ## 58 0.5699624 0.7284082 0.003697739 0.006968245 0.03756588 -1587.817
    ## 65 0.5430947 0.6886308 0.003145411 0.002879395 0.03095730 -1588.540
    ## 66 0.4564130 0.7519988 0.002186013 0.011739175 0.01679769 -1588.782

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
    ## [1,] 0.0000000 0.8169563 0.1790582 0.003985539
    ## [2,] 0.4561042 0.0000000 0.5340262 0.009869612
    ## [3,] 0.2485218 0.7013695 0.0000000 0.050108793
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
    ## [1,] -0.82266104  0.7080739  0.1106016 0.003985539
    ## [2,]  0.05234468 -0.3920744  0.3298601 0.009869612
    ## [3,]  0.02852153  0.6078923 -0.6865226 0.050108793
    ## [4,]  0.00000000  0.0000000  0.0000000 0.000000000
