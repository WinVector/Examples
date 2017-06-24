Advanced dplyr Quiz
===================

Being able to effectively do work through programming involves being able to both know how various packages work and anticipate package method outcomes in basic situations. Any mis-match here (be it a knowledge gap in the programmer, or an implementation gap in the package) can lead to bugs and confusion.

Below is our advanced `dplyr` quiz: can you anticipate the result of each of the example operations?

Start
=====

With the following version of `dplyr` please figure out the result of each example command. Note: we don't claim all of the below is correct `dplyr` code, however programming requires knowledge of what happens in incorrect cases (for examples which throw usable errors, and which perform subtle mal-calculations).

First let's start up the latest version of all the packages we are using.

``` r
# devtools::install_github('tidyverse/dplyr')
# devtools::install_github('tidyverse/dbplyr')
# devtools::install_github('rstats-db/RSQLite')
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.7.1.9000'

``` r
packageVersion("dbplyr")
```

    ## [1] '1.0.0.9000'

``` r
packageVersion("RSQlite")
```

    ## [1] '2.0'

``` r
packageVersion("magrittr")
```

    ## [1] '1.5'

``` r
base::date()
```

    ## [1] "Sat Jun 24 09:44:40 2017"

``` r
DORUN <- TRUE
```

Now the examples/quiz. Please take a moment and write down your answer before moving on to the solutions.

Local data.frames
=================

Column selection
----------------

``` r
data.frame(x = 1) %>% select('x')
```

    ##   x
    ## 1 1

``` r
y <- 'x'

data.frame(x = 1) %>% select(y)
```

    ##   x
    ## 1 1

``` r
data.frame(x = 1, y = 2) %>% select(y)
```

    ##   y
    ## 1 2

(From [dplyr 2904](https://github.com/tidyverse/dplyr/issues/2904).)

Piping into different targets (functions, blocks expressions):
--------------------------------------------------------------

`magrittr` pipe details:

``` r
data.frame(x = 1)  %>%  { bind_rows(list(., .)) }
```

    ##   x
    ## 1 1
    ## 2 1

``` r
data.frame(x = 1)  %>%    bind_rows(list(., .))
```

    ##   x
    ## 1 1
    ## 2 1
    ## 3 1

``` r
data.frame(x = 1)  %>%  ( bind_rows(list(., .)) )
```

    ## Error in eval_bare(dot$expr, dot$env): object '.' not found

Same with [Bizarro Pipe](https://cran.r-project.org/web/packages/replyr/vignettes/BizarroPipe.html):

``` r
data.frame(x = 1)  ->.;  { bind_rows(list(., .)) }
```

    ##   x
    ## 1 1
    ## 2 1

``` r
data.frame(x = 1)  ->.;    bind_rows(list(., .))
```

    ##   x
    ## 1 1
    ## 2 1

``` r
data.frame(x = 1)  ->.;  ( bind_rows(list(., .)) )
```

    ##   x
    ## 1 1
    ## 2 1

enquo rules
-----------

``` r
(function(x) select(data.frame(x = 1), !!enquo(x)))(x)
```

    ##   x
    ## 1 1

``` r
(function(x) data.frame(x = 1) %>% select(!!enquo(x)))(x)
```

    ## Error: `function (expr) 
    ## {
    ##     enexpr(expr)
    ## }` must resolve to integer column positions, not a function

(From [dplyr 2726](https://github.com/tidyverse/dplyr/issues/2726).)

Databases
=========

Setup:

``` r
db <- DBI::dbConnect(RSQLite::SQLite(), 
                     ":memory:")
dR <- dplyr::copy_to(db,
                     data.frame(x = 3.077, 
                                k = 'a', 
                                stringsAsFactors = FALSE), 
                     'dR')
```

nrow()
------

``` r
nrow(dR)
```

    ## [1] NA

(From [dplyr 2871](https://github.com/tidyverse/dplyr/issues/2871).)

union\_all()
------------

``` r
union_all(dR, dR)
```

    ## # Source:   lazy query [?? x 2]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##       x     k
    ##   <dbl> <chr>
    ## 1 3.077     a
    ## 2 3.077     a

``` r
union_all(dR, head(dR))
```

    ## Error: SQLite does not support set operations on LIMITs

(From [dplyr 2858](https://github.com/tidyverse/dplyr/issues/2858).)

mutate\_all funs()
------------------

``` r
dR %>% mutate_all(funs(round(., 2)))
```

    ## # Source:   lazy query [?? x 2]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##       x     k
    ##   <dbl> <dbl>
    ## 1  3.08     0

``` r
dR %>% mutate_all(funs(round(., digits = 2)))
```

    ## Warning: Named arguments ignored for SQL ROUND

    ## Warning: Named arguments ignored for SQL ROUND

    ## Error in rsqlite_send_query(conn@ptr, statement): near "AS": syntax error

(From [dplyr 2890](https://github.com/tidyverse/dplyr/issues/2890).)

rename
------

``` r
dR %>% rename(x2 = x) %>% rename(k2 = k)
```

    ## # Source:   lazy query [?? x 2]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##      x2    k2
    ##   <dbl> <chr>
    ## 1 3.077     a

``` r
dR %>% rename(x2 = x, k2 = k)
```

    ## Error in names(select)[match(old_vars, vars)] <- new_vars: NAs are not allowed in subscripted assignments

(From [dplyr 2860](https://github.com/tidyverse/dplyr/issues/2860).)
