This R-markdown sheet is the accompanying material for the following article: [Managing Spark data handles in R](http://www.win-vector.com/blog/2017/05/managing-spark-data-handles-in-r/).

<!-- README.md is generated from README.Rmd. Please edit that file -->
When working with big data with <a href="https://cran.r-project.org"><code>R</code></a> (say, <a href="https://github.com/WinVector/BigDataRStrata2017">using <code>Spark</code> and <code>sparklyr</code></a>) we have found it very convenient to keep data handles in a neat list or <code>data\_frame</code>.

Please read on for our handy hints on keeping your data handles neat.

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
  # add columns
  tableCollection$columns <- 
    lapply(tableCollection$handle,
           colnames)
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

    ## # A tibble: 3 x 6
    ##   tableName tablePath          handle   columns  nrow  ncol
    ##       <chr>     <chr>          <list>    <list> <dbl> <dbl>
    ## 1   data_01   data_01 <S3: tbl_spark> <chr [1]>    10     1
    ## 2   data_02   data_02 <S3: tbl_spark> <chr [2]>    10     2
    ## 3   data_03   data_03 <S3: tbl_spark> <chr [3]>    10     3

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
    ## 1 0.8381920
    ## 2 0.2152265
    ## 3 0.4796763
    ## 4 0.7895052
    ## 5 0.5568411
    ## 6 0.2292427
    ## 
    ## $data_02
    ## Source:   query [6 x 2]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 6 x 2
    ##         a_02      b_02
    ##        <dbl>     <dbl>
    ## 1 0.05961048 0.4676490
    ## 2 0.05157383 0.6068933
    ## 3 0.34839793 0.5738879
    ## 4 0.89676677 0.2294701
    ## 5 0.82129695 0.9208848
    ## 6 0.64586787 0.9176204
    ## 
    ## $data_03
    ## Source:   query [6 x 3]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 6 x 3
    ##         a_03       b_03      c_03
    ##        <dbl>      <dbl>     <dbl>
    ## 1 0.32545825 0.06744048 0.6493902
    ## 2 0.49768306 0.74133497 0.5790545
    ## 3 0.02933889 0.18580778 0.1952033
    ## 4 0.57943442 0.54503462 0.6997693
    ## 5 0.02982490 0.91786826 0.4519192
    ## 6 0.30321291 0.77739097 0.6126401

A particularly slick trick is to expand the columns column into a taller table that allows us to quickly identify which columns are in which tables.

``` r
expandColumns <- function(tableCollection) {
  columnMap <- tableCollection %>% 
    select(tableName, columns) %>%
    unnest(columns)
  columnMap
}

columnMap <- expandColumns(tableCollection)
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
# replyr equivilent (dev version)
tableCollection %>% 
  select(tableName, columns) %>% 
  replyr::expandColumn(colName = 'columns',
                       idxDest = 'columnNumer')
```

    ## # A tibble: 6 x 3
    ##   tableName columnNumer columns
    ##       <chr>       <int>   <chr>
    ## 1   data_01           1    a_01
    ## 2   data_02           1    a_02
    ## 3   data_02           2    b_02
    ## 4   data_03           1    a_03
    ## 5   data_03           2    b_03
    ## 6   data_03           3    c_03

The idea is: place all of the above functions into a shared script or package, and then use them to organize loading your `Spark` data references. With this practice you will have much less "spaghetti code", better document intent, and have a versatile workflow.

The principles we are using include:

-   Keep configuration out of code (i.e., maintain the file list in a spreadsheet). This makes working with others much easier.
-   Treat configuration as data (i.e., make sure the configuration is a nice regular table so that you can use `R` tools such as `tidyr::unnest()` to work with it).

``` r
spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  682237 36.5    1168576 62.5  1168576 62.5
    ## Vcells 1197179  9.2    2060183 15.8  1476115 11.3
