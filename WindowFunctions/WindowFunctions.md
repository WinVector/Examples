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
    ##  ) tsql_39366907550820502222_0000000000

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
           partitionby ="group", 
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
    ##                expr       min         lq       mean     median        uq
    ##  base_R_lookup_soln  70.77886   71.87442   82.30154   78.79368   85.6437
    ##   base_R_merge_soln 985.73607 1001.61202 1016.09712 1009.55543 1025.1233
    ##       max neval
    ##   104.417     5
    ##  1058.459     5

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
    ##          dplyr_soln 3545.4420 3597.6367 4403.4747 3842.0041 4694.8211
    ##      datatable_soln  294.2609  334.2081  414.3972  378.5495  488.2055
    ##         dtplyr_soln  534.7203  704.8316  787.5820  750.1034  791.2549
    ##    rqdatatable_soln  488.8316  720.6075  757.1495  761.0332  791.9466
    ##  base_R_lookup_soln 1314.2077 1373.1657 1473.9223 1456.9126 1504.2548
    ##        max neval
    ##  7347.8653    10
    ##   599.3328    10
    ##  1169.1007    10
    ##   997.6759    10
    ##  1830.2139    10

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
    ##          dplyr_soln 219.91423 228.81952 264.08625 258.66492 288.81289
    ##      datatable_soln  75.20412  82.76477 108.08750  88.94729 115.28512
    ##         dtplyr_soln 355.69799 368.02524 421.09500 390.96714 493.16737
    ##    rqdatatable_soln 175.10557 185.54118 244.23055 219.89990 278.26537
    ##  base_R_lookup_soln  74.83041  76.56702  95.81418  81.14828  94.51147
    ##       max neval
    ##  323.6208    10
    ##  189.9545    10
    ##  569.2427    10
    ##  405.8715    10
    ##  181.2697    10

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
