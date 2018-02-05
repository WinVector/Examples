filter
================
2/4/2018

Set up the problem (from [here](https://github.com/tidyverse/dplyr/issues/3335)).

``` r
library("feather")
df <- as.data.frame(matrix(nrow = 1, 
                           ncol = 100000,
                           data = 0.0))
```

[R](https://www.r-project.org) timing.

``` r
system.time(fetched_sample <- df[df$V1>1, , drop=FALSE])
```

    ##    user  system elapsed 
    ##   0.603   0.003   0.607

[dplyr](https://CRAN.R-project.org/package=dplyr) timing.

``` r
library("dplyr")

tb <- as_tibble(df)

td <- system.time(fetched_sample <- filter(tb, V1>1))
print(td)
```

    ##    user  system elapsed 
    ## 125.055   7.720 133.680

[data.table](https://CRAN.R-project.org/package=data.table) timing.

``` r
library("data.table")

dt <- data.table(df)

system.time(dfr <- dt[V1>1, ])
```

    ##    user  system elapsed 
    ##   2.006   0.025   2.172

[Python](https://www.python.org) [Pandas](https://pandas.pydata.org) timing.

``` r
start_pandas <- Sys.time()
system.time(write_feather(df, "df.feather"))
```

    ##    user  system elapsed 
    ##   0.260   0.201   0.470

``` python
import pandas
import feather
import timeit
start_time = timeit.default_timer()
df = feather.read_dataframe('df.feather')
print(type(df))
```

    ## <class 'pandas.core.frame.DataFrame'>

``` python
print(df.shape)
```

    ## (1, 100000)

``` python
end_time = timeit.default_timer()
# seconds
print(end_time - start_time)
```

    ## 1.6644117410178296

``` python
start_time = timeit.default_timer()
df_filtered = df.query('V1>1')
sp = df_filtered.shape
end_time = timeit.default_timer()
# seconds
print(end_time - start_time)
```

    ## 3.8060011630004738

``` r
end_pandas <- Sys.time()
print(start_pandas)
```

    ## [1] "2018-02-05 08:08:21 PST"

``` r
print(end_pandas)
```

    ## [1] "2018-02-05 08:08:30 PST"

``` r
print(end_pandas - start_pandas)
```

    ## Time difference of 8.999062 secs

Characterize dplyr dependence on column count.

``` r
library("ggplot2")
library("dplyr")

sizes <- round(exp(seq(from=log(10), 
                       to=log(100000), 
                       length.out=20)))
frames <- lapply(
  sizes,
  function(nc) {
    df <- as.data.frame(matrix(nrow = 1, 
                               ncol = nc,
                               data = 0.0))
    tb <- as_tibble(df)
    gc()
    ti <- system.time(fetched_sample <- filter(tb, V1>1))
    data.frame(ncol = nc, 
               duration_seconds = as.numeric(ti[["elapsed"]]))
  })
frames <- bind_rows(frames)

mlinear <- lm(duration_seconds ~ 0 + ncol, data = frames)
frames$linear_trend <- predict(mlinear, newdata = frames)
mquad <- lm(duration_seconds ~ 0 + I(ncol*ncol), data = frames)
frames$quadratic_trend <- predict(mquad, newdata = frames)

ggplot(frames, 
       aes(x = ncol, y = duration_seconds)) + 
  geom_smooth(se = FALSE) +
  geom_point() + 
  geom_line(aes(y = linear_trend),
            linetype = 2, color = "green", alpha=0.5) +
  geom_line(aes(y = 0.1*linear_trend),
            linetype = 2, color = "green", alpha=0.5) +
  geom_line(aes(y = 10*linear_trend),
            linetype = 2, color = "green", alpha=0.5) +
  geom_line(aes(y = quadratic_trend),
            linetype = 2, color = "red", alpha=0.5) +
   geom_line(aes(y = 0.1*quadratic_trend),
            linetype = 2, color = "red", alpha=0.5) +
   geom_line(aes(y = 10*quadratic_trend),
            linetype = 2, color = "red", alpha=0.5) +
  scale_y_log10() +
  scale_x_log10() + 
  ggtitle("dplyr filter task durations on log-log paper (slope estimates power law)",
          subtitle = "linear and quadtratic fits shown as slope 1 and 2 dashed lines")
```

    ## `geom_smooth()` using method = 'loess'

![](filter_files/figure-markdown_github/shape-1.png)
