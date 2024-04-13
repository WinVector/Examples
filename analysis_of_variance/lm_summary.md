lm summary
================
2024-04-13

``` r
set.seed(2024)

m_row <- 20
n_var <- 3
d <- data.frame(matrix(
  rnorm((n_var+1)*m_row), 
  nrow=m_row))
colnames(d)[n_var+1] <- 'y'
vars <- colnames(d)[1:n_var]
```

``` r
summary(lm(y ~., data=d))
```

    ## 
    ## Call:
    ## lm(formula = y ~ ., data = d)
    ## 
    ## Residuals:
    ##     Min      1Q  Median      3Q     Max 
    ## -2.0594 -0.6512  0.1713  0.7177  1.5147 
    ## 
    ## Coefficients:
    ##             Estimate Std. Error t value Pr(>|t|)
    ## (Intercept)  0.17968    0.25212   0.713    0.486
    ## X1           0.01775    0.21845   0.081    0.936
    ## X2           0.12782    0.29491   0.433    0.670
    ## X3          -0.33468    0.26910  -1.244    0.232
    ## 
    ## Residual standard error: 1.091 on 16 degrees of freedom
    ## Multiple R-squared:  0.1192, Adjusted R-squared:  -0.04592 
    ## F-statistic: 0.7219 on 3 and 16 DF,  p-value: 0.5535

``` r
summary(aov(y ~ ., data=d))
```

    ##             Df Sum Sq Mean Sq F value Pr(>F)
    ## X1           1  0.318  0.3177   0.267  0.612
    ## X2           1  0.419  0.4189   0.352  0.561
    ## X3           1  1.841  1.8412   1.547  0.232
    ## Residuals   16 19.045  1.1903

``` r
summary(aov(lm(y ~ ., data=d)))
```

    ##             Df Sum Sq Mean Sq F value Pr(>F)
    ## X1           1  0.318  0.3177   0.267  0.612
    ## X2           1  0.419  0.4189   0.352  0.561
    ## X3           1  1.841  1.8412   1.547  0.232
    ## Residuals   16 19.045  1.1903
