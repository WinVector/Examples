Prevalence Adjustment
================

``` r
library(wrapr)
library(numbers)
```

``` r
d <- wrapr::build_frame(
   "prediction"  , "truth" |
     0.875       , TRUE    |
     0.875       , TRUE    |
     0.250       , FALSE   )
d$orig_row_id <- seq_len(nrow(d))

knitr::kable(d)
```

| prediction | truth | orig\_row\_id |
| ---------: | :---- | ------------: |
|      0.875 | TRUE  |             1 |
|      0.875 | TRUE  |             2 |
|      0.250 | FALSE |             3 |

``` r
prevalence <- mean(d$truth)

prevalence
```

    ## [1] 0.6666667

``` r
epsilon <- 1.0e-9
stopifnot(abs(prevalence  -  mean(d$prediction)) < epsilon)
prevalence  -  mean(d$prediction)
```

    ## [1] 0

Build a deterministic re-sampled data set with 50% prevalence.

``` r
# get how many times to replicate each row group
count_table <- aggregate(
  count ~ truth, 
  data = transform(d, count = 1), 
  FUN = length)

multiple <- Reduce(LCM, count_table$count)
count_table$n_reps <- multiple / count_table$count

knitr::kable(count_table)
```

| truth | count | n\_reps |
| :---- | ----: | ------: |
| FALSE |     1 |       2 |
| TRUE  |     2 |       1 |

``` r
# replicate each row group by the target number of times
rep_table <- count_table %.>%
 lapply(
  seq_len(nrow(.)),
  function(i) {
    data.frame(
      truth = .$truth[[i]],
      row_rep = seq_len(.$n_reps[[i]]))
  }) %.>%
  do.call(rbind, .)

d_2 <- merge(d, rep_table, by = 'truth') %.>%
  .[order(.$orig_row_id, .$row_rep), ]
rownames(d_2) <- NULL

knitr::kable(d_2)
```

| truth | prediction | orig\_row\_id | row\_rep |
| :---- | ---------: | ------------: | -------: |
| TRUE  |      0.875 |             1 |        1 |
| TRUE  |      0.875 |             2 |        1 |
| FALSE |      0.250 |             3 |        1 |
| FALSE |      0.250 |             3 |        2 |

``` r
prevalence_2 <- mean(d_2$truth)

prevalence_2
```

    ## [1] 0.5

``` r
stopifnot(abs(prevalence_2  - mean(d_2$prediction)) > 1e-3)
mean(d_2$prediction)
```

    ## [1] 0.5625

<https://win-vector.com/2020/10/10/upcoming-series-probability-model-homotopy/>

``` r
sigmoid <- function(x) {
  1 / (1 + exp(-x))
}

logit <- function(x) {
  log( x / (1 - x) )
}

delta <- -logit(prevalence) + logit(prevalence_2)

delta
```

    ## [1] -0.6931472

Show only rows with different original scores.

``` r
d_2$orig_row_id <- NULL
d_2$row_rep <- NULL

indices <- match(sort(unique(d_2$prediction)), d_2$prediction)

indices
```

    ## [1] 3 1

Add our p-adjusted prediction and show the intereseting rows.

``` r
d_2$p_adjusted_prediction <- sigmoid(
  logit(d_2$prediction) + delta)

d_2 %.>%
  subset(., seq_len(nrow(.)) %in% indices, select = -truth) %.>%
  knitr::kable(.)
```

|   | prediction | p\_adjusted\_prediction |
| :- | ---------: | ----------------------: |
| 1 |      0.875 |               0.7777778 |
| 3 |      0.250 |               0.1428571 |

``` r
stopifnot(abs(prevalence_2  - mean(d_2$p_adjusted_prediction)) > 1e-3)
mean(d_2$p_adjusted_prediction)
```

    ## [1] 0.4603175

``` r
f <- function(d) {
  mean(d_2$truth) - mean(sigmoid(logit(d_2$prediction) + d))
}

delta_2 <- uniroot(f, c(-2, 2), tol = .Machine$double.eps)

delta_2
```

    ## $root
    ## [1] -0.4236489
    ## 
    ## $f.root
    ## [1] 0
    ## 
    ## $iter
    ## [1] 5
    ## 
    ## $init.it
    ## [1] NA
    ## 
    ## $estim.prec
    ## [1] 1.576351

``` r
d_2$u_adjusted_prediction <- sigmoid(
  logit(d_2$prediction) + delta_2$root)

d_2 %.>%
  subset(., seq_len(nrow(.)) %in% indices, select = -truth) %.>%
  knitr::kable(.)
```

|   | prediction | p\_adjusted\_prediction | u\_adjusted\_prediction |
| :- | ---------: | ----------------------: | ----------------------: |
| 1 |      0.875 |               0.7777778 |               0.8208712 |
| 3 |      0.250 |               0.1428571 |               0.1791288 |

``` r
stopifnot(abs(prevalence_2  -  mean(d_2$u_adjusted_prediction)) < epsilon)
mean(d_2$u_adjusted_prediction)
```

    ## [1] 0.5

Platt scaling <https://en.wikipedia.org/wiki/Platt_scaling>

``` r
platt_scaler <- glm(
  truth ~ logit(prediction), 
  data = d_2, 
  family = binomial())

d_2$platt_scaled_prediction <- predict(
  platt_scaler,
  newdata = d_2,
  type = 'response')

d_2 %.>%
  subset(., seq_len(nrow(.)) %in% indices, select = -truth) %.>%
  knitr::kable(.)
```

|   | prediction | p\_adjusted\_prediction | u\_adjusted\_prediction | platt\_scaled\_prediction |
| :- | ---------: | ----------------------: | ----------------------: | ------------------------: |
| 1 |      0.875 |               0.7777778 |               0.8208712 |                         1 |
| 3 |      0.250 |               0.1428571 |               0.1791288 |                         0 |

``` r
stopifnot(abs(prevalence_2  -  mean(d_2$platt_scaled_prediction)) < epsilon)
mean(d_2$platt_scaled_prediction)
```

    ## [1] 0.5

``` r
platt_shifter <- glm(
  truth ~ 1, 
  offset = logit(prediction),
  data = d_2, 
  family = binomial())

d_2$platt_shifted_prediction <- predict(
  platt_shifter,
  newdata = d_2,
  type = 'response')

d_2 %.>%
  subset(., seq_len(nrow(.)) %in% indices, select = -truth) %.>%
  knitr::kable(.)
```

|   | prediction | p\_adjusted\_prediction | u\_adjusted\_prediction | platt\_scaled\_prediction | platt\_shifted\_prediction |
| :- | ---------: | ----------------------: | ----------------------: | ------------------------: | -------------------------: |
| 1 |      0.875 |               0.7777778 |               0.8208712 |                         1 |                  0.8208712 |
| 3 |      0.250 |               0.1428571 |               0.1791288 |                         0 |                  0.1791288 |

``` r
stopifnot(abs(prevalence_2  -  mean(d_2$platt_shifted_prediction)) < epsilon)
mean(d_2$platt_shifted_prediction)
```

    ## [1] 0.5
