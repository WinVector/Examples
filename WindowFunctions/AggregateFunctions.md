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
    ##  ) tsql_58591674243505989231_0000000000
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
  times = 10L)
print(timings1)
```

    ## Unit: milliseconds
    ##                expr       min       lq      mean    median        uq
    ##          dplyr_soln 90.057213 94.14632 112.54812 104.24340 118.04166
    ##      datatable_soln  9.900004 12.65102  15.94681  14.24296  16.60382
    ##         dtplyr_soln 53.421789 63.56419 109.51679  74.01572 151.36640
    ##    rqdatatable_soln 10.801057 13.56356  15.21794  14.94448  17.24860
    ##  base_R_lookup_soln 67.230965 83.38247 113.65644 116.88634 130.43197
    ##        max neval
    ##  175.17569    10
    ##   28.50283    10
    ##  240.98074    10
    ##   20.70654    10
    ##  168.49241    10

``` r
# now try bigger example with small number of irrelevant columns
d <- mk_data(1000000, 10, 100000)
timings2 <- microbenchmark(
  dplyr_soln = dplyr_soln(d),
  datatable_soln = datatable_soln(d),
  dtplyr_soln = dtplyr_soln(d),
  rqdatatable_soln = rqdatatable_soln(d),
  base_R_lookup_soln = base_R_lookup_soln(d),
  times = 10L)
print(timings2)
```

    ## Unit: milliseconds
    ##                expr       min        lq      mean    median        uq
    ##          dplyr_soln 1543.9823 1573.6822 1791.9790 1658.5995 2072.7789
    ##      datatable_soln  141.4548  149.8420  206.4489  156.6491  214.6359
    ##         dtplyr_soln  612.9404  707.9020  788.0161  732.9196  791.7844
    ##    rqdatatable_soln  118.3758  120.9281  176.3847  179.3689  206.8276
    ##  base_R_lookup_soln 1189.4972 1254.8078 1435.4358 1328.5802 1524.9679
    ##        max neval
    ##  2406.0105    10
    ##   407.8885    10
    ##  1192.4385    10
    ##   267.2239    10
    ##  1948.3233    10

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
  times = 10L)
print(timings3)
```

    ## Unit: milliseconds
    ##                expr       min        lq      mean    median        uq
    ##          dplyr_soln  80.32505  83.64389  89.65582  88.83205  90.70663
    ##      datatable_soln  54.21628  59.88788  73.47135  65.45852  66.92157
    ##         dtplyr_soln 234.84862 252.28784 290.94890 294.13237 331.87897
    ##    rqdatatable_soln  10.19361  11.48504  33.37004  12.68630  15.79134
    ##  base_R_lookup_soln  65.61910  68.73846  91.15363  71.12531  84.39944
    ##       max neval
    ##  112.1866    10
    ##  164.7957    10
    ##  339.8169    10
    ##  117.0547    10
    ##  169.4107    10

Run on an idle Mac mini (Late 2014 model), macOS 10.13.6, 8 GB 1600 MHz
DDR3.

``` r
date()
```

    ## [1] "Sat Jun 29 17:29:29 2019"

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
