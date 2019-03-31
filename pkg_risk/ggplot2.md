ggplot2
================

Look at size of the ggplot2 `VECTOR_ELT()` issue.

``` r
library("rqdatatable")
```

    ## Loading required package: rquery

``` r
# # load package facts
# cran <- tools::CRAN_package_db()
# cr <- tools::CRAN_check_results()
# saveRDS(list(cran = cran, cr = cr), "cran_facts_2019_03_31.RDS")
lst <- readRDS("cran_facts_2019_03_31.RDS")
cran <- lst$cran
cr <- lst$cr
```

``` r
package_summary <- cr %.>%
  select_rows(.,
              !is.na(Status)) %.>%
  extend(., 
         one = 1) %.>%
  project(.,
          groupby = c("Package", "Status"),
          count = sum(one)) %.>%
  cdata::pivot_to_rowrecs(., 
                          columnToTakeKeysFrom = "Status",
                          columnToTakeValuesFrom = "count",
                          rowKeyColumns = "Package") %.>%
  extend(.,
         OK = ifelse(is.na(OK), 0, OK),
         NOTE = ifelse(is.na(NOTE), 0, NOTE),
         WARN = ifelse(is.na(WARN), 0, WARN),
         ERROR = ifelse(is.na(ERROR), 0, ERROR),
         FAIL = ifelse(is.na(FAIL), 0, FAIL)) %.>%
  extend(.,
         has_problem = (WARN + ERROR + FAIL)>0)
  
package_summary %.>% 
  head(.) %.>%
  knitr::kable(.)
```

| Package     |   OK|  NOTE|  WARN|  ERROR|  FAIL| has\_problem |
|:------------|----:|-----:|-----:|------:|-----:|:-------------|
| A3          |   12|     0|     0|      0|     0| FALSE        |
| abbyyR      |   12|     0|     0|      0|     0| FALSE        |
| abc         |    0|    12|     0|      0|     0| FALSE        |
| abc.data    |   12|     0|     0|      0|     0| FALSE        |
| ABC.RAP     |   11|     0|     1|      0|     0| TRUE         |
| ABCanalysis |   12|     0|     0|      0|     0| FALSE        |

``` r
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
      setdiff(si, c("", "R", 
                    "base", "compiler", "datasets", 
                    "graphics", "grDevices", "grid",
                    "methods", "parallel", "splines", 
                    "stats", "stats4", "tcltk", "tools",
                    "translations", "utils"))
    })
  strs
}

# collect the columns we want
d <- data.frame(
  Package = cran$Package,
  stringsAsFactors = FALSE)
d$Depends <- parse_lists(cran$Depends)
d$nDepends <- vapply(d$Depends, length, numeric(1))
d$Imports <- parse_lists(cran$Imports)
d$nImports <- vapply(d$Imports, length, numeric(1))
d$Suggests <- parse_lists(cran$Suggests)
d$nSuggests <- vapply(d$Suggests, length, numeric(1))

d$Depends_ggplot2 <- vapply(d$Depends, 
                            function(di) {
                              "ggplot2" %in% di
                            }, logical(1))
summary(d$Depends_ggplot2)
```

    ##    Mode   FALSE    TRUE 
    ## logical   13698     304

``` r
d$Imports_ggplot2 <- vapply(d$Imports, 
                            function(di) {
                              "ggplot2" %in% di
                            }, logical(1))
summary(d$Imports_ggplot2)
```

    ##    Mode   FALSE    TRUE 
    ## logical   12765    1237

``` r
d$Suggests_ggplot2 <- vapply(d$Suggests, 
                            function(di) {
                              "ggplot2" %in% di
                            }, logical(1))
summary(d$Suggests_ggplot2)
```

    ##    Mode   FALSE    TRUE 
    ## logical   13405     597

``` r
d <- d[, c("Package", "nDepends", "nImports", "nSuggests",
           "Depends_ggplot2", "Imports_ggplot2", "Suggests_ggplot2")]

d %.>%
  extend(., one = 1) %.>%
  project(., 
          groupby = qc(Depends_ggplot2, Imports_ggplot2, Suggests_ggplot2),
          count = sum(one)) %.>% 
  knitr::kable(.)
```

| Depends\_ggplot2 | Imports\_ggplot2 | Suggests\_ggplot2 |  count|
|:-----------------|:-----------------|:------------------|------:|
| FALSE            | FALSE            | FALSE             |  11865|
| FALSE            | FALSE            | TRUE              |    596|
| FALSE            | TRUE             | FALSE             |   1237|
| TRUE             | FALSE            | FALSE             |    303|
| TRUE             | FALSE            | TRUE              |      1|

``` r
# map check status into our data
nrow(d)
```

    ## [1] 14002

``` r
d <- natural_join(d, package_summary, 
                  by = "Package", 
                  jointype = "INNER")
(npackages <- nrow(d))
```

    ## [1] 14001

``` r
d %.>%
  extend(., 
         one = 1,
         uses_ggplot2 = (Depends_ggplot2 + Imports_ggplot2 + Suggests_ggplot2)>0) %.>%
  project(., 
          groupby = qc(uses_ggplot2, has_problem),
          count = sum(one)) %.>% 
  extend(., 
         fraction = count/sum(count)) %.>%
  knitr::kable(.)
```

| uses\_ggplot2 | has\_problem |  count|   fraction|
|:--------------|:-------------|------:|----------:|
| FALSE         | FALSE        |  10234|  0.7309478|
| FALSE         | TRUE         |   1630|  0.1164203|
| TRUE          | TRUE         |   1693|  0.1209199|
| TRUE          | FALSE        |    444|  0.0317120|

``` r
model <- glm(has_problem ~ Depends_ggplot2 + Imports_ggplot2 + Suggests_ggplot2, 
             data = d, 
             family = binomial)
summary(model)
```

    ## 
    ## Call:
    ## glm(formula = has_problem ~ Depends_ggplot2 + Imports_ggplot2 + 
    ##     Suggests_ggplot2, family = binomial, data = d)
    ## 
    ## Deviance Residuals: 
    ##     Min       1Q   Median       3Q      Max  
    ## -1.9090  -0.5437  -0.5437  -0.5437   1.9925  
    ## 
    ## Coefficients:
    ##                      Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept)          -1.83714    0.02667  -68.89   <2e-16 ***
    ## Depends_ggplot2TRUE   3.48293    0.15828   22.00   <2e-16 ***
    ## Imports_ggplot2TRUE   3.28731    0.07723   42.56   <2e-16 ***
    ## Suggests_ggplot2TRUE  2.83971    0.09620   29.52   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 15345  on 14000  degrees of freedom
    ## Residual deviance: 11660  on 13997  degrees of freedom
    ## AIC: 11668
    ## 
    ## Number of Fisher Scoring iterations: 4
