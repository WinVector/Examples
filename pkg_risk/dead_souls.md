Dead Souls
================

``` r
library("rqdatatable")
```

    ## Loading required package: rquery

``` r
# # load package facts
# cran <- tools::CRAN_package_db()
# cr <- tools::CRAN_check_results()
# saveRDS(list(cran = cran, cr = cr), "cran_facts_2019_05_04.RDS")
lst <- readRDS("cran_facts_2019_05_04.RDS")
cran <- lst$cran
```

``` r
base_pkgs <- c("", "R", 
               "base", "compiler", "datasets", 
               "graphics", "grDevices", "grid",
               "methods", "parallel", "splines", 
               "stats", "stats4", "tcltk", "tools",
               "translations", "utils")

# convert comma separated list into
# sequence of non-core package names
parse_lists <- function(strs) {
  strs[is.na(strs)] <- ""
  strs <- gsub("[(][^)]*[)]", "", strs)
  strs <- gsub("\\s+", "", strs)
  strs <- strsplit(strs, ",", fixed=TRUE)
  strs <- lapply(
    strs,
    function(si) {
      setdiff(si, base_pkgs)
    })
  strs
}

# collect the columns we want
d <- data.frame(
  Package = cran$Package,
  stringsAsFactors = FALSE)
for(use_type in c("Depends", "Imports", "Suggests", "LinkingTo")) {
  d[[use_type]] <- parse_lists(cran[[use_type]])
  d[[paste0("n_", use_type)]] <- vapply(d[[use_type]], length, numeric(1))
}
```

``` r
# look for orphans
refs <- unique(unlist(c(d$Depends, d$LinkingTo)))
ghosts <- setdiff(refs, d$Package)
d[vapply(d$Depends, function(di) { "impute" %in% di }, logical(1)), ]
```

    ##           Package                                  Depends n_Depends
    ## 3724         FAMT                           mnormt, impute         2
    ## 5448         iC10           pamr, impute, iC10TrainingData         3
    ## 5593   imputeLCMD       tmvtnorm, norm, pcaMethods, impute         4
    ## 7058     MetaPath    Biobase, GSEABase, genefilter, impute         4
    ## 7445  moduleColor                   impute, dynamicTreeCut         2
    ## 9182       polyPK                 impute, pcaMethods, xlsx         3
    ## 12040    snpReady Matrix, matrixcalc, stringr, rgl, impute         5
    ## 12782       swamp               impute, amap, gplots, MASS         4
    ##                                                                                Imports
    ## 3724                                                                                  
    ## 5448                                                                                  
    ## 5593                                                                                  
    ## 7058                                                                                  
    ## 7445                                                                                  
    ## 9182  imputeLCMD, plyr, sqldf, gplots, corrplot, circlize, mixOmics, pkr, Hmisc, ropls
    ## 12040                                                                                 
    ## 12782                                                                                 
    ##       n_Imports                   Suggests n_Suggests LinkingTo
    ## 3724          0                                     0          
    ## 5448          0                                     0          
    ## 5593          0                                     0          
    ## 7058          0                                     0          
    ## 7445          0                                     0          
    ## 9182         10           knitr, rmarkdown          2          
    ## 12040         0 knitr, rmarkdown, reshape2          3          
    ## 12782         0                                     0          
    ##       n_LinkingTo
    ## 3724            0
    ## 5448            0
    ## 5593            0
    ## 7058            0
    ## 7445            0
    ## 9182            0
    ## 12040           0
    ## 12782           0

``` r
bioc <- readxl::read_xlsx("Bioconductor3.9.xlsx")
ghosts <- setdiff(ghosts, bioc$Package)
print(ghosts)
```

    ## [1] "breastCancerVDX"

``` r
# http://www.bioconductor.org/packages/release/data/experiment/html/breastCancerVDX.html
```
