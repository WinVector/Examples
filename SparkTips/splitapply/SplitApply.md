<!-- README.md is generated from README.Rmd. Please edit that file -->
``` r
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.5.0'

``` r
packageVersion("sparklyr")
```

    ## [1] '0.5.4'

``` r
# local data example of 
# dplyr::group_by() %>% dplyr::do()
f <- . %>% 
  arrange(Sepal.Length, Sepal.Width, Petal.Length, Petal.Width) %>%
  head(2)

iris %>% 
  group_by(Species) %>% 
  do(f(.))
```

    ## Source: local data frame [6 x 5]
    ## Groups: Species [3]
    ## 
    ## # A tibble: 6 x 5
    ##   Sepal.Length Sepal.Width Petal.Length Petal.Width    Species
    ##          <dbl>       <dbl>        <dbl>       <dbl>     <fctr>
    ## 1          4.3         3.0          1.1         0.1     setosa
    ## 2          4.4         2.9          1.4         0.2     setosa
    ## 3          4.9         2.4          3.3         1.0 versicolor
    ## 4          5.0         2.0          3.5         1.0 versicolor
    ## 5          4.9         2.5          4.5         1.7  virginica
    ## 6          5.6         2.8          4.9         2.0  virginica

``` r
# try it again on Spark

sc <- sparklyr::spark_connect(version='2.0.2', 
                              master = "local")
diris <- copy_to(sc, iris, 'diris')
head(diris)
```

    ## Source:   query [6 x 5]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 6 x 5
    ##   Sepal_Length Sepal_Width Petal_Length Petal_Width Species
    ##          <dbl>       <dbl>        <dbl>       <dbl>   <chr>
    ## 1          5.1         3.5          1.4         0.2  setosa
    ## 2          4.9         3.0          1.4         0.2  setosa
    ## 3          4.7         3.2          1.3         0.2  setosa
    ## 4          4.6         3.1          1.5         0.2  setosa
    ## 5          5.0         3.6          1.4         0.2  setosa
    ## 6          5.4         3.9          1.7         0.4  setosa

``` r
# function with column names matching Spark column names
f2 <- . %>% 
  arrange(Sepal_Length, Sepal_Width, Petal_Length, Petal_Width) %>%
  head(2)

diris %>% 
  group_by(Species) %>% 
  do(f2(.))
```

    ## # A tibble: 3 x 2
    ##      Species     V2
    ##        <chr> <list>
    ## 1 versicolor <NULL>
    ## 2  virginica <NULL>
    ## 3     setosa <NULL>

``` r
# try it with replyr
# devtools::install_github('WinVector/replyr')
library("replyr")
packageVersion("replyr")
```

    ## [1] '0.3.902'

``` r
# gapply extract method, only appropriate for small number of
# groups, could use 'group_by', but that requires f2
# respect groups (head() does not and slice() isn't available
# on this verion of Spark/Sparklyr)
diris %>% 
  gapply('Species', partitionMethod='extract', f2)
```

    ## Source:   query [6 x 5]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 6 x 5
    ##      Species Sepal_Length Sepal_Width Petal_Length Petal_Width
    ##        <chr>        <dbl>       <dbl>        <dbl>       <dbl>
    ## 1 versicolor          5.0         2.0          3.5         1.0
    ## 2 versicolor          4.9         2.4          3.3         1.0
    ## 3     setosa          4.3         3.0          1.1         0.1
    ## 4     setosa          4.4         2.9          1.4         0.2
    ## 5  virginica          4.9         2.5          4.5         1.7
    ## 6  virginica          5.6         2.8          4.9         2.0

``` r
# Or in separate stages
diris %>% 
  replyr_split('Species') %>%
  lapply(f2) %>%
  replyr_bind_rows()
```

    ## Source:   query [6 x 5]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ## # A tibble: 6 x 5
    ##      Species Sepal_Length Sepal_Width Petal_Length Petal_Width
    ##        <chr>        <dbl>       <dbl>        <dbl>       <dbl>
    ## 1 versicolor          5.0         2.0          3.5         1.0
    ## 2 versicolor          4.9         2.4          3.3         1.0
    ## 3     setosa          4.3         3.0          1.1         0.1
    ## 4     setosa          4.4         2.9          1.4         0.2
    ## 5  virginica          4.9         2.5          4.5         1.7
    ## 6  virginica          5.6         2.8          4.9         2.0

``` r
sparklyr::spark_disconnect(sc)
rm(list=ls())
gc()
```

    ##           used (Mb) gc trigger (Mb) max used (Mb)
    ## Ncells  687773 36.8    1168576 62.5  1168576 62.5
    ## Vcells 1307039 10.0    2552219 19.5  1879769 14.4
