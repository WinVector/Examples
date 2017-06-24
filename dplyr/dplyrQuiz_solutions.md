Advanced dplyr Quiz (author: John Mount)
========================================

Being able to effectively perform meaningful work *using* [`R`](https://www.r-project.org) programming involves being able to both know how various packages work and anticipate package method outcomes in basic situations. Any mismatch there (be it a knowledge gap in the programmer, an implementation gap in a package, or a difference between programmer opinion and package doctrine) can lead to confusion, bugs and incorrect results.

Below is our advanced [`dplyr`](https://CRAN.R-project.org/package=dplyr) quiz. Can you anticipate the result of each of the example operations? Can you anticipate which commands are in error and which are valid `dplyr`?

Or another phrasing: here are our notes on `dplyr` corner-cases (in my *opinion*). You may not need to know how any of these work (it is often good to avoid corner-cases), but you should at least be confident you are avoiding the malformed ones.

Start
=====

With the current version of `dplyr` in mind, please anticipate the result of each example command. Note: we don't claim all of the examples below are correct `dplyr` code. However, effective programming requires knowledge of what happens in some incorrect cases (at least knowing which throw usable errors, and which perform quiet mal-calculations).

``` r
# Show versions we are using.
# devtools::install_github('tidyverse/dplyr')
# devtools::install_github('tidyverse/dbplyr')
# devtools::install_github('rstats-db/RSQLite')
# devtools::install_github('tidyverse/rlang')
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
packageVersion("rlang")
```

    ## [1] '0.1.1.9000'

``` r
packageVersion("magrittr")
```

    ## [1] '1.5'

``` r
base::date()
```

    ## [1] "Sat Jun 24 11:05:08 2017"

Now for the examples/quiz.

Please take a moment and write down your answers before moving on to the [solutions](https://github.com/WinVector/Examples/blob/master/dplyr/dplyrQuiz_solutions.md). This should give you a much more open mind as to what constitutes "[surprising behavior](https://en.wikipedia.org/wiki/Principle_of_least_astonishment)."

You can also run the quiz yourself by downloading and knitting the [source document](https://github.com/WinVector/Examples/blob/master/dplyr/dplyrQuiz.Rmd).

Please keep in mind while "you never want errors" you do sometimes want exceptions (which are unfortunately called "`Error:`" in `R`). Exceptions are an important way of stopping off-track computation and preventing later incorrect results. Exceptions can often be the desired outcome of a malformed calculation.

Local data.frames
=================

Column selection
----------------

``` r
data.frame(x = 1) %>% select(x)
```

    ##   x
    ## 1 1

``` r
data.frame(x = 1) %>% select('x')
```

    ##   x
    ## 1 1

``` r
y <- 'x' # value used in later examples

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
# values used in later examples
db <- DBI::dbConnect(RSQLite::SQLite(), 
                     ":memory:")
dL <- data.frame(x = 3.077, 
                k = 'a', 
                stringsAsFactors = FALSE)
dR <- dplyr::copy_to(db, dL, 'dR')
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

(From [dplyr 2890](https://github.com/tidyverse/dplyr/issues/2890) and [dplyr 2908](https://github.com/tidyverse/dplyr/issues/2908).)

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

Conclusion
==========

The above quiz is really my working notes on corner-cases to avoid. Not all of these are worth fixing. In many cases you can and should re-arrange your `dplyr` pipelines to avoid triggering the above cases. But to do that, you have to know what to avoid (hence the notes).

Also: please understand, some of these may *not* represent problems with the above packages. They may instead represent mistakes and misunderstandings on my part. Or opinions of mine that may differ from the considered opinions and experience of the people who have authored and who have to maintain these packages. Some things that might seem "easy to fix" to an outsider may already be set at a "best possible compromise" among many other considerations.

I may or may not keep these up to date depending on the utility of such a list going forward.
