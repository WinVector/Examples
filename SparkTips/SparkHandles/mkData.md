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
                  spark_write_parquet(hi, path= ni,
                                      mode= 'overwrite')
                  dplyr::db_drop_table(sc, ni)
                  ni
                },
                character(1))
print(tableNames)
```

    ## [1] "data_01" "data_02" "data_03"

``` r
spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  651676 34.9    1168576 62.5   940480 50.3
    ## Vcells 1134091  8.7    2060183 15.8  1302491 10.0
