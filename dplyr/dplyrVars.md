dplyr variable issues
================
John Mount
10/22/2017

``` r
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.7.4'

``` r
packageVersion("dbplyr")
```

    ## [1] '1.1.0.9000'

Trying `dplyr` on "local" or in-memory `data.frame` or `tbl`.

``` r
# value we are interested in a variable, for code neatness
genderTarget = 'male'

starwars %>%
  summarize(fracMatch = mean(ifelse(gender == genderTarget, 1, 0),
                            na.rm = TRUE))
```

    ## # A tibble: 1 x 1
    ##   fracMatch
    ##       <dbl>
    ## 1 0.7380952

``` r
# matches simple calculation 0.7380952
mean(starwars$gender==genderTarget, na.rm = TRUE)
```

    ## [1] 0.7380952

Same calculation fails for database backed data sources (not a `SQLite` issue, also fails for `Sparklyr`).

``` r
my_db <- dplyr::src_sqlite(":memory:", create = TRUE)
# or can connect with:
# my_db <- DBI::dbConnect(RSQLite::SQLite(), ":memory:")
# RSQLite::initExtension(my_db) # needed for many summary fns.
starwars_db <- copy_to(my_db,
                       select(starwars, -vehicles, -starships, -films),
                       'starwars_db')

# works
starwars_db %>% transmute(genderTarget = genderTarget)
```

    ## # Source:   lazy query [?? x 1]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##    genderTarget
    ##           <chr>
    ##  1         male
    ##  2         male
    ##  3         male
    ##  4         male
    ##  5         male
    ##  6         male
    ##  7         male
    ##  8         male
    ##  9         male
    ## 10         male
    ## # ... with more rows

``` r
# fails
starwars_db %>%
  summarize(fracMatch = mean(ifelse(gender == genderTarget, 1, 0),
                            na.rm = TRUE))
```

    ## na.rm not needed in SQL: NULL are always droppedFALSE

    ## Error in rsqlite_send_query(conn@ptr, statement): no such column: genderTarget

``` r
# fails
starwars_db %>%
  summarize(fracMatch = mean(if_else(gender == genderTarget, 1, 0),
                            na.rm = TRUE))
```

    ## na.rm not needed in SQL: NULL are always droppedFALSE

    ## Error in rsqlite_send_query(conn@ptr, statement): no such column: genderTarget

``` r
# attempted fix: use "!!" to force bind target to environment
# but notice result 0.7126437 does not match in memory result 0.7380952
starwars_db %>%
  summarize(fracMatch = mean(ifelse(gender == !!genderTarget, 1, 0),
                            na.rm = TRUE))
```

    ## na.rm not needed in SQL: NULL are always droppedFALSE

    ## # Source:   lazy query [?? x 1]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##   fracMatch
    ##       <dbl>
    ## 1 0.7126437

By hand work-around.

``` r
# work around
starwars_db %>%
  summarize(fracMatch = sum(ifelse(gender == !!genderTarget, 1, 0))/
              sum(!is.na(gender)))
```

    ## # Source:   lazy query [?? x 1]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##   fracMatch
    ##       <dbl>
    ## 1 0.7380952

``` r
# Example related to dplyr issues:
#    3139: https://github.com/tidyverse/dplyr/issues/3139
#    3148: https://github.com/tidyverse/dplyr/issues/3148
#    (and possibly) 3143: https://github.com/tidyverse/dplyr/issues/3143
#    3138: https://github.com/tidyverse/dplyr/issues/3138
# Some of the above are closed, but still relate to the
# behavior of dplyr, or what is needed to anticipate the
# behavior of dplyr.
#
```
