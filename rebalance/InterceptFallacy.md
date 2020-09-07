Intercept Fallacy
================

A common mis-understanding of linear regression and logistic regression
is that the intercept is thought to encode the unconditional mean or the
training data prevalence.

This is easily seen to not be the case. Consider the following example
in [R](https://www.r-project.org).

``` r
library(wrapr)
```

We set up our example data.

``` r
# build our example data
# modeling y as a function of x1 and x2 (plus intercept)

d <- wrapr::build_frame(
  "x1"  , "x2", "y" |
    0   , 0   , 0   |
    0   , 0   , 0   |
    0   , 1   , 1   |
    1   , 0   , 0   |
    1   , 0   , 0   |
    1   , 0   , 1   |
    1   , 1   , 0   )

knitr::kable(d)
```

| x1 | x2 | y |
| -: | -: | -: |
|  0 |  0 | 0 |
|  0 |  0 | 0 |
|  0 |  1 | 1 |
|  1 |  0 | 0 |
|  1 |  0 | 0 |
|  1 |  0 | 1 |
|  1 |  1 | 0 |

And let’s fit a logistic regression.

``` r
m <- glm(
  y ~ x1 + x2,
  data = d,
  family = binomial())

m$coefficients
```

    ## (Intercept)          x1          x2 
    ##  -1.2055937  -0.3129307   1.3620590

The probability encoded in the intercept term is given as follows.

``` r
pred <- predict(
  m, 
  newdata = data.frame(x1 = 0, x2 = 0), 
  type = 'response')

pred
```

    ##         1 
    ## 0.2304816

Notice the prediction 0.2304816 is neither the training outcome (`y`)
prevalence (0.2857143) nor the observed `y`-rate for rows that have `x1,
x2 = 0` (0).

The non-intercept coefficients *do* have an interpretation as the
expected change in log-odds ratio implied by a given variable (assuming
all other variables are held constant, which may *not* be a property of
the data\!). Also, the values non-intercept coefficients *added* to the
intercept predict the conditioned value of `y` with respect to each
variable (for details, please see
[here](https://win-vector.com/2011/09/14/the-simpler-derivation-of-logistic-regression/)).
