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
  "x1"  , "x2", "y", "w1"  |
    0   , 0   , 0  , 20  |
    0   , 1   , 1  , 10  |
    1   , 0   , 0  , 20  |
    1   , 0   , 1  , 10  |
    1   , 1   , 0  , 10  )

scale <- sum((1-d$y) * d$w1) / sum(d$y * d$w1) - 1  # move to 50/50 prevalence
d$w2 <- d$w1 + scale * d$y * d$w1

# display table
knitr::kable(d)
```

|  x1 |  x2 |   y |  w1 |  w2 |
|----:|----:|----:|----:|----:|
|   0 |   0 |   0 |  20 |  20 |
|   0 |   1 |   1 |  10 |  25 |
|   1 |   0 |   0 |  20 |  20 |
|   1 |   0 |   1 |  10 |  25 |
|   1 |   1 |   0 |  10 |  10 |

``` r
sum(d$y * d$w1) / sum(d$w1)
```

    ## [1] 0.2857143

``` r
sum(d$y * d$w2) / sum(d$w2)
```

    ## [1] 0.5

``` r
m_a <- glm(
  y ~ x1 + x2,
  data = d,
  weights = w1,
  family = binomial())
# add in predictions
d$pred_m_a <- predict(
  m_a, newdata = d, type = 'response')

coef(m_a)
```

    ## (Intercept)          x1          x2 
    ##  -1.2055937  -0.3129307   1.3620590

``` r
m_b <- glm(
  y ~ x1 + x2,
  data = d,
  weights = w2,
  family = binomial())
# add in predictions
d$pred_m_b <- predict(
  m_b, newdata = d, type = 'response')

coef(m_b)
```

    ## (Intercept)          x1          x2 
    ##  -0.5512784   0.1168985   1.4347723

``` r
# display table
knitr::kable(d)
```

|  x1 |  x2 |   y |  w1 |  w2 |  pred_m_a |  pred_m_b |
|----:|----:|----:|----:|----:|----------:|----------:|
|   0 |   0 |   0 |  20 |  20 | 0.2304816 | 0.3655679 |
|   0 |   1 |   1 |  10 |  25 | 0.5390367 | 0.7075457 |
|   1 |   0 |   0 |  20 |  20 | 0.1796789 | 0.3930810 |
|   1 |   0 |   1 |  10 |  25 | 0.1796789 | 0.3930810 |
|   1 |   1 |   0 |  10 |  10 | 0.4609633 | 0.7311357 |

Now notice the relative order of the predictions in rows 1 and 5 are
reversed in model `m_b` relative to the order given by model `m_a`.

``` r
comps <- d[c(1, 4), qc(pred_m_a, pred_m_b)]
stopifnot(comps[1, 'pred_m_a'] != comps[2, 'pred_m_a'])
stopifnot(comps[1, 'pred_m_b'] != comps[2, 'pred_m_b'])
stopifnot((comps[1, 'pred_m_a'] >= comps[2, 'pred_m_a']) != (comps[1, 'pred_m_b'] >= comps[2, 'pred_m_b']))

knitr::kable(comps)
```

|     |  pred_m_a |  pred_m_b |
|:----|----------:|----------:|
| 1   | 0.2304816 | 0.3655679 |
| 4   | 0.1796789 | 0.3930810 |

This means no monotone correction that looks only at the predictions can
make the same adaptations as these two prevalence tailored models. And
that is our demonstration.

As a side note, notice each model is unbiased in the simple sense it
matches the expected value of the outcome *with respect to the data
weighting it was trained on*. This is part of the advantage of [tailored
models](https://win-vector.com/2020/10/10/upcoming-series-probability-model-homotopy/).

``` r
mean(d$y) - mean(d$pred_m_a)
```

    ## [1] 0.08203211

``` r
(sum(d$w2 * d$y) / sum(d$w2))  -  (sum(d$w2 * d$pred_m_b) / sum(d$w2))
```

    ## [1] 1.601275e-12

A censoring process that doesn’t change the prevalence tends not to show
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
large_size <- 100000
group_size <- 5
d_large <- d_expanded[sample.int(nrow(d_expanded), size=large_size, replace=TRUE) , , drop=FALSE]
d_large$presentation_group <- do.call(
  c, 
  lapply(
    seq(large_size / group_size), 
    function(group_i) {rep(group_i, group_size)}
    ))
d_large$row_id <- seq(large_size)
rownames(d_large) <- NULL
# mark random positive per group
d_sel <- d_large
d_sel$random_order <- runif(n=large_size)
d_sel <- d_sel[d_sel$y==1, , drop=FALSE]
d_sel <- d_sel[order(d_sel$presentation_group, d_sel$random_order), , drop=FALSE]
d_sel$sampled_positive <- c(
  TRUE, 
  d_sel$presentation_group[seq(2, nrow(d_sel))] != d_sel$presentation_group[seq(nrow(d_sel)-1)])
d_large$sampled_positive = FALSE
d_large$sampled_positive[d_sel$row_id[d_sel$sampled_positive]] = TRUE

write.csv(d_large, file='d_large.csv', row.names = FALSE)
```

