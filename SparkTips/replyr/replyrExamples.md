<!-- README.md is generated from README.Rmd. Please edit that file -->
Why `replyr`
============

`replyr` stands for **RE**mote **PLY**ing of big data for **R**.

Why should [R](https://www.r-project.org) users try [`replyr`](https://CRAN.R-project.org/package=replyr)? Because it lets you take a number of common working patterns and apply them to remote data (such as databases or [`Spark`](https://spark.apache.org)).

`replyr` allows users to work with `Spark` or database data similar to how they work with local `data.frame`s. Some key capability gaps remedied by `replyr` include:

-   Summarizing data: `replyr_summary()`.
-   Combining tables: `replyr_union_all()`.
-   Binding tables by row: `replyr_bind_rows()`.
-   Using the split/apply/combine pattern (`dplyr::do()`): `replyr_split()`, `replyr::gapply()`.
-   Pivot/anti-pivot (`gather`/`spread`): `replyr_moveValuesToRows()`/ `replyr_moveValuesToColumns()`.
-   [Handle tracking](http://www.win-vector.com/blog/2017/06/managing-intermediate-results-when-using-rsparklyr/).
-   A [join controller](http://www.win-vector.com/blog/2017/06/use-a-join-controller-to-document-your-work/).

You may have already learned to decompose your local data processing into steps including the above, so retaining such capabilities makes working with `Spark` and [`sparklyr`](http://spark.rstudio.com) *much* easier. Some of the above capabilities will [likely come to the `tidyverse`](https://github.com/tidyverse/dplyr/issues/2923), but the above implementations are build purely on top of `dplyr` and are the ones [already being vetted and debugged](https://github.com/rstudio/sparklyr/issues/783) at production scale (I think these will be ironed out and reliable sooner).

[`replyr`](https://github.com/WinVector/replyr) is the product of collecting experience applying `R` at production scale with many clients, collecting issues and filling-in gaps.

Below are some examples.

------------------------------------------------------------------------

Examples
========

------------------------------------------------------------------------

Things are changing fast right now, so let's use the development versions of the packages for our examples.

``` r
base::date()
```

    ## [1] "Thu Jul  6 15:48:14 2017"

``` r
# devtools::install_github('rstudio/sparklyr')
# devtools::install_github('tidyverse/dplyr')
# devtools::install_github('tidyverse/dbplyr')
# devtools::install_github('WinVector/replyr')
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.7.1.9000'

``` r
packageVersion("dbplyr")
```

    ## [1] '1.1.0.9000'

``` r
library("tidyr")
packageVersion("tidyr")
```

    ## [1] '0.6.3'

``` r
library("replyr")
packageVersion("replyr")
```

    ## [1] '0.4.2'

``` r
suppressPackageStartupMessages(library("sparklyr"))
packageVersion("sparklyr")
```

    ## [1] '0.5.6.9010'

``` r
# more memory as suggested in https://github.com/rstudio/sparklyr/issues/783
config <- spark_config()
config[["sparklyr.shell.driver-memory"]] <- "8G"
sc <- sparklyr::spark_connect(version='2.1.0', 
                              hadoop_version = '2.7',
                              master = "local",
                              config = config)
```

`summary`
---------

Standard `summary()` and `glance()`, all fail on `Spark`.

``` r
mtcars_spark <- copy_to(sc, mtcars)

# gives summary of handle, not data
summary(mtcars_spark)
```

    ##     Length Class          Mode
    ## src 1      src_spark      list
    ## ops 2      op_base_remote list

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

    ## # Source:     lazy query [?? x 4]
    ## # Database:   spark_connection
    ## # Ordered by: car, fact
    ##            car  fact  value   class
    ##          <chr> <chr>  <dbl>   <chr>
    ##  1 AMC Javelin    am   0.00 numeric
    ##  2 AMC Javelin  carb   2.00 numeric
    ##  3 AMC Javelin   cyl   8.00 numeric
    ##  4 AMC Javelin  disp 304.00 numeric
    ##  5 AMC Javelin  drat   3.15 numeric
    ##  6 AMC Javelin  gear   3.00 numeric
    ##  7 AMC Javelin    hp 150.00 numeric
    ##  8 AMC Javelin   mpg  15.20 numeric
    ##  9 AMC Javelin  qsec  17.30 numeric
    ## 10 AMC Javelin    vs   0.00 numeric
    ## # ... with 342 more rows

Binding rows
------------

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

    ## Error in bind_rows_(x, .id): Argument 1 must be a data frame or a named atomic vector, not a tbl_spark/tbl_sql/tbl_lazy/tbl

### `union_all`

``` r
# ignores column names and converts all data to char
union_all(db1, db2)
```

    ## # Source:   lazy query [?? x 2]
    ## # Database: spark_connection
    ##       x     y
    ##   <int> <chr>
    ## 1     1     a
    ## 2     2     b
    ## 3     3     c
    ## 4     4     d

### `union`

``` r
# ignores column names and converts all data to char
# also will probably lose duplicate rows
union(db1, db2)
```

    ## # Source:   lazy query [?? x 2]
    ## # Database: spark_connection
    ##       x     y
    ##   <int> <chr>
    ## 1     4     d
    ## 2     1     a
    ## 3     3     c
    ## 4     2     b

### `replyr_bind_rows`

`replyr::replyr_bind_rows` can bind multiple `data.frame`s together.

``` r
replyr_bind_rows(list(db1, db2))
```

    ## # Source:   table<sparklyr_tmp_2b792efdb85e> [?? x 2]
    ## # Database: spark_connection
    ##       x     y
    ##   <int> <chr>
    ## 1     1     a
    ## 2     2     b
    ## 3     3     c
    ## 4     4     d

`dplyr::do`
-----------

Our example is just taking a few rows from each group of a grouped data set. Note: since we are not enforcing order by an arrange we can't expect the results to always match on database or `Spark` data sources.

### `dplyr::do` on local data

From `help('do', package='dplyr')`:

``` r
by_cyl <- group_by(mtcars, cyl)
do(by_cyl, head(., 2))
```

    ## # A tibble: 6 x 11
    ## # Groups:   cyl [3]
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

    ## # Source:   table<sparklyr_tmp_2b7956481634> [?? x 11]
    ## # Database: spark_connection
    ##     mpg   cyl  disp    hp  drat    wt  qsec    vs    am  gear  carb
    ##   <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl>
    ## 1  21.0     6 160.0   110  3.90 2.620 16.46     0     1     4     4
    ## 2  21.0     6 160.0   110  3.90 2.875 17.02     0     1     4     4
    ## 3  22.8     4 108.0    93  3.85 2.320 18.61     1     1     4     1
    ## 4  24.4     4 146.7    62  3.69 3.190 20.00     1     0     4     2
    ## 5  18.7     8 360.0   175  3.15 3.440 17.02     0     0     3     2
    ## 6  14.3     8 360.0   245  3.21 3.570 15.84     0     0     3     4

### `replyr` `gapply`

``` r
mtcars_spark %>%
  gapply('cyl',
         partitionMethod = 'extract',
         function(di) head(di, 2))
```

    ## # Source:   table<sparklyr_tmp_2b7969b619fa> [?? x 11]
    ## # Database: spark_connection
    ##     mpg   cyl  disp    hp  drat    wt  qsec    vs    am  gear  carb
    ##   <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl> <dbl>
    ## 1  21.0     6 160.0   110  3.90 2.620 16.46     0     1     4     4
    ## 2  21.0     6 160.0   110  3.90 2.875 17.02     0     1     4     4
    ## 3  22.8     4 108.0    93  3.85 2.320 18.61     1     1     4     1
    ## 4  24.4     4 146.7    62  3.69 3.190 20.00     1     0     4     2
    ## 5  18.7     8 360.0   175  3.15 3.440 17.02     0     0     3     2
    ## 6  14.3     8 360.0   245  3.21 3.570 15.84     0     0     3     4

`replyr::replyr_apply_f_mapped`
-------------------------------

[`wrapr::let`](http://www.win-vector.com/blog/2017/06/please-consider-using-wraprlet-for-replacement-tasks/) was only the secondary proposal in the original [2016 "Parametric variable names" article](http://www.win-vector.com/blog/2016/12/parametric-variable-names-and-dplyr/). What we really wanted was a stack of view so the data pretended to have names that matched the code (i.e., re-mapping the data, not the code).

With a bit of thought we can achieve this if we associate the data re-mapping with a function environment instead of with the data. So a re-mapping is active as long as a given controlling function is in control. In our case that function is `replyr::replyr_apply_f_mapped()` and works as follows:

Suppose the operation we wish to use is a rank-reducing function that has been supplied as function from somewhere else that we do not have control of (such as a package). The function could be simple such as the following, but we are going to assume we want to use it without alteration (including the without the small alteration of introducing `wrapr::let()`).

``` r
# an external function with hard-coded column names
DecreaseRankColumnByOne <- function(d) {
  d$RankColumn <- d$RankColumn - 1
  d
}
```

To apply this function to `d` (which doesn't have the expected column names!) we use `replyr::replyr_apply_f_mapped()` to create a new parameterized adapter as follows:

``` r
# our data
d <- data.frame(Sepal_Length = c(5.8,5.7),
                Sepal_Width = c(4.0,4.4),
                Species = 'setosa',
                rank = c(1,2))

# a wrapper to introduce parameters
DecreaseRankColumnByOneNamed <- function(d, ColName) {
  replyr::replyr_apply_f_mapped(d, 
                                f = DecreaseRankColumnByOne, 
                                nmap = c(RankColumn = ColName),
                                restrictMapIn = FALSE, 
                                restrictMapOut = FALSE)
}

# use
dF <- DecreaseRankColumnByOneNamed(d, 'rank')
print(dF)
```

    ##   Sepal_Length Sepal_Width Species rank
    ## 1          5.8         4.0  setosa    0
    ## 2          5.7         4.4  setosa    1

`replyr::replyr_apply_f_mapped()` renames the columns to the names expected by `DecreaseRankColumnByOne` (the mapping specified in `nmap`), applies `DecreaseRankColumnByOne`, and then inverts the mapping before returning the value.

------------------------------------------------------------------------

Handle management
-----------------

Many [`Sparklyr`](https://CRAN.R-project.org/package=sparklyr) tasks involve creation of intermediate or temporary tables. This can be through `dplyr::copy_to()` and through `dplyr::compute()`. These handles can represent a reference leak and eat up resources.

To help control handle lifetime the [`replyr`](https://CRAN.R-project.org/package=replyr) supplies handle trackers: record-retaining temporary name generators (and uses the same internally).

The actual function is pretty simple:

``` r
print(replyr::makeTempNameGenerator)
```

    ## function(prefix,
    ##                                   suffix= NULL) {
    ##   force(prefix)
    ##   if((length(prefix)!=1)||(!is.character(prefix))) {
    ##     stop("repyr::makeTempNameGenerator prefix must be a string")
    ##   }
    ##   if(is.null(suffix)) {
    ##     alphabet <- c(letters, toupper(letters), as.character(0:9))
    ##     suffix <- paste(base::sample(alphabet, size=20, replace= TRUE),
    ##                     collapse = '')
    ##   }
    ##   count <- 0
    ##   nameList <- list()
    ##   function(..., peek=FALSE, dumpList=FALSE, remove=NULL) {
    ##     if(length(list(...))>0) {
    ##       stop("replyr::makeTempNameGenerator tempname generate unexpected argument")
    ##     }
    ##     if(peek) {
    ##       return(names(nameList))
    ##     }
    ##     if(dumpList) {
    ##       v <- names(nameList)
    ##       nameList <<- list()
    ##       return(v)
    ##     }
    ##     if(!is.null(remove)) {
    ##       victims <- intersect(remove, names(nameList))
    ##       # this removes from lists
    ##       nameList[victims] <<- NULL
    ##       return(victims)
    ##     }
    ##     nm <- paste(prefix, suffix, sprintf('%010d',count), sep='_')
    ##     nameList[[nm]] <<- 1
    ##     count <<- count + 1
    ##     nm
    ##   }
    ## }
    ## <bytecode: 0x7fe3c88e7c30>
    ## <environment: namespace:replyr>

For instance to join a few tables it can be a good idea to call `compute` after each join for some data sources (else the generated `SQL` can become large and unmanageable). This sort of code looks like the following:

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
    # use non-temp name.
    joined <- compute(left_join(joined, ti, by='key'),
                    name= 'joinres')
  }
}

# clean up temps
temps <- tmpNamGen(dumpList = TRUE)
print(temps)
```

    ## [1] "JOINTMP_4xglKPvPg2RJ1JA2ThLf_0000000000"
    ## [2] "JOINTMP_4xglKPvPg2RJ1JA2ThLf_0000000001"
    ## [3] "JOINTMP_4xglKPvPg2RJ1JA2ThLf_0000000002"

``` r
for(ti in temps) {
  db_drop_table(sc, ti)
}

# show result
print(joined)
```

    ## # Source:   table<joinres> [?? x 6]
    ## # Database: spark_connection
    ##     key val_table_1 val_table_2 val_table_3 val_table_4 val_table_5
    ##   <int>       <dbl>       <dbl>       <dbl>       <dbl>       <dbl>
    ## 1     1   0.5586028   0.4997214  0.04852155   0.3198434   0.2351943
    ## 2     2   0.9288834   0.1207228  0.35252830   0.3176549   0.3150845
    ## 3     3   0.7160899   0.4654108  0.12161589   0.4482528   0.1583011

Careful introduction and management of materialized intermediates can conserve resources (both time and space) and greatly improve outcomes. We feel it is a good practice to set up an explicit temp name manager, pass it through all your `Sparklyr` transforms, and then clear temps in batches after the results no longer depend on the intermediates.

------------------------------------------------------------------------

Conclusion
==========

If you are serious about `R` controlled data processing in `Spark` or databases you should seriously consider using `replyr` in addition to [`dplyr`](https://CRAN.R-project.org/package=dplyr) and `sparklyr`.

``` r
sparklyr::spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  835835 44.7    1442291 77.1  1442291 77.1
    ## Vcells 1571628 12.0    2552219 19.5  1978666 15.1
