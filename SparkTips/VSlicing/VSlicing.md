<!-- README.md is generated from README.Rmd. Please edit that file -->
``` r
# devtools::install_github("rstudio/sparklyr")
suppressPackageStartupMessages(library("dplyr"))
library("sparklyr")
packageVersion("sparklyr")
```

    ## [1] '0.5.4.9003'

``` r
sc <- spark_connect(master = "local", version = "2.0.2")
d <- data.frame(y=c(1,1,1,0,0,0), x=c(1,1,0,0,0,1))
dS <- copy_to(sc, d)
model <- ml_logistic_regression(dS, y~x)
```

    ## * No rows dropped by 'na.omit' call

``` r
preds <- sdf_predict(model, dS) 
print(preds)
```

    ## # Source:   table<sparklyr_tmp_355e2a7dcfaa> [?? x 5]
    ## # Database: spark_connection
    ##       y     x rawPrediction probability prediction
    ##   <dbl> <dbl>        <list>      <list>      <dbl>
    ## 1     1     1     <dbl [2]>   <dbl [2]>          1
    ## 2     1     1     <dbl [2]>   <dbl [2]>          1
    ## 3     1     0     <dbl [2]>   <dbl [2]>          0
    ## 4     0     0     <dbl [2]>   <dbl [2]>          0
    ## 5     0     0     <dbl [2]>   <dbl [2]>          0
    ## 6     0     1     <dbl [2]>   <dbl [2]>          1

``` r
# extract the probablity locally
pLocal <- collect(preds)
pLocal$prob <- vapply(pLocal$probability,
                      function(ri) {ri[[2]]}, numeric(1))
print(pLocal)
```

    ## # A tibble: 6 x 6
    ##       y     x rawPrediction probability prediction      prob
    ##   <dbl> <dbl>        <list>      <list>      <dbl>     <dbl>
    ## 1     1     1     <dbl [2]>   <dbl [2]>          1 0.6666667
    ## 2     1     1     <dbl [2]>   <dbl [2]>          1 0.6666667
    ## 3     1     0     <dbl [2]>   <dbl [2]>          0 0.3333333
    ## 4     0     0     <dbl [2]>   <dbl [2]>          0 0.3333333
    ## 5     0     0     <dbl [2]>   <dbl [2]>          0 0.3333333
    ## 6     0     1     <dbl [2]>   <dbl [2]>          1 0.6666667

``` r
# extract the probablity remotely
# Solution in dev-version of Sparklyr:
#  https://github.com/rstudio/sparklyr/issues/648
#  https://github.com/rstudio/sparklyr/pull/667
sdf_separate_column(
    preds,
    "probability",
    list("p1"= 1, "p2" = 2)
)
```

    ## # Source:   table<sparklyr_tmp_355e29ccb7b1> [?? x 7]
    ## # Database: spark_connection
    ##       y     x rawPrediction probability prediction        p1        p2
    ##   <dbl> <dbl>        <list>      <list>      <dbl>     <dbl>     <dbl>
    ## 1     1     1     <dbl [2]>   <dbl [2]>          1 0.3333333 0.6666667
    ## 2     1     1     <dbl [2]>   <dbl [2]>          1 0.3333333 0.6666667
    ## 3     1     0     <dbl [2]>   <dbl [2]>          0 0.6666667 0.3333333
    ## 4     0     0     <dbl [2]>   <dbl [2]>          0 0.6666667 0.3333333
    ## 5     0     0     <dbl [2]>   <dbl [2]>          0 0.6666667 0.3333333
    ## 6     0     1     <dbl [2]>   <dbl [2]>          1 0.3333333 0.6666667

``` r
spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  697129 37.3    1168576 62.5   940480 50.3
    ## Vcells 1168663  9.0    2060183 15.8  1365679 10.5
