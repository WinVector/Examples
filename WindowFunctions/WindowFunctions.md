WindowFunctions
================

Backing materials for [“My Favorite data.table
Feature”](http://www.win-vector.com/blog/2019/06/my-favorite-data-table-feature/).
Timings will be slightly different as we have since re-run this
worksheet.

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
  extend(., 
         partitionby ="group", 
         fraction := value/sum(value)) %.>%
  to_sql(., rquery_default_db_info()) %.>%
  cat(.)
```

    ## SELECT
    ##  "group",
    ##  "value",
    ##  "value" / sum ( "value" ) OVER (  PARTITION BY "group" ) AS "fraction"
    ## FROM (
    ##  SELECT
    ##   "group",
    ##   "value"
    ##  FROM
    ##   "d"
    ##  ) tsql_65091634801521878401_0000000000

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
    mutate(fraction = value/sum(value)) %>%
    ungroup()
}

dplyr_soln(d)
```

    ## # A tibble: 4 x 3
    ##   group value fraction
    ##   <chr> <int>    <dbl>
    ## 1 a         1    0.333
    ## 2 a         2    0.667
    ## 3 b         3    0.429
    ## 4 b         4    0.571

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
  dt[, fraction := value/sum(value), by = "group"][]
}

datatable_soln(d)
```

    ##    group value  fraction
    ## 1:     a     1 0.3333333
    ## 2:     a     2 0.6666667
    ## 3:     b     3 0.4285714
    ## 4:     b     4 0.5714286

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
    mutate(fraction = value/sum(value)) %>%
    ungroup()
}

dplyr_soln(d)
```

    ## # A tibble: 4 x 3
    ##   group value fraction
    ##   <chr> <int>    <dbl>
    ## 1 a         1    0.333
    ## 2 a         2    0.667
    ## 3 b         3    0.429
    ## 4 b         4    0.571

``` r
library("rqdatatable")
packageVersion("rqdatatable")
```

    ## [1] '1.1.9'

``` r
rqdatatable_soln <- function(d) {
  d %.>%
    extend(., 
           partitionby = "group", 
           fraction := value/sum(value))
}

rqdatatable_soln(d)
```

    ##    group value  fraction
    ## 1:     a     1 0.3333333
    ## 2:     a     2 0.6666667
    ## 3:     b     3 0.4285714
    ## 4:     b     4 0.5714286

``` r
base_R_lookup_soln <- function(d) {
  sums <- tapply(d$value, d$group, sum)
  d$fraction <- d$value/sums[d$group] # or transform(d, fraction = value/sums[group]) 
  d
}

base_R_lookup_soln(d)
```

    ##   group value  fraction
    ## 1     a     1 0.3333333
    ## 2     a     2 0.6666667
    ## 3     b     3 0.4285714
    ## 4     b     4 0.5714286

``` r
base_R_merge_soln <- function(d) {
  sums <- tapply(d$value, d$group, sum)
  sums_frame <- data.frame(group = names(sums),
                           sum = as.numeric(sums),
                           stringsAsFactors = FALSE)
  result <- merge(d, sums_frame, by = "group")
  result$fraction <- result$value/result$sum
  result$sum <- NULL
  result
}

base_R_merge_soln(d)
```

    ##   group value  fraction
    ## 1     a     1 0.3333333
    ## 2     a     2 0.6666667
    ## 3     b     3 0.4285714
    ## 4     b     4 0.5714286

``` r
base_R_ave_soln <- function(d) {
  sums <- ave(d$value, d$group, FUN = sum)
  d$fraction <- d$value/sums
  d
}

base_R_ave_soln(d)
```

    ##   group value  fraction
    ## 1     a     1 0.3333333
    ## 2     a     2 0.6666667
    ## 3     b     3 0.4285714
    ## 4     b     4 0.5714286

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

