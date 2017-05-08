<!-- README.md is generated from README.Rmd. Please edit that file -->
``` r
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
library("sparklyr")
sc <- spark_connect(master = "local", version = "2.0.0")
d <- data.frame(y=c(1,1,1,0,0,0), x=c(1,1,0,0,0,1))
dS <- copy_to(sc, d)
model <- ml_logistic_regression(dS, y~x)
```

    ## * No rows dropped by 'na.omit' call

``` r
preds <- sdf_predict(model, dS) 
print(preds)
```

    ## Source:   query [6 x 5]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##       y     x rawPrediction probability prediction
    ##   <dbl> <dbl>        <list>      <list>      <dbl>
    ## 1     1     1     <dbl [2]>   <dbl [2]>          1
    ## 2     1     1     <dbl [2]>   <dbl [2]>          1
    ## 3     1     0     <dbl [2]>   <dbl [2]>          0
    ## 4     0     0     <dbl [2]>   <dbl [2]>          0
    ## 5     0     0     <dbl [2]>   <dbl [2]>          0
    ## 6     0     1     <dbl [2]>   <dbl [2]>          1

``` r
pLocal <- collect(preds)

# any idea how to perform this next step on preds
# inside Spark?
# Some direct Spark SQL query? (query optimizer rejects [1] notation)?
# http://stackoverflow.com/questions/33220916/explode-transpose-multiple-columns-in-spark- 
# http://stackoverflow.com/questions/43589762/sparklyr-how-to-explode-a-list-column-into-t 
# help("ft_sql_transformer")? # not much to go on
pLocal$prob <- vapply(pLocal$probability,
                      function(ri) {ri[[2]]}, numeric(1))
print(pLocal)
```

    ## # A tibble: 6 × 6
    ##       y     x rawPrediction probability prediction      prob
    ##   <dbl> <dbl>        <list>      <list>      <dbl>     <dbl>
    ## 1     1     1     <dbl [2]>   <dbl [2]>          1 0.6666667
    ## 2     1     1     <dbl [2]>   <dbl [2]>          1 0.6666667
    ## 3     1     0     <dbl [2]>   <dbl [2]>          0 0.3333333
    ## 4     0     0     <dbl [2]>   <dbl [2]>          0 0.3333333
    ## 5     0     0     <dbl [2]>   <dbl [2]>          0 0.3333333
    ## 6     0     1     <dbl [2]>   <dbl [2]>          1 0.6666667
