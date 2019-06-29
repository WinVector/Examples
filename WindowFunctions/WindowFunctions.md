WindowFunctions
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
    ##  ) tsql_93887685089181500000_0000000000

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
  base_R_lookup_soln = base_R_lookup_soln(d),
  base_R_merge_soln = base_R_merge_soln(d),
  times = 5L)
print(timings1)
```

    ## Unit: milliseconds
    ##                expr       min         lq       mean     median         uq
    ##  base_R_lookup_soln   70.6214   71.15655   83.75928   81.68444   94.32267
    ##   base_R_merge_soln 1006.9388 1015.58817 1221.15268 1065.15864 1238.35575
    ##        max neval
    ##   101.0113     5
    ##  1779.7220     5

``` r
# merge solution is bad, likely due to merge() step

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
    ##          dplyr_soln 3453.5092 3519.5205 3987.8501 3764.5597 3850.1427
    ##      datatable_soln  289.0628  328.2310  384.4908  349.8896  425.2604
    ##         dtplyr_soln  574.2986  640.6621  801.8947  724.8340 1002.1765
    ##    rqdatatable_soln  463.0133  653.7966  816.4745  807.6268  953.0376
    ##  base_R_lookup_soln 1341.3012 1358.4321 1476.3975 1446.0355 1538.2011
    ##        max neval
    ##  6601.8748    10
    ##   601.8762    10
    ##  1053.3063    10
    ##  1366.4888    10
    ##  1803.7111    10

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
    ##                expr       min        lq     mean    median       uq
    ##          dplyr_soln 210.36176 218.86410 243.5021 229.25856 244.8467
    ##      datatable_soln  72.78887  75.86477 110.6873  81.40946 139.8924
    ##         dtplyr_soln 270.43692 382.29037 443.0467 441.47911 541.9696
    ##    rqdatatable_soln 162.40317 197.00949 279.5261 258.59914 370.6062
    ##  base_R_lookup_soln  75.33275  81.08655 101.1837  97.69725 119.9376
    ##       max neval
    ##  366.7221    10
    ##  202.5554    10
    ##  573.0294    10
    ##  431.8661    10
    ##  146.9001    10

Run on an idle Mac mini (Late 2014 model), macOS 10.13.6, 8 GB 1600 MHz
DDR3.

``` r
date()
```

    ## [1] "Sat Jun 29 10:40:55 2019"

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
