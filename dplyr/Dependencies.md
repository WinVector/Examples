Dependencies
================
Win-Vector LLC
12/1/2017

This is an example of an erroneous calculation in `dplyr` `0.7.4` with databases, likely arising from mishandling of expression to expression dependencies (which [we have written about before](http://www.win-vector.com/blog/2017/09/my-advice-on-dplyrmutate/)). Since this is not a security issue, can cause non-signaled incorrect results, and has an easy fix: we have decided to document it here and to [distribute an announcement](http://www.win-vector.com/blog/2017/12/please-inspect-your-dplyrdatabase-code/).

First we set up our example.

``` r
suppressPackageStartupMessages(library("dplyr"))
packageVersion("dplyr")
```

    ## [1] '0.7.4'

``` r
my_db <- DBI::dbConnect(RSQLite::SQLite(),
                        ":memory:")
d <- dplyr::copy_to(
  my_db, 
  data.frame(valuesA = c("A", NA, NA),
             valuesB = c("B", NA, NA),
             canUseFix1 = c(TRUE, TRUE, FALSE),
             fix1 = c('Fix_1_V1', "Fix_1_V2", "Fix_1_V3"),
             canUseFix2 = c(FALSE, FALSE, TRUE),
             fix2 = c('Fix_2_V1', "Fix_2_V2", "Fix_2_V3"),
             stringsAsFactors = FALSE),
  'd', 
  temporary = TRUE, overwrite = TRUE)
knitr::kable(dplyr::collect(d))
```

| valuesA | valuesB |  canUseFix1| fix1       |  canUseFix2| fix2       |
|:--------|:--------|-----------:|:-----------|-----------:|:-----------|
| A       | B       |           1| Fix\_1\_V1 |           0| Fix\_2\_V1 |
| NA      | NA      |           1| Fix\_1\_V2 |           0| Fix\_2\_V2 |
| NA      | NA      |           0| Fix\_1\_V3 |           1| Fix\_2\_V3 |

For our example we are using `canUseFix1*` columns to find which positions of our `values*` columns can be replaced by the corresponding fix values. This is a common situation in data processing: where you have a column you wish to populate from a ordered sequence of alternate sources.

We could write this as nested `ifelse()` or coalesce. But suppose we had written the code as below.

``` r
fixed <- dplyr::mutate(
  d,
  valuesA := ifelse(is.na(valuesA) & canUseFix1, 
                    fix1, valuesA),
  valuesA := ifelse(is.na(valuesA) & canUseFix2, 
                    fix2, valuesA),
  valuesB := ifelse(is.na(valuesB) & canUseFix1, 
                    fix1, valuesB),
  valuesB := ifelse(is.na(valuesB) & canUseFix2, 
                    fix2, valuesB))

fixed %>%
  dplyr::select(., valuesA, valuesB) %>%
  dplyr::collect(.) %>%
  knitr::kable(.)
```

| valuesA    | valuesB    |
|:-----------|:-----------|
| A          | B          |
| Fix\_1\_V2 | Fix\_1\_V2 |
| NA         | Fix\_2\_V3 |

Notice this *silently* failed! It gave a wrong answer, with no indicated error.

The third `valuesA` value remains at `NA` even though it should have been repaired by the fix 2 rule. This is not due to order of statements as the fix rules were deliberately chosen to apply to disjoint rows.

Looking further we see `dplyr` seem to generate incomplete `SQL` (not all the intended transforms seem to survive the translation, notice there are 3 `CASE WHEN` statements in the generated `SQL`, not 4):

``` r
d  %>%
  dplyr::mutate(
    .,
    valuesA := ifelse(is.na(valuesA) & canUseFix1, 
                      fix1, valuesA),
    valuesA := ifelse(is.na(valuesA) & canUseFix2, 
                      fix2, valuesA),
    valuesB := ifelse(is.na(valuesB) & canUseFix1, 
                      fix1, valuesB),
    valuesB := ifelse(is.na(valuesB) & canUseFix2, 
                      fix2, valuesB)) %>%
  dplyr::show_query(.)
```

    ## <SQL>
    ## SELECT `valuesA`, `canUseFix1`, `fix1`, `canUseFix2`, `fix2`, CASE WHEN (((`valuesB`) IS NULL) AND `canUseFix2`) THEN (`fix2`) ELSE (`valuesB`) END AS `valuesB`
    ## FROM (SELECT `valuesA`, `canUseFix1`, `fix1`, `canUseFix2`, `fix2`, CASE WHEN (((`valuesB`) IS NULL) AND `canUseFix1`) THEN (`fix1`) ELSE (`valuesB`) END AS `valuesB`
    ## FROM (SELECT `valuesB`, `canUseFix1`, `fix1`, `canUseFix2`, `fix2`, CASE WHEN (((`valuesA`) IS NULL) AND `canUseFix1`) THEN (`fix1`) ELSE (`valuesA`) END AS `valuesA`
    ## FROM `d`))

For our recommended current work-around, please see [here](http://winvector.github.io/FluidData/DplyrDependencies.html).

------------------------------------------------------------------------

``` r
sessionInfo()
```

    ## R version 3.4.2 (2017-09-28)
    ## Platform: x86_64-apple-darwin15.6.0 (64-bit)
    ## Running under: macOS Sierra 10.12.6
    ## 
    ## Matrix products: default
    ## BLAS: /Library/Frameworks/R.framework/Versions/3.4/Resources/lib/libRblas.0.dylib
    ## LAPACK: /Library/Frameworks/R.framework/Versions/3.4/Resources/lib/libRlapack.dylib
    ## 
    ## locale:
    ## [1] en_US.UTF-8/en_US.UTF-8/en_US.UTF-8/C/en_US.UTF-8/en_US.UTF-8
    ## 
    ## attached base packages:
    ## [1] stats     graphics  grDevices utils     datasets  methods   base     
    ## 
    ## other attached packages:
    ## [1] dplyr_0.7.4
    ## 
    ## loaded via a namespace (and not attached):
    ##  [1] Rcpp_0.12.14.2    knitr_1.17        bindr_0.1        
    ##  [4] magrittr_1.5      bit_1.1-12        R6_2.2.2         
    ##  [7] rlang_0.1.4       highr_0.6         stringr_1.2.0    
    ## [10] blob_1.1.0        tools_3.4.2       DBI_0.7          
    ## [13] dbplyr_1.1.0      htmltools_0.3.6   yaml_2.1.14      
    ## [16] bit64_0.9-7       assertthat_0.2.0  rprojroot_1.2    
    ## [19] digest_0.6.12     tibble_1.3.4.9003 bindrcpp_0.2     
    ## [22] memoise_1.1.0     glue_1.2.0        evaluate_0.10.1  
    ## [25] RSQLite_2.0       rmarkdown_1.8     stringi_1.1.6    
    ## [28] compiler_3.4.2    pillar_1.0.1      backports_1.1.1  
    ## [31] pkgconfig_2.0.1

Also note: as of `December 1, 2017` upgrading the development versions of `dbplyr` and `dplyr` is *not* sufficient to fix the issue:

``` r
devtools::install_github("tidyverse/dbplyr")
devtools::install_github("tidyverse/dplyr")

base::date()
#> [1] "Fri Dec  1 09:32:56 2017"
packageVersion("dbplyr")
#> [1] '1.1.0.9000'
packageVersion("dplyr")
#> [1] '0.7.4.9000'

my_db <- DBI::dbConnect(RSQLite::SQLite(),
                        ":memory:")
d <- dplyr::copy_to(
  my_db, 
  data.frame(valuesA = c("A", NA, NA),
             valuesB = c("B", NA, NA),
             canUseFix1 = c(TRUE, TRUE, FALSE),
             fix1 = c('Fix_1_V1', "Fix_1_V2", "Fix_1_V3"),
             canUseFix2 = c(FALSE, FALSE, TRUE),
             fix2 = c('Fix_2_V1', "Fix_2_V2", "Fix_2_V3"),
             stringsAsFactors = FALSE),
  'd', 
  temporary = TRUE, overwrite = TRUE)
dplyr::mutate(
  d,
  valuesA := ifelse(is.na(valuesA) & canUseFix1, 
                    fix1, valuesA),
  valuesA := ifelse(is.na(valuesA) & canUseFix2, 
                    fix2, valuesA),
  valuesB := ifelse(is.na(valuesB) & canUseFix1, 
                    fix1, valuesB),
  valuesB := ifelse(is.na(valuesB) & canUseFix2, 
                    fix2, valuesB))
#> # Source: lazy query [?? x 6]
#> # Database: sqlite 3.19.3 [:memory:]
#>   valuesA  canUseFix1 fix1     canUseFix2 fix2     valuesB 
#>   <chr>         <int> <chr>         <int> <chr>    <chr>   
#> 1 A                 1 Fix_1_V1          0 Fix_2_V1 B       
#> 2 Fix_1_V2          1 Fix_1_V2          0 Fix_2_V2 Fix_1_V2
#> 3 <NA>              0 Fix_1_V3          1 Fix_2_V3 Fix_2_V3
```
