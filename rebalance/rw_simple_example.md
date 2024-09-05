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
  "x1"  , "x2", "y", "w1" |
    0   , 0   , 0  , 20   |
    0   , 1   , 1  , 10   |
    1   , 0   , 0  , 20   |
    1   , 0   , 1  , 10   |
    1   , 1   , 0  , 10   )

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
stopifnot((comps[1, 'pred_m_a'] >= comps[2, 'pred_m_a']) != 
            (comps[1, 'pred_m_b'] >= comps[2, 'pred_m_b']))

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

Expand data.

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
d_large$presentation_group <- do.call(
  c, 
  lapply(
    seq(large_size / group_size), 
    function(group_i) {rep(group_i, group_size)}
    ))
d_large$row_id <- seq(large_size)
rownames(d_large) <- NULL
```

``` r
# fuzz a bit
for (c in c('x1', 'x2')) {
    d_large[c] = d_large[c] + 0.1 * rnorm(n=nrow(d_large))
}
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
    ## (Intercept) -0.514676   0.004012 -128.28   <2e-16 ***
    ## x1           0.091548   0.004489   20.39   <2e-16 ***
    ## x2           1.370788   0.004807  285.19   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 1386294  on 999999  degrees of freedom
    ## Residual deviance: 1288274  on 999997  degrees of freedom
    ## AIC: 1288280
    ## 
    ## Number of Fisher Scoring iterations: 4

Noisily censor to top pick.

``` r
d_large$sort_order <- -predict(m_large, newdata=d_large, type='link') + 0.1 * rnorm(n=nrow(d_large))
```

``` r
# mark random positive per group
d_sel <- d_large
d_sel <- d_sel[d_sel$y==1, , drop=FALSE]
d_sel <- d_sel[order(d_sel$presentation_group, d_sel$sort_order), , drop=FALSE]
d_sel$sampled_positive <- c(
  TRUE, 
  d_sel$presentation_group[seq(2, nrow(d_sel))] != d_sel$presentation_group[seq(nrow(d_sel)-1)])
d_large$sampled_positive = FALSE
d_large$sampled_positive[d_sel$row_id[d_sel$sampled_positive]] = TRUE
```

``` r
write.csv(d_large[ , c('x1', 'x2', 'y', 'presentation_group', 'sampled_positive')], file='d_large.csv', row.names = FALSE)
```

``` r
knitr::kable(d_large[seq(10), , drop=FALSE])
```

|         x1 |         x2 |   y | presentation_group | row_id | sort_order | sampled_positive |
|-----------:|-----------:|----:|-------------------:|-------:|-----------:|:-----------------|
|  1.0386577 |  0.0086633 |   1 |                  1 |      1 |  0.4969384 | FALSE            |
|  0.0551755 |  0.8276934 |   1 |                  1 |      2 | -0.6626657 | FALSE            |
| -0.1832702 |  1.0036545 |   1 |                  1 |      3 | -0.8635774 | TRUE             |
|  1.0488625 | -0.2082705 |   0 |                  1 |      4 |  0.7071943 | FALSE            |
| -0.1306283 |  0.0941564 |   0 |                  1 |      5 |  0.3404483 | FALSE            |
|  0.1609292 |  1.0108265 |   1 |                  2 |      6 | -0.9143600 | FALSE            |
|  1.3039749 |  1.2159358 |   0 |                  2 |      7 | -1.3445031 | FALSE            |
|  0.0429537 |  1.0221667 |   1 |                  2 |      8 | -1.0887148 | TRUE             |
|  0.0912462 | -0.0900513 |   0 |                  2 |      9 |  0.7915774 | FALSE            |
| -0.1133648 | -0.0413047 |   0 |                  2 |     10 |  0.5067952 | FALSE            |

Effect if we suppress some positives by changing them to negatives
(largest score takes all).

``` r
# limit down to at most one positive per group by changing outcomes (largest score takes all)
d_large_censored_changed <- d_large
d_large_censored_changed$y = d_large_censored_changed$y * d_large_censored_changed$sampled_positive
```

``` r
knitr::kable(d_large_censored_changed[seq(10), , drop=FALSE])
```

