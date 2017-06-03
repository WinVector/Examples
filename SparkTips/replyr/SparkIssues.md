<!-- README.md is generated from README.Rmd. Please edit that file -->
``` r
base::date()
```

    ## [1] "Sat Jun  3 10:45:56 2017"

``` r
packageVersion("replyr")
```

    ## [1] '0.3.902'

``` r
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.5.0'

``` r
suppressPackageStartupMessages("spaklyr")
```

    ## [1] "spaklyr"

``` r
packageVersion("sparklyr")
```

    ## [1] '0.5.5'

``` r
devtools::session_info()
```

    ## Session info -------------------------------------------------------------

    ##  setting  value                       
    ##  version  R version 3.4.0 (2017-04-21)
    ##  system   x86_64, darwin15.6.0        
    ##  ui       X11                         
    ##  language (EN)                        
    ##  collate  en_US.UTF-8                 
    ##  tz       America/Los_Angeles         
    ##  date     2017-06-03

    ## Packages -----------------------------------------------------------------

    ##  package    * version    date       source                          
    ##  assertthat   0.2.0      2017-04-11 CRAN (R 3.4.0)                  
    ##  backports    1.1.0      2017-05-22 CRAN (R 3.4.0)                  
    ##  base       * 3.4.0      2017-04-21 local                           
    ##  compiler     3.4.0      2017-04-21 local                           
    ##  datasets   * 3.4.0      2017-04-21 local                           
    ##  DBI          0.6-1      2017-04-01 CRAN (R 3.4.0)                  
    ##  devtools     1.13.2     2017-06-02 CRAN (R 3.4.0)                  
    ##  digest       0.6.12     2017-01-27 CRAN (R 3.4.0)                  
    ##  dplyr      * 0.5.0      2016-06-24 CRAN (R 3.4.0)                  
    ##  evaluate     0.10       2016-10-11 CRAN (R 3.4.0)                  
    ##  graphics   * 3.4.0      2017-04-21 local                           
    ##  grDevices  * 3.4.0      2017-04-21 local                           
    ##  htmltools    0.3.6      2017-04-28 CRAN (R 3.4.0)                  
    ##  knitr        1.16       2017-05-18 CRAN (R 3.4.0)                  
    ##  magrittr     1.5        2014-11-22 CRAN (R 3.4.0)                  
    ##  memoise      1.1.0      2017-04-21 CRAN (R 3.4.0)                  
    ##  methods    * 3.4.0      2017-04-21 local                           
    ##  R6           2.2.1      2017-05-10 CRAN (R 3.4.0)                  
    ##  Rcpp         0.12.11    2017-05-22 CRAN (R 3.4.0)                  
    ##  rlang        0.1.1.9000 2017-05-29 Github (tidyverse/rlang@c351186)
    ##  rmarkdown    1.5        2017-04-26 CRAN (R 3.4.0)                  
    ##  rprojroot    1.2        2017-01-16 CRAN (R 3.4.0)                  
    ##  stats      * 3.4.0      2017-04-21 local                           
    ##  stringi      1.1.5      2017-04-07 CRAN (R 3.4.0)                  
    ##  stringr      1.2.0      2017-02-18 CRAN (R 3.4.0)                  
    ##  tibble       1.3.3      2017-05-28 CRAN (R 3.4.0)                  
    ##  tools        3.4.0      2017-04-21 local                           
    ##  utils      * 3.4.0      2017-04-21 local                           
    ##  withr        1.0.2      2016-06-20 CRAN (R 3.4.0)                  
    ##  yaml         2.1.14     2016-11-12 CRAN (R 3.4.0)

``` r
sc <- sparklyr::spark_connect(version='2.0.2', 
                              master = "local")
print(sc)
```

    ## $master
    ## [1] "local[4]"
    ## 
    ## $method
    ## [1] "shell"
    ## 
    ## $app_name
    ## [1] "sparklyr"
    ## 
    ## $config
    ## $config$sparklyr.cores.local
    ## [1] 4
    ## 
    ## $config$spark.sql.shuffle.partitions.local
    ## [1] 4
    ## 
    ## $config$spark.env.SPARK_LOCAL_IP.local
    ## [1] "127.0.0.1"
    ## 
    ## $config$sparklyr.csv.embedded
    ## [1] "^1.*"
    ## 
    ## $config$`sparklyr.shell.driver-class-path`
    ## [1] ""
    ## 
    ## attr(,"config")
    ## [1] "default"
    ## attr(,"file")
    ## [1] "/Library/Frameworks/R.framework/Versions/3.4/Resources/library/sparklyr/conf/config-template.yml"
    ## 
    ## $spark_home
    ## [1] "/Users/johnmount/Library/Caches/spark/spark-2.0.2-bin-hadoop2.7"
    ## 
    ## $backend
    ## A connection with                               
    ## description "->localhost:49969"
    ## class       "sockconn"         
    ## mode        "wb"               
    ## text        "binary"           
    ## opened      "opened"           
    ## can read    "yes"              
    ## can write   "yes"              
    ## 
    ## $monitor
    ## A connection with                              
    ## description "->localhost:8880"
    ## class       "sockconn"        
    ## mode        "rb"              
    ## text        "binary"          
    ## opened      "opened"          
    ## can read    "yes"             
    ## can write   "yes"             
    ## 
    ## $output_file
    ## [1] "/var/folders/7q/h_jp2vj131g5799gfnpzhdp80000gn/T//RtmpSAGQR9/file4b15ba7a2dd_spark.log"
    ## 
    ## $spark_context
    ## <jobj[5]>
    ##   class org.apache.spark.SparkContext
    ##   org.apache.spark.SparkContext@2b57eb01
    ## 
    ## $java_context
    ## <jobj[6]>
    ##   class org.apache.spark.api.java.JavaSparkContext
    ##   org.apache.spark.api.java.JavaSparkContext@6cf89d7a
    ## 
    ## $hive_context
    ## <jobj[9]>
    ##   class org.apache.spark.sql.SparkSession
    ##   org.apache.spark.sql.SparkSession@772123d2
    ## 
    ## attr(,"class")
    ## [1] "spark_connection"       "spark_shell_connection"
    ## [3] "DBIConnection"

``` r
mtcars2 <- mtcars %>%
  mutate(car = row.names(mtcars)) %>%
  copy_to(sc, ., 'mtcars2')

tempNameGenerator <- replyr::makeTempNameGenerator("TESTTABS")
```

Seems to reliably hang `Spark` (in about 5 passes through the loop on average), sometimes crashing `R`.

``` r
for(i in seq_len(100)) {
  print(paste('start',i,base::date()))
  localRes <- mtcars2 %>%
    replyr::replyr_moveValuesToRows(nameForNewKeyColumn= 'fact', 
                                    nameForNewValueColumn= 'value', 
                                    columnsToTakeFrom= colnames(mtcars),
                                    nameForNewClassColumn= 'class',
                                    tempNameGenerator = tempNameGenerator) %>%
    collect() %>%
    as.data.frame()
  tmps <- tempNameGenerator(dumpList = TRUE)
  for(ti in tmps) {
    db_drop_table(sc, ti)
  }
  print(paste(' done',i,base::date()))
}
```

![](crash.png)

``` r
sparklyr::spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  704777 37.7    1168576 62.5   940480 50.3
    ## Vcells 1204768  9.2    2060183 15.8  1478902 11.3
