For [`R`](https://cran.r-project.org) [`dplyr`](https://CRAN.R-project.org/package=dplyr) users one of the promises of the new [`rlang`/`tidyeval`](https://CRAN.R-project.org/package=rlang) system is an improved ability to [program over `dplyr`](http://dplyr.tidyverse.org/articles/programming.html) itself. In particular to add new verbs that encapsulate previously compound steps into better self-documenting atomic steps.

Let's take a look at this capability.

First let's start `dplyr`.

``` r
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.7.1.9000'

A `dplyr` pattern that I have seen use often is the "`group_by() %>% mutate()`" pattern. This historically has been shorthand for a "`group_by() %>% summarize()`" followed by a `join()`. It is easiest to show by example.

The following code:

``` r
mtcars %>% 
  group_by(cyl, gear) %>%
  mutate(group_mean_mpg = mean(mpg), 
            group_mean_disp = mean(disp)) %>% 
  select(cyl, gear, mpg, disp, 
         group_mean_mpg, group_mean_disp) %>%
  head()
```

    ## # A tibble: 6 x 6
    ## # Groups:   cyl, gear [4]
    ##     cyl  gear   mpg  disp group_mean_mpg group_mean_disp
    ##   <dbl> <dbl> <dbl> <dbl>          <dbl>           <dbl>
    ## 1     6     4  21.0   160         19.750        163.8000
    ## 2     6     4  21.0   160         19.750        163.8000
    ## 3     4     4  22.8   108         26.925        102.6250
    ## 4     6     3  21.4   258         19.750        241.5000
    ## 5     8     3  18.7   360         15.050        357.6167
    ## 6     6     3  18.1   225         19.750        241.5000

is taken to be shorthand for:

``` r
mtcars %>% 
  group_by(cyl, gear) %>%
  summarize(group_mean_mpg = mean(mpg), 
            group_mean_disp = mean(disp)) %>% 
  left_join(mtcars, ., by = c('cyl', 'gear')) %>%
  select(cyl, gear, mpg, disp, 
         group_mean_mpg, group_mean_disp) %>%
  head()
```

    ##   cyl gear  mpg disp group_mean_mpg group_mean_disp
    ## 1   6    4 21.0  160         19.750        163.8000
    ## 2   6    4 21.0  160         19.750        163.8000
    ## 3   4    4 22.8  108         26.925        102.6250
    ## 4   6    3 21.4  258         19.750        241.5000
    ## 5   8    3 18.7  360         15.050        357.6167
    ## 6   6    3 18.1  225         19.750        241.5000

The advantages of the shorthand are:

-   The analyst only has to specify the grouping column once.
-   The data (`mtcars`) enters the pipeline only once.
-   The analyst doesn't have to start thinking about joins immediately.

Frankly I've never liked the shorthand. I feel it is a "magic extra" that a new user would have no way of anticipating from common use of `group_by()` and `summarize()`. I very much like the idea of wrapping this important common use case into a single verb. Adjoining "windowed" or group-calculated columns is a common and important step in analysis, and well worth having its own verb.

Below is our attempt at elevating this pattern into a packaged verb.

``` r
#' Simulate the group_by/mutate pattern with an explicit summarize and join.
#' 
#' Group a data frame by the groupingVars and compute user summaries on 
#' this data frame (user summaries specified in ...), then join these new
#' columns back into the original data and return to the user.
#' This works around https://github.com/tidyverse/dplyr/issues/2960 .
#' And it is a demonstration of a higher-order dplyr verb.
#' Author: John Mount, Win-Vector LLC.
#' 
#' @param d data.frame
#' @param groupingVars character vector of column names to group by.
#' @param ... list of dplyr::mutate() expressions.
#' @value d with grouped summaries added as extra columns
#' 
#' @examples
#' 
#' add_group_summaries(mtcars, 
#'                     c("cyl", "gear"), 
#'                     group_mean_mpg = mean(mpg), 
#'                     group_mean_disp = mean(disp)) %>%
#'   head()
#' 
#' @export
#' 
add_group_summaries <- function(d, groupingVars, ...) {
  # convert char vector into quosure vector
  # These interfaces are still changing, so take care.
  groupingQuos <- lapply(groupingVars, 
                         function(si) { quo(!!as.name(si)) })
  dg <- ungroup(d) # just in case
  dg <- group_by(dg, !!!groupingQuos)
  ds <- summarize(dg, ...)
  # work around https://github.com/tidyverse/dplyr/issues/2963
  ds <- ungroup(ds)
  left_join(d, ds, by= groupingVars)
}
```

This works as follows:

``` r
mtcars %>% 
  add_group_summaries(c("cyl", "gear"), 
                      group_mean_mpg = mean(mpg), 
                      group_mean_disp = mean(disp)) %>%
  select(cyl, gear, mpg, disp, 
         group_mean_mpg, group_mean_disp) %>%
  head()
```

    ##   cyl gear  mpg disp group_mean_mpg group_mean_disp
    ## 1   6    4 21.0  160         19.750        163.8000
    ## 2   6    4 21.0  160         19.750        163.8000
    ## 3   4    4 22.8  108         26.925        102.6250
    ## 4   6    3 21.4  258         19.750        241.5000
    ## 5   8    3 18.7  360         15.050        357.6167
    ## 6   6    3 18.1  225         19.750        241.5000

And this also works on database-backed `dplyr` data (which the shorthand currently does not, please see [`dplyr` 2887 issue](https://github.com/tidyverse/dplyr/issues/2887) and [`dplyr` issue 2960](https://github.com/tidyverse/dplyr/issues/2960)).

``` r
con <- DBI::dbConnect(RSQLite::SQLite(), ":memory:")
copy_to(con, mtcars)
mtcars2 <- tbl(con, "mtcars")

mtcars2 %>% 
  group_by(cyl, gear) %>%
  mutate(group_mean_mpg = mean(mpg), 
         group_mean_disp = mean(disp))
```

    ## Error: Window function `avg()` is not supported by this database

``` r
mtcars2 %>% 
  add_group_summaries(c("cyl", "gear"), 
                      group_mean_mpg = mean(mpg), 
                      group_mean_disp = mean(disp)) %>%
  select(cyl, gear, mpg, disp, 
         group_mean_mpg, group_mean_disp) %>%
  head()
```

    ## # Source:   lazy query [?? x 6]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##     cyl  gear   mpg  disp group_mean_mpg group_mean_disp
    ##   <dbl> <dbl> <dbl> <dbl>          <dbl>           <dbl>
    ## 1     6     4  21.0   160         19.750        163.8000
    ## 2     6     4  21.0   160         19.750        163.8000
    ## 3     4     4  22.8   108         26.925        102.6250
    ## 4     6     3  21.4   258         19.750        241.5000
    ## 5     8     3  18.7   360         15.050        357.6167
    ## 6     6     3  18.1   225         19.750        241.5000

Another great verb in this style is `group_summarize`:

``` r
#' group_by and summarize as an atomic action.
#' 
#' Group a data frame by the groupingVars and compute user summaries on 
#' this data frame (user summaries specified in ...).  Enforces the 
#' good dplyr pipeline design principle of keeping group_by and
#' summarize close together.
#' Author: John Mount, Win-Vector LLC.
#' 
#' @param d data.frame
#' @param groupingVars character vector of column names to group by.
#' @param ... list of dplyr::mutate() expressions.
#' @value d summarized by groups
#' 
#' @examples
#' 
#' group_summarize(mtcars, 
#'                     c("cyl", "gear"), 
#'                     group_mean_mpg = mean(mpg), 
#'                     group_mean_disp = mean(disp)) %>%
#'   head()
#' 
#' @export
#' 
group_summarize <- function(d, groupingVars, ...) {
  # convert char vector into quosure vector
  # These interfaces are still changing, so take care.
  groupingQuos <- lapply(groupingVars, 
                         function(si) { quo(!!as.name(si)) })
  dg <- ungroup(d) # just in case
  dg <- group_by(dg, !!!groupingQuos)
  ds <- summarize(dg, ...)
  # work around https://github.com/tidyverse/dplyr/issues/2963
  ungroup(ds)
}
```

``` r
mtcars2 %>% 
  group_summarize(c("cyl", "gear"), 
                  group_mean_mpg = mean(mpg), 
                  group_mean_disp = mean(disp)) %>%
  select(cyl, gear,
         group_mean_mpg, group_mean_disp)
```

    ## # Source:   lazy query [?? x 4]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##     cyl  gear group_mean_mpg group_mean_disp
    ##   <dbl> <dbl>          <dbl>           <dbl>
    ## 1     4     3         21.500        120.1000
    ## 2     4     4         26.925        102.6250
    ## 3     4     5         28.200        107.7000
    ## 4     6     3         19.750        241.5000
    ## 5     6     4         19.750        163.8000
    ## 6     6     5         19.700        145.0000
    ## 7     8     3         15.050        357.6167
    ## 8     8     5         15.400        326.0000
