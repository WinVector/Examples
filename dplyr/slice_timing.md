dplyr::slice timing
================

``` r
# From: https://github.com/tidyverse/dplyr/issues/4312
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
library("ggplot2")
```

    ## Registered S3 methods overwritten by 'ggplot2':
    ##   method         from 
    ##   [.quosures     rlang
    ##   c.quosures     rlang
    ##   print.quosures rlang

``` r
library("rqdatatable")
```

    ## Loading required package: rquery

``` r
library("cdata")
packageVersion("dplyr")
```

    ## [1] '0.8.0.1'

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

``` r
d0 <- iris


f <- function(k, d0) {
  d <- data.frame(data.table::rbindlist(rep(list(d0), k)))
  rownames(d) <- NULL
  d <- tbl_df(d)
  gc()
  tm <- microbenchmark::microbenchmark(
    slice(d, 1),
    d[1, ],
    times = 3L
  )
  td <- data.frame(tm)
  td$nrow <- nrow(d)
  td
}


times <- lapply(2^(0:20), 
                function(k) {
                  f(k, d0)
                })
times <- data.frame(data.table::rbindlist(times))
times$seconds <- times$time/1e9


ggplot(data = times, 
       mapping = aes(x = nrow, y = seconds, color = expr)) + 
  geom_point() + 
  geom_smooth(se = FALSE) + 
  scale_x_log10() + 
  scale_y_log10() + 
  theme(legend.position = "bottom") +
  scale_color_brewer(palette = "Dark2") +
  ggtitle("Example 1 (standard rep): time to extract first row, dplyr::slice() versus base R [, ]",
          subtitle = "task time plotted as a function of number of data rows")
```

    ## `geom_smooth()` using method = 'loess' and formula 'y ~ x'

![](slice_timing_files/figure-gfm/unnamed-chunk-1-1.png)<!-- -->

``` r
# compute time ratios
layout <- blocks_to_rowrecs_spec(
  wrapr::qchar_frame(
    "expr"         , "seconds"     |
      "slice(d, 1)", slice_time |
      "d[1, ]"     , base_R_time      ),
  recordKeys = "nrow")

print(layout)
```

    ## {
    ##  block_record <- wrapr::qchar_frame(
    ##    "nrow"  , "expr"       , "seconds"   |
    ##      .     , "slice(d, 1)", slice_time  |
    ##      .     , "d[1, ]"     , base_R_time )
    ##  block_keys <- c('nrow', 'expr')
    ## 
    ##  # becomes
    ## 
    ##  row_record <- wrapr::qchar_frame(
    ##    "nrow"  , "slice_time", "base_R_time" |
    ##      .     , slice_time  , base_R_time   )
    ##  row_keys <- c('nrow')
    ## 
    ##  # args: c(checkNames = TRUE, checkKeys = TRUE, strict = FALSE, allow_rqdatatable = FALSE)
    ## }

``` r
calc_ratios <- local_td(times) %.>%
  project(., 
          groupby = c("expr", "nrow"),
          seconds = mean(seconds)) %.>%
  layout %.>%
  extend(.,
         ratio = slice_time/base_R_time)

cat(format(calc_ratios))
```

    ## table(times; 
    ##   expr,
    ##   time,
    ##   nrow,
    ##   seconds) %.>%
    ##  project(., seconds := mean(seconds),
    ##   g= expr, nrow) %.>%
    ##  non_sql_node(., blocks_to_rowrecs(.)) %.>%
    ##  extend(.,
    ##   ratio := slice_time / base_R_time)

``` r
ratios <- times %.>% calc_ratios

ggplot(data = ratios, 
       mapping = aes(x = nrow, y = ratio)) +
  geom_point() + 
  geom_smooth(se = FALSE) + 
  scale_x_log10() + 
  scale_y_log10() + 
  theme(legend.position = "bottom") +
  scale_color_brewer(palette = "Dark2") +
  ggtitle("Example 1 (standard rep): ratio of time to extract first row, dplyr::slice() over base R [, ]",
          subtitle = "ratio plotted as a function of number of data rows")
```

    ## `geom_smooth()` using method = 'loess' and formula 'y ~ x'

![](slice_timing_files/figure-gfm/unnamed-chunk-1-2.png)<!-- -->

``` r
f2 <- function(k) {
  # first touch seems to trigger a conversion, so only measure that
  d <- data.frame(x = 1:k, y = 1:k)
  rownames(d) <- NULL
  d <- tbl_df(d)
  gc()
  tm <- microbenchmark::microbenchmark(
    slice(d, 1),
    times = 1L
  )
  td1 <- data.frame(tm)
  td1$nrow <- nrow(d)
  d <- data.frame(x = 1:k, y = 1:k)
  rownames(d) <- NULL
  d <- tbl_df(d)
  gc()
  tm <- microbenchmark::microbenchmark(
    d[1, ],
    times = 1L
  )
  td2 <- data.frame(tm)
  td2$nrow <- nrow(d)
  rbind(td1, td2)
}


times_ALTREP <- lapply(2^(0:30), f2)
times_ALTREP <- data.frame(data.table::rbindlist(times_ALTREP))
times_ALTREP$seconds <- times_ALTREP$time/1e9


ggplot(data = times_ALTREP, 
       mapping = aes(x = nrow, y = seconds, color = expr)) + 
  geom_point() + 
  geom_smooth(se = FALSE) + 
  scale_x_log10() + 
  scale_y_log10() + 
  theme(legend.position = "bottom") +
  scale_color_brewer(palette = "Dark2") +
  ggtitle("Example 2 (ALTREP): time to extract first row, dplyr::slice() versus base R [, ]",
          subtitle = "task time plotted as a function of number of data rows")
```

    ## `geom_smooth()` using method = 'loess' and formula 'y ~ x'

![](slice_timing_files/figure-gfm/unnamed-chunk-1-3.png)<!-- -->

``` r
# compute time ratios
ratios_ALTREP <- times_ALTREP %.>% calc_ratios

ggplot(data = ratios_ALTREP, 
       mapping = aes(x = nrow, y = ratio)) +
  geom_point() + 
  geom_smooth(se = FALSE) + 
  scale_x_log10() + 
  scale_y_log10() + 
  theme(legend.position = "bottom") +
  scale_color_brewer(palette = "Dark2") +
  ggtitle("Example 2 (ALTREP): ratio of time to extract first row, dplyr::slice() over base R [, ]",
          subtitle = "ratio plotted as a function of number of data rows")
```

    ## `geom_smooth()` using method = 'loess' and formula 'y ~ x'

![](slice_timing_files/figure-gfm/unnamed-chunk-1-4.png)<!-- -->
