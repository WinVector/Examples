AggregateFunctions
================

``` r
d <- wrapr::build_frame(
   "group"  , "value" |
     "a"    , 1L      |
     "a"    , 2L      |
     "b"    , 3L      |
     "b"    , 4L      )

knitr::kable(d)
```

| group | value |
| :---- | ----: |
| a     |     1 |
| a     |     2 |
| b     |     3 |
| b     |     4 |

``` r
library("rquery")

mk_td("d", c("group", "value")) %.>%
  project(., 
         groupby = "group", 
         sum := sum(value)) %.>%
  to_sql(., rquery_default_db_info()) %.>%
  cat(.)
```

    ## SELECT "group", sum ( "value" ) AS "sum" FROM (
    ##  SELECT
    ##   "group",
    ##   "value"
    ##  FROM
    ##   "d"
    ##  ) tsql_64581470151344345522_0000000000
    ## GROUP BY
    ##  "group"

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
packageVersion("dplyr")
```

    ## [1] '0.8.1'

``` r
dplyr_soln <- function(d) {
  d %>% 
    group_by(group) %>%
    summarize(sum = sum(value)) %>%
    ungroup()
}

dplyr_soln(d)
```

    ## # A tibble: 2 x 2
    ##   group   sum
    ##   <chr> <int>
    ## 1 a         3
    ## 2 b         7

``` r
library("data.table")
```

    ## 
    ## Attaching package: 'data.table'

    ## The following objects are masked from 'package:dplyr':
    ## 
    ##     between, first, last

``` r
packageVersion("data.table")
```

    ## [1] '1.12.2'

``` r
datatable_soln <- function(d) {
  dt <- data.table::as.data.table(d)
  dt[, .(sum = sum(value)), by = "group"]
}

datatable_soln(d)
```

    ##    group sum
    ## 1:     a   3
    ## 2:     b   7

``` r
library("dtplyr")
packageVersion("dtplyr")
```

    ## [1] '0.0.3'

``` r
dtplyr_soln <- function(d) {
  d %>% 
    data.table::as.data.table() %>%
    group_by(group) %>%
    mutate(sum = sum(value)) %>%
    ungroup()
}

dplyr_soln(d)
```

    ## # A tibble: 2 x 2
    ##   group   sum
    ##   <chr> <int>
    ## 1 a         3
    ## 2 b         7

``` r
library("rqdatatable")
packageVersion("rqdatatable")
```

    ## [1] '1.1.9'

``` r
rqdatatable_soln <- function(d) {
  d %.>%
    project(., 
           groupby = "group", 
           sum := sum(value))
}

rqdatatable_soln(d)
```

    ##    group sum
    ## 1:     a   3
    ## 2:     b   7

``` r
base_R_lookup_soln <- function(d) {
  sums <- tapply(d$value, d$group, sum)
  data.frame(group = names(sums),
             sum = as.numeric(sums),
             stringsAsFactors = FALSE)
}

base_R_lookup_soln(d)
```

    ##   group sum
    ## 1     a   3
    ## 2     b   7

``` r
base_R_rowsum_soln <- function(d) {
  res <- as.data.frame(rowsum(d$value, d$group))
  colnames(res) <- "group"
  res$sum = rownames(res)
  rownames(res) <- NULL
  res
}

base_R_rowsum_soln(d)
```

    ##   group sum
    ## 1     3   a
    ## 2     7   b

``` r
library("microbenchmark")


mk_data <- function(nrow, nextracol, npossiblegroups) {
  d <- data.frame(group = sample(paste0("g_", seq_len(npossiblegroups)), nrow, replace = TRUE),
                  value = rnorm(nrow),
                  stringsAsFactors = FALSE)
  for(ci in paste0("c_", seq_len(nextracol))) {
    d[[ci]] <- rnorm(nrow)
  }
  d
}


set.seed(235253)

d <- mk_data(100000, 10, 10000)
timings1 <- microbenchmark(
  dplyr_soln = dplyr_soln(d),
  datatable_soln = datatable_soln(d),
  dtplyr_soln = dtplyr_soln(d),
  rqdatatable_soln = rqdatatable_soln(d),
  base_R_lookup_soln = base_R_lookup_soln(d),
  base_R_rowsum_soln = base_R_rowsum_soln(d),
  times = 10L)
