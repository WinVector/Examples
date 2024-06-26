traj_graph_2
================
2024-06-23

``` r
library(ggplot2)
```

    ## Warning: package 'ggplot2' was built under R version 4.3.2

``` r
library(data.table)
```

    ## Warning: package 'data.table' was built under R version 4.3.2

``` r
library(wrapr)
```

    ## 
    ## Attaching package: 'wrapr'

    ## The following objects are masked from 'package:data.table':
    ## 
    ##     :=, let

``` r
set.seed(2024)
```

``` r
build_traj <- function(d_ex, lambda_max = 3, length.out = 100) {
    frame <- list()
    model_coefs <- NULL
    suppressWarnings(
      for(lambda in seq(0, lambda_max, length.out = length.out)) {
        model <- glm(y ~ x1 + x2, family=binomial(), data=d_ex, weights = 1 + lambda * d_ex$y)
        model_coefs <- coef(model)
        preds <- predict(model, type='response', newdata=d_ex)
        row_frame <- as.data.frame(t(as.matrix(preds)))
        row_frame['lambda'] <- lambda
        frame <- c(frame, list(row_frame))
      }
    )
    frame <- do.call(rbind, frame)
    return(list(frame=frame, model_coefs=model_coefs))
}
```

``` r
plot_traj_graph <- function(d_ex, ..., lambda_max = 3, title = '') {
  to[frame, model_coefs] <- build_traj(d_ex, lambda_max = lambda_max)
  plot_dat <- data.frame(data.table::melt(
    data.table(frame), 
    variable.name = 'row',
    value.name = 'score',
    id.vars='lambda'))
  g <- ggplot(
    data=plot_dat,
    mapping=aes(x=lambda, y=score, color=row, shape=row)
  ) +
    geom_line(alpha=0.5) +
    geom_point(alpha=0.5) +
    ggtitle(title)
  return(list(plot=g, model_coefs=model_coefs))
}
```

``` r
d_ex_1 <- wrapr::build_frame(
   "x1"  , "x2", "y" |
     0   , 0   , 0   |
     1   , 0   , 1   |
     -2  , 0   , 0   |
     0   , 2   , 1   |
     1   , 2   , 1   |
     1   , 1   , 0   )
```

``` r
to[plot, model_coefs] <- plot_traj_graph(d_ex_1, title='ex_1')
print(model_coefs)
```

    ## (Intercept)          x1          x2 
    ##   -0.563986    1.882809    1.378345

``` r
plot
```

![](traj_graph_2_files/figure-gfm/unnamed-chunk-5-1.png)<!-- -->

``` r
 d_ex_2 <- wrapr::build_frame(
    "x1"  , "x2", "x3", "x4", "y"   |
      -4L ,  4L ,  0L , -2L , TRUE  |
       3L , -5L , -1L , -1L , TRUE  |
       1L , -3L , -1L , -3L , TRUE  |
      -5L , -2L , -3L , -5L , TRUE  |
       4L , -3L ,  1L , -5L , FALSE |
      -1L ,  3L ,  2L , -3L , TRUE  |
       2L ,  2L , -2L , -2L , FALSE |
      -5L ,  3L , -3L ,  5L , TRUE  |
       5L ,  5L , -1L , -1L , FALSE |
      -2L , -5L ,  2L , -4L , FALSE )
```

``` r
to[plot, model_coefs] <- plot_traj_graph(d_ex_2, title='ex_2')
print(model_coefs)
```

    ## (Intercept)          x1          x2 
    ##   1.8930684  -0.5586554  -0.1716650

``` r
plot
```

    ## Warning: The shape palette can deal with a maximum of 6 discrete values because more
    ## than 6 becomes difficult to discriminate
    ## ℹ you have requested 10 values. Consider specifying shapes manually if you need
    ##   that many have them.

    ## Warning: Removed 400 rows containing missing values or values outside the scale range
    ## (`geom_point()`).

![](traj_graph_2_files/figure-gfm/unnamed-chunk-7-1.png)<!-- -->

``` r
d_ex_3 <- wrapr::build_frame(
   "x1"  , "x2", "y" |
     0   , 0   , 0   |
     1   , 0   , 1   |
     0   , 1   , 1   |
     1   , 1   , 0   |
     -1  , 1   , 0   |
     1   , -1  , 0   )
```

``` r
to[plot, model_coefs] <- plot_traj_graph(d_ex_3, lambda_max = 1000, title='ex_3')
print(model_coefs)
```

    ## (Intercept)          x1          x2 
    ##  -0.6931479   7.6009037   7.6009037

``` r
plot
```

![](traj_graph_2_files/figure-gfm/unnamed-chunk-9-1.png)<!-- -->