``` r
knitr::kable(d_large[seq(10), , drop=FALSE])
```

|  x1 |  x2 |   y | presentation_group | row_id | sampled_positive |
|----:|----:|----:|-------------------:|-------:|:-----------------|
|   1 |   0 |   1 |                  1 |      1 | TRUE             |
|   0 |   1 |   1 |                  1 |      2 | FALSE            |
|   0 |   1 |   1 |                  1 |      3 | FALSE            |
|   1 |   0 |   0 |                  1 |      4 | FALSE            |
|   0 |   0 |   0 |                  1 |      5 | FALSE            |
|   0 |   1 |   1 |                  2 |      6 | TRUE             |
|   1 |   1 |   0 |                  2 |      7 | FALSE            |
|   0 |   1 |   1 |                  2 |      8 | FALSE            |
|   0 |   0 |   0 |                  2 |      9 | FALSE            |
|   0 |   0 |   0 |                  2 |     10 | FALSE            |

Effect if we supress some positives by changing them to negatives
(independently).

``` r
# limit down to at most one positive per group by changing outcomes (indpendently)
d_large_censored_changed <- d_large
d_large_censored_changed$y = d_large_censored_changed$y * d_large_censored_changed$sampled_positive
```

``` r
knitr::kable(d_large_censored_changed[seq(10), , drop=FALSE])
```

|  x1 |  x2 |   y | presentation_group | row_id | sampled_positive |
|----:|----:|----:|-------------------:|-------:|:-----------------|
|   1 |   0 |   1 |                  1 |      1 | TRUE             |
|   0 |   1 |   0 |                  1 |      2 | FALSE            |
|   0 |   1 |   0 |                  1 |      3 | FALSE            |
|   1 |   0 |   0 |                  1 |      4 | FALSE            |
|   0 |   0 |   0 |                  1 |      5 | FALSE            |
|   0 |   1 |   1 |                  2 |      6 | TRUE             |
|   1 |   1 |   0 |                  2 |      7 | FALSE            |
|   0 |   1 |   0 |                  2 |      8 | FALSE            |
|   0 |   0 |   0 |                  2 |      9 | FALSE            |
|   0 |   0 |   0 |                  2 |     10 | FALSE            |

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
    ##             Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept) -0.57495    0.01304  -44.08   <2e-16 ***
    ## x1           0.15270    0.01469   10.39   <2e-16 ***
    ## x2           1.46331    0.01570   93.19   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 138629  on 99999  degrees of freedom
    ## Residual deviance: 128249  on 99997  degrees of freedom
    ## AIC: 128255
    ## 
    ## Number of Fisher Scoring iterations: 4

``` r
p_large <- predict(m_large, newdata=d, type='response')
```

``` r
# fit on large censored sample
m_large_censored_changed <- glm(
  y ~ x1 + x2,
  data = d_large_censored_changed,
  family = binomial())

summary(m_large_censored_changed)
```

    ## 
    ## Call:
    ## glm(formula = y ~ x1 + x2, family = binomial(), data = d_large_censored_changed)
    ## 
    ## Coefficients:
    ##             Estimate Std. Error  z value Pr(>|z|)    
    ## (Intercept) -1.80525    0.01667 -108.282  < 2e-16 ***
    ## x1           0.07393    0.01780    4.153 3.28e-05 ***
    ## x2           0.83507    0.01785   46.772  < 2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 98192  on 99999  degrees of freedom
    ## Residual deviance: 95748  on 99997  degrees of freedom
    ## AIC: 95754
    ## 
    ## Number of Fisher Scoring iterations: 4

``` r
p_large_censored_changed <- predict(m_large_censored_changed, newdata=d, type='response')
```

``` r
c_large_censored_changed <- data.frame(
  x1=d$x1,
  x2=d$x2,
  y=d$y,
  p_large=p_large, 
  p_large_censored_changed=p_large_censored_changed)

knitr::kable(c_large_censored_changed)
```

|  x1 |  x2 |   y |   p_large | p_large_censored_changed |
|----:|----:|----:|----------:|-------------------------:|
|   0 |   0 |   0 | 0.3600963 |                0.1412134 |
|   0 |   1 |   1 | 0.7085520 |                0.2748457 |
|   1 |   0 |   0 | 0.3959788 |                0.1504196 |
|   1 |   0 |   1 | 0.3959788 |                0.1504196 |
|   1 |   1 |   0 | 0.7390544 |                0.2898236 |

