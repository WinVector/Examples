Advanced dplyr Quiz (author: John Mount)
========================================

Being able to effectively perform meaningful work *using* [`R`](https://www.r-project.org) programming involves being able to both know how various packages work and anticipate package method outcomes in basic situations. Any mismatch there (be it a knowledge gap in the programmer, an implementation gap in a package, or a difference between programmer opinion and package doctrine) can lead to confusion, bugs and incorrect results.

Below is our advanced [`dplyr`](https://CRAN.R-project.org/package=dplyr) quiz. Can you anticipate the result of each of the example operations? Can you anticipate which commands are in error and which are valid `dplyr`?

Or another phrasing: here are our notes on `dplyr` corner-cases (in my *opinion*). You may not need to know how any of these work (it is often good to avoid corner-cases), but you should at least be confident you are avoiding the malformed ones.

<img src="Samuel_Johnson_by_Joshua_Reynolds_2.png" width="400">

"Please read on for the answers!"

Start
=====

With the current version of `dplyr` in mind, please anticipate the result of each example command. Note: we don't claim all of the examples below are correct `dplyr` code. However, effective programming requires knowledge of what happens in some incorrect cases (at least knowing which throw usable errors, and which perform quiet mal-calculations).

``` r
# Show versions we are using.
# optional
# devtools::install_github('tidyverse/dplyr')
# devtools::install_github('tidyverse/dbplyr')
# devtools::install_github('rstats-db/RSQLite')
# devtools::install_github('tidyverse/rlang')
packageVersion("dplyr")
```

    ## [1] '0.7.2'

``` r
packageVersion("dbplyr")
```

    ## [1] '1.1.0.9000'

``` r
packageVersion("RSQlite")
```

    ## [1] '2.0'

``` r
packageVersion("rlang")
```

    ## [1] '0.1.2'

``` r
packageVersion("magrittr")
```

    ## [1] '1.5'

``` r
base::date()
```

    ## [1] "Tue Aug 15 06:56:21 2017"

``` r
suppressPackageStartupMessages(library("dplyr"))
```

Now for the examples/quiz.

Please take a moment to [try the quiz](https://github.com/WinVector/Examples/blob/master/dplyr/dplyrQuiz.md), and write down your answers before moving on to the [solutions](https://github.com/WinVector/Examples/blob/master/dplyr/dplyrQuiz_solutions.md). This should give you a much more open mind as to what constitutes "[surprising behavior](https://en.wikipedia.org/wiki/Principle_of_least_astonishment)."

You can also run the quiz yourself by downloading and knitting the [source document](https://github.com/WinVector/Examples/blob/master/dplyr/dplyrQuiz.Rmd).

Please keep in mind while "you never want errors" you do sometimes want exceptions (which are unfortunately called "`Error:`" in `R`). Exceptions are an important way of stopping off-track computation and preventing later incorrect results. Exceptions can often be the desired outcome of a malformed calculation.

Not all of the questions are "trick", some of them are just convenient ways to remember different `dplyr` conventions.

Local data.frames
=================

Column selection
----------------

``` r
data.frame(x = 1) %>% 
  select(x)
```

    ##   x
    ## 1 1

``` r
# Two questions: 
#  1) Should this next one work?
#  2) Does this next one work?
data.frame(x = 1) %>% 
  select('x')
```

    ##   x
    ## 1 1

``` r
y <- 'x' # value used in later examples

# Hint: this is new for dplyr 0.7.* 
# (dplyr 0.5.0 only did this for integers).
# This is going to be a massive source
# of unexpected results, bugs, and
# incorrect analyses.
data.frame(x = 1) %>% 
  select(y)
```

    ##   x
    ## 1 1

``` r
data.frame(x = 1, y = 2) %>% 
  select(y)
```

    ##   y
    ## 1 2

``` r
rm(list='y') # clean up
```

(From [`dplyr` issue 2904](https://github.com/tidyverse/dplyr/issues/2904).)

rename
------

``` r
data.frame(x = 1) %>%
  rename(!!rlang::sym('y') := x)
```

    ##   y
    ## 1 1

``` r
data.frame(x = 1) %>%
  rename((!!rlang::sym('y')) := x)
```

    ## Error: LHS must be a name or string

distinct
--------

``` r
data.frame(x = c(1, 1)) %>% 
  select(one_of(character(0))) %>%
  distinct() %>%
  nrow()
```

    ## [1] 2

(From [`dplyr` issue 2954](https://github.com/tidyverse/dplyr/issues/2954).)

rename and mutate
-----------------

``` r
data.frame(x=1, y=2) %>% rename(x=y, y=x)
```

    ##   y x
    ## 1 1 2

``` r
data.frame(x=1, y=2) %>% mutate(x=y, y=x)
```

    ##   x y
    ## 1 2 2

NULL (constant versus in a variable)
------------------------------------

``` r
data.frame(x=1, y=2) %>% mutate(x = NULL)
```

    ##   y
    ## 1 2

``` r
z <- NULL # value used in later examples
data.frame(x=1, y=2) %>% mutate(x = z)
```

    ## Error in mutate_impl(.data, dots): Column `x` is of unsupported type NULL

``` r
data.frame(x=1, y=2) %>% mutate(x = !!z)
```

    ##   y
    ## 1 2

``` r
rm(list='z') # clean up
```

(From [`dplyr` issue 2945](https://github.com/tidyverse/dplyr/issues/2945).)

Column grouping
---------------

``` r
y <- 'x' # value used in later examples

data.frame(x = 1) %>% 
  group_by(.data[[y]]) %>% 
  summarize(count = n()) %>% 
  colnames()
```

    ## [1] "y"     "count"

``` r
rm(list='y') # clean up
```

``` r
world <- "homeworld"

starwars %>%
  group_by(.data[[world]]) %>%
  summarise_at(vars(height:mass), mean, na.rm = TRUE) %>%
  head()
```

    ## # A tibble: 6 x 3
    ##            world   height  mass
    ##            <chr>    <dbl> <dbl>
    ## 1       Alderaan 176.3333    64
    ## 2    Aleen Minor  79.0000    15
    ## 3         Bespin 175.0000    79
    ## 4     Bestine IV 180.0000   110
    ## 5 Cato Neimoidia 191.0000    90
    ## 6          Cerea 198.0000    82

``` r
homeworld <- "homeworld"

starwars %>%
  group_by(.data[[homeworld]]) %>%
  summarise_at(vars(height:mass), mean, na.rm = TRUE) %>%
  head()
```

    ## Error in mutate_impl(.data, dots): Evaluation error: Must subset with a string.

(From [`dplyr` issue 2916](https://github.com/tidyverse/dplyr/issues/2916) and [`dplyr` issue 2991](https://github.com/tidyverse/dplyr/issues/2991), notation taken from [here](https://blog.rstudio.org/2017/06/13/dplyr-0-7-0/)).

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

summary
-------

``` r
data.frame(x = c(1, 2), y = c(3, 3)) %>% 
  group_by(x) %>% 
  summarize(y)
```

    ## # A tibble: 2 x 2
    ##       x     y
    ##   <dbl> <dbl>
    ## 1     1     3
    ## 2     2    NA

(From [`dplyr` issue 2915](https://github.com/tidyverse/dplyr/issues/2915).)

enquo rules
-----------

This section is about `enquo()`, or passing unquoted variable names to functions that use `dplyr` methods. Please skip it if you don't write such code, or if you use something like [`wrapr::let()`](https://github.com/WinVector/wrapr/blob/master/README.md) for such replacements.

``` r
(function(z) select(data.frame(x = 1), !!enquo(z)))(x)
```

    ##   x
    ## 1 1

``` r
(function(z) data.frame(x = 1) %>% select(!!enquo(z)))(x)
```

    ## Error: `function (expr) 
    ## {
    ##     enexpr(expr)
    ## }` must resolve to integer column positions, not a function

(From [`dplyr` issue 2726](https://github.com/tidyverse/dplyr/issues/2726).)

``` r
y <- NULL # value used in later examples

(function(z) mutate(data.frame(x = 1), !!quo_name(enquo(z)) := 2))(y)
```

    ##   x y
    ## 1 1 2

``` r
(function() mutate(data.frame(x = 1), !!quo_name(enquo(y)) := 2))()
```

    ##   x function (expr) ...
    ## 1 1                   2

``` r
(function(z) select(data.frame(y = 1), !!enquo(z)))(y)
```

    ##   y
    ## 1 1

``` r
(function() select(data.frame(y = 1), !!enquo(y)))()
```

    ## Error: `function (expr) 
    ## {
    ##     enexpr(expr)
    ## }` must resolve to integer column positions, not a function

``` r
(function() mutate(data.frame(x = 1), !!rlang::ensym(y) := 2))()
```

    ## Error: 'ensym' is not an exported object from 'namespace:rlang'

(From [`rlang` issue 203](https://github.com/tidyverse/rlang/issues/203).)

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
nrow(dL)
```

    ## [1] 1

``` r
nrow(dR)
```

    ## [1] NA

(From [`dplyr` issue 2871](https://github.com/tidyverse/dplyr/issues/2871).)

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
union_all(dL, head(dL))
```

    ##       x k
    ## 1 3.077 a
    ## 2 3.077 a

``` r
union_all(dR, head(dR))
```

    ## Error: SQLite does not support set operations on LIMITs

(From [`dplyr` issue 2858](https://github.com/tidyverse/dplyr/issues/2858).)

mutate\_all funs()
------------------

``` r
dR %>% 
  mutate_all(funs(round(., 2)))
```

    ## # Source:   lazy query [?? x 2]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##       x     k
    ##   <dbl> <dbl>
    ## 1  3.08     0

``` r
dL %>% select(x) %>% 
  mutate_all(funs(round(., digits = 2)))
```

    ##      x
    ## 1 3.08

``` r
dR %>% select(x) %>% 
  mutate_all(funs(round(., digits = 2)))
```

    ## Warning: Named arguments ignored for SQL ROUND

    ## Error in rsqlite_send_query(conn@ptr, statement): near "AS": syntax error

(From [`dplyr` issue 2890](https://github.com/tidyverse/dplyr/issues/2890) and [`dplyr` issue 2908](https://github.com/tidyverse/dplyr/issues/2908).)

rename
------

``` r
dR %>% 
  rename(x2 = x) %>% rename(k2 = k)
```

    ## # Source:   lazy query [?? x 2]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##      x2    k2
    ##   <dbl> <chr>
    ## 1 3.077     a

``` r
dL %>% 
  rename(x2 = x, k2 = k)
```

    ##      x2 k2
    ## 1 3.077  a

``` r
dR %>% 
  rename(x2 = x, k2 = k)
```

    ## Error in names(select)[match(old_vars, vars)] <- new_vars: NAs are not allowed in subscripted assignments

(From [`dplyr` issue 2860](https://github.com/tidyverse/dplyr/issues/2860).)

Conclusion
==========

The above quiz is really my working notes on both how things work (so many examples are correct), and corner-cases to avoid. Some of the odd cases are simple bugs (which will likely be fixed), and some are legacy behaviors from earlier versions of `dplyr`. In many cases you can and should re-arrange your `dplyr` pipelines to avoid triggering the above issues. But to do that, you have to know what to avoid (hence the notes).

My quiz-grading priniciple comes from *Software for Data Analysis: Programming with R* by John Chambers (Springer 2008):

> ... the computations and the software for data analysis should be trustworthy: they should do what the claim, and be seen to do so. Neither those how view the results of data analysis nor, in many cases, the statisticians performing the analysis can directly validate extensive computations on large and complicated data processes. Ironically, the steadily increasing computer power applied to data analysis often distances the result further from direct checking by the recipient. The many computational steps between original data source and displayed results must all be truthful, or the effect of the analysis may be worthless, if not pernicious. This places an obligation on all creators of software to program in such a way that the computations can be understood and trusted.

The point is: to know a long calculation is correct, we must at least know all the small steps did what we (the analyst) intended (and not something else). To go back to one of our examples: the analyst must know the column selected in their analysis was *always* the one they intended.

Also: please understand, some of these may *not* represent problems with the above packages. They may instead represent mistakes and misunderstandings on my part. Or opinions of mine that may differ from the considered opinions and experience of the people who have authored and who have to maintain these packages. Some things that might seem "easy to fix" to an outsider may already be set at a "best possible compromise" among many other considerations.

I may or may not keep these up to date depending on the utility of such a list going forward.

<img src="TheUsualSuspects.gif" >

"Remebering we came to <code>R</code> to do statistics and machine learning."

\[ [quiz](https://github.com/WinVector/Examples/blob/master/dplyr/dplyrQuiz.md) \] \[ [solutions](https://github.com/WinVector/Examples/blob/master/dplyr/dplyrQuiz_solutions.md) \]