|         x1 |         x2 |   y | presentation_group | row_id | sort_order | sampled_positive |
|-----------:|-----------:|----:|-------------------:|-------:|-----------:|:-----------------|
|  1.0386577 |  0.0086633 |   0 |                  1 |      1 |  0.4969384 | FALSE            |
|  0.0551755 |  0.8276934 |   0 |                  1 |      2 | -0.6626657 | FALSE            |
| -0.1832702 |  1.0036545 |   1 |                  1 |      3 | -0.8635774 | TRUE             |
|  1.0488625 | -0.2082705 |   0 |                  1 |      4 |  0.7071943 | FALSE            |
| -0.1306283 |  0.0941564 |   0 |                  1 |      5 |  0.3404483 | FALSE            |
|  0.1609292 |  1.0108265 |   0 |                  2 |      6 | -0.9143600 | FALSE            |
|  1.3039749 |  1.2159358 |   0 |                  2 |      7 | -1.3445031 | FALSE            |
|  0.0429537 |  1.0221667 |   1 |                  2 |      8 | -1.0887148 | TRUE             |
|  0.0912462 | -0.0900513 |   0 |                  2 |      9 |  0.7915774 | FALSE            |
| -0.1133648 | -0.0413047 |   0 |                  2 |     10 |  0.5067952 | FALSE            |

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
    ##              Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept) -2.141398   0.006037  -354.7   <2e-16 ***
    ## x1          -1.131305   0.006407  -176.6   <2e-16 ***
    ## x2           2.213397   0.006472   342.0   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 983224  on 999999  degrees of freedom
    ## Residual deviance: 733909  on 999997  degrees of freedom
    ## AIC: 733915
    ## 
    ## Number of Fisher Scoring iterations: 5

``` r
c_large_censored_changed <- data.frame(
  x1=d$x1,
  x2=d$x2,
  y=d$y,
  p_large=predict(m_large, newdata=d, type='response'), 
  p_large_censored_changed=predict(m_large_censored_changed, newdata=d, type='response'))

knitr::kable(c_large_censored_changed)
```

|  x1 |  x2 |   y |   p_large | p_large_censored_changed |
|----:|----:|----:|----------:|-------------------------:|
|   0 |   0 |   0 | 0.3740980 |                0.1051378 |
|   0 |   1 |   1 | 0.7018478 |                0.5179919 |
|   1 |   0 |   0 | 0.3957686 |                0.0365196 |
|   1 |   0 |   1 | 0.3957686 |                0.0365196 |
|   1 |   1 |   0 | 0.7206445 |                0.2574420 |

``` r
comps_censored_changed <- c_large_censored_changed[c(1, 4), , drop=FALSE]
stopifnot(comps_censored_changed[1, 'p_large'] != comps_censored_changed[2, 'p_large'])
stopifnot(comps_censored_changed[1, 'p_large_censored_changed'] != comps_censored_changed[2, 'p_large_censored_changed'])
stopifnot((comps_censored_changed[1, 'p_large'] >= comps_censored_changed[2, 'p_large']) != 
            (comps_censored_changed[1, 'p_large_censored_changed'] >= comps_censored_changed[2, 'p_large_censored_changed']))

knitr::kable(comps_censored_changed)
```

|     |  x1 |  x2 |   y |   p_large | p_large_censored_changed |
|:----|----:|----:|----:|----------:|-------------------------:|
| 1   |   0 |   0 |   0 | 0.3740980 |                0.1051378 |
| 4   |   1 |   0 |   1 | 0.3957686 |                0.0365196 |

Effect if we suppress some positives by deletign rows (independently).

``` r
# limit down to at most one positive per group by censoring out some positive rows
d_large_censored_deleted <- d_large[d_large$sampled_positive | (d_large$y == 0), , drop=FALSE]
```

``` r
knitr::kable(d_large_censored_deleted[seq(10), , drop=FALSE])
```

