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
# spark_install(version = "2.0.2")

# set up a local "practice" Spark instance
sc <- spark_connect(master = "local",
                    version = "2.0.2")
#print(sc)
```

``` r
tableNames <- c("data_01", "data_02", "data_03")

# load the parquet files to register them
# to the Spark cluster.
# Could keep handles at this point, 
#  or get them with:
#   DBI::dbListTables(sc)/dplyr::tbl(sc, tableNamei)

readParquets <- function(tableNames) {
  tableCollection <- data_frame(tableName= tableNames)
  tableCollection$handle <- lapply(
    tableCollection$tableName,
    function(tableNamei) {
      spark_read_parquet(sc, tableNamei, tableNamei)
    }
  )
  tableCollection
}

tableCollection <- readParquets(tableNames)
print(tableCollection)
```

    ## # A tibble: 3 x 2
    ##   tableName          handle
    ##       <chr>          <list>
    ## 1   data_01 <S3: tbl_spark>
    ## 2   data_02 <S3: tbl_spark>
    ## 3   data_03 <S3: tbl_spark>

``` r
# or if we want to grab all tables
# sparklyr already knows about (note this can be expensive!):
tableNames <- DBI::dbListTables(sc)
```

A `data.frame` is a great place to keep what you know about your `Spark` handles in one place. Let's add some details.

``` r
addDetails <- function(tableNames) {
  tableCollection <- data_frame(tableName = tableNames)
  
  # get the references
  tableCollection$handle <-
    lapply(tableCollection$tableName,
           function(tableNamei) {
             dplyr::tbl(sc, tableNamei)
           })
  
  # and tableNames to handles for convenience
  # and printing
  names(tableCollection$handle) <-
    tableCollection$tableName
  
  # add in some details (note: nrow can be expensive)
  tableCollection$nrow <- vapply(tableCollection$handle, 
                                 nrow, 
                                 numeric(1))
  tableCollection$ncol <- vapply(tableCollection$handle, 
                                 ncol, 
                                 numeric(1))
  tableCollection
}

tableCollection <- addDetails(tableNames)

# convenient printing
print(tableCollection)
```

    ## # A tibble: 3 x 4
    ##   tableName          handle  nrow  ncol
    ##       <chr>          <list> <dbl> <dbl>
    ## 1   data_01 <S3: tbl_spark>    10     1
    ## 2   data_02 <S3: tbl_spark>    10     2
    ## 3   data_03 <S3: tbl_spark>    10     3

``` r
# look at the top of each table (also forces
# evaluation!).
lapply(tableCollection$handle, 
       head)
```

    ## $data_01
    ## Source:   query [6 x 1]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 6 x 1
    ##        a_01
    ##       <dbl>
    ## 1 0.8274947
    ## 2 0.2876151
    ## 3 0.6638404
    ## 4 0.1918336
    ## 5 0.9111187
    ## 6 0.8802026
    ## 
    ## $data_02
    ## Source:   query [6 x 2]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 6 x 2
    ##        a_02       b_02
    ##       <dbl>      <dbl>
    ## 1 0.3937457 0.34936496
    ## 2 0.0195079 0.74376380
    ## 3 0.9760512 0.00261368
    ## 4 0.4388773 0.70325800
    ## 5 0.9747534 0.40327283
    ## 6 0.6054003 0.53224218
    ## 
    ## $data_03
    ## Source:   query [6 x 3]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 6 x 3
    ##         a_03      b_03        c_03
    ##        <dbl>     <dbl>       <dbl>
    ## 1 0.59512263 0.2615939 0.592753768
    ## 2 0.72292799 0.7287428 0.003926143
    ## 3 0.51846687 0.3641869 0.874463146
    ## 4 0.01174093 0.9648346 0.177722575
    ## 5 0.86250126 0.3891915 0.857614579
    ## 6 0.33082723 0.2633013 0.233822140

``` r
columnDictionary <- function(tableCollection) {
  tableCollection$columns <- 
    lapply(tableCollection$handle,
           colnames)
  
  columnMap <- tableCollection %>% 
    select(tableName, columns) %>%
    unnest(columns)
  columnMap
}

columnMap <- columnDictionary(tableCollection)
print(columnMap)
```

    ## # A tibble: 6 x 2
    ##   tableName columns
    ##       <chr>   <chr>
    ## 1   data_01    a_01
    ## 2   data_02    a_02
    ## 3   data_02    b_02
    ## 4   data_03    a_03
    ## 5   data_03    b_03
    ## 6   data_03    c_03

``` r
# do not save handles, they are not really re-loadable
# in all situations.
saveRDS(tableCollection, 
        file='tableCollectionWrong.RDS')
```

``` r
# save as CSV so users can edit it.
# re-derive all other columns later.
write.csv(tableCollection[ ,'tableName', drop=FALSE], 
          quote= FALSE,
          row.names = FALSE,
          file='tableCollection.csv')
```

``` r
spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  666977 35.7    1168576 62.5  1168576 62.5
    ## Vcells 1158507  8.9    2060183 15.8  1390899 10.7
