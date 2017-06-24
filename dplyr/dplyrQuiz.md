Advanced dplyr Quiz (author: John Mount)
========================================

Being able to effectively perform meaningful work *using* [`R`](https://www.r-project.org) programming involves being able to both know how various packages work and anticipate package method outcomes in basic situations. Any mismatch there (be it a knowledge gap in the programmer, an implementation gap in a package, or a difference between programmer opinion and package doctrine) can lead to confusion, bugs and incorrect results.

Below is our advanced [`dplyr`](https://CRAN.R-project.org/package=dplyr) quiz. Can you anticipate the result of each of the example operations? Can you anticipate which commands are in error and which are valid `dplyr`?

Or another phrasing: here are our notes on `dplyr` corner-cases (in my *opinion*). You may not need to know how any of these work (it is often good to avoid corner-cases), but you should at least be confident you are avoiding the malformed ones.

Start
=====

With the current version of `dplyr` in mind, please anticipate the result of each example command. Note: we don't claim all of the examples below are correct `dplyr` code. However, effective programming requires knowledge of what happens in some incorrect cases (at least knowing which throw usable errors, and which perform quiet mal-calculations).

``` r
suppressPackageStartupMessages(library("dplyr"))
```

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

# Two questions: 
#  1) Should this next one work?
#  2) Does this next one work?
data.frame(x = 1) %>% select('x')

y <- 'x' # value used in later examples

data.frame(x = 1) %>% select(y)
data.frame(x = 1, y = 2) %>% select(y)
```

(From [dplyr 2904](https://github.com/tidyverse/dplyr/issues/2904).)

Piping into different targets (functions, blocks expressions):
--------------------------------------------------------------

`magrittr` pipe details:

``` r
data.frame(x = 1)  %>%  { bind_rows(list(., .)) }
data.frame(x = 1)  %>%    bind_rows(list(., .))
data.frame(x = 1)  %>%  ( bind_rows(list(., .)) )
```

Same with [Bizarro Pipe](https://cran.r-project.org/web/packages/replyr/vignettes/BizarroPipe.html):

``` r
data.frame(x = 1)  ->.;  { bind_rows(list(., .)) }
data.frame(x = 1)  ->.;    bind_rows(list(., .))
data.frame(x = 1)  ->.;  ( bind_rows(list(., .)) )
```

enquo rules
-----------

``` r
(function(x) select(data.frame(x = 1), !!enquo(x)))(x)
(function(x) data.frame(x = 1) %>% select(!!enquo(x)))(x)
```

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

(From [dplyr 2871](https://github.com/tidyverse/dplyr/issues/2871).)

union\_all()
------------

``` r
union_all(dR, dR)
union_all(dR, head(dR))
```

(From [dplyr 2858](https://github.com/tidyverse/dplyr/issues/2858).)

mutate\_all funs()
------------------

``` r
dR %>% mutate_all(funs(round(., 2)))
dR %>% mutate_all(funs(round(., digits = 2)))
```

(From [dplyr 2890](https://github.com/tidyverse/dplyr/issues/2890) and [dplyr 2908](https://github.com/tidyverse/dplyr/issues/2908).)

rename
------

``` r
dR %>% rename(x2 = x) %>% rename(k2 = k)
dR %>% rename(x2 = x, k2 = k)
```

(From [dplyr 2860](https://github.com/tidyverse/dplyr/issues/2860).)

Conclusion
==========

The above quiz is really my working notes on corner-cases to avoid. Not all of these are worth fixing. In many cases you can and should re-arrange your `dplyr` pipelines to avoid triggering the above cases. But to do that, you have to know what to avoid (hence the notes).

Also: please understand, some of these may *not* represent problems with the above packages. They may instead represent mistakes and misunderstandings on my part. Or opinions of mine that may differ from the considered opinions and experience of the people who have authored and who have to maintain these packages. Some things that might seem "easy to fix" to an outsider may already be set at a "best possible compromise" among many other considerations.

I may or may not keep these up to date depending on the utility of such a list going forward.
