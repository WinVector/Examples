<!-- README.md is generated from README.Rmd. Please edit that file -->
``` r
base::date()
```

    ## [1] "Sat Jun  3 15:19:28 2017"

``` r
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.5.0'

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
sc <- NULL

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
    ## description "->localhost:50577"
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
    ## [1] "/var/folders/7q/h_jp2vj131g5799gfnpzhdp80000gn/T//RtmpkelPvw/file47b3ec1b2e3_spark.log"
    ## 
    ## $spark_context
    ## <jobj[5]>
    ##   class org.apache.spark.SparkContext
    ##   org.apache.spark.SparkContext@3fd6f69a
    ## 
    ## $java_context
    ## <jobj[6]>
    ##   class org.apache.spark.api.java.JavaSparkContext
    ##   org.apache.spark.api.java.JavaSparkContext@6633394d
    ## 
    ## $hive_context
    ## <jobj[9]>
    ##   class org.apache.spark.sql.SparkSession
    ##   org.apache.spark.sql.SparkSession@77ba6a1a
    ## 
    ## attr(,"class")
    ## [1] "spark_connection"       "spark_shell_connection"
    ## [3] "DBIConnection"

``` r
mtcars2 <- mtcars %>%
  mutate(car = row.names(mtcars)) 

frameList <- mtcars2 %>% 
  tidyr::gather(key='fact', value='value', -car) %>% 
  split(., .$fact) 

frameListS <- lapply(names(frameList), 
                     function(ni) {
                       copy_to(sc, frameList[[ni]], ni)
                     }
)
names(frameListS) <- names(frameList)

n1 <- names(frameListS)[[1]]
nrest <- setdiff(names(frameListS),n1)
```

``` r
#' Compute union_all of tables.  Cut down from \code{replyr::replyr_union_all()} for debugging.
#'
#' @param sc remote data source tables are on (and where to copy-to and work), NULL for local tables.
#' @param tabA not-NULL table with at least 1 row on sc data source, and columns \code{c("car", "fact", "value")}.
#' @param tabB not-NULL table with at least 1 row on same data source as tabA and columns \code{c("car", "fact", "value")}.
#' @return table with all rows of tabA and tabB (union_all).
#'
#' @export
example_union_all <- function(sc, tabA, tabB) {
  cols <- intersect(colnames(tabA), colnames(tabB))
  expectedCols <- c("car", "fact", "value")
  if((length(cols)!=length(expectedCols)) ||
     (!all.equal(cols, expectedCols))) {
    stop(paste("example_union_all: column set must be exactly", 
               paste(expectedCols, collapse = ', ')))
  }
  mergeColName <- 'exampleunioncol'
  # build a 2-row table to control the union
  controlTable <- data.frame(exampleunioncol= c('a', 'b'),
                             stringsAsFactors = FALSE)
  if(!is.null(sc)) {
    controlTable <- copy_to(sc, controlTable,
                            temporary=TRUE)
  }
  # decorate left and right tables for the merge
  tabA <- tabA %>%
    select(one_of(cols)) %>%
    mutate(exampleunioncol = as.character('a'))
  tabB <- tabB %>%
    select(one_of(cols)) %>%
    mutate(exampleunioncol = as.character('b'))
  # do the merges
  joined <- controlTable %>%
    left_join(tabA, by=mergeColName) %>%
    left_join(tabB, by=mergeColName, suffix = c('_a', '_b'))
  # coalesce the values
  joined <- joined %>%
    mutate(car = ifelse(exampleunioncol=='a', car_a, car_b))
  joined <- joined %>%
    mutate(fact = ifelse(exampleunioncol=='a', fact_a, fact_b))
  joined <- joined %>%
    mutate(value = ifelse(exampleunioncol=='a', value_a, value_b))
  joined %>%
    select(one_of(cols)) %>%
    dplyr::compute()
}
```

``` r
for(i in seq_len(100)) { 
  print(paste('start',i,base::date()))
  # very crude binding of rows (actual code would always bind small bits)
  res <- frameListS[[n1]]
  for(fi in nrest) {
    print(paste(' start',i,fi,base::date()))
    oi <- frameListS[[fi]]
    res <- example_union_all(sc, res, oi)
    print(paste(' done',i,fi,base::date()))
  }
  local <- res %>%
    collect() %>%
    as.data.frame()
  print(paste(' done',i,base::date()))
}
```

``` r
if(!is.null(sc)) {
  sparklyr::spark_disconnect(sc)
}
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  706832 37.8    1168576 62.5   940480 50.3
    ## Vcells 1197220  9.2    2060183 15.8  1499000 11.5
