<!-- README.md is generated from README.Rmd. Please edit that file -->
``` r
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.5.0'

``` r
library("sparklyr")
packageVersion("sparklyr")
```

    ## [1] '0.5.4'

``` r
library("replyr")
packageVersion("replyr")
```

    ## [1] '0.3.902'

``` r
sc <- sparklyr::spark_connect(version='2.0.2', 
                              master = "local")
diris <- copy_to(sc, iris, 'diris')
```

``` r
summary(diris)
```

    ##     Length Class          Mode
    ## src 1      src_spark      list
    ## ops 3      op_base_remote list

``` r
replyr_summary(diris)
```

    ##         column index     class nrows nna nunique min max     mean
    ## 1 Sepal_Length     1   numeric   150   0      NA 4.3 7.9 5.843333
    ## 2  Sepal_Width     2   numeric   150   0      NA 2.0 4.4 3.057333
    ## 3 Petal_Length     3   numeric   150   0      NA 1.0 6.9 3.758000
    ## 4  Petal_Width     4   numeric   150   0      NA 0.1 2.5 1.199333
    ## 5      Species     5 character   150   0      NA  NA  NA       NA
    ##          sd lexmin    lexmax
    ## 1 0.8280661   <NA>      <NA>
    ## 2 0.4358663   <NA>      <NA>
    ## 3 1.7652982   <NA>      <NA>
    ## 4 0.7622377   <NA>      <NA>
    ## 5        NA setosa virginica

``` r
sparklyr::spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  668429 35.7    1168576 62.5  1168576 62.5
    ## Vcells 1276511  9.8    2060183 15.8  1723062 13.2
