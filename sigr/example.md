[`sigr`](https://CRAN.R-project.org/package=sigr) is a simple [`R`](https://cran.r-project.org) package that conveniently formats a few statistics and their significance tests. This allows the analyst to use the correct test no matter what modeling package or procedure they use.

![](sigr.png)

Model Example
-------------

Let's take as our example the following linear relation between `x` and `y`:

``` r
library('sigr')
set.seed(353525)
d <- data.frame(x= rnorm(5))
d$y <- 2*d$x + 0.5*rnorm(nrow(d))
```

`stats::lm()` has among the most complete summaries of all models in `R`, so we easily get can see the quality of fit and its significance:

``` r
model <- lm(y~x, d=d)
summary(model)
```

    ## 
    ## Call:
    ## lm(formula = y ~ x, data = d)
    ## 
    ## Residuals:
    ##       1       2       3       4       5 
    ##  0.3292  0.3421  0.0344 -0.1671 -0.5387 
    ## 
    ## Coefficients:
    ##             Estimate Std. Error t value Pr(>|t|)   
    ## (Intercept)   0.4201     0.2933   1.432  0.24747   
    ## x             2.1117     0.2996   7.048  0.00587 **
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## Residual standard error: 0.4261 on 3 degrees of freedom
    ## Multiple R-squared:  0.943,  Adjusted R-squared:  0.9241 
    ## F-statistic: 49.67 on 1 and 3 DF,  p-value: 0.005871

`sigr::wrapFTest()` can render the relevant model quality summary.

``` r
cat(render(wrapFTest(model),
    pLargeCutoff=1))
```

**F Test** summary: (<i>R<sup>2</sup></i>=0.94, *F*(1,3)=50, *p*=0.0059).

Note: `sigr` reports the un-adjusted R-squared, as this is the one that significance is reported for in `summary::lm()`.

`sigr` also carries around the important summary components for use in code.

``` r
unclass(wrapFTest(model))
```

    ## $test
    ## [1] "F Test"
    ## 
    ## $numdf
    ## [1] 1
    ## 
    ## $dendf
    ## [1] 3
    ## 
    ## $FValue
    ## [1] 49.66886
    ## 
    ## $R2
    ## [1] 0.9430403
    ## 
    ## $pValue
    ## [1] 0.005871236

In this function `sigr` is much like `broom::glance()` or `modelr::rsquare()`.

``` r
broom::glance(model)
```

    ##   r.squared adj.r.squared     sigma statistic     p.value df    logLik
    ## 1 0.9430403     0.9240538 0.4261232  49.66886 0.005871236  2 -1.552495
    ##       AIC      BIC deviance df.residual
    ## 1 9.10499 7.933304 0.544743           3

``` r
modelr::rsquare(model, d)
```

    ## [1] 0.9430403

This is something like what is reported by `caret::train()` (where `caret` controls the model training process).

``` r
cr <- caret::train(y~x, d, 
                   method = 'lm')
```

    ## Loading required package: lattice

    ## Loading required package: ggplot2

    ## Warning in nominalTrainWorkflow(x = x, y = y, wts = weights, info =
    ## trainInfo, : There were missing values in resampled performance measures.

``` r
cr$results
```

    ##   intercept      RMSE  Rsquared    RMSESD   RsquaredSD
    ## 1      TRUE 0.9631662 0.9998162 0.6239989 0.0007577834

``` r
summary(cr$finalModel)
```

    ## 
    ## Call:
    ## lm(formula = .outcome ~ ., data = dat)
    ## 
    ## Residuals:
    ##      X1      X2      X3      X4      X5 
    ##  0.3292  0.3421  0.0344 -0.1671 -0.5387 
    ## 
    ## Coefficients:
    ##             Estimate Std. Error t value Pr(>|t|)   
    ## (Intercept)   0.4201     0.2933   1.432  0.24747   
    ## x             2.1117     0.2996   7.048  0.00587 **
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## Residual standard error: 0.4261 on 3 degrees of freedom
    ## Multiple R-squared:  0.943,  Adjusted R-squared:  0.9241 
    ## F-statistic: 49.67 on 1 and 3 DF,  p-value: 0.005871

(I presume `cr$results$Rsquared` is a model quality report and not a consistency of cross-validation procedure report. If it is a model quality report it is somehow inflated, perhaps by the resampling procedure. So I apologize for using either `caret::train()` or its results incorrectly. I did read the manual and examples.)

Data example
------------

The issue of taking summary statistics (and significances) from models include:

-   Working only from models limits you to models that include the statistic you want.
-   Working only from models is mostly "in-sample." You need additional procedures for test or hold-out data.

With `sigr` it is also easy to reconstruct quality and significance from the predictions, no matter where they came from (without needing the model data structures).

### In-sample example

``` r
d$pred <- predict(model, newdata = d)
```

``` r
cat(render(wrapFTest(d, 'pred', 'y'),
    pLargeCutoff=1))
```

**F Test** summary: (<i>R<sup>2</sup></i>=0.94, *F*(1,3)=50, *p*=0.0059).

In this mode it is a lot like `ModelMetrics::rmse()` or `caret::postResample()`.

``` r
ModelMetrics::rmse(d$y, d$pred)
```

    ## [1] 0.3300736

``` r
caret::postResample(d$y, d$pred)
```

    ##      RMSE  Rsquared 
    ## 0.3300736 0.9430403

Notice we reconstruct the summary statistic and significance, independent of the model data structures. This means the test is generic and can be used on any regression (modulo informing the significance model of the appropriate number of parameters). And also can be used on held-out or test data.

### Out of sample example

If we had more data we can look at the quality of the prediction on that data (though you have to take care in understanding the number of degrees of freedom is different for held-out data).

``` r
d2 <- data.frame(x= rnorm(5))
d2$y <- 2*d2$x + 0.5*rnorm(nrow(d2))
d2$pred <-  predict(model, newdata = d2)
```

``` r
cat(render(wrapFTest(d2, 'pred', 'y'),
    pLargeCutoff=1))
```

**F Test** summary: (<i>R<sup>2</sup></i>=0.76, *F*(1,3)=9.6, *p*=0.054).

### Exotic model example

We could have used `glmnet` instead of `lm`:

``` r
library("glmnet")
```

    ## Loading required package: Matrix

    ## Loading required package: foreach

    ## Loaded glmnet 2.0-5

``` r
d$one <- 1 # make sure we have at least 2 columns
xmat <- as.matrix(d[, c('one','x')])
glmnetModel <- cv.glmnet(xmat, d$y)
```

    ## Warning: Option grouped=FALSE enforced in cv.glmnet, since < 3 observations
    ## per fold

``` r
summary(glmnetModel)
```

    ##            Length Class  Mode     
    ## lambda     53     -none- numeric  
    ## cvm        53     -none- numeric  
    ## cvsd       53     -none- numeric  
    ## cvup       53     -none- numeric  
    ## cvlo       53     -none- numeric  
    ## nzero      53     -none- numeric  
    ## name        1     -none- character
    ## glmnet.fit 12     elnet  list     
    ## lambda.min  1     -none- numeric  
    ## lambda.1se  1     -none- numeric

``` r
d$predg <- as.numeric(predict(glmnetModel, 
                              newx= xmat))
```

``` r
cat(render(wrapFTest(d, 'predg', 'y'),
    pLargeCutoff=1))
```

**F Test** summary: (<i>R<sup>2</sup></i>=0.91, *F*(1,3)=30, *p*=0.012).

Plotting
--------

Because `sigr` can render to "`LaTex`" it can (when used in conjunction with `latex2exp`) also produce formatted titles for plots.

``` r
library("ggplot2")
library("latex2exp")


f <- paste0(format(model$coefficients['x'], digits= 3), 
            '*x + ',
            format(model$coefficients['(Intercept)'], digits= 3))
title <- paste0("linear y ~ ", f, " relation")
subtitle <- latex2exp::TeX(render(wrapFTest(d, 'pred', 'y'), 
                                          format= 'latex'))
ggplot(data=d, mapping=aes(x=pred, y=y)) + 
  geom_point() + geom_abline(color='blue') +
  xlab(f) +
  ggtitle(title, 
          subtitle= subtitle)
```

![](example_files/figure-markdown_github/plot-1.png)

Conclusion
----------

`sigr` computes a few statistics or summaries (with standard significance estimates) and returns the calculation in both machine readable and formatted forms. For non-standard summaries `sigr` includes some resampling methods for significance estimation. For formatting `sigr` tries to get near the formats specified by "The American Psychological Association." `sigr` works with models (such as `lm` and `glm(family='binomial')`) or data, and is a small package with few dependencies.
