`sigr` formats significance tests.

![](sigr.png)

``` r
library('sigr')
d <- data.frame(x=1:5)
set.seed(353525)
d$y <- 2*d$x + rnorm(nrow(d))
```

``` r
model <- lm(y~x, data=d)
d$pred <- predict(model, newdata = d)

summary(model)
```

    ## 
    ## Call:
    ## lm(formula = y ~ x, data = d)
    ## 
    ## Residuals:
    ##         1         2         3         4         5 
    ## -0.786973  1.117243 -0.009319 -0.185198 -0.135753 
    ## 
    ## Coefficients:
    ##             Estimate Std. Error t value Pr(>|t|)   
    ## (Intercept)  -1.0473     0.8391  -1.248  0.30053   
    ## x             2.1011     0.2530   8.304  0.00366 **
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## Residual standard error: 0.8001 on 3 degrees of freedom
    ## Multiple R-squared:  0.9583, Adjusted R-squared:  0.9444 
    ## F-statistic: 68.96 on 1 and 3 DF,  p-value: 0.003659

``` r
broom::glance(model)
```

    ##   r.squared adj.r.squared     sigma statistic     p.value df    logLik
    ## 1 0.9583119     0.9444159 0.8000775  68.96306 0.003658704  2 -4.702395
    ##        AIC     BIC deviance df.residual
    ## 1 15.40479 14.2331 1.920372           3

``` r
cat(render(wrapFTest(model),
    pSmallCutoff=0))
```

**F Test** summary: (<i>R<sup>2</sup></i>=0.96, *F*(1,3)=69, *p*=0.0037).

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
    ## [1] 68.96306
    ## 
    ## $R2
    ## [1] 0.9583119
    ## 
    ## $pValue
    ## [1] 0.003658704

``` r
cat(render(wrapFTest(d, 'pred', 'y'),
    pSmallCutoff=0))
```

**F Test** summary: (<i>R<sup>2</sup></i>=0.96, *F*(1,3)=69, *p*=0.0037).

``` r
cat(render(wrapFTest(d, 'x', 'y'),
    pSmallCutoff=0))
```

**F Test** summary: (<i>R<sup>2</sup></i>=0.14, *F*(1,3)=0.5, *p*=n.s.).

``` r
cat(render(wrapCorTest(d, 'x', 'y'),
    pSmallCutoff=0))
```

**Pearson's product-moment correlation**: (*r*=0.98, *p*=0.0037).
