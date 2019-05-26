wrapr: for sweet R code
=======================

This article is on writing sweet [`R`](https://cran.r-project.org) code
using the [`wrapr`](https://CRAN.R-project.org/package=wrapr) package.

![](wraprs.png)

The problem
-----------

Consider the following R puzzle. You are given: a data.frame, the name
of a column that you wish to find missing values (NA) in, and the name
of a column to land the result. For instance:

``` r
d <- data.frame(x = c(1, NA))
print(d)
```

    ##    x
    ## 1  1
    ## 2 NA

``` r
cname <- 'x'
print(cname)
```

    ## [1] "x"

``` r
rname <- paste(cname, 'isNA', sep = '_')
print(rname)
```

    ## [1] "x_isNA"

How do you write generic code to populate the column x\_isNA with which
rows of x are missing?

The “base R” solution
---------------------

In “base R” (R without additional packages) this is easy.

When you know the column names while writing the code:

``` r
d2 <- d
d2$x_isNA <- is.na(d2$x)

print(d2)
```

    ##    x x_isNA
    ## 1  1  FALSE
    ## 2 NA   TRUE

And when you don’t know the column names while writing the code (but
know they will arrive in variables later):

``` r
d2 <- d
d2[[rname]] <- is.na(d2[[cname]])
```

The “base R” solution really is quite elegant.

The “all in” non-standard evaluation dplyr::mutate solution (pre-rlang)
-----------------------------------------------------------------------

As far as I can tell the “all in” non-standard evaluation dplyr::mutate
solution is something like the following.

When you know the column names while writing the code:

``` r
library("dplyr")
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
d %>% mutate(x_isNA = is.na(x))
```

    ##    x x_isNA
    ## 1  1  FALSE
    ## 2 NA   TRUE

And when you don’t know the column names while writing the code (but
know they will arrive in variables later):

``` r
d %>%
  mutate_(.dots =
            stats::setNames(list(lazyeval::interp(
              ~ is.na(VAR),
              VAR = as.name(cname)
            )),
            rname))
```

    ## Warning: mutate_() is deprecated. 
    ## Please use mutate() instead
    ## 
    ## The 'programming' vignette or the tidyeval book can help you
    ## to program with mutate() : https://tidyeval.tidyverse.org
    ## This warning is displayed once per session.

    ##    x x_isNA
    ## 1  1  FALSE
    ## 2 NA   TRUE

The “all in” non-standard evaluation dplyr::mutate solution (rlang)
-------------------------------------------------------------------

rlang obsoleted the above and now suggests code such as the following:

``` r
d %>%
  mutate(!!rlang::sym(rname) := is.na(!!rlang::sym(cname)))
```

    ##    x x_isNA
    ## 1  1  FALSE
    ## 2 NA   TRUE

Note “the obvious” rlang solution does not work:

``` r
d %>%
  mutate(!!rname := is.na(!!cname))
```

    ##    x x_isNA
    ## 1  1  FALSE
    ## 2 NA  FALSE

(though the above sort of notation is allowed “in select contexts”.)

The sweet wrapr::let dplyr::mutate solution
===========================================

We will only work the harder “when you don’t yet know the column name”
(or parametric) version:

``` r
library("wrapr")
```

    ## 
    ## Attaching package: 'wrapr'

    ## The following object is masked from 'package:dplyr':
    ## 
    ##     coalesce

``` r
let(list(CNAME = cname, RNAME = rname),
    d %>% mutate(RNAME = is.na(CNAME))
)
```

    ##    x x_isNA
    ## 1  1  FALSE
    ## 2 NA   TRUE

I think that this is pretty
[sweet](https://www.youtube.com/embed/nG9fXbhoPJE), and can really level
up your dplyr game.

`wrapr::let` is available from CRAN and already has a number of
satisfied users:

![](C1v_VNBXUAA8c7M.jpg-large.jpg)

If function behavior depends on variable names, then convenient control
of functions is eventually going to require convenient control of
variable names; so needing to re-map variable names at some point is
inevitable.
