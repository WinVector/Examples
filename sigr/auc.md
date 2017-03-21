##### Setup.

``` r
set.seed(224)

mkData <- function(n) {
  d <- data.frame(x= runif(n),   # predictor
                  y= rnorm(n)>=0 # outcome/truth
  )
  d$cx <- 1-d$x # complement of x
  d$ny <- !d$y  # not y
  d
}
d <- mkData(5)
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

##### `AUC`

``` r
aucAUC <- function(predictions, target) {
  AUC::auc(AUC::roc(predictions, 
                  factor(ifelse(target, "1", "0"))))
}

aucAUC(d$x, d$y) +
  aucAUC(d$cx, d$y)
```

    ## [1] 1

``` r
aucAUC(d$x, d$y) +
  aucAUC(d$x, d$ny)
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

### Timing

``` r
library("microbenchmark")

dTime <- mkData(10000)

ModelMetrics::auc(dTime$y, dTime$x)
```

    ## [1] 0.5125198

``` r
sigr::calcAUC(dTime$x, dTime$y)
```

    ## [1] 0.5125198

``` r
aucROCR(dTime$x, dTime$y)
```

    ## [1] 0.5125198

``` r
aucAUC(dTime$x, dTime$y)
```

    ## [1] 0.5125198

``` r
aucCaret(dTime$x, dTime$y)
```

    ## [1] 0.5125198

``` r
pROC::auc(y~x, dTime, direction= '<')
```

    ## Area under the curve: 0.5125

``` r
res <- microbenchmark(
  ModelMetrics::auc(dTime$y, dTime$x),
  sigr::calcAUC(dTime$x, dTime$y),
  aucROCR(dTime$x, dTime$y),
  aucAUC(dTime$x, dTime$y),
  aucCaret(dTime$x, dTime$y),
  pROC::auc(y~x, dTime, direction= '<')
)

# select down columns and control units
library("dplyr")
```

    ## 
    ## Attaching package: 'dplyr'

    ## The following objects are masked from 'package:stats':
    ## 
    ##     filter, lag

    ## The following objects are masked from 'package:base':
    ## 
    ##     intersect, setdiff, setequal, union

``` r
res %>% 
  group_by(expr) %>%
  mutate(time = time/1e9) %>% # move from NanoSeconds to seconds
  summarize(meanTimeS = mean(time), 
            medianTimeS = median(time)) %>%
  arrange(medianTimeS)
```

    ## # A tibble: 6 × 3
    ##                                       expr   meanTimeS medianTimeS
    ##                                     <fctr>       <dbl>       <dbl>
    ## 1      ModelMetrics::auc(dTime$y, dTime$x) 0.002809079 0.002619565
    ## 2          sigr::calcAUC(dTime$x, dTime$y) 0.009960525 0.004000801
    ## 3               aucCaret(dTime$x, dTime$y) 0.025471632 0.021540099
    ## 4                aucROCR(dTime$x, dTime$y) 0.047789639 0.045066673
    ## 5                 aucAUC(dTime$x, dTime$y) 0.108710819 0.101732337
    ## 6 pROC::auc(y ~ x, dTime, direction = "<") 0.934411745 0.890861189
