<!-- README.md is generated from README.Rmd. Please edit that file -->
``` r
library("sparklyr")
#packageVersion('sparklyr')
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
#packageVersion('dplyr')
library("tidyr")

# Please see the following video for installation help
#  https://youtu.be/qnINvPqcRvE
# spark_install(version = "2.1.0")

# set up a local "practice" Spark instance
sc <- spark_connect(master = "local",
                    version = "2.1.0")
#print(sc)
```

``` r
# build notional data, but do not
# leave it in the system (so we can
# demonstrate loading).
tableNames <- vapply(1:3,
                function(i) {
                  di <- data.frame(x= runif(10))
                  colnames(di) <- letters[[1]]
                  for(j in seq_len(i-1)) {
                    di[[letters[[j+1]]]] <- runif(nrow(di))
                  }
                  colnames(di) <-
                    paste(colnames(di),
                          sprintf("%02d", i), 
                          sep='_')
                  ni <- paste('data',
                              sprintf("%02d", i),
                              sep='_')
                  hi <- copy_to(sc, di, 
                                name= ni,
                                overwrite= TRUE)
                  spark_write_parquet(hi, path= ni)
                  dplyr::db_drop_table(sc, ni)
                  ni
                },
                character(1))
```

``` r
# load the parquet files to register them
# to the Spark cluster.
# Could keep handles at this point, 
#  or get them with:
#   DBI::dbListTables(sc)/dplyr::tbl(sc, tableNamei)
tableCollection <- data_frame(tableName= tableNames)
tableCollection$handle <- lapply(
  tableCollection$tableName,
  function(tableNamei) {
    spark_read_parquet(sc, tableNamei, tableNamei)
  }
)
```

``` r
# or if we want to grab all tables
# sparklyr already knows about:
tableCollection <- data_frame(tableName = DBI::dbListTables(sc))
tableCollection$handle <-
  lapply(tableCollection$tableName,
         function(tableNamei) {
          dplyr::tbl(sc, tableNamei)
         })
```

``` r
# convenient printing
print(tableCollection)
```

    ## # A tibble: 3 × 2
    ##   tableName          handle
    ##       <chr>          <list>
    ## 1   data_01 <S3: tbl_spark>
    ## 2   data_02 <S3: tbl_spark>
    ## 3   data_03 <S3: tbl_spark>

``` r
# and tableNames to handles for convenience
names(tableCollection$handle) <-
  tableCollection$tableName

# look at the top of each table (also forces
# evaluation!).
lapply(tableCollection$handle, 
       head)
```

    ## $data_01
    ## Source:   query [6 x 1]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##         a_01
    ##        <dbl>
    ## 1 0.53031902
    ## 2 0.81205617
    ## 3 0.96298460
    ## 4 0.56292297
    ## 5 0.08646447
    ## 6 0.63204431
    ## 
    ## $data_02
    ## Source:   query [6 x 2]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##        a_02        b_02
    ##       <dbl>       <dbl>
    ## 1 0.6078470 0.336698420
    ## 2 0.9288143 0.835399110
    ## 3 0.9247622 0.102489387
    ## 4 0.8188444 0.857938155
    ## 5 0.5263422 0.369312502
    ## 6 0.3566867 0.007589028
    ## 
    ## $data_03
    ## Source:   query [6 x 3]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##         a_03       b_03       c_03
    ##        <dbl>      <dbl>      <dbl>
    ## 1 0.92620037 0.12823404 0.15106311
    ## 2 0.99075185 0.04795382 0.09637433
    ## 3 0.10495406 0.87920848 0.10943815
    ## 4 0.05829383 0.88589079 0.83802477
    ## 5 0.18510065 0.28034014 0.57139770
    ## 6 0.22895962 0.01881221 0.73205577

``` r
# get dimensions of each table
lapply(tableCollection$handle, 
       dim)
```

    ## $data_01
    ## [1] 10  1
    ## 
    ## $data_02
    ## [1] 10  2
    ## 
    ## $data_03
    ## [1] 10  3

``` r
tableCollection$column <- 
  lapply(tableCollection$handle,
         colnames)

# tidyr ‘0.6.1’ help(unnest) says:
# "Each row must have the same number of entries."
# but that seem not to be an actual constraint.
columnMap <- tableCollection %>% 
  select(tableName, column) %>%
  unnest(column)
print(columnMap)
```

    ## # A tibble: 6 × 2
    ##   tableName column
    ##       <chr>  <chr>
    ## 1   data_01   a_01
    ## 2   data_02   a_02
    ## 3   data_02   b_02
    ## 4   data_03   a_03
    ## 5   data_03   b_03
    ## 6   data_03   c_03

``` r
# we have experimental support for expanding columns 
# in the dev version of replyr
# https://github.com/WinVector/replyr
if(requireNamespace('replyr', quietly = TRUE)) {
  if(exists('expandColumn', 
            where= asNamespace('replyr'), 
            mode='function')) {
    tableCollection %>% 
      select(tableName, column) %>%
      replyr::expandColumn('column',
                           rowidSource= 'tableName',
                           idxDest= 'columnNumber')
  }
}
```

    ## # A tibble: 6 × 3
    ##   tableName columnNumber column
    ##       <chr>        <int>  <chr>
    ## 1   data_01            1   a_01
    ## 2   data_02            1   a_02
    ## 3   data_02            2   b_02
    ## 4   data_03            1   a_03
    ## 5   data_03            2   b_03
    ## 6   data_03            3   c_03

``` r
spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##          used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells 525036 28.1     940480 50.3   750400 40.1
    ## Vcells 720384  5.5    1308461 10.0   928517  7.1
