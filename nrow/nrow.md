
It is Needlessly Difficult to Count Rows Using `dplyr`
======================================================

<!-- *.md is generated from *.Rmd. Please edit that file -->
-   Question: how hard is it to count rows using the [`R`](https://www.r-project.org) package [`dplyr`](https://CRAN.R-project.org/package=dplyr)?
-   Answer: surprisingly difficult.

When trying to count rows using `dplyr` or `dplyr` controlled data-structures (remote `tbl`s such as `Sparklyr` or `dbplyr` structures) one is [sailing between Scylla and Charybdis](https://en.wikipedia.org/wiki/Between_Scylla_and_Charybdis). The task being to avoid `dplyr` corner-cases and irregularities (a few of which I attempt to document in this ["`dplyr` inferno"](https://github.com/WinVector/Examples/blob/master/dplyr/dplyrQuiz.md)).

<center>
<a href="https://en.wikipedia.org/wiki/Between_Scylla_and_Charybdis"> <img src="800px-Johann_Heinrich_Füssli_054.jpg" width="300"> </a>
</center>
Let's take an example from [`sparklyr` issue 973](https://github.com/rstudio/sparklyr/issues/973):

``` r
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.7.2.9000'

``` r
library("sparklyr")
packageVersion("sparklyr")
```

    ## [1] '0.6.2'

``` r
sc <- spark_connect(master = "local")
```

    ## * Using Spark: 2.1.0

``` r
db_drop_table(sc, 'extab', force = TRUE)
```

    ## [1] 0

``` r
DBI::dbGetQuery(sc, "DROP TABLE IF EXISTS extab")
DBI::dbGetQuery(sc, "CREATE TABLE extab (n TINYINT)")
DBI::dbGetQuery(sc, "INSERT INTO extab VALUES (1), (2), (3)")

dRemote <- tbl(sc, "extab")
print(dRemote)
```

    ## # Source:   table<extab> [?? x 1]
    ## # Database: spark_connection
    ##       n
    ##   <raw>
    ## 1    01
    ## 2    02
    ## 3    03

``` r
dLocal <- data.frame(n = as.raw(1:3))
print(dLocal)
```

    ##    n
    ## 1 01
    ## 2 02
    ## 3 03

Many `Apache Spark` big data projects use the `TINYINT` type to save space. `TINYINT` behaves as a numeric type on the `Spark` side (you can run it through `SparkML` machine learning models correctly), and the translation of this type to `R`'s `raw` type (which is not an arithmetic or numerical type) is something that is likely to be fixed very soon. However, there are other reasons a table might have `R` `raw` columns in them, so we should expect our tools to work properly with such columns present.

Now let's try to count the rows of this table:

``` r
nrow(dRemote)
```

    ## [1] NA

That doesn't work ([apparently by choice!](http://www.win-vector.com/blog/2017/08/why-to-use-the-replyr-r-package/)). And I find myself in the odd position of having to defend expecting `nrow()` to return the number of rows.

There are a number of common legitimate uses of `nrow()` in user code and package code including:

-   Checking if a table is empty.
-   Checking the relative sizes of tables to re-order or optimize complicated joins (something our [join planner](http://www.win-vector.com/blog/2017/07/join-dependency-sorting/) might add one day).
-   Confirming data size is the same as reported in other sources (`Spark`, `database`, and so on).
-   Reporting amount of work performed or rows-per-second processed.

The obvious generic `dplyr` idiom would then be `dplyr::tally()` (our code won't know to call the new `sparklyr::sdf_nrow()` function, without writing code to check we are in fact looking at a `Sparklyr` reference structure):

``` r
tally(dRemote)
```

    ## # Source:   lazy query [?? x 1]
    ## # Database: spark_connection
    ##      nn
    ##   <dbl>
    ## 1     3

That returns the count for `Spark` (which according to `help(tally)` is *not* whath should happen, the stated return should be the sum of the values in the `n` column), but not for local tables. This is filled as [`sparklyr` issue 982](https://github.com/rstudio/sparklyr/issues/982) (no idea if it affects other `dbplyr` clients such as `PostgreSQL`).

``` r
dLocal %>% 
  tally
```

    ## Using `n` as weighting variable

    ## Error in summarise_impl(.data, dots): Evaluation error: invalid 'type' (raw) of argument.

The above code usually either errors-out (if the column is `raw`) or creates a new total column called `nn` with the sum of the `n` column instead of the count.

``` r
data.frame(n=100) %>% 
  tally
```

    ## Using `n` as weighting variable

    ##    nn
    ## 1 100

We could try adding a column and summing that:

``` r
dLocal %>% 
  transmute(constant = 1.0) %>%
  summarize(n = sum(constant))
```

    ## Error in mutate_impl(.data, dots): Column `n` is of unsupported type raw vector

That fails due to [`dplyr` issue 3069](https://github.com/tidyverse/dplyr/issues/3069): local `mutate()` fails if there are any `raw` columns present (even if they are not the columns you are attempting to work with).

We can try removing the dangerous column prior to other steps:

``` r
dLocal %>% 
  select(-n) %>%
  tally
```

    ## data frame with 0 columns and 3 rows

That does not work on local tables, as `tally` fails to count 0-column objects ([`dplyr` issue 3071](https://github.com/tidyverse/dplyr/issues/3071); probably the same issue exists for may `dplyr` verbs as we saw a related issue for [`dplyr::distinct`](https://github.com/tidyverse/dplyr/issues/2954)).

And the method does not work on remote tables either (`Spark`, or database tables) as many of them do not appear to support 0-column results:

``` r
dRemote %>% 
  select(-n) %>%
  tally
```

    ## Error: Query contains no columns

In fact we start to feel trapped here. For a data-object whose only column is of type `raw` we can't remove all the `raw` columns as we would then form a zero-column result (which does not seem to always be legal), but we can not add columns as that is a current bug for local frames. We could try some other transforms (such as joins, but we don't have safe columns to join on).

At best we can try something like this:

``` r
nrow2 <- function(d) {
  n <- nrow(d)
  if(!is.na(n)) {
    return(n)
  }
  d %>% 
    ungroup() %>%
    transmute(constant = 1.0) %>% 
    summarize(tot = sum(constant)) %>%
    pull()
}

dRemote %>% 
  nrow2()
```

    ## [1] 3

``` r
dLocal %>% 
  nrow2()
```

    ## [1] 3

We are still [experimenting with work-arounds](https://winvector.github.io/replyr/reference/replyr_nrow.html) in the [`replyr` package](https://winvector.github.io/replyr/) (but it is necessarily [ugly code](https://github.com/WinVector/replyr/blob/master/R/nrow.R)).

``` r
spark_disconnect(sc)
```
