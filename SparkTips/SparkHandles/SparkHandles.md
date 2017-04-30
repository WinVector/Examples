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
    ## 1 0.49587995
    ## 2 0.52825684
    ## 3 0.67778846
    ## 4 0.16127533
    ## 5 0.04035134
    ## 6 0.87350050
    ## 
    ## $data_02
    ## Source:   query [6 x 2]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##        a_02       b_02
    ##       <dbl>      <dbl>
    ## 1 0.3679410 0.62483751
    ## 2 0.6697498 0.29327292
    ## 3 0.8637405 0.05334572
    ## 4 0.7298208 0.50183116
    ## 5 0.4254752 0.69691922
    ## 6 0.3087400 0.07590462
    ## 
    ## $data_03
    ## Source:   query [6 x 3]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##         a_03      b_03      c_03
    ##        <dbl>     <dbl>     <dbl>
    ## 1 0.96590152 0.7724133 0.2958221
    ## 2 0.68143015 0.4223004 0.9090244
    ## 3 0.13725659 0.2756238 0.2222813
    ## 4 0.06594144 0.1379500 0.3834114
    ## 5 0.33325658 0.2561333 0.1527903
    ## 6 0.68229600 0.8385715 0.1413857

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
rm(list=ls())
gc()
```

    ##          used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells 516567 27.6     940480 50.3   750400 40.1
    ## Vcells 697256  5.4    1308461 10.0   928383  7.1