``` r
# comps_censored_changed <- c_large_censored_changed[c(1, 2), , drop=FALSE]
# stopifnot(comps_censored_changed[1, 'p_large'] != comps_censored_changed[2, 'p_large'])
# stopifnot(comps_censored_changed[1, 'p_large_censored_changed'] != comps_censored_changed[2, 'p_large_censored_changed'])
# stopifnot((comps_censored_changed[1, 'p_large'] >= comps_censored_changed[2, 'p_large_censored_changed']) != (comps_censored_changed[1, 'p_large'] >= comps_censored_changed[2, 'p_large_censored_changed']))
# 
# knitr::kable(comps_censored_changed)
```

Effect if we suppress some positives by deletign rows (independently).

``` r
# limit down to at most one positive per group by censoring out some positive rows
d_large_censored_deleted <- d_large[d_large$sampled_positive | (d_large$y == 0), , drop=FALSE]
```

``` r
knitr::kable(d_large_censored_deleted[seq(10), , drop=FALSE])
```

|     |  x1 |  x2 |   y | presentation_group | row_id | sampled_positive |
|:----|----:|----:|----:|-------------------:|-------:|:-----------------|
| 1   |   1 |   0 |   1 |                  1 |      1 | TRUE             |
| 4   |   1 |   0 |   0 |                  1 |      4 | FALSE            |
| 5   |   0 |   0 |   0 |                  1 |      5 | FALSE            |
| 6   |   0 |   1 |   1 |                  2 |      6 | TRUE             |
| 7   |   1 |   1 |   0 |                  2 |      7 | FALSE            |
| 9   |   0 |   0 |   0 |                  2 |      9 | FALSE            |
| 10  |   0 |   0 |   0 |                  2 |     10 | FALSE            |
| 11  |   0 |   1 |   1 |                  3 |     11 | TRUE             |
| 12  |   1 |   0 |   0 |                  3 |     12 | FALSE            |
| 13  |   0 |   0 |   0 |                  3 |     13 | FALSE            |

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
    ##             Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept) -0.57495    0.01304  -44.08   <2e-16 ***
    ## x1           0.15270    0.01469   10.39   <2e-16 ***
    ## x2           1.46331    0.01570   93.19   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 138629  on 99999  degrees of freedom
    ## Residual deviance: 128249  on 99997  degrees of freedom
    ## AIC: 128255
    ## 
    ## Number of Fisher Scoring iterations: 4

``` r
p_large <- predict(m_large, newdata=d, type='response')
```

``` r
# fit on large censored sample
m_large_censored_deleted <- glm(
  y ~ x1 + x2,
  data = d_large_censored_deleted,
  family = binomial())

summary(m_large_censored_deleted)
```

    ## 
    ## Call:
    ## glm(formula = y ~ x1 + x2, family = binomial(), data = d_large_censored_deleted)
    ## 
    ## Coefficients:
    ##             Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept) -1.24808    0.01501  -83.16   <2e-16 ***
    ## x1          -0.31413    0.01788  -17.57   <2e-16 ***
    ## x2           1.39280    0.01833   75.98   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 82034  on 69288  degrees of freedom
    ## Residual deviance: 75654  on 69286  degrees of freedom
    ## AIC: 75660
    ## 
    ## Number of Fisher Scoring iterations: 4

``` r
p_large_censored_deleted <- predict(m_large_censored_deleted, newdata=d, type='response')
```

``` r
c_large_censored_deleted <- data.frame(
  x1=d$x1,
  x2=d$x2,
  y=d$y,
  p_large=p_large, 
  p_large_censored_deleted=p_large_censored_deleted)

knitr::kable(c_large_censored_deleted)
```

|  x1 |  x2 |   y |   p_large | p_large_censored_deleted |
|----:|----:|----:|----------:|-------------------------:|
|   0 |   0 |   0 | 0.3600963 |                0.2230332 |
|   0 |   1 |   1 | 0.7085520 |                0.5361175 |
|   1 |   0 |   0 | 0.3959788 |                0.1733301 |
|   1 |   0 |   1 | 0.3959788 |                0.1733301 |
|   1 |   1 |   0 | 0.7390544 |                0.4577489 |

``` r
# comps_censored_deleted <- c_large_censored_deleted[c(1, 2), , drop=FALSE]
# stopifnot(comps_censored_deleted[1, 'p_large'] != comps_censored_deleted[2, 'p_large'])
# stopifnot(comps_censored_deleted[1, 'p_large_censored_deleted'] != comps_censored_deleted[2, 'p_large_censored_deleted'])
# stopifnot((comps_censored_deleted[1, 'p_large'] >= comps_censored_deleted[2, 'p_large_censored_deleted']) != (comps_censored_deleted[1, 'p_large'] >= comps_censored_deleted[2, 'p_large_censored_deleted']))
# 
# knitr::kable(comps_censored_deleted)
```
