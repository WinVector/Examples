XICOR on the Peas Data Set
================
Nina Zumel
1/24/2022

Attempt to reproduce the results from Chatterjee’s paper

``` r
library(XICOR)
library(ggplot2)
library(dplyr)
```

    ## 
    ## Attaching package: 'dplyr'

    ## The following objects are masked from 'package:stats':
    ## 
    ##     filter, lag

    ## The following objects are masked from 'package:base':
    ## 
    ##     intersect, setdiff, setequal, union

``` r
library(psychTools)
```

``` r
data(peas)

# xi(X, Y)
calculateXI(peas$parent, peas$child, seed=NULL)
```

    ## [1] 0.131143

``` r
# xi(Y, X)
calculateXI(peas$child, peas$parent, seed=NULL)
```

    ## [1] 0.9225

Default behavior, average 10K simulation.

This is sets the seed to the same constant every time, so it’s actually
deterministic every run. Certainly not to be trusted for a significance
calculation.

``` r
N = 10000
xiXY = numeric(N)
xiYX = numeric(N)

for(i in 1:N) {
  xiXY = calculateXI(peas$parent, peas$child)
  xiYX = calculateXI(peas$child, peas$parent)
  
}

results = data.frame(seed = 'default', 
                     direction = c('XY', 'YX'),
                     xi = c(mean(xiXY), mean(xiYX)))

knitr::kable(results)
```

| seed    | direction |        xi |
|:--------|:----------|----------:|
| default | XY        | 0.1008343 |
| default | YX        | 0.9225000 |

Set the seed parameter to NULL. This seeds the run with the system time,
so it’s more likely to be correct.

``` r
xiXY = numeric(N)
xiYX = numeric(N)

for(i in 1:N) {
  xiXY = calculateXI(peas$parent, peas$child, seed=NULL)
  xiYX = calculateXI(peas$child, peas$parent, seed=NULL)
  
}

rerun = data.frame(seed = 'systime', 
                     direction = c('XY', 'YX'),
                     xi = c(mean(xiXY), mean(xiYX)))

knitr::kable(rerun)
```

| seed    | direction |        xi |
|:--------|:----------|----------:|
| systime | XY        | 0.1141543 |
| systime | YX        | 0.9225000 |
