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
# wrong way to re-load tables (tried to de-serialize handles)
tableCollection <- readRDS('tableCollectionWrong.RDS')
print(tableCollection)
```

    ## # A tibble: 3 x 2
    ##   tableName          handle
    ##       <chr>          <list>
    ## 1   data_01 <S3: tbl_spark>
    ## 2   data_02 <S3: tbl_spark>
    ## 3   data_03 <S3: tbl_spark>

``` r
head(tableCollection$handle[[1]])
```

    ## Error in writeBin(con, backend): can only write to a binary connection

``` r
spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  659444 35.3    1168576 62.5   940480 50.3
    ## Vcells 1144560  8.8    2060183 15.8  1417057 10.9
