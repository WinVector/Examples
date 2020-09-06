Probility Density Model Examples
================

``` r
library(WVPlots)
```

    ## Loading required package: wrapr

    ## Warning: replacing previous import 'vctrs::data_frame' by 'tibble::data_frame'
    ## when loading 'dplyr'

``` r
d_uniform <- data.frame(x = runif(1000)) 
d_uniform$probablistic_outcome <- d_uniform$x >= runif(nrow(d_uniform))

DoubleDensityPlot(d_uniform, 'x', 'probablistic_outcome', truth_target = TRUE, title = 'well callibrated probability model, uniform density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-2-1.png)<!-- -->

``` r
ShadowHist(d_uniform, 'x', 'probablistic_outcome', title = 'well callibrated probability model, uniform density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-2-2.png)<!-- -->

``` r
ROCPlot(d_uniform, 'x', 'probablistic_outcome', truthTarget = TRUE, title = 'well callibrated probability model, uniform density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-2-3.png)<!-- -->

``` r
d_uniform$deterministic_outcome <- d_uniform$x >= 0.5

DoubleDensityPlot(d_uniform, 'x', 'deterministic_outcome', truth_target = TRUE, 
                  title = 'perfect classification rule, uniform density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-3-1.png)<!-- -->

``` r
ShadowHist(d_uniform, 'x', 'deterministic_outcome', 
           title = 'perfect classification rule, uniform density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-3-2.png)<!-- -->

``` r
ROCPlot(d_uniform, 'x', 'deterministic_outcome', truthTarget = TRUE, 
        title = 'perfect classification rule, uniform density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-3-3.png)<!-- -->

``` r
d_beta <- data.frame(x = rbeta(1000, shape1 = 0.5, shape2 = 0.5)) 
d_beta$probablistic_outcome <- d_beta$x >= runif(nrow(d_beta))

DoubleDensityPlot(d_beta, 'x', 'probablistic_outcome', truth_target = TRUE, 
                  title = 'well callibrated probability model, beta density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-4-1.png)<!-- -->

``` r
ShadowHist(d_beta, 'x', 'probablistic_outcome', title = 'well callibrated probability model, beta density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-4-2.png)<!-- -->

``` r
ROCPlot(d_beta, 'x', 'probablistic_outcome', truthTarget = TRUE, 
        title = 'well callibrated probability model, beta density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-4-3.png)<!-- -->

``` r
d_beta$deterministic_outcome <- d_beta$x >= 0.5

DoubleDensityPlot(d_beta, 'x', 'deterministic_outcome', truth_target = TRUE, 
                  title = 'perfect classification rule, beta density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-5-1.png)<!-- -->

``` r
ShadowHist(d_beta, 'x', 'deterministic_outcome', 
           title = 'perfect classification rule, beta density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-5-2.png)<!-- -->

``` r
ROCPlot(d_beta, 'x', 'deterministic_outcome', truthTarget = TRUE, 
        title = 'perfect classification rule, beta density')
```

![](DensityExample_files/figure-gfm/unnamed-chunk-5-3.png)<!-- -->
