<!-- README.md is generated from README.Rmd. Please edit that file -->
When using `R` to work over a big data system (such as `Spark`) much of your work is over "data handles" and not actual data (data handles are objects that control access to remote data).

Data handles are a lot like sockets or file-handles in that they can not be safely serialized and restored (i.e., you can not save them into a `.RDS` file and then restore them into another session). This means when you are starting or re-starting a project you must "ready" all of your data references. Your projects will be much easier to manage and document if you load your references using the methods we show below.

Let's set-up our example `Spark` cluster:

``` r
library("sparklyr")
#packageVersion('sparklyr')
suppressPackageStartupMessages(library("dplyr"))
#packageVersion('dplyr')
suppressPackageStartupMessages(library("tidyr"))

# Please see the following video for installation help
#  https://youtu.be/qnINvPqcRvE
# spark_install(version = "2.0.2")

# set up a local "practice" Spark instance
sc <- spark_connect(master = "local",
                    version = "2.0.2")
#print(sc)
```

Data is much easier to manage than code, and much easier to compute over. So the more information you can keep as pure data the better off you will be. In this case we are loading the chosen names and paths of `parquet` data we wish to work with from an external file that is easy for the user to edit.

``` r
# Read user's specification of files and paths.
userSpecification <- read.csv('tableCollection.csv',
                             header = TRUE,
                 strip.white = TRUE,
                 stringsAsFactors = FALSE)
print(userSpecification)
```

    ##   tableName tablePath
    ## 1   data_01   data_01
    ## 2   data_02   data_02
    ## 3   data_03   data_03

We can now read these `parquet` files (usually stored in `Hadoop`) into our `Spark` environment as follows.

``` r
readParquets <- function(userSpecification) {
  userSpecification <- as_data_frame(userSpecification)
  userSpecification$handle <- lapply(
    seq_len(nrow(userSpecification)),
    function(i) {
      spark_read_parquet(sc, 
                         name = userSpecification$tableName[[i]], 
                         path = userSpecification$tablePath[[i]])
    }
  )
  userSpecification
}

tableCollection <- readParquets(userSpecification)
print(tableCollection)
```

    ## # A tibble: 3 x 3
    ##   tableName tablePath          handle
    ##       <chr>     <chr>          <list>
    ## 1   data_01   data_01 <S3: tbl_spark>
    ## 2   data_02   data_02 <S3: tbl_spark>
    ## 3   data_03   data_03 <S3: tbl_spark>

A `data.frame` is a great place to keep what you know about your `Spark` handles in one place. Let's add some details to our `Spark` handles.

``` r
addDetails <- function(tableCollection) {
  tableCollection <- as_data_frame(tableCollection)
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

tableCollection <- addDetails(userSpecification)

# convenient printing
print(tableCollection)
```

    ## # A tibble: 3 x 5
    ##   tableName tablePath          handle  nrow  ncol
    ##       <chr>     <chr>          <list> <dbl> <dbl>
    ## 1   data_01   data_01 <S3: tbl_spark>    10     1
    ## 2   data_02   data_02 <S3: tbl_spark>    10     2
    ## 3   data_03   data_03 <S3: tbl_spark>    10     3

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

A particularly slick trick is to expand the columns column into a taller table that allows us to quickly identify which columns are in which tables.

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

The idea is: place all of the above functions into a shared script or package, and then use them to organize loading your `Spark` data references. With this practice you will have much less "spaghetti code", better document intent, and have a versatile workflow.

The principles we are using are:

-   Keep configuration out of code (i.e., maintain the file list in a spreadsheet). This makes working with others much easier.
-   Treat configuration as data (i.e., make sure the configuration is a nice regular table so that you can use `R` tools such as `tidyr::unnest()` to work with it).

``` r
spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  672653   36    1168576 62.5  1168576 62.5
    ## Vcells 1171890    9    2060183 15.8  1406471 10.8
