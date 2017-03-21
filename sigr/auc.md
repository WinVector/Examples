##### Setup.

``` r
set.seed(224)
d <- data.frame(x= runif(5),   # predictor
                y= rnorm(5)>=0 # outcome/truth
)
d$cx <- 1-d$x # complement of x
d$ny <- !d$y  # not y
print(d)
```

    ##           x     y         cx    ny
    ## 1 0.7538008 FALSE 0.24619925  TRUE
    ## 2 0.5867451 FALSE 0.41325491  TRUE
    ## 3 0.3844693  TRUE 0.61553066 FALSE
    ## 4 0.9483048 FALSE 0.05169519  TRUE
    ## 5 0.6525606  TRUE 0.34743940 FALSE

##### `ModelMetrics`

``` r
ModelMetrics::auc(d$y, d$x) +
  ModelMetrics::auc(d$y, d$cx)
```

    ## [1] 1

``` r
ModelMetrics::auc(d$y, d$x) +
  ModelMetrics::auc(d$ny, d$x)
```

    ## [1] 1

##### `sigr`

``` r
sigr::calcAUC(d$x, d$y) + 
  sigr::calcAUC(d$cx, d$y)
```

    ## [1] 1

``` r
sigr::calcAUC(d$x, d$y) +
  sigr::calcAUC(d$x, d$ny)
```

    ## [1] 1

##### `ROCR`

``` r
aucROCR <- function(predictions, target) {
  pred <- ROCR::prediction(predictions,
                           target)
  perf_AUC <- ROCR::performance(pred,
                                "auc")
  perf_AUC@y.values[[1]]
}

aucROCR(d$x, d$y) + 
  aucROCR(d$cx, d$y)
```

    ## [1] 1

``` r
aucROCR(d$x, d$y) + 
  aucROCR(d$x, d$ny)
```

    ## [1] 1

##### `caret`

``` r
aucCaret <- function(predictions, target) {
  classes <- c("class1", "class2")
  df <- data.frame(obs= ifelse(target, 
                               "class1", 
                               "class2"),
                 pred = ifelse(predictions>0.5, 
                               "class1", 
                               "class2"),
                 class1 = predictions,
                 class2 = 1-predictions)
  caret::twoClassSummary(df, lev=classes)[['ROC']]
}


aucCaret(d$x, d$y) + 
  aucCaret(d$cx, d$y)
```

    ## [1] 1

``` r
aucCaret(d$x, d$y) + 
  aucCaret(d$x, d$ny)
```

    ## [1] 1

##### `pROC`

``` r
pROC::auc(y~x, d) + 
  pROC::auc(y~cx, d) # wrong
```

    ## [1] 1.666667

More tries with `pROC`.

From `help(roc)`

> direction
>
> in which direction to make the comparison? "auto" (default): automatically define in which group the median is higher and take the direction accordingly. "&gt;": if the predictor values for the control group are higher than the values of the case group (controls &gt; t &gt;= cases). "&lt;": if the predictor values for the control group are lower or equal than the values of the case group (controls &lt; t &lt;= cases).

``` r
pROC::auc(y~x, d, direction= '<') + 
  pROC::auc(y~cx, d, direction= '<')
```

    ## [1] 1

``` r
pROC::auc(y~x, d, direction= '<') +
  pROC::auc(ny~x, d, direction= '<')
```

    ## [1] 1

##### `AUC`

``` r
tryCatch(
  AUC::auc(AUC::roc(d$x, d$y)),
  error = function(e) {e})
```

    ## Warning in is.na(x): is.na() applied to non-(list or vector) of type 'NULL'

    ## Warning in is.na(e2): is.na() applied to non-(list or vector) of type
    ## 'NULL'

    ## Warning in is.na(e2): is.na() applied to non-(list or vector) of type
    ## 'NULL'

    ## <simpleError in AUC::roc(d$x, d$y): Not enough distinct predictions to compute area under the ROC curve.>
