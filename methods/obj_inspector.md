Suggested packages
================

Find suggested packages (without package order) for `R` objects.

First: define the suggestion function.

``` r
source("find_pkgs.R")
```

Example 1: an `xts` object.

``` r
library("tidyverse") # extra packages to show interference effects
```

    ## Registered S3 methods overwritten by 'ggplot2':
    ##   method         from 
    ##   [.quosures     rlang
    ##   c.quosures     rlang
    ##   print.quosures rlang

    ## ── Attaching packages ─────────────────────────────────────────────────────────────────────────────── tidyverse 1.2.1 ──

    ## ✔ ggplot2 3.1.1     ✔ purrr   0.3.2
    ## ✔ tibble  2.1.1     ✔ dplyr   0.8.1
    ## ✔ tidyr   0.8.3     ✔ stringr 1.4.0
    ## ✔ readr   1.3.1     ✔ forcats 0.4.0

    ## ── Conflicts ────────────────────────────────────────────────────────────────────────────────── tidyverse_conflicts() ──
    ## ✖ dplyr::filter() masks stats::filter()
    ## ✖ dplyr::lag()    masks stats::lag()

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

    ## 
    ## Attaching package: 'xts'

    ## The following objects are masked from 'package:dplyr':
    ## 
    ##     first, last

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

    ## The following objects are masked from 'package:dplyr':
    ## 
    ##     between, first, last

    ## The following object is masked from 'package:purrr':
    ## 
    ##     transpose

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

    ## [1] "dplyr"   "ggplot2" "tibble"  "tidyr"

``` r
suggested_packages(d, show_details = c("dplyr", "ggplot2", "tidyr"))
```

    ## [1] "dplyr"   "ggplot2" "tibble"  "tidyr"  
    ## attr(,"explain")
    ##     class           methods   generics package
    ## 1  tbl_df  all.equal.tbl_df  all.equal   dplyr
    ## 2  tbl_df  anti_join.tbl_df  anti_join   dplyr
    ## 3  tbl_df   arrange_.tbl_df   arrange_   dplyr
    ## 4  tbl_df    arrange.tbl_df    arrange   dplyr
    ## 5  tbl_df  auto_copy.tbl_df  auto_copy   dplyr
    ## 6  tbl_df  distinct_.tbl_df  distinct_   dplyr
    ## 7  tbl_df   distinct.tbl_df   distinct   dplyr
    ## 8  tbl_df    filter_.tbl_df    filter_   dplyr
    ## 9  tbl_df     filter.tbl_df     filter   dplyr
    ## 10 tbl_df    fortify.tbl_df    fortify ggplot2
    ## 11 tbl_df  full_join.tbl_df  full_join   dplyr
    ## 12 tbl_df inner_join.tbl_df inner_join   dplyr
    ## 13 tbl_df  left_join.tbl_df  left_join   dplyr
    ## 14 tbl_df    mutate_.tbl_df    mutate_   dplyr
    ## 15 tbl_df     mutate.tbl_df     mutate   dplyr
    ## 16 tbl_df  nest_join.tbl_df  nest_join   dplyr
    ## 17 tbl_df       nest.tbl_df       nest   tidyr
    ## 18 tbl_df right_join.tbl_df right_join   dplyr
    ## 19 tbl_df  semi_join.tbl_df  semi_join   dplyr
    ## 20 tbl_df     slice_.tbl_df     slice_   dplyr
    ## 21 tbl_df      slice.tbl_df      slice   dplyr
    ## 22 tbl_df summarise_.tbl_df summarise_   dplyr
    ## 23 tbl_df  summarise.tbl_df  summarise   dplyr
    ## 24    tbl        as.tbl.tbl     as.tbl   dplyr
    ## 25    tbl       fortify.tbl    fortify ggplot2

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

Example 5: nested stuff.

``` r
df2 <- data.frame(x = 1)
df2$y <- list(tibble(x = 5))

class(df2)
```

    ## [1] "data.frame"

``` r
suggested_packages(df2)
```

    ## [1] "dplyr"   "ggplot2" "tibble"  "tidyr"

The idea is: `saveRDS()` could be augmented to add the
`suggested_packages()` as an attribute of what it writes out, say
".suggested\_packages`. Then`readRDS()\` could look for this attribute
and issue a warning if any of them are not attached during the read.

The problem we are working around is `R` objects that don’t work
correctly if their package is not attached (common to `xts`, `tibble`,
and `data.table`).
