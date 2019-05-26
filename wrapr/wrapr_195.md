magrittr\_195
================

``` r
# an arbitrary R-code example from https://github.com/tidyverse/magrittr/issues/195

gen <- function(x) function() eval(quote(x))
fn <- gen(1)
fn()
```

    ## [1] 1

``` r
# take "fn() returns 1" as reference (desired) behavior
```

``` r
# magrittr attempting re-write of gen(1) as 1 %>% gen()
library(magrittr)

fn_magrittr <- 1 %>% gen()
fn_magrittr()
```

    ## $value
    ## function() eval(quote(x))
    ## <bytecode: 0x7faf6e80f700>
    ## <environment: 0x7faf6dc55718>
    ## 
    ## $visible
    ## [1] TRUE

``` r
# not equal to 1, the reference behavior.
```

``` r
# wrapr attempting re-write of gen(1) as 1 %.>% gen(.)
library(wrapr)

fn_wrapr <- 1 %.>% gen(.)
fn_wrapr()
```

    ## [1] 1

``` r
# returns 1, the target reference behavior.
```
