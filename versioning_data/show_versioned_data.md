show versioned data
================
2024-09-19

## Introduction

In our note [Please Version
Data](https://win-vector.com/2024/09/09/please-version-data/) (and
[Please Version Data
(source)](https://github.com/WinVector/Examples/blob/main/versioning_data/Please_Version_Data.md))
we wished that a data source (in this case move attendance) was
[bi-temporal](https://en.wikipedia.org/wiki/Bitemporal_modeling) or
versioned. In this note we outline how to work with bi-temporal database
in `R`.

Let’s start up `R`.

``` r
library(DBI)
library(RSQLite)
source("pull_data_by_use.R")
```

Our previous example’s analysis depended on being able to switch from a
corrected data file `Roxie_schedule_as_known_after_August.csv` to a more
useful one (for machine learning) that would more accurately reflect
what would be known when a forward in in time forecasting model is to be
applied: `Roxie_schedule_as_known_before_August.csv`.

The issue being: a model applied to the future would only have itself
future projections of necessary explanatory variables, and not have
access to later back-filled corrections. Thus to train a model on
“August data” to be applied in September, we demonstrated it was in fact
much better to have what was thought about August back in July as our
training data (and not what was known about August later in September).

This is under the rubric: train and evaluate a model to simulate how you
are going to use it (and not according to some set of rules).

## Bi-temporal data

The above gets confusing as we are taking about data for a given month
(August 2024) *and* a second date (called the “as of date”) of what
changing view we have of this date (in this case as of July 2024). These
two date/time keys (fact date and as of date) give us the name
“bi-temporal.”

## Our Example

Let’s take a look a full bi-temporal data store that could produce the
previous `Roxie_schedule_as_known_before_August.csv` and
`Roxie_schedule_as_known_after_August.csv` data views.

Typically such data is maintained in a relational database, and accessed
as a query or view. Let’s connect to a pre-prepared example database.

``` r
con <- dbConnect(
  RSQLite::SQLite(), 
  "movie_data.sqlite", 
  flags=SQLITE_RO)
```

The movie attendance data is stored as follows.

``` r
dbGetQuery(
  con, 
  "SELECT * from d_data_log ORDER BY _fi, _usi LIMIT 6") |>
  knitr::kable()
```

|  \_fi | \_usi | Date       | Movie                                                | Time    | Attendance |
|------:|------:|:-----------|:-----------------------------------------------------|:--------|-----------:|
| 87777 |  1337 | 2024-08-01 | Chronicles of a Wandering Saint                      | 6:40 pm |         47 |
| 87778 |  1337 | 2024-08-01 | Longlegs                                             | 8:35 pm |        233 |
| 87778 |  1338 | 2024-08-01 | Longlegs                                             | 8:35 pm |        114 |
| 87779 |  1337 | 2024-08-01 | Staff Pick: Melvin and Howard (35mm)                 | 8:45 pm |         47 |
| 87779 |  1338 | 2024-08-01 | Staff Pick: Melvin and Howard (35mm)                 | 8:45 pm |         23 |
| 87780 |  1337 | 2024-08-02 | Made in England: The Films of Powell and Pressburger | 6:00 pm |        233 |

This table is a running log of new row values.

## The key control fields

Notice we have two new columns (in additional to our original data
columns):

- `_fi`: the “fact ID.” Each fact in the database now has an ID. This
  lets us talk about different values associated with the same fact.
- `_usi`: the “update sequence index.” Each update to the table
  (modifications, insertions, and deletions) now has an index. This
  index is monotone increasing in time. Updates are also atomic: for a
  given time all of the changes due to an update have either not yet
  happened, or already happened.

Notice our displayed 6 rows is actually only 3 facts shown for two
different update indexes (`1337` and `1338`).

## The update log

We also have 2 new tables. The first is the `update_log` which relates
the `_usi` to datetimes, and can store notes and additional data
provenance fields (`note`) and the official data stamp (`as_of_date`,
which is when the data is to be considered to be “known”, and can differ
from `_update_time`).

``` r
dbGetQuery(
  con, 
  "SELECT * from update_log ORDER BY _usi") |>
  knitr::kable()
```

| \_usi | \_update_time        | note                           | as_of_date |
|------:|:---------------------|:-------------------------------|:-----------|
|  1212 | 2024-06-12 18:45:15Z | mal-formatted records removed  | 2024-05-31 |
|  1337 | 2024-08-02 23:45:15Z | after July 2024 data refresh   | 2024-07-31 |
|  1338 | 2024-09-03 22:12:00Z | after August 2024 data refresh | 2024-08-31 |

## How to use

To retrieve a view of what the data was supposed to look like pick an
`as_of_date` and then find the largest `_usi` corresponding to this
`as_of_date` (or before if there are no `_usi` with the given
`as_of_date`).

``` r
usi_before_August = dbGetQuery(
  con, 
  "SELECT MAX(_usi) FROM update_log WHERE as_of_date <= '2024-07-31'")[1, 1]

usi_before_August
```

    ## [1] 1337

With our `_usi` in hand, we can than access a view of the data with
exactly what was known at this point. In this view:

- Records inserted or altered up to the `_usi` time are available in
  their most recent form no later than the `_usi`.
- Records deleted by the the `_usi` time are not shown (as they would
  not be in that view).

The “no later than” discipline means rows that haven’t been updated are
stored only once and don’t replicate “per snapshot.”

The
[query](https://github.com/WinVector/Examples/blob/main/versioning_data/pull_data_by_use.R)
itself is a bit large, but it is exactly what relational databases are
built for.

We pull an initial data sample:

``` r
d_before_August <- pull_data_by_usi(
  con, 
  usi_before_August,
  return_intenal_keys = TRUE)
```

``` r
d_before_August |>
  head(n=3) |>
  knitr::kable()
```

|  \_fi | \_usi | Date       | Movie                                | Time    | Attendance |
|------:|------:|:-----------|:-------------------------------------|:--------|-----------:|
| 87777 |  1337 | 2024-08-01 | Chronicles of a Wandering Saint      | 6:40 pm |         47 |
| 87778 |  1337 | 2024-08-01 | Longlegs                             | 8:35 pm |        233 |
| 87779 |  1337 | 2024-08-01 | Staff Pick: Melvin and Howard (35mm) | 8:45 pm |         47 |

Notice we have only the older “Attendance ~ Theater Capacity” data rows
that were available in July.

Later we can pull the “as of 2024-08-31” data.

``` r
usi_after_August = dbGetQuery(
  con, 
  "SELECT MAX(_usi) FROM update_log WHERE as_of_date <= '2024-08-31'")[1, 1]

usi_after_August
```

    ## [1] 1338

``` r
d_after_August <- pull_data_by_usi(
  con, 
  usi_after_August, 
  return_intenal_keys = TRUE)
```

``` r
d_after_August |>
  head(n=3) |>
  knitr::kable()
```

|  \_fi | \_usi | Date       | Movie                                                | Time    | Attendance |
|------:|------:|:-----------|:-----------------------------------------------------|:--------|-----------:|
| 87778 |  1338 | 2024-08-01 | Longlegs                                             | 8:35 pm |        114 |
| 87779 |  1338 | 2024-08-01 | Staff Pick: Melvin and Howard (35mm)                 | 8:45 pm |         23 |
| 87780 |  1338 | 2024-08-02 | Made in England: The Films of Powell and Pressburger | 6:00 pm |        204 |

Now we have the “after the event, Attendance is updated to show how may
tickets actually sold.”

### Internal keys

Normally, for hygiene reasons, we recommend not showing/sharing internal
keys when they are not needed. It cuts down consfusion and mis-use. In
our above `pull_data_by_usi()` we showed the internal keys to make
discription easier. In model training we would pull data that looks more
like the following.

``` r
pull_data_by_usi(
  con, 
  usi_before_August) |>
  head(n=3) |>
  knitr::kable()
```

| Date       | Movie                                | Time    | Attendance |
|:-----------|:-------------------------------------|:--------|-----------:|
| 2024-08-01 | Chronicles of a Wandering Saint      | 6:40 pm |         47 |
| 2024-08-01 | Longlegs                             | 8:35 pm |        233 |
| 2024-08-01 | Staff Pick: Melvin and Howard (35mm) | 8:45 pm |         47 |

## Procedures

What “as_of_date” to use is a domain specific question. In our note
[“Please Version
Data”](https://www.r-bloggers.com/2024/09/please-version-data/) we
advocated that during model training one should use an as_of_date that
simulates how fresh data would be when the model is applied.

A minor detail is: deleted rows can’t carry the `_usi` and `_fi`
advisory fields. So to *simulate* row deletion we *do not* delete rows
from our data store, instead keep an additional `d_row_deletions` table
that tells us when rows are to be considered deleted.

``` r
dbGetQuery(
  con, 
  "SELECT * FROM d_row_deletions ORDER BY _usi, _fi") |>
  knitr::kable()
```

| \_usi |  \_fi |
|------:|------:|
|  1212 |  3312 |
|  1212 |  3313 |
|  1338 | 87777 |

## The `_fi`

The `_fi` (fact IDs) are critically important. Setting them correctly is
a major data maintenance task. They are what prevent (or at least bound)
a [“Ship of Theseus”](https://en.wikipedia.org/wiki/Ship_of_Theseus)
meltdown in our data rows (or the “row of Theseus”). Different versions
of a row (indexed by the `_usi`) are “the same row” if and only if they
share the same `_fi`, no matter how many titles, keys, names, or fields
change or migrate to other rows.

<center>
<a href="https://commons.wikimedia.org/wiki/File:HMSTheseus1897.jpg"><img src="./HMSTheseus1897.jpg" height=300></a>
<p/>
(Don’t trust even names, the wrong Ship of Theseus)
</center>

## Conclusion

This bi-temporal data model allows for time-rewinding on:

- Record (or row) creation.
- Record (or row) alteration.
- Row deletion.
- Sets of updates taken as a “all at once” or atomic blocks.

This is implemented as an “append only” data store (no rows are altered
or deleted in the actual data store, alterations and deletions are
simulated by a filtering query).

## Appendix

### Maintinance

To add or update data one:

- Starts a database transaction (to control visibility and atomic nature
  of an update).
- Reserves a new `_usi` and adds it to the `update_log`.
- Takes in new data and data changes as diffs from the previous `_usi`
  (to minimize data size) and inserts complete new rows with the new
  `_usi`.
- Marks any rows considered to be deleted in the `d_row_deletions`
  table.
- Completes or aborts the database transaction.

For a row to “be altered” we must have unique keying to say something is
a “new value in an old row” versus “a new row that looks a lot like an
old row.” So to update data we must have some (domain specific) concept
of row identity- or assigning the `_fi` key. We could use the `_fi` key
itself, but it usually makes more sense to also have domain specific set
of fields considered to be “primary domain keys” (though there are
issues if values of these keys change, which is another reason why we
have `_fi`). Just keep in mind: the system does not support altering the
the `_fi` or `_usi` keys in a time-rewindable manner. These keys are
what implement the time rewinding.

The “append only” nature of the data store is just a convention to
support playing an *intended view* of time forward and backward. For
changes we do not intend to undo or replay we would directly alter the
data store. For instance deleting PII (personally identifiable
information) would be done by censoring all fields of all row versions,
or even deleting rows from the data store (instead of just marking as
deleted in the `d_row_deletions` table).

We have a sketched out example of new data ingestion
[here](https://github.com/WinVector/Examples/blob/main/versioning_data/BuildVersionBase.md).
However, maintaining the bi-temporal database is exactly the step the
anlyst hopes to delegate or ignore. The analyst needs to assume a
bitemporal source and use it well.

``` r
dbDisconnect(con)
```
