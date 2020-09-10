ROC\_beta
================

``` r
library(ggplot2)
```

``` r
mk_curve <- function(a, b) {
  d <- data.frame(
    t = seq(0, 1, length.out = 101)
  )
  d$y <- pbeta(d$t, shape1 = a, shape2 = b)
  # d$x <- 1 - pbeta(1 - d$t, shape1 = a, shape2 = b)
  d$x <- pbeta(d$t, shape1 = b, shape2 = a)
  d$a <- a
  d$b <- b
  d$what <- paste0('a=', a, ', b=', b)
  d
}

d1 <- mk_curve(2, 3.1)
d2 <- mk_curve(1.93, 3)

ggplot() + 
  geom_line(data = d1,
            mapping = aes(x = x, y = y),
            color = 'DarkGreen') +
  geom_line(data = d2,
            mapping = aes(x = x, y = y),
            color = "Purple") + 
  theme(aspect.ratio=1)
```

![](ROC_beta_files/figure-gfm/unnamed-chunk-2-1.png)<!-- -->

``` r
d1 <- mk_curve(2, 3.1)
d2 <- mk_curve(2, 30)

ggplot() + 
  geom_line(data = d1,
            mapping = aes(x = x, y = y),
            color = 'DarkGreen') +
  geom_line(data = d2,
            mapping = aes(x = x, y = y),
            color = "Purple") + 
  theme(aspect.ratio=1)
```

![](ROC_beta_files/figure-gfm/unnamed-chunk-2-2.png)<!-- -->

``` r
d1 <- mk_curve(2, 3.1)
d2 <- mk_curve(3, 3)

ggplot() + 
  geom_line(data = d1,
            mapping = aes(x = x, y = y),
            color = 'DarkGreen') +
  geom_line(data = d2,
            mapping = aes(x = x, y = y),
            color = "Purple") + 
  theme(aspect.ratio=1)
```

![](ROC_beta_files/figure-gfm/unnamed-chunk-2-3.png)<!-- -->

``` r
d1 <- mk_curve(6, 14)
d2 <- mk_curve(3, 7)

ggplot() + 
  geom_line(data = d1,
            mapping = aes(x = x, y = y),
            color = 'DarkGreen') +
  geom_line(data = d2,
            mapping = aes(x = x, y = y),
            color = "Purple") + 
  theme(aspect.ratio=1)
```

![](ROC_beta_files/figure-gfm/unnamed-chunk-2-4.png)<!-- -->