# first compare base_R_lookup_soln() to base_R_merge_soln()
d <- mk_data(100000, 10, 10000)
timings1 <- microbenchmark(
  dplyr_soln = dplyr_soln(d),
  datatable_soln = datatable_soln(d),
  dtplyr_soln = dtplyr_soln(d),
  rqdatatable_soln = rqdatatable_soln(d),
  base_R_lookup_soln = base_R_lookup_soln(d),
  base_R_merge_soln = base_R_merge_soln(d),
  base_R_ave_soln = base_R_ave_soln(d),
  times = 5L)
print(timings1)
```

    ## Unit: milliseconds
    ##                expr       min        lq       mean     median         uq
    ##          dplyr_soln 208.86172 211.23851  214.92834  215.51877  218.66900
    ##      datatable_soln  27.58407  27.91690   37.08973   39.56568   42.36004
    ##         dtplyr_soln  45.24744  47.16940   57.54716   56.55981   67.16639
    ##    rqdatatable_soln  49.50242  51.96162   73.20169   58.01081   64.44770
    ##  base_R_lookup_soln  74.61456  77.25313   92.92758   89.76125  109.46147
    ##   base_R_merge_soln 966.48667 999.02050 1047.65113 1087.60085 1091.22055
    ##     base_R_ave_soln  80.34756  82.48274   98.31047   82.81353  100.16647
    ##         max neval
    ##   220.35370     5
    ##    48.02194     5
    ##    71.59274     5
    ##   142.08589     5
    ##   113.54747     5
    ##  1093.92706     5
    ##   145.74204     5

``` r
# merge solution is bad, likely due to cost of merge() step

# now try bigger example with small number of irrelevant columns
d <- mk_data(1000000, 10, 100000)
timings2 <- microbenchmark(
  dplyr_soln = dplyr_soln(d),
  datatable_soln = datatable_soln(d),
  dtplyr_soln = dtplyr_soln(d),
  rqdatatable_soln = rqdatatable_soln(d),
  base_R_lookup_soln = base_R_lookup_soln(d),
  base_R_ave_soln = base_R_ave_soln(d),
  times = 10L)
print(timings2)
```

    ## Unit: milliseconds
    ##                expr       min        lq      mean    median        uq
    ##          dplyr_soln 3536.0378 3579.7881 3620.5774 3606.9280 3613.6726
    ##      datatable_soln  272.5039  310.9330  343.5773  320.6331  378.3368
    ##         dtplyr_soln  565.8834  737.2592  800.2368  782.1983  902.6253
    ##    rqdatatable_soln  557.3124  583.2941  706.7368  699.3231  758.8063
    ##  base_R_lookup_soln 1320.4560 1347.6206 1409.3101 1376.7020 1450.9999
    ##     base_R_ave_soln 1353.5795 1371.9668 1427.5839 1391.2620 1496.7291
    ##        max neval
    ##  3750.2049    10
    ##   505.2334    10
    ##   970.7965    10
    ##  1058.5922    10
    ##  1565.3882    10
    ##  1581.0163    10

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
  base_R_ave_soln = base_R_ave_soln(d),
  times = 10L)
print(timings3)
```

    ## Unit: milliseconds
    ##                expr       min        lq      mean    median        uq
    ##          dplyr_soln 201.58665 207.31926 213.73509 210.23327 215.62834
    ##      datatable_soln  67.78353  70.48399 112.78156  96.88809 171.16055
    ##         dtplyr_soln 238.86614 265.16600 313.71999 337.85567 349.00317
    ##    rqdatatable_soln 166.00339 169.39873 207.53317 187.52156 267.85092
    ##  base_R_lookup_soln  70.17179  75.20082  76.66798  76.17772  77.15854
    ##     base_R_ave_soln  75.22433  75.84596  83.31147  80.01347  86.27543
    ##        max neval
    ##  234.41137    10
    ##  195.66240    10
    ##  362.26320    10
    ##  283.48345    10
    ##   84.51599    10
    ##  111.65765    10

Run on an idle Mac mini (Late 2014 model), macOS 10.13.6, 8 GB 1600 MHz
DDR3.

``` r
date()
```

    ## [1] "Sun Jun 30 10:17:34 2019"

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