``` r
want_frame <- function(frame) {
  check_eps = 0.03
  n_f_rows <- nrow(frame)
  have_cross <- FALSE
  have_increasing <- FALSE
  have_decreasing <- FALSE
  have_non_monotone <- FALSE
  for(col in colnames(frame)) {
    if(col != 'lambda') {
      col_v <- frame[[col]]
      have_increasing <- have_increasing || ((col_v[[1]] + check_eps) < col_v[[n_f_rows]])
      have_decreasing <- have_decreasing || ((col_v[[1]] - check_eps) > col_v[[n_f_rows]])
      have_non_monotone <- have_non_monotone || (min(col_v) + check_eps < min(col_v[[1]], col_v[[n_f_rows]])) || (max(col_v) - check_eps > max(col_v[[1]], col_v[[n_f_rows]])) 
      for(col2 in colnames(frame)) {
        if(col2 != 'lambda') {
          col2_v <- frame[[col2]]
          see_cross <- (abs(col_v[[1]] - col2_v[[1]]) > check_eps) && (abs(col_v[[n_f_rows]] - col2_v[[n_f_rows]]) > check_eps) && (col_v[[n_f_rows]] != col2_v[[n_f_rows]]) && ((col_v[[1]] > col2_v[[1]]) != (col_v[[n_f_rows]] > col2_v[[n_f_rows]]))
          have_cross <- have_cross || see_cross
        }
      }
    }
  }
  return(have_increasing && have_decreasing && have_cross)
}
```

``` r
mk_example <- function() {
  d_cols <- c('x1', 'x2', 'y')
  n_rows <- 10
  while(TRUE) {
    d_ex <- data.frame(matrix(
      sample(seq(-20, 20), size = length(d_cols) * n_rows, replace = TRUE),
      ncol=length(d_cols)))
    colnames(d_ex) <- d_cols
    d_ex['y'] = d_ex['y'] >= 0
    to[frame, model_coefs] <- build_traj(d_ex)
    if(want_frame(frame)) {
      return(d_ex)
    }
  }
}
```

``` r
d_ex <- mk_example()
```

``` r
cat(wrapr::draw_frame(d_ex))
```

    ## d_ex <- wrapr::build_frame(
    ##    "x1"  , "x2", "y"   |
    ##      -12L,   8L, TRUE  |
    ##       10L, -17L, TRUE  |
    ##        8L, -13L, TRUE  |
    ##       18L,  -9L, FALSE |
    ##       17L,  13L, FALSE |
    ##      -20L, -11L, FALSE |
    ##        0L,  12L, FALSE |
    ##       15L, -12L, FALSE |
    ##       17L, -16L, FALSE |
    ##      -12L,  14L, TRUE  )

``` r
knitr::kable(d_ex)
```

|  x1 |  x2 | y     |
|----:|----:|:------|
| -12 |   8 | TRUE  |
|  10 | -17 | TRUE  |
|   8 | -13 | TRUE  |
|  18 |  -9 | FALSE |
|  17 |  13 | FALSE |
| -20 | -11 | FALSE |
|   0 |  12 | FALSE |
|  15 | -12 | FALSE |
|  17 | -16 | FALSE |
| -12 |  14 | TRUE  |

``` r
to[plot, model_coefs] <- plot_traj_graph(d_ex, title='ex')
print(model_coefs)
```

    ## (Intercept)          x1          x2 
    ##  1.15381279 -0.12114995 -0.06336498

``` r
plot
```

    ## Warning: The shape palette can deal with a maximum of 6 discrete values because more
    ## than 6 becomes difficult to discriminate
    ## ℹ you have requested 10 values. Consider specifying shapes manually if you need
    ##   that many have them.

    ## Warning: Removed 400 rows containing missing values or values outside the scale range
    ## (`geom_point()`).

![](traj_graph_2_files/figure-gfm/unnamed-chunk-15-1.png)<!-- -->

``` r
w_1 <- rep(1, nrow(d_ex))
model_1 <- glm(
  y ~ x1 + x2, 
  family=binomial(), 
  data=d_ex, 
  weights = w_1)
soln_1 <- coef(model_1)

soln_1
```

    ## (Intercept)          x1          x2 
    ## -0.23785437 -0.05733315 -0.01072208

``` r
eps <- 1e-5
w_2 <- w_1 + eps * d_ex$y
model_2 <- glm(
  y ~ x1 + x2, 
  family=binomial(), 
  data=d_ex, 
  weights = w_2)
soln_2 <- coef(model_2)

soln_2
```

    ## (Intercept)          x1          x2 
    ## -0.23784424 -0.05733338 -0.01072231

``` r
diff <- (soln_2 - soln_1) / eps

diff
```

    ## (Intercept)          x1          x2 
    ##  1.01304096 -0.02326024 -0.02357553

``` r
w <- w_1
p <- predict(model_1, type='response', newdata=d_ex)
y <- as.numeric(d_ex[['y']])
sum_M = matrix(0, nrow=3, ncol=3)
sum_V = rep(0, 3)
for(i in seq(nrow(d_ex))){
  x_i <- c(1, as.numeric(d_ex[i, c('x1', 'x2')]))
  sum_M <- sum_M + w[[i]] * p[[i]] * (1 - p[[i]]) * (x_i %*% t(x_i))
  sum_V <- sum_V + y[[i]] * (y[[i]] - p[[i]]) * x_i
}
b <- solve(sum_M, sum_V)

b
```

    ## [1]  1.01304587 -0.02326021 -0.02357555
