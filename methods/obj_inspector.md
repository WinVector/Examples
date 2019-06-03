Suggested packages
================

Find suggested packages (without package order) for `R` objects.

First: define the suggestion function.

``` r
source("find_pkgs.R")
```

Example 1: an `xts` object.

``` r
library("tibble")
library("xts")
```

    ## Loading required package: zoo

    ## 
    ## Attaching package: 'zoo'

    ## The following objects are masked from 'package:base':
    ## 
    ##     as.Date, as.Date.numeric

    ## Registered S3 method overwritten by 'xts':
    ##   method     from
    ##   as.zoo.xts zoo

``` r
data(sample_matrix)
sample.xts <- as.xts(sample_matrix, descr='my new xts object')

suggested_packages(sample.xts)
```

    ## [1] "xts" "zoo"

However, notice if `data.table` is attached the advice changes.

``` r
library("data.table")
```

    ## 
    ## Attaching package: 'data.table'

    ## The following objects are masked from 'package:xts':
    ## 
    ##     first, last

``` r
suggested_packages(sample.xts)
```

    ## [1] "data.table" "xts"        "zoo"

We can ask for more details to see why this is.

``` r
suggested_packages(sample.xts, show_details = "data.table")
```

    ## [1] "data.table" "xts"        "zoo"       
    ## attr(,"explain")
    ##   class           methods      generics    package
    ## 1   xts as.data.table.xts as.data.table data.table

Example 2: a `tibble`.

``` r
d <- as_tibble(data.frame(x = 1))

suggested_packages(d)
```

    ## [1] "tibble"

Example 3: a `data.table`.

``` r
dt <- data.table(x = 2)

suggested_packages(dt)
```

    ## [1] "data.table"

Example 4: `data.frame`

``` r
df <- data.frame(x = 4)

suggested_packages(df)
```

    ## NULL

Example 5: nested crap.

``` r
df2 <- data.frame(x = 1)
df2$y <- list(tibble(x = 5))

class(df2)
```

    ## [1] "data.frame"

``` r
suggested_packages(df2)
```

    ## [1] "tibble"

The idea is: `saveRDS()` could be augmented to add the
`suggested_packages()` as an attribute of what it writes out, say
".suggested\_packages`. Then`readRDS()\` could look for this attribute
and issue a warning if any of them are not attached during the read.

The problem we are working around is `R` objects that don’t work
correctly if their package is not attached (common to `xts`, `tibble`,
and `data.table`).
