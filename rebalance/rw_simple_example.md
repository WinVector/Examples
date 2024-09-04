rw_simple_example
================

Support code for the article [“Tailored Models are Not The Same as
Simple
Corrections”](https://win-vector.com/2020/10/11/tailored-models-are-not-the-same-as-simple-corrections/).

``` r
# attach our packages
library(wrapr)

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
d[c(1, 5), qc(pred_m_0.29, pred_m_0.50)]
```

    ##   pred_m_0.29 pred_m_0.50
    ## 1   0.2304816   0.3655679
    ## 5   0.1796789   0.3930810

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
