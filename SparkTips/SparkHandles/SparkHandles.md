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
    ## 1 0.17158271
    ## 2 0.13397375
    ## 3 0.02972442
    ## 4 0.48990982
    ## 5 0.83161956
    ## 6 0.46294927
    ## 
    ## $data_02
    ## Source:   query [6 x 2]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##         a_02      b_02
    ##        <dbl>     <dbl>
    ## 1 0.96522497 0.3531768
    ## 2 0.34316774 0.4826805
    ## 3 0.95103905 0.7627694
    ## 4 0.74743734 0.6508688
    ## 5 0.05248657 0.4758940
    ## 6 0.61457383 0.1363878
    ## 
    ## $data_03
    ## Source:   query [6 x 3]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##        a_03      b_03       c_03
    ##       <dbl>     <dbl>      <dbl>
    ## 1 0.6672825 0.1711225 0.96934094
    ## 2 0.1435421 0.1724123 0.53129371
    ## 3 0.7949332 0.8072997 0.05173393
    ## 4 0.2137769 0.8585870 0.28063665
    ## 5 0.5197736 0.2449442 0.57633105
    ## 6 0.2170971 0.9882924 0.51546109

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
    ## Ncells 524488 28.1     940480 50.3   750400 40.1
    ## Vcells 719768  5.5    1308461 10.0   928517  7.1
