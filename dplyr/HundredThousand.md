Is 10,000 cells large?
================
Win-Vector LLC
2/12/2018

Trick question: is a `10,000` cell numeric `data.frame` large or small?

In the era of "big data" `10,000` cells is minuscule. Such data could be fit on fewer than `1,000` punched cards (or less than half a box).

<center>
<img src="punch-card.png">
</center>
The joking answer is: it is small when they are selling you the software, but can be considered unfairly large later.

Example
=======

Let's look at a few examples in [`R`](https://cran.r-project.org). First let's set up our examples. A `10,000` row by one column `data.frame` (probably fairly close the common mental model of a `100,000` cell `data.frame`), and a `100,000` column by one row `data.frame` (frankly bit of an abuse, but large data warehouses with millions of rows and `500` to `1,000` columns are not uncommon).

``` r
dTall <- as.data.frame(matrix(data = 0.0, 
                              nrow = 10000, 
                              ncol = 1))

dWide <- as.data.frame(matrix(data = 0.0, 
                              nrow = 1,
                              ncol = 10000))
```

For our example problem we will try to select (zero) rows based on a condition written against the first column.

Base R
======

For standard `R` working with either `data.frame` is not a problem.

``` r
system.time(nrow(dTall[dTall$V1>0, , drop = FALSE]))
```

    ##    user  system elapsed 
    ##       0       0       0

``` r
system.time(nrow(dWide[dWide$V1>0, , drop = FALSE]))
```

    ##    user  system elapsed 
    ##   0.059   0.004   0.064

dplyr
=====

For `dplyr` the tall frame is no problem, but the wide frame can take almost 5 minutes to filter.

``` r
library("dplyr")
```

    ## 
    ## Attaching package: 'dplyr'

    ## The following objects are masked from 'package:stats':
    ## 
    ##     filter, lag

    ## The following objects are masked from 'package:base':
    ## 
    ##     intersect, setdiff, setequal, union

``` r
system.time(dTall %>% filter(V1>0) %>% tally())
```

    ##    user  system elapsed 
    ##   0.059   0.003   0.061

``` r
system.time(dWide %>% filter(V1>0) %>% tally())
```

    ##    user  system elapsed 
    ##   2.224   0.087   2.320

We will dig deeper into the `dplyr` timing on the wide table later.

Databases
=========

Most databases don't really like to work with a ridiculous number of columns.

RSQLite
-------

`RSQLite` refuses to worm with the wide frame.

``` r
db <- DBI::dbConnect(RSQLite::SQLite(), 
                     ":memory:")
```

``` r
DBI::dbWriteTable(db, "dTall", dTall,
                  overwrite = TRUE,
                  temporary = TRUE)

DBI::dbWriteTable(db, "dWide", dWide,
                  overwrite = TRUE,
                  temporary = TRUE)
```

    ## Error in rsqlite_send_query(conn@ptr, statement): too many columns on dWide

``` r
DBI::dbDisconnect(db)
```

PostgreSQL
----------

PostgreSQL refuses the wide frame, stating a hard limit of `1600` columns.

``` r
db <- DBI::dbConnect(RPostgres::Postgres(),
                     host = 'localhost',
                     port = 5432,
                     user = 'postgres',
                     password = 'pg')
```

``` r
DBI::dbWriteTable(db, "dTall", dTall,
                  overwrite = TRUE,
                  temporary = TRUE)

DBI::dbWriteTable(db, "dWide", dWide,
                  overwrite = TRUE,
                  temporary = TRUE)
```

    ## Error in result_create(conn@ptr, statement): Failed to fetch row: ERROR:  tables can have at most 1600 columns

``` r
DBI::dbDisconnect(db)
```

Spark
-----

Spark fails, losing the cluster connection when attempting to write the wide frame.

``` r
spark <- sparklyr::spark_connect(version='2.2.0', 
                                 master = "local")
```

``` r
DBI::dbWriteTable(spark, "dTall", dTall,
                  temporary = TRUE)

DBI::dbWriteTable(db, "dWide", dWide,
                  temporary = TRUE)
```

    ## Error in connection_quote_identifier(conn@ptr, x): Invalid connection

``` r
sparklyr::spark_disconnect(spark)
```

Why I care
==========

Some clients have run into intermittent issues on `Spark` at around 700 columns. One step of working around the issue was trying a range of sizes to try and figure out where the issue was and get a repeatable failure ( always an imporant step in debugging).

Extra: dplyr again at larger scale.
===================================

Let's look a bit more closely at that dplyr run-time.
We will try to get the nature of the column dependency by pushing the column count ever further up: to `100,000`.

This is still less than a megabyte of data. It can fit on a 1986 era `1.44 MB` floppy disk.

<center>
<img src="Floppy_disk_300_dpi.jpg">
</center>
``` r
dWide <- as.data.frame(matrix(data = 0.0, 
                              nrow = 1,
                              ncol = 100000))

dwt <- system.time(dWide %>% filter(V1>0) %>% tally())
print(dwt)
```

    ##    user  system elapsed 
    ## 251.441  28.067 283.060

Python
------

For comparison we can measure how long it would take to write the results out to disk, start up a [Python](https://www.python.org) interpreter, use [Pandas](https://pandas.pydata.org) do do the work, and then read the result back in to `R`.

``` r
start_pandas <- Sys.time()
feather::write_feather(dWide, "df.feather")
```

``` python
import pandas
import feather
df = feather.read_dataframe('df.feather')
print(type(df))
```

    ## <class 'pandas.core.frame.DataFrame'>

``` python
print(df.shape)
```

    ## (1, 100000)

``` python
df_filtered = df.query('V1>1')
feather.write_dataframe(df_filtered, 'dr.feather')
```

``` r
res <- feather::read_feather('dr.feather')
nrow(res)
```

    ## [1] 0

``` r
end_pandas <- Sys.time()
python_duration <- difftime(end_pandas, start_pandas, 
                            unit = "secs")
print(python_duration)
```

    ## Time difference of 21.05746 secs

``` r
ratio <- as.numeric(dwt['elapsed'])/as.numeric(python_duration)
print(ratio)
```

    ## [1] 13.44227

This is slow, but still 13.4 times faster than using `dplyr`.
