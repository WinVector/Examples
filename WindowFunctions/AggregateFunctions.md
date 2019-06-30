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
    ##  ) tsql_88423853009367798682_0000000000
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
  dt[, list(sum = sum(value)), by = "group"]
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
    ##                expr       min        lq      mean    median        uq
    ##          dplyr_soln 104.36746 111.47936 121.68849 120.49694 131.06930
    ##      datatable_soln  11.38687  15.66917  18.20750  17.10564  22.58313
    ##         dtplyr_soln  60.97170  64.52915 100.76422  73.60517 144.69103
    ##    rqdatatable_soln  12.85540  14.43563  17.42355  15.62907  17.72362
    ##  base_R_lookup_soln  82.76607  92.04244 103.90669  92.54040  96.80224
    ##        max neval
    ##  139.50024    10
    ##   26.35489    10
    ##  168.14311    10
    ##   33.51638    10
    ##  209.30101    10

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
    ##          dplyr_soln 1768.3320 1937.7464 2068.4152 2089.1402 2134.3383
    ##      datatable_soln  143.9574  170.5984  244.8870  196.5139  270.4079
    ##         dtplyr_soln  743.2921  789.9880  870.6912  838.8895  892.1501
    ##    rqdatatable_soln  114.4732  149.7780  186.9856  162.4099  220.5923
    ##  base_R_lookup_soln 1246.9553 1344.8032 1603.3240 1651.8532 1693.7059
    ##        max neval
    ##  2471.4399    10
    ##   482.2308    10
    ##  1240.5779    10
    ##   318.2165    10
    ##  2116.6516    10

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
    ##                expr        min        lq      mean    median        uq
    ##          dplyr_soln  82.378788  84.95316  89.11358  87.12364  90.43574
    ##      datatable_soln  53.252407  55.34744  70.55867  59.55131  65.15286
    ##         dtplyr_soln 226.403444 243.87508 281.92697 286.52095 322.12152
    ##    rqdatatable_soln   9.638939  10.84006  33.00082  11.59810  16.23251
    ##  base_R_lookup_soln  63.898388  69.02701  90.95358  70.44159  85.68363
    ##       max neval
    ##  107.2206    10
    ##  170.9068    10
    ##  327.3176    10
    ##  121.4666    10
    ##  177.3301    10

Run on an idle Mac mini (Late 2014 model), macOS 10.13.6, 8 GB 1600 MHz
DDR3.

``` r
date()
```

    ## [1] "Sat Jun 29 17:22:32 2019"

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
