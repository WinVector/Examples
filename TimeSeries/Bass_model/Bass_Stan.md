Bass Model by Stan
================
2025-03-14

See also:
<https://srdas.github.io/MLBook/productForecastingBassModel.html>

``` r
library(rstan)
```

    ## Loading required package: StanHeaders

    ## 
    ## rstan version 2.32.6 (Stan version 2.32.2)

    ## For execution on a local, multicore CPU with excess RAM we recommend calling
    ## options(mc.cores = parallel::detectCores()).
    ## To avoid recompilation of unchanged Stan programs, we recommend calling
    ## rstan_options(auto_write = TRUE)
    ## For within-chain threading using `reduce_sum()` or `map_rect()` Stan functions,
    ## change `threads_per_chain` option:
    ## rstan_options(threads_per_chain = 1)

``` r
library(ggplot2)
library(geomtextpath)
knitr::opts_chunk$set(fig.height = 6, fig.width = 9)
```

Data from:

<https://stackoverflow.blog/2017/09/06/incredible-growth-python/>
<https://trends.stackoverflow.co/?tags=python>

saved as: stackoverflow-trends-chart-python.svg exported to:
stackoverflow-trends-chart-python.png

converted with
<https://web.eecs.utk.edu/~dcostine/personal/PowerDeviceLib/DigiTest/index.html>

``` r
# read data
d_all <- read.csv('tag_trends_Pyton.csv', stringsAsFactors = FALSE, strip.white = TRUE)
d_all['date'] = as.Date(d_all[['date']])
```

``` r
tag <- 'Python'
d_match <- d_all[d_all$tag == tag, c('date', 'percent', 'tag')]
n_pad <- 36
new_dates <- seq(d_match$date[nrow(d_match)], by='1 month', length.out = n_pad + 1)[2:(n_pad + 1)]
```

``` r
d_plot <- rbind(
  d_match,
  data.frame(
    date = new_dates,
    percent = NA,
    tag = d_match$tag[[1]]))
d_plot['what'] = 'actuals'
```

``` r
fit_pred_given_train_date <- function(train_cut_date) {
  d_train <- d_match[d_match$date <= train_cut_date, , drop = FALSE]
  # run Stan model
  # see:
  # https://github.com/WinVector/Examples/blob/31066ae1d42c369ffcf3d0544f3972ed4f691e2c/MetaAnalysis/Amlodipine/ExaminingMetaAnalysis.m
  stan_data = list(
    N = nrow(d_train),
    s = array(d_train$percent, dim = nrow(d_train)),
    cumsum_s = array(cumsum(d_train$percent), dim = nrow(d_train)),
    total_s = sum(d_train$percent)
  )
  res <- as.data.frame(stan(
    file = "Bass_Stan.stan",
    data = stan_data,
    chains = 4,                 # number of Markov chains
    warmup = 2000,              # number of warmup iterations per chain
    iter = 4000,                # total number of iterations per chain
    cores = 4,                  # number of cores (could use one per chain)
    refresh = 0                # no progress shown
  ))
  cm <- colMeans(res)
  plot_Bass_curve <- function(values, n_pad, p, q, m) {
    #PLOT THE FITTED MODEL, shifted to match values
    nqtrs = length(values)
    t=seq(-4 * nqtrs, 4 * nqtrs + n_pad)
    FF = expression(p*(exp((p+q)*t)-1)/(p*exp((p+q)*t)+q))
    ff = D(FF,"t")
    fn_f = as.numeric(eval(ff)*m)
    pred <- fn_f
    errs <- vapply(
      seq(0, length(pred) - length(values) - 1), 
      function(i) {
        sum((pred[seq(1 + i, length(values) + i)] - values)**2)
      }, 
      FUN.VALUE = numeric(1))
    best_i = which.min(errs) - 1
    pred <- pred[seq(1 + best_i, length(values) + best_i + n_pad)]
    return(pred)
  }
  preds <- plot_Bass_curve(
    d_train$percent, 
    n_pad = n_pad, 
    p = cm[['p']],
    q = cm[['q']], 
    m = cm[['m']])
  preds <- c(preds, rep(NA, nrow(d_plot) - length(preds)))
  d_predict <- d_plot
  d_predict['percent'] <- preds
  d_predict['what'] <- paste0("Stan_pred_", train_cut_date)
  d_predict['is_forecast'] <- d_predict$date > train_cut_date
  return(d_predict)
}
```

``` r
d_predict <- lapply(
  seq(as.Date('2018-01-01'), as.Date('2025-01-01'), by = '1 year'),
  fit_pred_given_train_date)
```

    ## Warning: There were 3979 divergent transitions after warmup. See
    ## https://mc-stan.org/misc/warnings.html#divergent-transitions-after-warmup
    ## to find out why this is a problem and how to eliminate them.

    ## Warning: Examine the pairs() plot to diagnose sampling problems

    ## Warning: There were 4375 divergent transitions after warmup. See
    ## https://mc-stan.org/misc/warnings.html#divergent-transitions-after-warmup
    ## to find out why this is a problem and how to eliminate them.

    ## Warning: Examine the pairs() plot to diagnose sampling problems

    ## Warning: There were 4485 divergent transitions after warmup. See
    ## https://mc-stan.org/misc/warnings.html#divergent-transitions-after-warmup
    ## to find out why this is a problem and how to eliminate them.

    ## Warning: Examine the pairs() plot to diagnose sampling problems

    ## Warning: There were 4553 divergent transitions after warmup. See
    ## https://mc-stan.org/misc/warnings.html#divergent-transitions-after-warmup
    ## to find out why this is a problem and how to eliminate them.

    ## Warning: Examine the pairs() plot to diagnose sampling problems

    ## Warning: There were 3652 divergent transitions after warmup. See
    ## https://mc-stan.org/misc/warnings.html#divergent-transitions-after-warmup
    ## to find out why this is a problem and how to eliminate them.

    ## Warning: Examine the pairs() plot to diagnose sampling problems

    ## Warning: There were 2 divergent transitions after warmup. See
    ## https://mc-stan.org/misc/warnings.html#divergent-transitions-after-warmup
    ## to find out why this is a problem and how to eliminate them.

    ## Warning: Examine the pairs() plot to diagnose sampling problems

``` r
d_predict <- do.call(rbind, d_predict)
```

``` r
saveRDS(
  list(d_plot = d_plot, d_predict = d_predict), 
  paste0(tag, "_predictions_Bass.RDS"))
```

``` r
ggplot(mapping = aes(x = date, y = percent)) +
  geom_point(data = na.omit(d_plot)) +
  geom_line(
    data = na.omit(d_predict),
    mapping = aes(color = what, linetype = is_forecast)) +
  geom_textvline(
    data = data.frame(
      date = as.Date('2022-11-30'),
      label = 'ChatGPT release'
      ),
      mapping = aes(xintercept = date, label = label),
    ) + 
  ggtitle(paste0(tag, " projection as a function of training date"))
```

![](Bass_Stan_files/figure-gfm/unnamed-chunk-9-1.png)<!-- -->
