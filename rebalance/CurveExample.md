CurveExample
================

``` r
library(ggplot2)
```

    ## Warning: replacing previous import 'vctrs::data_frame' by 'tibble::data_frame'
    ## when loading 'dplyr'

``` r
a = 3.2
b = 2.4

t = seq(0, 1, length.out = 101)
```

``` r
parametric_example <- data.frame(
  x = 1 - pbeta(t, b, a),
  y = 1 - pbeta(t, a, b))

s <- log(1 - pbeta(0.5, b, a)) / log(0.5)
print(s)
```

    ## [1] 1.484192

``` r
# 1, s solution
parametric_example_s <- data.frame(
  x = 1 - pbeta(t, 1, s),
  y = 1 - pbeta(t, s, 1))

ggplot(mapping = aes(x = x, y = y)) +
  geom_point(data = parametric_example, color = "Orange") + 
  geom_line(data = parametric_example_s, color = "DarkBlue") + 
  ggtitle("a, b system compared to 1, s system")
```

![](CurveExample_files/figure-gfm/unnamed-chunk-3-1.png)<!-- -->

``` r
equation_example <- data.frame(
  x = seq(0, 1, length.out = 101))
equation_example$y <-  1 - (1 - equation_example$x^(1/s))^s

ggplot(mapping = aes(x = x, y = y)) +
  geom_point(data = parametric_example, color = "Orange") + 
  geom_line(data = equation_example, color = "DarkBlue") + 
  ggtitle("a, b system compared equation plot")
```

![](CurveExample_files/figure-gfm/unnamed-chunk-4-1.png)<!-- -->
