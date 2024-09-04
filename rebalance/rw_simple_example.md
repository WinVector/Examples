rw_simple_example
================

Support code for the article [“Tailored Models are Not The Same as
Simple
Corrections”](https://win-vector.com/2020/10/11/tailored-models-are-not-the-same-as-simple-corrections/).

``` r
# attach our packages
library(wrapr)
set.seed(2024)


# build our example data
# modeling y as a function of x1 and x2 (plus intercept)
d <- wrapr::build_frame(
  "x1"  , "x2", "y", "w1", "w2" |
    0   , 0   , 0  , 2   , 4    |
    0   , 1   , 1  , 1   , 5    |
    1   , 0   , 0  , 2   , 4    |
    1   , 0   , 1  , 1   , 5    |
    1   , 1   , 0  , 1   , 2    )

# display table
knitr::kable(d)
```

|  x1 |  x2 |   y |  w1 |  w2 |
|----:|----:|----:|----:|----:|
|   0 |   0 |   0 |   2 |   4 |
|   0 |   1 |   1 |   1 |   5 |
|   1 |   0 |   0 |   2 |   4 |
|   1 |   0 |   1 |   1 |   5 |
|   1 |   1 |   0 |   1 |   2 |

``` r
# fit a model at prevalence 0.2857143
m_0.29 <- glm(
  y ~ x1 + x2,
  data = d,
  weights = w1,
  family = binomial())
# add in predictions
d$pred_m_0.29 <- predict(
  m_0.29, newdata = d, type = 'response')

coef(m_0.29)
```

    ## (Intercept)          x1          x2 
    ##  -1.2055937  -0.3129307   1.3620590

``` r
# fit a model at prevalence 0.5
m_0.50 <- glm(
  y ~ x1 + x2,
  data = d,
  weights = w2,
  family = binomial())
# add in predictions
d$pred_m_0.50 <- predict(
  m_0.50, newdata = d, type = 'response')

coef(m_0.50)
```

    ## (Intercept)          x1          x2 
    ##  -0.5512784   0.1168985   1.4347723

``` r
# display table
knitr::kable(d)
```

|  x1 |  x2 |   y |  w1 |  w2 | pred_m_0.29 | pred_m_0.50 |
|----:|----:|----:|----:|----:|------------:|------------:|
|   0 |   0 |   0 |   2 |   4 |   0.2304816 |   0.3655679 |
|   0 |   1 |   1 |   1 |   5 |   0.5390367 |   0.7075457 |
|   1 |   0 |   0 |   2 |   4 |   0.1796789 |   0.3930810 |
|   1 |   0 |   1 |   1 |   5 |   0.1796789 |   0.3930810 |
|   1 |   1 |   0 |   1 |   2 |   0.4609633 |   0.7311357 |

Now notice the relative order of the predictions in rows 1 and 5 are
reversed in model `m_0.50` relative to the order given by model
`m_0.29`.

``` r
comps <- d[c(1, 3), qc(pred_m_0.29, pred_m_0.50)]
stopifnot(comps[1, 'pred_m_0.29'] != comps[2, 'pred_m_0.29'])
stopifnot(comps[1, 'pred_m_0.50'] != comps[2, 'pred_m_0.50'])
stopifnot((comps[1, 'pred_m_0.29'] >= comps[2, 'pred_m_0.29']) != (comps[1, 'pred_m_0.50'] >= comps[2, 'pred_m_0.50']))

knitr::kable(comps)
```

|     | pred_m_0.29 | pred_m_0.50 |
|:----|------------:|------------:|
| 1   |   0.2304816 |   0.3655679 |
| 3   |   0.1796789 |   0.3930810 |

This means no monotone correction that looks only at the predictions can
make the same adaptations as these two prevalence tailored models. And
that is our demonstration.

As a side note, notice each model is unbiased in the simple sense it
matches the expected value of the outcome *with respect to the data
weighting it was trained on*. This is part of the advantage of [tailored
models](https://win-vector.com/2020/10/10/upcoming-series-probability-model-homotopy/).

``` r
mean(d$y) - mean(d$pred_m_0.29)
```

    ## [1] 0.08203211

``` r
(sum(d$w2 * d$y) / sum(d$w2))  -  (sum(d$w2 * d$pred_m_0.50) / sum(d$w2))
```

    ## [1] 1.110223e-16

A censoring process that doesn’t change the prevalance tends not to show
the above effect.

``` r
# replicate data frame by w2 weights
d_expanded <- lapply(
  seq(nrow(d)),
  function(row_i) {
    do.call(rbind, rep(list(d[row_i, c('x1', 'x2', 'y')]), d[row_i, 'w2']))
  })
d_expanded <- do.call(rbind, d_expanded)
rownames(d_expanded) <- NULL
# expand to a large re-sampling
large_size <- 1000000
group_size <- 5
d_large <- d_expanded[sample.int(nrow(d_expanded), size=large_size, replace=TRUE) , , drop=FALSE]
d_large$presentaiton_group <- do.call(
  c, 
  lapply(
    seq(large_size / group_size), 
    function(group_i) {rep(group_i, group_size)}
    ))
rownames(d_large) <- NULL
# mark random positive per group
d_sel <- d_large
d_sel$random_order <- runif(n=large_size)
d_sel$row_id <- seq(large_size)
d_sel <- d_sel[d_sel$y==1, , drop=FALSE]
d_sel <- d_sel[order(d_sel$presentaiton_group, d_sel$random_order), , drop=FALSE]
d_sel <- d_sel[
  c(TRUE, d_sel$presentaiton_group[seq(2, nrow(d_sel))] != d_sel$presentaiton_group[seq(nrow(d_sel)-1)]),
  , drop=FALSE]
# limit down to at most one positive per group by censoring out some positive rows
selected_indices <- sort(unique(c(d_sel$row_id, seq(large_size)[d_large$y == 0])))
d_large_censored <- d_large[selected_indices, , drop=FALSE]
rownames(d_large_censored) <- NULL
```

``` r
knitr::kable(d_large[seq(10), , drop=FALSE])
```

|  x1 |  x2 |   y | presentaiton_group |
|----:|----:|----:|-------------------:|
|   0 |   0 |   0 |                  1 |
|   0 |   1 |   1 |                  1 |
|   1 |   0 |   0 |                  1 |
|   1 |   0 |   1 |                  1 |
|   1 |   0 |   0 |                  1 |
|   0 |   1 |   1 |                  2 |
|   0 |   0 |   0 |                  2 |
|   1 |   0 |   0 |                  2 |
|   1 |   0 |   1 |                  2 |
|   1 |   0 |   1 |                  2 |

``` r
knitr::kable(d_large_censored[seq(10), , drop=FALSE])
```

|  x1 |  x2 |   y | presentaiton_group |
|----:|----:|----:|-------------------:|
|   0 |   0 |   0 |                  1 |
|   0 |   1 |   1 |                  1 |
|   1 |   0 |   0 |                  1 |
|   1 |   0 |   0 |                  1 |
|   0 |   0 |   0 |                  2 |
|   1 |   0 |   0 |                  2 |
|   1 |   0 |   1 |                  2 |
|   0 |   0 |   0 |                  3 |
|   1 |   0 |   0 |                  3 |
|   1 |   0 |   1 |                  3 |

``` r
# fit on large sample
m_large <- glm(
  y ~ x1 + x2,
  data = d_large,
  family = binomial())

summary(m_large)
```

    ## 
    ## Call:
    ## glm(formula = y ~ x1 + x2, family = binomial(), data = d_large)
    ## 
    ## Coefficients:
    ##              Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept) -0.549798   0.004118 -133.50   <2e-16 ***
    ## x1           0.119643   0.004630   25.84   <2e-16 ***
    ## x2           1.430469   0.004934  289.91   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 1386294  on 999999  degrees of freedom
    ## Residual deviance: 1285089  on 999997  degrees of freedom
    ## AIC: 1285095
    ## 
    ## Number of Fisher Scoring iterations: 4

``` r
p_large <- predict(m_large, newdata=d, type='response')
```

``` r
# fit on large censored sample
m_large_censored <- glm(
  y ~ x1 + x2,
  data = d_large_censored,
  family = binomial())

summary(m_large_censored)
```

    ## 
    ## Call:
    ## glm(formula = y ~ x1 + x2, family = binomial(), data = d_large_censored)
    ## 
    ## Coefficients:
    ##              Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept) -1.230174   0.004742 -259.45   <2e-16 ***
    ## x1          -0.322941   0.005638  -57.28   <2e-16 ***
    ## x2           1.359989   0.005778  235.36   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 821530  on 693457  degrees of freedom
    ## Residual deviance: 760066  on 693455  degrees of freedom
    ## AIC: 760072
    ## 
    ## Number of Fisher Scoring iterations: 4

``` r
p_large_censored <- predict(m_large_censored, newdata=d, type='response')
```

``` r
c_large <- data.frame(
  p_large=p_large, 
  p_large_censored=p_large_censored)

knitr::kable(c_large)
```

|   p_large | p_large_censored |
|----------:|-----------------:|
| 0.3659113 |        0.2261510 |
| 0.7069613 |        0.5324082 |
| 0.3940895 |        0.1746368 |
| 0.3940895 |        0.1746368 |
| 0.7311204 |        0.4518680 |

``` r
comps_censored <- c_large[c(1, 2), , drop=FALSE]
stopifnot(comps_censored[1, 'p_large'] != comps_censored[2, 'p_large'])
stopifnot(comps_censored[1, 'p_large_censored'] != comps_censored[2, 'p_large_censored'])
stopifnot((comps_censored[1, 'p_large'] >= comps_censored[2, 'p_large_censored']) != (comps_censored[1, 'pred_m_0.50'] >= comps_censored[2, 'p_large_censored']))

knitr::kable(comps_censored)
```

|   p_large | p_large_censored |
|----------:|-----------------:|
| 0.3659113 |        0.2261510 |
| 0.7069613 |        0.5324082 |
