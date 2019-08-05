Tides.Rmd
================

``` r
library(TideHarmonics)
library(wrapr)
```

    ## Warning: package 'wrapr' was built under R version 3.5.2

``` r
library(ggplot2)
```

    ## Warning: package 'ggplot2' was built under R version 3.5.2

``` r
tides <- readRDS('tides.RDS')
```

``` r
base_date_time =  as.POSIXct('2001/01/01 00:00', tz = "UTC")
first_date_time =  as.POSIXct('2019/06/01 00:00', tz = "UTC")
cut_date_time = as.POSIXct('2019/07/15 00:00', tz = "UTC")
```

``` r
dtrain <- tides[tides$dt<cut_date_time, , drop = FALSE]
dtest <- tides[tides$dt>=cut_date_time, , drop = FALSE]
```

``` r
model <- ftide(dtrain$tide_feet, dtrain$dt)
dtrain$pred <- predict(model,
                      from=dtrain$dt[1],
                      to=dtrain$dt[nrow(dtrain)],
                      by=0.1)
dtest$pred <- predict(model,
                      from=dtest$dt[1],
                      to=dtest$dt[nrow(dtest)],
                      by=0.1)
```

``` r
ggplot(aes(x=dt), data=dtest) +
  geom_line(aes(y=tide_feet), color='blue', alpha=0.5) + 
  geom_line(aes(y=pred), color='black', alpha=0.5) +
  ggtitle("prediction (blue) superimposed on actuals on test")
```

![](TidesR_files/figure-gfm/unnamed-chunk-6-1.png)<!-- -->

``` r
ggplot(aes(x=pred, y=tide_feet), data=dtest) +
  geom_point(alpha=0.1) + 
  ggtitle("prediction versus actual on test")
```

![](TidesR_files/figure-gfm/unnamed-chunk-7-1.png)<!-- -->
