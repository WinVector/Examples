GCD by Herminte Normal Form
================
2024-11-17

Extended GCD as Herminte normal form version of [the remainder
problem](https://github.com/WinVector/Examples/blob/main/puzzles/DividingCoconuts/RemainderProblem.ipynb).

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

Links:

- [W. A. Blankinship, “A New Version of the Euclidean Algorithm”, The
  American Mathematical Monthly, Vol. 70, No. 7 (Aug. - Sep., 1963),
  Taylor & Francis, Ltd. for Mathematical Association of America,
  pp. 742-745](https://www.jstor.org/stable/2312260).
- George Havas, Bohdan S. Majewski, and Keith R. Matthews, “Extended GCD
  and Hermite Normal Form Algorithms via Lattice Basis Reduction”,
  Experimental Mathematics 7:2, K Peters, Ltd. 058-6458/1998, pp. 1-25.
- [S. A. Rankin, “The Euclidean Algorithm and the Linear Diophantine
  Equation ax + by = gcd(a, b)”, The American Mathematical Monthly, Vol.
  120, No. 6 (June–July 2013),
  pp. 562-564](https://www.jstor.org/stable/10.4169/amer.math.monthly.120.06.562).
