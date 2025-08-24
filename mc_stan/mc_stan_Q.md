stan_ex
================
2025-08-23

Working the problem shared in: [J. Rickert, “Multistate Models for
Medical
Applications”](https://rviews.rstudio.com/2023/04/19/multistate-models-for-medical-applications/).

Attempt at a Q solution. A different “assume no unobserved transitions”
solution can be found
[here](https://github.com/WinVector/Examples/blob/main/mc_stan/mc_stan.md).

``` r
library(msm)
library(rstan)
library(cdata)
library(ggplot2)
```

``` r
forward_only = FALSE
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
if (forward_only) {
  while(TRUE) {
    regressions = c(FALSE, (diff(cav$pt_idx) == 0) & (diff(cav$state) < 0))
    if (sum(regressions) <= 0) {
      break
    }
    cav = cav[regressions == FALSE, , drop=FALSE]
  }
}
```

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

We encode this in Q-form where a state `i` to state `j` transition
(`i=j` allowed) after time `t` is observed with probability
`exp(t Q)[i, j]`.

We model state 4 as absorbing. We can perform the analysis with
different assumptions.

Let’s translate this into Stan as distributional statements.

``` r
stan_src = "
data {
  int<lower=0, upper=1> forward_only;
  int<lower=1> m_examples;
  int<lower=2> n_states;
  int<lower=1> n_patients;
  array[m_examples] int<lower=1, upper=n_patients> pt_idx;
  vector[m_examples] years;
  array[m_examples] int<lower=1, upper=n_states> state;
}
parameters {
  matrix<lower=0>[n_states - 1, n_states] Qd;
}
transformed parameters {
  matrix[n_states, n_states] Q;
  for (i in 1:n_states - 1) {
    for (j in 1:n_states) {
      if ( ((forward_only==1) && (i < j)) || ((forward_only==0) && (i != j)) ) {
        Q[i, j] = Qd[i, j];
      } else {
        Q[i, j] = 0;
      }
    }
  }
  for (j in 1:n_states) {
    Q[n_states , j] = 0;
  }
  for (i in 1:n_states - 1) {
    for (j in 1:n_states) {
      if (i != j) {
        Q[i, i] = Q[i, i] - Qd[i, j];
      }
    }
  }
}
model {
  // diffuse priors
  for (i in 1:n_states - 1) {
    for (j in 1:n_states) {
       Qd[i, j] ~ exponential(0.01);
    }
  }
  // relation to observations
  for (i in 2:m_examples) {
     if ((pt_idx[i-1] == pt_idx[i]) && (state[i - 1] < n_states)) {
       real t;
       matrix[n_states, n_states] expQ;
       real pij;
       t = years[i] - years[i-1];
       expQ = matrix_exp( t * Q );
       pij = expQ[state[i-1], state[i]];
       target += log(pij + 1e-6);
     }
  }
}
"
```

Let’s use Stan to find a set of parameters for which the observations
are likely.

``` r
model = stan_model(
  model_code=stan_src
)
```

``` r
stan_data <- list(
  forward_only = if (forward_only) 1 else 0,
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
  warmup = 500,               # number of warmup iterations per chain
  iter = 1000,                # total number of iterations per chain
  pars = "Q",
  # refresh = 0                # no progress shown
))
```

``` r
res = res[res$lp__ >= quantile(res$lp__, 0.9), , drop=FALSE]
res_row = colMeans(res)
```

``` r
head(res)
```

    ##        Q[1,1]    Q[2,1]      Q[3,1] Q[4,1]    Q[1,2]     Q[2,2]    Q[3,2]
    ## 10 -0.1747797 0.2444584 0.022114062      0 0.1239382 -0.6443086 0.1011909
    ## 12 -0.1926914 0.2268416 0.016813758      0 0.1432877 -0.6322553 0.1382339
    ## 52 -0.1846018 0.2319540 0.019818213      0 0.1348084 -0.6289951 0.2047384
    ## 56 -0.1736322 0.2553609 0.014757069      0 0.1259770 -0.6577024 0.1860791
    ## 67 -0.1769937 0.2479096 0.002912616      0 0.1282249 -0.5929378 0.1473756
    ## 76 -0.1856984 0.2749688 0.007888328      0 0.1283586 -0.6521430 0.1677132
    ##    Q[4,2]      Q[1,3]    Q[2,3]     Q[3,3] Q[4,3]     Q[1,4]     Q[2,4]
    ## 10      0 0.002827728 0.3090444 -0.5020005      0 0.04801382 0.09080577
    ## 12      0 0.001605071 0.3288552 -0.4921926      0 0.04779863 0.07655847
    ## 52      0 0.000614109 0.3189977 -0.5598363      0 0.04917934 0.07804344
    ## 56      0 0.002429527 0.3023400 -0.5790168      0 0.04522563 0.10000155
    ## 67      0 0.003084828 0.2564211 -0.4734320      0 0.04568390 0.08860712
    ## 76      0 0.006534632 0.2783546 -0.5236316      0 0.05080524 0.09881956
    ##       Q[3,4] Q[4,4]      lp__
    ## 10 0.3786955      0 -2008.251
    ## 12 0.3371449      0 -2009.475
    ## 52 0.3352797      0 -2009.137
    ## 56 0.3781807      0 -2009.313
    ## 67 0.3231438      0 -2009.183
    ## 76 0.3480300      0 -2009.342

We now pull out an estimate of the so-called Q matrix.

``` r
n_states = max(cav$state)
Q = matrix(0, nrow=n_states, ncol=n_states)
for (i in 1:(n_states - 1)) {
  for (j in 1:n_states) {
       Q[i, j] = as.numeric(res_row[paste0('Q[', i, ',', j, ']')])
     }
}

Q
```

    ##             [,1]       [,2]       [,3]       [,4]
    ## [1,] -0.17573062  0.1241915  0.0030183 0.04852079
    ## [2,]  0.23297446 -0.6128267  0.2990639 0.08078832
    ## [3,]  0.02035461  0.1444356 -0.5053547 0.34056448
    ## [4,]  0.00000000  0.0000000  0.0000000 0.00000000

It is a standard argument that the probability of observing a patient
starting in state $i$ being in state $j$ at time $t$ is then
$\text{exp}(t Q)[i, j]$. An example of the `0.1` year situation is as
follows.

``` r
Matrix::expm(0.1 * Q)
```

    ## 4 x 4 Matrix of class "dgeMatrix"
    ##             [,1]       [,2]         [,3]        [,4]
    ## [1,] 0.982720988 0.01194349 0.0004696576 0.004865867
    ## [2,] 0.022430370 0.94089943 0.0282871558 0.008383042
    ## [3,] 0.002128799 0.01367201 0.9509252536 0.033273934
    ## [4,] 0.000000000 0.00000000 0.0000000000 1.000000000

As is usual with exponents, the `k* 0.1` year estimate is the `k'th`
power of the `0.1` year estimate.

``` r
Matrix::expm(3 * 0.1 * Q) - (Matrix::expm(0.1 * Q) %*% Matrix::expm(0.1 * Q) %*% Matrix::expm(0.1 * Q))
```

    ## 4 x 4 Matrix of class "dgeMatrix"
    ##               [,1]         [,2]          [,3]          [,4]
    ## [1,] -3.330669e-16 6.938894e-18  0.000000e+00 -1.734723e-18
    ## [2,]  0.000000e+00 4.440892e-16  1.387779e-17  1.387779e-17
    ## [3,] -1.734723e-18 6.938894e-18 -2.220446e-16  0.000000e+00
    ## [4,]  0.000000e+00 0.000000e+00  0.000000e+00  0.000000e+00

Notice we have not referred to the [Kolmogorov
equations](https://en.wikipedia.org/wiki/Kolmogorov_equations#Continuous-time_Markov_chains),
instead attempting to infer parameters that entail a Q-matrix which we
can use to build detailed summaries.

``` r
time_frame = data.frame(
  year = seq(from=0, to=10, by=0.1),
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

![](mc_stan_Q_files/figure-gfm/unnamed-chunk-17-1.png)<!-- -->