print(timings1)
```

    ## Unit: milliseconds
    ##                expr      min       lq     mean   median        uq
    ##          dplyr_soln 82.95625 85.74020 97.04060 88.93448  95.22629
    ##      datatable_soln 12.34045 13.93616 23.49183 15.65336  17.72476
    ##         dtplyr_soln 41.76450 46.22861 80.01999 61.41470 130.83551
    ##    rqdatatable_soln 10.12923 10.34734 13.35223 11.33273  15.16798
    ##  base_R_lookup_soln 67.30436 69.41154 70.46854 70.22242  71.32351
    ##  base_R_rowsum_soln 50.18078 53.50744 56.64433 56.60232  57.22709
    ##        max neval
    ##  158.78108    10
    ##   91.11644    10
    ##  132.62622    10
    ##   24.67890    10
    ##   74.83208    10
    ##   70.46381    10

``` r
# now try bigger example with small number of irrelevant columns
d <- mk_data(1000000, 10, 100000)
timings2 <- microbenchmark(
  dplyr_soln = dplyr_soln(d),
  datatable_soln = datatable_soln(d),
  dtplyr_soln = dtplyr_soln(d),
  rqdatatable_soln = rqdatatable_soln(d),
  base_R_lookup_soln = base_R_lookup_soln(d),
  base_R_rowsum_soln = base_R_rowsum_soln(d),
  times = 10L)
print(timings2)
```

    ## Unit: milliseconds
    ##                expr       min        lq      mean    median        uq
    ##          dplyr_soln 1547.4541 1553.7968 1582.8668 1568.1207 1585.4786
    ##      datatable_soln  144.3517  160.5772  240.2964  196.3359  322.1019
    ##         dtplyr_soln  438.4907  570.9246  654.7556  644.5101  710.7757
    ##    rqdatatable_soln  114.5250  117.5074  146.9228  118.8135  121.6196
    ##  base_R_lookup_soln 1170.3287 1196.1089 1233.7108 1226.9868 1251.7046
    ##  base_R_rowsum_soln  843.8267  855.3658  863.9446  859.5422  862.9960
    ##        max neval
    ##  1716.8970    10
    ##   477.1752    10
    ##   874.5188    10
    ##   303.7196    10
    ##  1382.4422    10
    ##   925.2906    10

``` r
# now try medium example with large number of irrelevant columns
# translators such as dtplyr and rqdatatable are likely sensitive to column counts
d <- mk_data(100000, 100, 10000)
timings3 <- microbenchmark(
  dplyr_soln = dplyr_soln(d),
  datatable_soln = datatable_soln(d),
  dtplyr_soln = dtplyr_soln(d),
  rqdatatable_soln = rqdatatable_soln(d),
  base_R_lookup_soln = base_R_lookup_soln(d),
  base_R_rowsum_soln = base_R_rowsum_soln(d),
  times = 10L)
print(timings3)
```

    ## Unit: milliseconds
    ##                expr       min        lq      mean    median        uq
    ##          dplyr_soln  84.55775  85.42075  88.41586  86.35019  92.47375
    ##      datatable_soln  56.68657  62.98793  88.36672  71.59314  80.34042
    ##         dtplyr_soln 244.30240 275.18221 322.33611 343.55403 363.71855
    ##    rqdatatable_soln  10.85768  11.61928  14.01273  12.72290  16.74629
    ##  base_R_lookup_soln  64.59400  66.30166  69.50648  70.39127  71.66023
    ##  base_R_rowsum_soln  50.11060  52.90172  53.98529  54.36638  55.19334
    ##        max neval
    ##   93.90378    10
    ##  172.03391    10
    ##  366.40239    10
    ##   19.72826    10
    ##   72.51333    10
    ##   56.17392    10

Run on an idle Mac mini (Late 2014 model), macOS 10.13.6, 8 GB 1600 MHz
DDR3.

``` r
date()
```

    ## [1] "Sun Jun 30 10:29:51 2019"

``` r
R.version
```

    ##                _                           
    ## platform       x86_64-apple-darwin15.6.0   
    ## arch           x86_64                      
    ## os             darwin15.6.0                
    ## system         x86_64, darwin15.6.0        
    ## status                                     
    ## major          3                           
    ## minor          6.0                         
    ## year           2019                        
    ## month          04                          
    ## day            26                          
    ## svn rev        76424                       
    ## language       R                           
    ## version.string R version 3.6.0 (2019-04-26)
    ## nickname       Planting of a Tree
