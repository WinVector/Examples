Advanced dplyr Quiz
================
John Mount
9/24/2018

Advanced dplyr Quiz
===================

[`dplyr`](https://CRAN.R-project.org/package=dplyr) is promoted as having a regular interface (implicitly meaning an interface more regular than base-[`R`](https://www.r-project.org)). This is, unfortunately, not the case.

The `dplyr` system is built up of many exceptions and sub-systems (tidyselect, hybrideval, rlang) and legacy choices (choices that may or may not have made sense when made, but are harmful now). In my opinion `dplyr` can be more irregular than base-`R`, despite many claims and much teaching to the contrary. By all means use `dplyr`, but *please* take its marketing with a grain of salt (especially when working with new users). Also understand, if your method of promoting `dplyr` is to try and make the case that `R` is unusable: you are at best chasing users away from `R` (likely into `Python`, where they will actually be quite happy).

Below is our advanced [`dplyr`](https://CRAN.R-project.org/package=dplyr) quiz. It tries to show how anticipating the result of each operation can be difficult.

<img src="Samuel_Johnson_by_Joshua_Reynolds_2.png" width="400">

"Please read on for the answers!"

Start
=====

With the current version of `dplyr` in mind, please anticipate the result of each example command. Note: we don't claim all of the examples below are correct `dplyr` code. However, effective programming requires knowledge of what happens in some incorrect cases (at least knowing which throw usable errors, and which perform quiet mal-calculations).

``` r
# Show versions we are using.
packageVersion("dplyr")
```

    ## [1] '0.7.7'

``` r
packageVersion("dbplyr")
```

    ## [1] '1.2.2'

``` r
packageVersion("RSQlite")
```

    ## [1] '2.1.1'

``` r
packageVersion("rlang")
```

    ## [1] '0.3.0.1'

``` r
packageVersion("magrittr")
```

    ## [1] '1.5'

``` r
base::date()
```

    ## [1] "Sat Nov  3 16:16:41 2018"

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

`dplyr` usually selects column names using the name captured from un-evaluated user code. For example the following code selects the variable "`x`".

``` r
data.frame(x = 1) %>% 
  select(x)
```

    ##   x
    ## 1 1

It gets confusing if a string (possibly acting as a column name) or number (possibly acting as a column index) is used. Try and guess what column each of the two following `dplyr` pipelines produce.

``` r
y <- 'x' # value used in later examples

data.frame(x = 1, y = 2) %>% 
  select(y)
```

    ##   y
    ## 1 2

``` r
data.frame(x = 1) %>% 
  select(y)
```

    ##   x
    ## 1 1

``` r
rm(list='y') # clean up
```

(From [`dplyr` issue 2904](https://github.com/tidyverse/dplyr/issues/2904), see also [here](http://www.win-vector.com/blog/2018/09/a-subtle-flaw-in-some-popular-r-nse-interfaces/).)

distinct
--------

Removing a column from a `data.frame` should never increase the number of distinct rows. In the next two pipelines please guess the row counts.

``` r
data.frame(x = c(1, 1)) %>% 
  distinct() %>%
  nrow()
```

    ## [1] 1

``` r
data.frame(x = c(1, 1)) %>% 
  select(one_of(character(0))) %>%
  distinct() %>%
  nrow()
```

    ## [1] 2

(From [`dplyr` issue 2954](https://github.com/tidyverse/dplyr/issues/2954).)

tally
-----

It can be hard to predict what column `count` or `tally` will land their counts in (usually `n`, but often `nn`, even when there is no conflict). Please try and guess the column name produced by the following pipelines.

``` r
data.frame(g = c(1, 1, 2), n = 0) %>% 
  select(-n) %>%
  count(., g)
```

    ## # A tibble: 2 x 2
    ##       g     n
    ##   <dbl> <int>
    ## 1     1     2
    ## 2     2     1

``` r
data.frame(g = c(1, 1, 2), n = 0) %>% 
  count(., g)
```

    ## # A tibble: 2 x 2
    ##       g    nn
    ##   <dbl> <int>
    ## 1     1     2
    ## 2     2     1

Not being able to reliably anticipate the result column name makes it difficult to use that produced value later.

[`dplyr` issue 3838](https://github.com/tidyverse/dplyr/issues/3838).

rename and mutate
-----------------

NULL (constant versus in a variable)
------------------------------------

In `R` is traditional to use `NULL` assignment to remove columns. In the code below *if* [referential transparency](https://en.wikipedia.org/wiki/Referential_transparency) were respected we should have values behaving the same as variables containing the same values. Please anticipate the result of each of the following pipelines.

``` r
data.frame(x=1, y=2) %>% mutate(x = NULL)
```

    ##   y
    ## 1 2

``` r
z <- NULL 
data.frame(x=1, y=2) %>% mutate(x = z)
```

    ## Error in mutate_impl(.data, dots): Column `x` is of unsupported type NULL

``` r
rm(list='z') # clean up
```

(From [`dplyr` issue 2945](https://github.com/tidyverse/dplyr/issues/2945).)

Arrange
-------

The `help(arrange, package = "dplyr")` says that the "`...`" arguments to arrange are a "Comma separated list of unquoted variable names. Use desc() to sort a variable in descending order."

With that in mind what should be the result of the following code?

``` r
mtcars %>%
  arrange(-hp/cyl) %>%
  head()
```

    ##    mpg cyl disp  hp drat    wt  qsec vs am gear carb
    ## 1 15.0   8  301 335 3.54 3.570 14.60  0  1    5    8
    ## 2 15.8   8  351 264 4.22 3.170 14.50  0  1    5    4
    ## 3 14.3   8  360 245 3.21 3.570 15.84  0  0    3    4
    ## 4 13.3   8  350 245 3.73 3.840 15.41  0  0    3    4
    ## 5 19.7   6  145 175 3.62 2.770 15.50  0  1    5    6
    ## 6 14.7   8  440 230 3.23 5.345 17.42  0  0    3    4

Assuming code like the above is in fact allowed (and not protected against) when should the result of the next two examples be? (Hint: should they be equal?)

``` r
iris2 <- data.frame(
  Petal.Width = c(1.3, 0.2, 0.6, 0.3),
  Species = c("versicolor", "setosa", "setosa", "setosa"),
  stringsAsFactors = FALSE)

iris2 %>%
  group_by(Species) %>%
  arrange(Species, Petal.Width) %>%
  head()
```

    ## # A tibble: 4 x 2
    ## # Groups:   Species [2]
    ##   Petal.Width Species   
    ##         <dbl> <chr>     
    ## 1         0.2 setosa    
    ## 2         0.3 setosa    
    ## 3         0.6 setosa    
    ## 4         1.3 versicolor

``` r
iris2 %>%
  group_by(Species) %>%
  arrange(Species, order(Petal.Width)) %>%
  head()
```

    ## # A tibble: 4 x 2
    ## # Groups:   Species [2]
    ##   Petal.Width Species   
    ##         <dbl> <chr>     
    ## 1         0.3 setosa    
    ## 2         0.6 setosa    
    ## 3         0.2 setosa    
    ## 4         1.3 versicolor

``` r
rm(list = "iris2")
```

(From [3782](https://github.com/tidyverse/dplyr/issues/3782).)

summarize
---------

``` r
dplyr::summarize(data.frame(x = 1), 
                 x = max(x), 
                 min_x = min(x))
```

    ##   x min_x
    ## 1 1     0

Databases
=========

`dplyr` code can run on databases, through the `dbplyr` adapter. One would expect the purpose of this is to have the "same code same semantics" (to the limit that is practical on databases).

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

`dplyr` does not allow `nrow()` to return the number of rows on a database table.

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

One of the following four examples fails. The reason is the `SQL` `dplyr` generated was not supported by the `SQLite` database.

``` r
union_all(dL, dL)
```

    ##       x k
    ## 1 3.077 a
    ## 2 3.077 a

``` r
union_all(dR, dR)
```

    ## # Source:   lazy query [?? x 2]
    ## # Database: sqlite 3.22.0 [:memory:]
    ##       x k    
    ##   <dbl> <chr>
    ## 1  3.08 a    
    ## 2  3.08 a

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

The above issue is indeed a shortcoming of the database, but it is possible to generate `SQL` to perform this task and that is the claim of `dbplyr`.

(From [`dplyr` issue 2858](https://github.com/tidyverse/dplyr/issues/2858).)

variable/value tracking
-----------------------

``` r
d_local <- data.frame(x = 1)

d_local %>% 
  mutate(y = 1, y = y + 1, y = y + 1)
```

    ##   x y
    ## 1 1 3

``` r
d_remote <- dplyr::copy_to(db, d_local, 
                           "d_remote")

d_remote %>% 
  mutate(y = 1, y = y + 1, y = y + 1)
```

    ## # Source:   lazy query [?? x 2]
    ## # Database: sqlite 3.22.0 [:memory:]
    ##       x     y
    ##   <dbl> <dbl>
    ## 1     1     2

Conclusion
==========

The above quiz is really my working notes on both how things work (so many examples are correct), and corner-cases to avoid. Some of the odd cases are simple bugs (which will likely be fixed), and some are legacy behaviors from earlier versions of `dplyr` (which makes fixing them difficult). In many cases you can and should re-arrange your `dplyr` pipelines to avoid triggering the above issues. But to do that, you have to know what to avoid (hence the notes).

My quiz-grading principle comes from *Software for Data Analysis: Programming with R* by John Chambers (Springer 2008):

> ... the computations and the software for data analysis should be trustworthy: they should do what the claim, and be seen to do so. Neither those how view the results of data analysis nor, in many cases, the statisticians performing the analysis can directly validate extensive computations on large and complicated data processes. Ironically, the steadily increasing computer power applied to data analysis often distances the result further from direct checking by the recipient. The many computational steps between original data source and displayed results must all be truthful, or the effect of the analysis may be worthless, if not pernicious. This places an obligation on all creators of software to program in such a way that the computations can be understood and trusted.

The point is: to know a long calculation is correct, we must at least know all the small steps did what we (the analyst) intended (and not something else). To go back to one of our examples: the analyst must know the column selected in their analysis was *always* the one they intended.

`dplyr` has been subject to very rapid evolution, and has accumulated as least as many legacy behaviors (choices that don't currently make sense, but are hard to change) as base-`R` itself. In fact I feel when using base-`R` as long as one remembers to use `drop = FALSE` and `stringsAsFactors = FALSE` (two defaults that must forever be left in these undesirable settings for legacy reasons) one can code in a fairly safe and consistent manner. I believe base-`R` is in fact more regular than `dplyr` (despite the [`R`-inferno](https://www.burns-stat.com/pages/Tutor/R_inferno.pdf)).

I may or may not keep these up to date depending on the utility of such a list going forward.

<img src="TheUsualSuspects.gif" >

"Remebering we came to <code>R</code> to do statistics and machine learning."

\[ [quiz](https://github.com/WinVector/Examples/blob/master/dplyr/dplyrQuiz.md) \] \[ [solutions](https://github.com/WinVector/Examples/blob/master/dplyr/dplyrQuiz_solutions.md) \]