|     |         x1 |         x2 |   y | presentation_group | row_id | sort_order | sampled_positive |
|:----|-----------:|-----------:|----:|-------------------:|-------:|-----------:|:-----------------|
| 3   | -0.1832702 |  1.0036545 |   1 |                  1 |      3 | -0.8635774 | TRUE             |
| 4   |  1.0488625 | -0.2082705 |   0 |                  1 |      4 |  0.7071943 | FALSE            |
| 5   | -0.1306283 |  0.0941564 |   0 |                  1 |      5 |  0.3404483 | FALSE            |
| 7   |  1.3039749 |  1.2159358 |   0 |                  2 |      7 | -1.3445031 | FALSE            |
| 8   |  0.0429537 |  1.0221667 |   1 |                  2 |      8 | -1.0887148 | TRUE             |
| 9   |  0.0912462 | -0.0900513 |   0 |                  2 |      9 |  0.7915774 | FALSE            |
| 10  | -0.1133648 | -0.0413047 |   0 |                  2 |     10 |  0.5067952 | FALSE            |
| 12  |  0.9241317 |  0.0704743 |   0 |                  3 |     12 |  0.3950271 | FALSE            |
| 13  | -0.1233697 |  0.0379949 |   0 |                  3 |     13 |  0.3528725 | FALSE            |
| 14  | -0.0496189 |  1.0059239 |   1 |                  3 |     14 | -0.8503976 | TRUE             |

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
    ##              Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept) -1.648181   0.005606  -294.0   <2e-16 ***
    ## x1          -1.806179   0.007370  -245.1   <2e-16 ***
    ## x2           2.821850   0.007196   392.1   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 821580  on 693455  degrees of freedom
    ## Residual deviance: 533681  on 693453  degrees of freedom
    ## AIC: 533687
    ## 
    ## Number of Fisher Scoring iterations: 5

``` r
c_large_censored_deleted <- data.frame(
  x1=d$x1,
  x2=d$x2,
  y=d$y,
  p_large=predict(m_large, newdata=d, type='response'),
  p_large_censored_deleted=predict(m_large_censored_deleted, newdata=d, type='response'))

knitr::kable(c_large_censored_deleted)
```

|  x1 |  x2 |   y |   p_large | p_large_censored_deleted |
|----:|----:|----:|----------:|-------------------------:|
|   0 |   0 |   0 | 0.3740980 |                0.1613549 |
|   0 |   1 |   1 | 0.7018478 |                0.7638075 |
|   1 |   0 |   0 | 0.3957686 |                0.0306391 |
|   1 |   0 |   1 | 0.3957686 |                0.0306391 |
|   1 |   1 |   0 | 0.7206445 |                0.3469415 |

``` r
comps_censored_deleted <- c_large_censored_deleted[c(1, 4), , drop=FALSE]
stopifnot(comps_censored_deleted[1, 'p_large'] != comps_censored_deleted[2, 'p_large'])
stopifnot(comps_censored_deleted[1, 'p_large_censored_deleted'] != comps_censored_deleted[2, 'p_large_censored_deleted'])
stopifnot((comps_censored_deleted[1, 'p_large'] >= comps_censored_deleted[2, 'p_large']) != 
            (comps_censored_deleted[1, 'p_large_censored_deleted'] >= comps_censored_deleted[2, 'p_large_censored_deleted']))

knitr::kable(comps_censored_deleted)
```

|     |  x1 |  x2 |   y |   p_large | p_large_censored_deleted |
|:----|----:|----:|----:|----------:|-------------------------:|
| 1   |   0 |   0 |   0 | 0.3740980 |                0.1613549 |
| 4   |   1 |   0 |   1 | 0.3957686 |                0.0306391 |

Show all our predictions.

``` r
d$pred_all <- predict(m_large, newdata=d, type='response')
d$pred_all <- predict(m_large_censored_changed, newdata=d, type='response')
d$pred_all <- predict(m_large_censored_deleted, newdata=d, type='response')

knitr::kable(d)
```

|  x1 |  x2 |   y |  w1 |  w2 |  pred_m_a |  pred_m_b |  pred_all |
|----:|----:|----:|----:|----:|----------:|----------:|----------:|
|   0 |   0 |   0 |  20 |  20 | 0.2304816 | 0.3655679 | 0.1613549 |
|   0 |   1 |   1 |  10 |  25 | 0.5390367 | 0.7075457 | 0.7638075 |
|   1 |   0 |   0 |  20 |  20 | 0.1796789 | 0.3930810 | 0.0306391 |
|   1 |   0 |   1 |  10 |  25 | 0.1796789 | 0.3930810 | 0.0306391 |
|   1 |   1 |   0 |  10 |  10 | 0.4609633 | 0.7311357 | 0.3469415 |
