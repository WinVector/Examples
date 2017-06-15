<!-- *.md is generated from *.Rmd. Please edit that file -->
Here is an absolutely *horrible* way to confuse yourself and get an inflated reported `R-squared` on a simple linear regression model in [`R`](https://www.r-project.org).

First let's set up our problem with a data set where the quantity to be predicted (`y`) has no real relation to the independent variable (`x`). We will first build our example data:

``` r
library("sigr")
library("broom")
set.seed(23255)

d <- data.frame(y= runif(100),
                x= ifelse(runif(100)>=0.5, 'a', 'b'),
                stringsAsFactors = FALSE)
```

Now let's build a model and look at the summary statistics returned as part of the model fitting process:

``` r
m1 <- lm(y~x, data=d)
t(broom::glance(m1))
```

    ##                        [,1]
    ## r.squared       0.002177326
    ## adj.r.squared  -0.008004538
    ## sigma           0.302851476
    ## statistic       0.213843593
    ## p.value         0.644796456
    ## df              2.000000000
    ## logLik        -21.432440763
    ## AIC            48.864881526
    ## BIC            56.680392084
    ## deviance        8.988463618
    ## df.residual    98.000000000

``` r
d$pred1 <- predict(m1, newdata = d)
```

I *strongly* prefer to directly calculate the the model performance statistics off the predictions (it lets us easily compare different modeling methods), so let's also do that also:

``` r
cat(render(sigr::wrapFTest(d, 'pred1', 'y'),
           format='markdown'))
```

**F Test** summary: (<i>R<sup>2</sup></i>=0.0022, *F*(1,98)=0.21, *p*=n.s.).

So far so good. Let's now remove the "intercept term" by adding the "`0+`" from the fitting command.

``` r
m2 <- lm(y~0+x, data=d)
t(broom::glance(m2))
```

    ##                        [,1]
    ## r.squared      7.524811e-01
    ## adj.r.squared  7.474297e-01
    ## sigma          3.028515e-01
    ## statistic      1.489647e+02
    ## p.value        1.935559e-30
    ## df             2.000000e+00
    ## logLik        -2.143244e+01
    ## AIC            4.886488e+01
    ## BIC            5.668039e+01
    ## deviance       8.988464e+00
    ## df.residual    9.800000e+01

``` r
d$pred2 <- predict(m2, newdata = d)
```

Uh oh. That *appeared* to vastly improve the reported `R-squared` and the significance ("`p.value`")!

That does not make sense, anything `m2` can do `m1` can also do. In fact the two models make essentially identical predictions, which we confirm below:

``` r
sum((d$pred1 - d$y)^2)
```

    ## [1] 8.988464

``` r
sum((d$pred2 - d$y)^2)
```

    ## [1] 8.988464

``` r
max(abs(d$pred1 - d$pred2))
```

    ## [1] 4.440892e-16

``` r
head(d)
```

    ##             y x     pred1     pred2
    ## 1 0.007509118 b 0.5098853 0.5098853
    ## 2 0.980353615 a 0.5380361 0.5380361
    ## 3 0.055880927 b 0.5098853 0.5098853
    ## 4 0.993814410 a 0.5380361 0.5380361
    ## 5 0.636617385 b 0.5098853 0.5098853
    ## 6 0.154032277 a 0.5380361 0.5380361

Let's double check the fit quality of the predictions.

``` r
cat(render(sigr::wrapFTest(d, 'pred2', 'y'),
           format='markdown'))
```

**F Test** summary: (<i>R<sup>2</sup></i>=0.0022, *F*(1,98)=0.21, *p*=n.s.).

Ah. The prediction fit quality is identical to the first time (as one would expect). This is yet another reason to directly calculate model fit quality from the predictions: it isolates you from any foibles of how the modeling software does it.

The answer to our puzzles of "what went wrong" is something we have written about before [here](http://www.win-vector.com/blog/2016/12/be-careful-evaluating-model-predictions/).

Roughly what is going on is:

If the fit formula sent `lm()` has no intercept (triggered by the "`0+`") notation then `summary.lm()` changes how it computes `r.squared` as follows (from `help(summary.lm)`):

<pre>
r.squared   R^2, the ‘fraction of variance explained by the model’,
              R^2 = 1 - Sum(R[i]^2) / Sum((y[i]- y*)^2),
            where y* is the mean of y[i] if there is an intercept and zero otherwise.
</pre>
This is pretty bad.

Then to add insult to injury the "`0+`" notation also changes how `R` encodes the categorical variable `x`.

Compare:

``` r
summary(m1)
```

    ## 
    ## Call:
    ## lm(formula = y ~ x, data = d)
    ## 
    ## Residuals:
    ##      Min       1Q   Median       3Q      Max 
    ## -0.53739 -0.23265 -0.02039  0.27247  0.47111 
    ## 
    ## Coefficients:
    ##             Estimate Std. Error t value Pr(>|t|)    
    ## (Intercept)  0.53804    0.04515  11.918   <2e-16 ***
    ## xb          -0.02815    0.06088  -0.462    0.645    
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## Residual standard error: 0.3029 on 98 degrees of freedom
    ## Multiple R-squared:  0.002177,   Adjusted R-squared:  -0.008005 
    ## F-statistic: 0.2138 on 1 and 98 DF,  p-value: 0.6448

``` r
summary(m2)
```

    ## 
    ## Call:
    ## lm(formula = y ~ 0 + x, data = d)
    ## 
    ## Residuals:
    ##      Min       1Q   Median       3Q      Max 
    ## -0.53739 -0.23265 -0.02039  0.27247  0.47111 
    ## 
    ## Coefficients:
    ##    Estimate Std. Error t value Pr(>|t|)    
    ## xa  0.53804    0.04515   11.92   <2e-16 ***
    ## xb  0.50989    0.04084   12.49   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## Residual standard error: 0.3029 on 98 degrees of freedom
    ## Multiple R-squared:  0.7525, Adjusted R-squared:  0.7474 
    ## F-statistic:   149 on 2 and 98 DF,  p-value: < 2.2e-16

Notice the second model directly encodes both levels of `x`. This means that if `m1` has `pred1 = a + b * (x=='b')` we can reproduce this model (intercept and all) as `m2`: `pred2 = a * (x=='a') + (a+b) * (x=='b')`. I.e., the invariant `(x=='a') + (x=='b') == 1` means `m2` can imitate the model with the intercept term.

The presumed (and I think weak) justification of `summary.lm()` switching the model quality assessment method is something along the lines that `mean(y)` may not be in the model's concept space and this might lead to reporting negative `R-squared`. I don't have any problem with negative `R-squared`, it can be taken to mean you did worse than the unconditional average. However, even if you accept the (no-warning) scoring method switch: that argument doesn't apply here. `m2` can imitate having an intercept, so it isn't unfair to check if it is better than using only the intercept.
