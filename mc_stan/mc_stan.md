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

``` r
unique(cav$state)
```

    ## [1] 1 2 3 4

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
    ## 16 0.1117771 0.9107910 0.5563224 0.8072418 0.4877638 0.2070548 0.1906809
    ## 29 0.1182994 0.8390753 0.6383566 0.8218126 0.4308002 0.3448029 0.1769441
    ## 34 0.1175728 0.8122443 0.6120411 0.8254118 0.4283582 0.2521401 0.1724068
    ## 35 0.1135881 0.9452308 0.5998294 0.8046824 0.4883482 0.2357641 0.1892020
    ## 46 0.1062699 0.8623818 0.6326565 0.8310621 0.5165730 0.2510608 0.1661709
    ## 79 0.1203141 0.8602104 0.6567315 0.8159983 0.4484316 0.3092398 0.1754100
    ##      Pd[2,2]   Pd[3,2]     Pd[1,3]     Pd[2,3]    Pd[3,3]      lp__
    ## 16 0.5056185 0.7549363 0.002077362 0.006617621 0.03800892 -1588.393
    ## 29 0.5507399 0.5656126 0.001243263 0.018459903 0.08958451 -1588.724
    ## 34 0.5576029 0.6759211 0.002181409 0.014038981 0.07193871 -1587.897
    ## 35 0.5050987 0.7288428 0.006115601 0.006553083 0.03539309 -1588.339
    ## 46 0.4782064 0.7082499 0.002767005 0.005220656 0.04068934 -1588.756
    ## 79 0.5444161 0.6673174 0.008591729 0.007152224 0.02344288 -1588.126

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
    ## [1,] 0.0000000 0.8167639 0.1792965 0.003939604
    ## [2,] 0.4563015 0.0000000 0.5340446 0.009653838
    ## [3,] 0.2492236 0.7022662 0.0000000 0.048510225
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
    ## [1,] -0.82288941  0.7082904  0.1106595 0.003939604
    ## [2,]  0.05241097 -0.3916701  0.3296053 0.009653838
    ## [3,]  0.02862592  0.6089989 -0.6861351 0.048510225
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
    ## [1,] 0.921195520 0.06700413 0.01136186 0.0004384922
    ## [2,] 0.004978949 0.96272357 0.03127220 0.0010252821
    ## [3,] 0.002805482 0.05782530 0.93465034 0.0047188754
    ## [4,] 0.000000000 0.00000000 0.00000000 1.0000000000

As is usual with exponents, the `k* 0.1` year estimate is the `k'th`
power of the `0.1` year estimate.

``` r
Matrix::expm(3 * 0.1 * Q) - (Matrix::expm(0.1 * Q) %*% Matrix::expm(0.1 * Q) %*% Matrix::expm(0.1 * Q))
```

    ## 4 x 4 Matrix of class "dgeMatrix"
    ##               [,1]          [,2]          [,3]          [,4]
    ## [1,]  1.110223e-16 -2.775558e-17 -6.938894e-18  0.000000e+00
    ## [2,] -3.469447e-18 -3.330669e-16 -2.775558e-17 -4.336809e-19
    ## [3,] -1.734723e-18 -5.551115e-17 -4.440892e-16 -3.469447e-18
    ## [4,]  0.000000e+00  0.000000e+00  0.000000e+00  0.000000e+00

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

![](mc_stan_files/figure-gfm/unnamed-chunk-17-1.png)<!-- -->
