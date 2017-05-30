<!-- README.md is generated from README.Rmd. Please edit that file -->
Our next "R and big data tip" is: summarizing big data.

We always say "if you are not looking at the data, you are not doing science"- and for big data you are very dependent on summaries (as you can't actually look at everything).

Simple question: is there an easy way to summarize big data on [`R`](https://www.r-project.org)?

The answer is: yes, but we suggest you use the [`replyr`](https://CRAN.R-project.org/package=replyr) package to do so.

Let's set up a trivial example.

``` r
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.5.0'

``` r
library("sparklyr")
packageVersion("sparklyr")
```

    ## [1] '0.5.5'

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

The usual `S3`-`summary()` summarizes the handle, not the data.

``` r
summary(diris)
```

    ##     Length Class          Mode
    ## src 1      src_spark      list
    ## ops 3      op_base_remote list

`tibble::glimpse()` throws.

``` r
packageVersion("tibble")
```

    ## [1] '1.3.3'

``` r
# errors-out
glimpse(diris)
```

    ## Observations: 150
    ## Variables: 5

    ## Error in if (width[i] <= max_width[i]) next: missing value where TRUE/FALSE needed

`broom::glance()` throws.

``` r
packageVersion("broom")
```

    ## [1] '0.4.2'

``` r
broom::glance(diris)
```

    ## Error: glance doesn't know how to deal with data of class tbl_sparktbl_sqltbl_lazytbl

`replyr_summary()` works, and returns results in a `data.frame`.

``` r
replyr_summary(diris) %>%
  select(-nunique, -index, -nrows)
```

    ##         column     class nna min max     mean        sd lexmin    lexmax
    ## 1 Sepal_Length   numeric   0 4.3 7.9 5.843333 0.8280661   <NA>      <NA>
    ## 2  Sepal_Width   numeric   0 2.0 4.4 3.057333 0.4358663   <NA>      <NA>
    ## 3 Petal_Length   numeric   0 1.0 6.9 3.758000 1.7652982   <NA>      <NA>
    ## 4  Petal_Width   numeric   0 0.1 2.5 1.199333 0.7622377   <NA>      <NA>
    ## 5      Species character   0  NA  NA       NA        NA setosa virginica

------------------------------------------------------------------------

``` r
sparklyr::spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  762733 40.8    1442291 77.1  1168576 62.5
    ## Vcells 1394817 10.7    2552219 19.5  1819886 13.9
