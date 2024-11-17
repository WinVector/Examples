GCD by Herminte Normal Form
================
2024-11-17

``` r
# extended GCD by Hermite normal form
library(numbers)

a = matrix(c(
  723217 - 480608, 508811 - 480608),
  nrow = 1, ncol = 2, byrow = TRUE)

a
```

    ##        [,1]  [,2]
    ## [1,] 242609 28203

``` r
hnf <- hermiteNF(a)

hnf
```

    ## $H
    ##      [,1] [,2]
    ## [1,]   79    0
    ## 
    ## $U
    ##      [,1] [,2]
    ## [1,]  -88 -357
    ## [2,]  757 3071

``` r
stopifnot(all(a %*% hnf$U == hnf$H))

hnf$H  # GCD
```

    ##      [,1] [,2]
    ## [1,]   79    0

``` r
hnf$U[ , 1]  # multipliers
```

    ## [1] -88 757

``` r
hnf$U[1 , 1] * a[1, 1] + hnf$U[2 , 1] * a[1, 2]
```

    ## [1] 79
