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
names <- vapply(1:3,
                function(i) {
                  di <- data.frame(x=runif(10))
                  ni <- paste('data', sprintf("%02d", i), sep='_')
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
#   DBI::dbListTables(sc)/dplyr::tbl(sc, namei)
tableCollection <- data_frame(name= names)
tableCollection$handle <- lapply(
  tableCollection$name,
  function(namei) {
    spark_read_parquet(sc, namei, namei)
  }
)
```

``` r
# or if we want to grab all tables
# sparklyr already knows about:
tableCollection <- data_frame(name = DBI::dbListTables(sc))
tableCollection$handle <-
  lapply(tableCollection$name,
         function(namei) {
          dplyr::tbl(sc, namei)
         })
```

``` r
# and names to handles for convenience
names(tableCollection$handle) <-
  tableCollection$name

# look at the top of each table (also forces
# evaluation!).
lapply(tableCollection$handle, 
       head)
```

    ## $data_01
    ## Source:   query [6 x 1]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##            x
    ##        <dbl>
    ## 1 0.76633984
    ## 2 0.35680472
    ## 3 0.03367087
    ## 4 0.56471979
    ## 5 0.32892782
    ## 6 0.65412008
    ## 
    ## $data_02
    ## Source:   query [6 x 1]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##           x
    ##       <dbl>
    ## 1 0.9171616
    ## 2 0.6586442
    ## 3 0.6486551
    ## 4 0.5853624
    ## 5 0.3501948
    ## 6 0.6811760
    ## 
    ## $data_03
    ## Source:   query [6 x 1]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##            x
    ##        <dbl>
    ## 1 0.02706922
    ## 2 0.97042013
    ## 3 0.58138557
    ## 4 0.18882467
    ## 5 0.80100210
    ## 6 0.91616047

``` r
# get dimensions of each table
lapply(tableCollection$handle, 
       dim)
```

    ## $data_01
    ## [1] 10  1
    ## 
    ## $data_02
    ## [1] 10  1
    ## 
    ## $data_03
    ## [1] 10  1

``` r
rm(list=ls())
gc()
```

    ##          used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells 511451 27.4     940480 50.3   750400 40.1
    ## Vcells 694419  5.3    1308461 10.0   925004  7.1
