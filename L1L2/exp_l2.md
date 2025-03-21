L1/L2 Metric Agreement
================
2023-06-06

Barry Rowlingson and John Mount asked the following question.

> For a positive integer $n$, take $v_1$, $v_2$ vectors in
> $\mathbb{R}^n$ with each coordinate generated IID normal mean zero,
> standard deviation 1. Call the probability that
> $(||v_1||_1 \ge ||v_2||_1) = (||v_1||_2 \ge ||v_2||_2)$ $p_n$. What is
> $\lim_{n \rightarrow \infty} p_n$?

Is this an obvious known result?

For $n = 1$ these to metrics are identical, so $p_1 = 1$. For large $n$
we expect disagreement, but strong correlation between the $L_1$ and
$L_2$ metrics above.

Let’s look at that empirically.

``` r
set.seed(2023)
library(parallel)


estimate_p_n <- function(dimension, experiment_reps = 1000000) {  # noisy empirical estimate
  f_l1 <- function(x) { sum(abs(x)) }
  f_l2 <- function(x) { sqrt(sum(x^2)) }  # sqrt() doesn't affect order, so could leave it out.
  # define our experiment
  experiment <- function(ignored_argument) { 
    s1 <- rnorm(dimension)
    s2 <- rnorm(dimension)
    (f_l1(s1) > f_l1(s2)) == (f_l2(s1) > f_l2(s2))  # value to return
  }
  # run our experiment many times, collecting results
  vec <- vapply(seq(experiment_reps), experiment, logical(1))
  # compute empirical estimate of p_dimension
  mean(vec)
}
```

$p_{100}$ is likely somewhere near the following.

``` r
estimate_p_n(100)
```

    ## [1] 0.886824

$p_{101}$ is likely somewhere near the following.

``` r
estimate_p_n(101)
```

    ## [1] 0.886648

A (noisy, empirical graph) of $p_n$ is given as follows.

``` r
d <- data.frame(
  dimension = seq(100)
)
d$p_dimension <- as.numeric(mclapply(
  d$dimension, 
  estimate_p_n, 
  mc.cores = detectCores()))
```

``` r
plot(d)
```

![](exp_l2_files/figure-gfm/unnamed-chunk-5-1.png)<!-- -->

We can also try for a more precise empirical estimate of the “L2/L1 AUC value.”

``` r
res_list <- mclapply(
  seq(100),
  function(...) {
    estimate_p_n(10000, experiment_reps = 1000000)
  },
  mc.cores = detectCores())
res <- mean(as.numeric(res_list))
res
```

    ## [1] 0.8854221

We have a solution deriving the above constant [here](https://github.com/WinVector/Examples/blob/main/L1L2/L1L2.ipynb).
