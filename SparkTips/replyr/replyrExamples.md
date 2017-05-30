<!-- README.md is generated from README.Rmd. Please edit that file -->
Why `replyr`
============

`replyr` stands for **RE**mote **PLY**ing of big data for **R**.

Why should [R](https://www.r-project.org) users try [`replyr`](https://CRAN.R-project.org/package=replyr)? Because it lets you take a number of common working patterns and apply them to remote data (such as databases or [`Spark`](https://spark.apache.org)).

`replyr` allows users to work with `Spark` data similar to how they work with local `data.frame`s. Some key capability gaps remedied by `replyr` include:

-   Summarizing data: `replyr_summary()`.
-   Binding tables by row: `replyr_bind_rows()`.
-   Using the split/apply/combine pattern (`dplyr::do()`): `replyr_split()`, `replyr::gapply()`.
-   Pivot/anti-pivot (`gather`/`spread`): `replyr_moveValuesToRows()`/ `replyr_moveValuesToColumns()`.
-   Parametric programming (`wrapr::let()` and `replyr::replyr_apply_f_mapped()`).
-   Handle tracking.

You may have already learned to decompose your local data processing into steps including the above, so retaining such capabilities makes working with `Spark` and [`sparklyr`](http://spark.rstudio.com) *much* easier.

Below are some examples.

------------------------------------------------------------------------

Examples
========

------------------------------------------------------------------------

``` r
base::date()
```

    ## [1] "Tue May 30 08:30:01 2017"

``` r
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.5.0'

``` r
library("tidyr")
packageVersion("tidyr")
```

    ## [1] '0.6.3'

``` r
library("replyr")
# either:
#  install.packages("replyr")
# or
#  devtools::install_github('WinVector/replyr')
packageVersion("replyr")
```

    ## [1] '0.3.902'

``` r
suppressPackageStartupMessages("spaklyr")
```

    ## [1] "spaklyr"

``` r
packageVersion("sparklyr")
```

    ## [1] '0.5.5'

``` r
sc <- sparklyr::spark_connect(version='2.0.2', 
                              master = "local")
```

`summary`
---------

Standard `summary()`, `glimpse()`, `glance()`, all fail on `Spark`.

``` r
mtcars_spark <- copy_to(sc, mtcars)

# gives summary of handle, not data
summary(mtcars_spark)
```

    ##     Length Class          Mode
    ## src 1      src_spark      list
    ## ops 3      op_base_remote list

``` r
# errors-out
glimpse(mtcars_spark)
```

    ## Observations: 32
    ## Variables: 11

    ## Error in if (width[i] <= max_width[i]) next: missing value where TRUE/FALSE needed

``` r
packageVersion("broom")
```

    ## [1] '0.4.2'

``` r
broom::glance(mtcars_spark)
```

    ## Error: glance doesn't know how to deal with data of class tbl_sparktbl_sqltbl_lazytbl

`replyr_summary` works.

``` r
replyr_summary(mtcars_spark) %>%
  select(-lexmin, -lexmax, -nunique, -index)
```

    ##    column   class nrows nna    min     max       mean          sd
    ## 1     mpg numeric    32   0 10.400  33.900  20.090625   6.0269481
    ## 2     cyl numeric    32   0  4.000   8.000   6.187500   1.7859216
    ## 3    disp numeric    32   0 71.100 472.000 230.721875 123.9386938
    ## 4      hp numeric    32   0 52.000 335.000 146.687500  68.5628685
    ## 5    drat numeric    32   0  2.760   4.930   3.596563   0.5346787
    ## 6      wt numeric    32   0  1.513   5.424   3.217250   0.9784574
    ## 7    qsec numeric    32   0 14.500  22.900  17.848750   1.7869432
    ## 8      vs numeric    32   0  0.000   1.000   0.437500   0.5040161
    ## 9      am numeric    32   0  0.000   1.000   0.406250   0.4989909
    ## 10   gear numeric    32   0  3.000   5.000   3.687500   0.7378041
    ## 11   carb numeric    32   0  1.000   8.000   2.812500   1.6152000

------------------------------------------------------------------------

`gather`/`spread`
-----------------

`tidyr` pretty much only works on local data.

``` r
mtcars2 <- mtcars %>%
  mutate(car = row.names(mtcars)) %>%
  copy_to(sc, ., 'mtcars2')

# errors out
mtcars2 %>% 
  tidyr::gather('fact', 'value')
```

    ## Error in UseMethod("gather_"): no applicable method for 'gather_' applied to an object of class "c('tbl_spark', 'tbl_sql', 'tbl_lazy', 'tbl')"

``` r
mtcars2 %>%
  replyr_moveValuesToRows(nameForNewKeyColumn= 'fact', 
                          nameForNewValueColumn= 'value', 
                          columnsToTakeFrom= colnames(mtcars),
                          nameForNewClassColumn= 'class') %>%
  arrange(car, fact)
```

    ## Source:   query [352 x 4]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 352 x 4
    ##     fact         car  value   class
    ##    <chr>       <chr>  <dbl>   <chr>
    ##  1    am AMC Javelin   0.00 numeric
    ##  2  carb AMC Javelin   2.00 numeric
    ##  3   cyl AMC Javelin   8.00 numeric
    ##  4  disp AMC Javelin 304.00 numeric
    ##  5  drat AMC Javelin   3.15 numeric
    ##  6  gear AMC Javelin   3.00 numeric
    ##  7    hp AMC Javelin 150.00 numeric
    ##  8   mpg AMC Javelin  15.20 numeric
    ##  9  qsec AMC Javelin  17.30 numeric
    ## 10    vs AMC Javelin   0.00 numeric
    ## # ... with 342 more rows

`replyr_bind_rows`
------------------

`dplyr` `bind_rows`, `union`, and `union_all` are all currently unsuitable for use on `Spark`. `replyr::replyr_union_all()` and `replyr::replyr_bind_rows()` supply working alternatives.

### `bind_rows()`

``` r
db1 <- copy_to(sc, 
               data.frame(x=1:2, y=c('a','b'), 
                          stringsAsFactors=FALSE),
               name='db1')
db2 <- copy_to(sc, 
               data.frame(y=c('c','d'), x=3:4, 
                          stringsAsFactors=FALSE),
               name='db2')

# Errors out as it tries to operate on the handles instead of the data.
bind_rows(list(db1, db2))
```

    ## Error in bind_rows_(x, .id): incompatible sizes (1 != 3)

### `union_all`

``` r
# ignores column names and converts all data to char
union_all(db1, db2)
```

    ## Source:   query [4 x 2]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 4 x 2
    ##       x     y
    ##   <chr> <chr>
    ## 1     1     a
    ## 2     2     b
    ## 3     c     3
    ## 4     d     4

### `union`

``` r
# ignores column names and converts all data to char
# also will probably lose duplicate rows
union(db1, db2)
```

    ## Source:   query [4 x 2]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 4 x 2
    ##       x     y
    ##   <chr> <chr>
    ## 1     2     b
    ## 2     c     3
    ## 3     1     a
    ## 4     d     4

### `replyr_bind_rows`

`replyr::replyr_bind_rows` can bind multiple `data.frame`s together.

``` r
replyr_bind_rows(list(db1, db2))
```

    ## Source:   query [4 x 2]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 4 x 2
    ##       x     y
    ##   <int> <chr>
    ## 1     2     b
    ## 2     1     a
    ## 3     4     d
    ## 4     3     c

`dplyr::do`
-----------

Our example is just taking a few rows from each group of a grouped data set. Note: since we are not enforcing order by an arrange we can't expect the results to always match on database or `Spark` data sources.

### `dplyr::do` on local data

From `help('do', package='dplyr')`:

``` r
by_cyl <- group_by(mtcars, cyl)
do(by_cyl, head(., 2))
```

    ## Source: local data frame [6 x 11]
    ## Groups: cyl [3]
    ## 
    ## # A tibble: 6 x 11
    ##     mpg   cyl  disp    hp  drat    wt  qsec    vs    am  gear  carb
    ##   <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl>
    ## 1  22.8     4 108.0    93  3.85 2.320 18.61     1     1     4     1
    ## 2  24.4     4 146.7    62  3.69 3.190 20.00     1     0     4     2
    ## 3  21.0     6 160.0   110  3.90 2.620 16.46     0     1     4     4
    ## 4  21.0     6 160.0   110  3.90 2.875 17.02     0     1     4     4
    ## 5  18.7     8 360.0   175  3.15 3.440 17.02     0     0     3     2
    ## 6  14.3     8 360.0   245  3.21 3.570 15.84     0     0     3     4

------------------------------------------------------------------------

### `dplyr::do` on `Spark`

``` r
by_cyl <- group_by(mtcars_spark, cyl)
do(by_cyl, head(., 2))
```

    ## # A tibble: 3 x 2
    ##     cyl     V2
    ##   <dbl> <list>
    ## 1     6 <NULL>
    ## 2     4 <NULL>
    ## 3     8 <NULL>

Notice we did not get back usable results.

### `replyr` split/apply

``` r
mtcars_spark %>%
  replyr_split('cyl', 
               partitionMethod = 'extract') %>%
  lapply(function(di) head(di, 2)) %>%
  replyr_bind_rows()
```

    ## Source:   query [6 x 11]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 6 x 11
    ##     cyl   mpg  disp    hp  drat    wt  qsec    vs    am  gear  carb
    ##   <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl>
    ## 1     6  21.0 160.0   110  3.90 2.875 17.02     0     1     4     4
    ## 2     6  21.0 160.0   110  3.90 2.620 16.46     0     1     4     4
    ## 3     8  18.7 360.0   175  3.15 3.440 17.02     0     0     3     2
    ## 4     8  14.3 360.0   245  3.21 3.570 15.84     0     0     3     4
    ## 5     4  22.8 108.0    93  3.85 2.320 18.61     1     1     4     1
    ## 6     4  24.4 146.7    62  3.69 3.190 20.00     1     0     4     2

### `replyr` `gapply`

``` r
mtcars_spark %>%
  gapply('cyl',
         partitionMethod = 'extract',
         function(di) head(di, 2))
```

    ## Source:   query [6 x 11]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 6 x 11
    ##     cyl   mpg  disp    hp  drat    wt  qsec    vs    am  gear  carb
    ##   <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl>
    ## 1     6  21.0 160.0   110  3.90 2.875 17.02     0     1     4     4
    ## 2     6  21.0 160.0   110  3.90 2.620 16.46     0     1     4     4
    ## 3     8  18.7 360.0   175  3.15 3.440 17.02     0     0     3     2
    ## 4     8  14.3 360.0   245  3.21 3.570 15.84     0     0     3     4
    ## 5     4  22.8 108.0    93  3.85 2.320 18.61     1     1     4     1
    ## 6     4  24.4 146.7    62  3.69 3.190 20.00     1     0     4     2

------------------------------------------------------------------------

`wrapr::let`
------------

`wrapr::let` allows execution of arbitrary code with substituted variable names (note this is subtly different than binding values for names as with `base::substitute` or `base::with`). This allows the user to write arbitrary `dplyr` code in the case of ["parametric variable names"](http://www.win-vector.com/blog/2016/12/parametric-variable-names-and-dplyr/) (that is when variable names are not known at coding time, but will become available later at run time as values in other variables) without directly using the `dplyr` "underbar forms" (and the direct use of `lazyeval::interp` and `.dots=stats::setNames` to use the `dplyr` "underbar forms").

Example:

``` r
library('dplyr')
```

``` r
# nice parametric function we write
ComputeRatioOfColumns <- function(d,NumeratorColumnName,DenominatorColumnName,ResultColumnName) {
  wrapr::let(
    alias=list(NumeratorColumn=NumeratorColumnName,
               DenominatorColumn=DenominatorColumnName,
               ResultColumn=ResultColumnName),
    expr={
      # (pretend) large block of code written with concrete column names.
      # due to the let wrapper in this function it will behave as if it was
      # using the specified paremetric column names.
      d %>% mutate(ResultColumn = NumeratorColumn/DenominatorColumn)
    })
}

# example data
d <- data.frame(a=1:5, b=3:7)

# example application
d %>% ComputeRatioOfColumns('a','b','c')
```

    ##   a b         c
    ## 1 1 3 0.3333333
    ## 2 2 4 0.5000000
    ## 3 3 5 0.6000000
    ## 4 4 6 0.6666667
    ## 5 5 7 0.7142857

`wrapr::let` makes construction of abstract functions over `dplyr` controlled data much easier. It is designed for the case where the "`expr`" block is large sequence of statements and pipelines.

`wrapr::let` is based on `gtools::strmacro` by Gregory R. Warnes.

`replyr::replyr_apply_f_mapped`
-------------------------------

`wrapr::let` was only the secondary proposal in the original [2016 "Parametric variable names" article](http://www.win-vector.com/blog/2016/12/parametric-variable-names-and-dplyr/). What we really wanted was a stack of views so the data pretended to have column names that matched the code (i.e., re-mapping the data, not the code).

With a bit of thought we can achieve this if we associate the data re-mapping with a function environment instead of with the data. In this design a re-mapping is active as long as a given controlling function is in control. In our case that function is `replyr::replyr_apply_f_mapped()` and works as follows:

Suppose the operation we wish to use is a rank-reducing function that has been supplied as function from somewhere else that we do not have control of (such as a package). The function could be simple such as the following, but we are going to assume we want to use it without alteration (including the without the small alteration of introducing `wrapr::let()`) because it has been supplied from external code or a package.

``` r
# an external function with hard-coded column names
DecreaseRankColumnByOne <- function(d) {
  d$RankColumn <- d$RankColumn - 1
  d
}
```

To apply this function to `d` (which doesn't have the expected column names!) we use `replyr::replyr_apply_f_mapped()` as follows:

``` r
d <- data.frame(Sepal_Length = c(5.8,5.7),
                Sepal_Width = c(4.0,4.4),
                Species = 'setosa',
                rank = c(1,2))

# map our data to expected column names so we can use function
nmap <- c(GroupColumn='Species',
          ValueColumn='Sepal_Length',
          RankColumn='rank')
print(nmap)
```

    ##    GroupColumn    ValueColumn     RankColumn 
    ##      "Species" "Sepal_Length"         "rank"

``` r
dF <- replyr::replyr_apply_f_mapped(d, DecreaseRankColumnByOne, nmap,
                                    restrictMapIn = FALSE, 
                                    restrictMapOut = FALSE)
print(dF)
```

    ##   Sepal_Length Sepal_Width Species rank
    ## 1          5.8         4.0  setosa    0
    ## 2          5.7         4.4  setosa    1

`replyr::replyr_apply_f_mapped()` renames the columns to the names expected by `DecreaseRankColumnByOne` (the mapping specified in `nmap`), applies `DecreaseRankColumnByOne`, and then inverts the mapping before returning the value. For functions that require additional arguments we suggest the usual wrapping or Currying solutions.

------------------------------------------------------------------------

Handle management
-----------------

A lot of `Spark` tasks involve creation of intermediate or temporary tables. This can be explicit (through `dplyr::copy_to()`) and implicit (through `dplyr::compute()`). These handles can represent a reference leak and eat up resources. To deal with this `replyr` supplies record-retaining temporary name generators (and uses the same internally).

For instance to join a few tables it is a good idea to call compute after each join (else the generated `SQL` can become large and unmanageable). This sort of code looks like the following:

``` r
# create example data
names <- paste('table', 1:5, sep='_')
tables <- lapply(names, 
                 function(ni) {
                   di <- data.frame(key= 1:3)
                   di[[paste('val',ni,sep='_')]] <- runif(nrow(di))
                   copy_to(sc, di, ni)
                 })

# build our temp name generator
tmpNamGen <- replyr::makeTempNameGenerator('JOINTMP')
# left join the tables in sequence
joined <- tables[[1]]
for(i in seq(2,length(tables))) {
  ti <- tables[[i]]
  if(i<length(tables)) {
    joined <- compute(left_join(joined, ti, by='key'),
                    name= tmpNamGen())
  } else {
    joined <- compute(left_join(joined, ti, by='key'),
                    name= 'joinres')
  }
}

# clean up temps
temps <- tmpNamGen(dumpList = TRUE)
print(temps)
```

    ## [1] "JOINTMP_veALtgz1mIxe8uiKo5eA_00000"
    ## [2] "JOINTMP_veALtgz1mIxe8uiKo5eA_00001"
    ## [3] "JOINTMP_veALtgz1mIxe8uiKo5eA_00002"

``` r
for(ti in temps) {
  db_drop_table(sc, ti)
}

# show result
print(joined)
```

    ## Source:   query [3 x 6]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 3 x 6
    ##     key val_table_1 val_table_2 val_table_3 val_table_4 val_table_5
    ##   <int>       <dbl>       <dbl>       <dbl>       <dbl>       <dbl>
    ## 1     1  0.06867673   0.9122907   0.9919031   0.6748867   0.8373639
    ## 2     2  0.50676554   0.2801610   0.7070883   0.7734393   0.9625326
    ## 3     3  0.73922930   0.8049749   0.9540539   0.7294797   0.6902958

Careful introduction and management of materialized intermediates can conserve resources and greatly improve outcomes.

------------------------------------------------------------------------

Conclusion
==========

If you are serious about `R` controlled data processing in `Spark` you should seriously consider using `replyr` in addition to [`dplyr`](https://CRAN.R-project.org/package=dplyr) and `sparklyr`.

Be aware of the functionality we demonstrated depends on using the development version of `replyr`. Though we will, of course, advance the CRAN version as soon as practical. `replyr` is by design a "sits on top" or "pure `R`" package, that is it doesn't directly introduce any `C++`, cross-language calling, or network interfaces itself (leaving that to `dplyr`, `dbplyr`, and `sparklyr`). This means `replyr` builds up complex functionality we want in terms of functionality already exposed by other packages.

This also means if we see a *non*-`R` exception such as the following:

``` r
 *** caught segfault ***
address 0x0, cause 'unknown'

Traceback:
 1: r_replyr_bind_rows(lst, colnames, tempNameGenerator)
```

That while this *may* indicate an issue in `replyr` it likely indicates an issue in `R` or one of the called packages that is directly working with non-`R` resources.

Note: all of the above was demonstrated using the released CRAN 0.5.0 version of `dplyr` not the (2017-05-30) [0.6.0 release candidate development version of `dplyr`](https://github.com/tidyverse/dplyr/commit/c7ca37436c140173a3bf0e7f15d55b604b52c0b4). The assumption is that *some* of the work-arounds may become less necessary as we go forward (`glimpse()` and `glance()` in particular are likely to pick up `Spark` capabilities). We kept with the 0.5.0 production `dplyr` as our experience is: the 0.6.0 version does not currently fully inter-operate with the [CRAN released version of `sparklyr` (0.5.5 2017-05-26)](https://CRAN.R-project.org/package=sparklyr) and other database sources (please see [here](https://github.com/tidyverse/dplyr/issues/2825), [here](https://github.com/tidyverse/dplyr/issues/2823), and [here](https://github.com/tidyverse/dplyr/issues/2776) for some of the known issues). While the [current development version of `sparklyr`](https://github.com/rstudio/sparklyr/commit/d981cd54326b5663b7311d5f30adeec68dacd1fe) does incorporate some improvements, it does not appear to be specially marked or tagged as release candidate.

I'll probably re-run this worksheet after these packages get new CRAN releases.

------------------------------------------------------------------------

``` r
sparklyr::spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  795353 42.5    1442291 77.1  1168576 62.5
    ## Vcells 1452284 11.1    2552219 19.5  1916751 14.7
