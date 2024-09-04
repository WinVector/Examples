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
  "x1"  , "x2", "y", "w2" |
    0   , 0   , 0  , 2    |
    0   , 0   , 0  , 2    |
    0   , 1   , 1  , 5    |
    1   , 0   , 0  , 2    |
    1   , 0   , 0  , 2    |
    1   , 0   , 1  , 5    |
    1   , 1   , 0  , 2    )

# display table
knitr::kable(d)
```

|  x1 |  x2 |   y |  w2 |
|----:|----:|----:|----:|
|   0 |   0 |   0 |   2 |
|   0 |   0 |   0 |   2 |
|   0 |   1 |   1 |   5 |
|   1 |   0 |   0 |   2 |
|   1 |   0 |   0 |   2 |
|   1 |   0 |   1 |   5 |
|   1 |   1 |   0 |   2 |

``` r
# fit a model at prevalence 0.2857143
m_0.29 <- glm(
  y ~ x1 + x2,
  data = d,
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

|  x1 |  x2 |   y |  w2 | pred_m_0.29 | pred_m_0.50 |
|----:|----:|----:|----:|------------:|------------:|
|   0 |   0 |   0 |   2 |   0.2304816 |   0.3655679 |
|   0 |   0 |   0 |   2 |   0.2304816 |   0.3655679 |
|   0 |   1 |   1 |   5 |   0.5390367 |   0.7075457 |
|   1 |   0 |   0 |   2 |   0.1796789 |   0.3930810 |
|   1 |   0 |   0 |   2 |   0.1796789 |   0.3930810 |
|   1 |   0 |   1 |   5 |   0.1796789 |   0.3930810 |
|   1 |   1 |   0 |   2 |   0.4609633 |   0.7311357 |

Now notice the relative order of the predictions in rows 1 and 5 are
reversed in model `m_0.50` relative to the order given by model
`m_0.29`.

``` r
comps <- d[c(1, 5), qc(pred_m_0.29, pred_m_0.50)]
stopifnot(comps[1, 'pred_m_0.29'] != comps[2, 'pred_m_0.29'])
stopifnot(comps[1, 'pred_m_0.50'] != comps[2, 'pred_m_0.50'])
stopifnot((comps[1, 'pred_m_0.29'] >= comps[2, 'pred_m_0.29']) != (comps[1, 'pred_m_0.50'] >= comps[2, 'pred_m_0.50']))

knitr::kable(comps)
```

|     | pred_m_0.29 | pred_m_0.50 |
|:----|------------:|------------:|
| 1   |   0.2304816 |   0.3655679 |
| 5   |   0.1796789 |   0.3930810 |

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

    ## [1] -1.165734e-14

``` r
(sum(d$w2 * d$y) / sum(d$w2))  -  (sum(d$w2 * d$pred_m_0.50) / sum(d$w2))
```

    ## [1] -2.88658e-15

A censoring process that doesn’t change the prevalance tends not to show
the above effect.

``` r
# replicate data frame by weights
d_expanded <- lapply(
  seq(nrow(d)),
  function(row_i) {
    do.call(rbind, rep(list(d[row_i, c('x1', 'x2', 'y')]), d[row_i, 'w2']))
  })
d_expanded <- do.call(rbind, d_expanded)
rownames(d_expanded) <- NULL
```

``` r
large_size <- 1000000
d_large <- d_expanded[sample.int(nrow(d_expanded), size=large_size, replace=TRUE) , , drop=FALSE]
d_large_censored <- d_large
d_large_censored$y <- d_large_censored$y * rbinom(n=large_size, prob=0.1, size=1)
```

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
    ##             Estimate Std. Error  z value Pr(>|z|)    
    ## (Intercept) -3.25698    0.00958 -339.964  < 2e-16 ***
    ## x1           0.07536    0.01007    7.481 7.39e-14 ***
    ## x2           0.65602    0.01008   65.103  < 2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 397154  on 999999  degrees of freedom
    ## Residual deviance: 392553  on 999997  degrees of freedom
    ## AIC: 392559
    ## 
    ## Number of Fisher Scoring iterations: 6

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
| 0.3659113 |        0.0370770 |
| 0.3659113 |        0.0370770 |
| 0.7069613 |        0.0690766 |
| 0.3940895 |        0.0398633 |
| 0.3940895 |        0.0398633 |
| 0.3940895 |        0.0398633 |
| 0.7311204 |        0.0740828 |
