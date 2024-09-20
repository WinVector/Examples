build versioned db
================
2024-09-19

An example of building the versioned database for [Please Version
Data](https://win-vector.com/2024/09/09/please-version-data/), [Please
Version Data
(source)](https://github.com/WinVector/Examples/blob/main/versioning_data/Please_Version_Data.md),
and [show versioned
data](https://github.com/WinVector/Examples/blob/main/versioning_data/show_versioned_data.md).

``` r
library(DBI)
# library(RSQLite)
source("pull_data_by_use.R")
```

``` r
con <- dbConnect(RSQLite::SQLite(), "movie_data.sqlite")
```

Read initial data, normalize column names, and assign `_fi` and `_usi`.

``` r
# read our first data
d_before_August_orig <- read.csv(
  'Roxie_schedule_as_known_before_August.csv', 
  strip.white = TRUE, 
  stringsAsFactors = FALSE)
d_before_August_orig$Attendance <- d_before_August_orig$EstimatedAttendance
d_before_August_orig$EstimatedAttendance <- NULL
d_before_August <- d_before_August_orig
# d_before_August$Date <- as.Date(d_before_August$Date)
orig_cols <- colnames(d_before_August_orig)
d_before_August$`_fi` <- 87776 + 1:nrow(d_before_August)
d_before_August$`_usi` <- 1337
domain_primary_keys = c('Date', 'Movie', 'Time')
d_before_August <- d_before_August[, c('_fi', '_usi', orig_cols), drop = FALSE]
stopifnot(sum(duplicated(d_before_August[, domain_primary_keys])) == 0)
```

Create first versions of all tables.

``` r
# start transaction
dbBegin(con)
```

``` r
update_log <- data.frame(
  `_usi` = c(1212, 1337),
  `_update_time` = c('2024-06-12 18:45:15Z', '2024-08-02 23:45:15Z'),
  note = c('mal-formatted records removed', 'after July 2024 data refresh'),
  as_of_date = c('2024-05-31', '2024-07-31'),
  check.names = FALSE
)
dbWriteTable(con, 'update_log', update_log, overwrite=TRUE)
dbGetQuery(con, "SELECT * from update_log") |>
  knitr::kable()
```

| \_usi | \_update_time        | note                          | as_of_date |
|------:|:---------------------|:------------------------------|:-----------|
|  1212 | 2024-06-12 18:45:15Z | mal-formatted records removed | 2024-05-31 |
|  1337 | 2024-08-02 23:45:15Z | after July 2024 data refresh  | 2024-07-31 |

``` r
dbWriteTable(con, 'd_data_log', d_before_August, overwrite=TRUE)
dbGetQuery(con, "SELECT * from d_data_log") |>
  head() |>
  knitr::kable()
```

|  \_fi | \_usi | Date       | Movie                                                | Time    | Attendance |
|------:|------:|:-----------|:-----------------------------------------------------|:--------|-----------:|
| 87777 |  1337 | 2024-08-01 | Chronicles of a Wandering Saint                      | 6:40 pm |         47 |
| 87778 |  1337 | 2024-08-01 | Eno                                                  | 6:40 pm |        233 |
| 87779 |  1337 | 2024-08-01 | Longlegs                                             | 8:35 pm |        233 |
| 87780 |  1337 | 2024-08-01 | Staff Pick: Melvin and Howard (35mm)                 | 8:45 pm |         47 |
| 87781 |  1337 | 2024-08-02 | Made in England: The Films of Powell and Pressburger | 6:00 pm |        233 |
| 87782 |  1337 | 2024-08-02 | Lyd                                                  | 6:30 pm |        233 |

``` r
d_row_deletions <- data.frame(
  `_usi` = c(1212, 1212),
  `_fi` = c(3312, 3313),
  check.names = FALSE
)
dbWriteTable(con, 'd_row_deletions', d_row_deletions, overwrite=TRUE)
dbGetQuery(con, "SELECT * from d_row_deletions")|>
  knitr::kable()
```

| \_usi | \_fi |
|------:|-----:|
|  1212 | 3312 |
|  1212 | 3313 |

``` r
# commit transaction
dbCommit(con)
```

Now the bi-temporal database is up. We can then try to update it based
on a new data pull from our simulated movie data vendor. Much better
would be for the vendor to share access to an already organized
bi-temporal database.

To update the data we need to determine what rows to insert, update, and
delete (all domain-specific changes) and assign a `_usi` for the whole
transaction and new `_fi` for any new rows.

``` r
# start transaction
dbBegin(con)
```

``` r
# confirm we have right _usi
max_usi <- dbGetQuery(con, "SELECT MAX(_usi) AS _usi from update_log")[1, 1]
if (max_usi != 1337) {
  # abort
  dbRollback(con)
  stopifnot(FALSE)
}
```

``` r
# get current view to compute deltas relative to
d_before_August <- pull_data_by_usi(con, 1337, return_intenal_keys = TRUE)
```

``` r
# read next glob of data
d_after_August_orig <- read.csv(
  'Roxie_schedule_as_known_after_August.csv', 
  strip.white = TRUE, 
  stringsAsFactors = FALSE)
d_after_August <- d_after_August_orig
# d_after_August$Date <- as.Date(d_after_August$Date)
d_after_August$`_usi` <- 1338
d_after_merged <- merge(
  d_after_August, 
  d_before_August[ , c('_fi', domain_primary_keys)], 
  by = domain_primary_keys,
  all.x = TRUE,
  all.y = FALSE)
stopifnot(nrow(d_after_merged) == nrow(d_after_August))
# TODO: new ID, and deleted ID cases, and no change in data cases
d_after_August <- d_after_merged[, c('_fi', '_usi', orig_cols), drop = FALSE]
stopifnot(sum(duplicated(d_after_August[, domain_primary_keys])) == 0)
```

We now have the new rows we want to insert. A production level
implementation would have to handle

- New IDs for new rows.
- Not inserting rows that have not changed.
- Marking deleted rows.

None of these are present in our current data, so we just update our
tables.

``` r
dbWriteTable(con, 'd_data_log', d_after_August, append=TRUE)
```

``` r
update_log <- data.frame(
  `_usi` = c(1338),
  `_update_time` = c('2024-09-03 22:12:00Z'),
  note = c('after August 2024 data refresh'),
  as_of_date = c('2024-08-31'),
  check.names = FALSE
)
dbWriteTable(con, 'update_log', update_log, append=TRUE)
head(dbGetQuery(con, "SELECT * from update_log"))
```

    ##   _usi         _update_time                           note as_of_date
    ## 1 1212 2024-06-12 18:45:15Z  mal-formatted records removed 2024-05-31
    ## 2 1337 2024-08-02 23:45:15Z   after July 2024 data refresh 2024-07-31
    ## 3 1338 2024-09-03 22:12:00Z after August 2024 data refresh 2024-08-31

``` r
# commit transaction
dbCommit(con)
```

Display our views.

``` r
d_before_August_view <- pull_data_by_usi(con, 1337)
```

``` r
head(d_before_August_view)
```

    ##         Date                                                Movie    Time
    ## 1 2024-08-01                      Chronicles of a Wandering Saint 6:40 pm
    ## 2 2024-08-01                                                  Eno 6:40 pm
    ## 3 2024-08-01                                             Longlegs 8:35 pm
    ## 4 2024-08-01                 Staff Pick: Melvin and Howard (35mm) 8:45 pm
    ## 5 2024-08-02 Made in England: The Films of Powell and Pressburger 6:00 pm
    ## 6 2024-08-02                                                  Lyd 6:30 pm
    ##   Attendance
    ## 1         47
    ## 2        233
    ## 3        233
    ## 4         47
    ## 5        233
    ## 6        233

``` r
d_after_August_view <- pull_data_by_usi(con, 1338)
```

``` r
head(d_after_August_view)
```

    ##         Date                                                Movie    Time
    ## 1 2024-08-01                      Chronicles of a Wandering Saint 6:40 pm
    ## 2 2024-08-01                                                  Eno 6:40 pm
    ## 3 2024-08-01                                             Longlegs 8:35 pm
    ## 4 2024-08-01                 Staff Pick: Melvin and Howard (35mm) 8:45 pm
    ## 5 2024-08-02 Made in England: The Films of Powell and Pressburger 6:00 pm
    ## 6 2024-08-02                                                  Lyd 6:30 pm
    ##   Attendance
    ## 1          6
    ## 2         10
    ## 3        114
    ## 4         23
    ## 5        204
    ## 6        213

Confirm the views reproduce the original data.

``` r
# confirm equivalent
equivalent_data_frames <- function(a, b) {
  if(!(all(dim(a) == dim(b)))) {
    return(FALSE)
  }
  cols <- sort(colnames(a))
  if(!all(cols == sort(colnames(b)))) {
    return(FALSE)
  }
  a <- a[, cols, drop=FALSE]
  b <- b[, cols, drop=FALSE]
  a <- a[do.call(order, a), , drop = FALSE]
  b <- b[do.call(order, b), , drop = FALSE]
  return(all(a==b))
}
```

``` r
stopifnot(equivalent_data_frames(d_before_August_orig, d_before_August_view[ , orig_cols]))
stopifnot(equivalent_data_frames(d_after_August_orig, d_after_August_view[ , orig_cols]))
```

``` r
dbDisconnect(con)
```
