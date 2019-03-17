pgk\_risk
================

``` r
# load package facts
cran <- tools::CRAN_package_db()
cr <- tools::CRAN_check_results()

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
d$nUsing <- d$nDepends + d$nImports

# map check status into our data
d$Status <- NA_character_
smap <- as.character(cr$Status)
names(smap) <- as.character(cr$Package)
d$Status <- smap[d$Package]

# take a look
head(d)
```

    ##       Package                                Depends nDepends
    ## 1          A3                        xtable, pbapply        2
    ## 2      abbyyR                                               0
    ## 3         abc abc.data, nnet, quantreg, MASS, locfit        5
    ## 4    abc.data                                               0
    ## 5     ABC.RAP                                               0
    ## 6 ABCanalysis                                               0
    ##                                  Imports nImports nUsing Status
    ## 1                                               0      2     OK
    ## 2 httr, XML, curl, readr, plyr, progress        6      6     OK
    ## 3                                               0      5   NOTE
    ## 4                                               0      0     OK
    ## 5                                               0      0   WARN
    ## 6                                plotrix        1      1     OK

``` r
# summarize status
table(d$Status, useNA = "ifany")
```

    ## 
    ## ERROR  FAIL  NOTE    OK  WARN 
    ##   255     1  2354 10606   705

``` r
# build a simple model
m <- glm(Status!="OK" ~ nUsing,
         data = d,
         family = binomial)
summary(m)
```

    ## 
    ## Call:
    ## glm(formula = Status != "OK" ~ nUsing, family = binomial, data = d)
    ## 
    ## Deviance Residuals: 
    ##     Min       1Q   Median       3Q      Max  
    ## -0.7671  -0.7574  -0.7289  -0.6314   2.1651  
    ## 
    ## Coefficients:
    ##              Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept) -1.072744   0.026204 -40.938  < 2e-16 ***
    ## nUsing      -0.029253   0.005721  -5.113 3.17e-07 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 15283  on 13920  degrees of freedom
    ## Residual deviance: 15255  on 13919  degrees of freedom
    ## AIC: 15259
    ## 
    ## Number of Fisher Scoring iterations: 4

``` r
# notice more package use reduces chance of Status!="OK"
# however, we are mostly modeing if status is OK versus NOTE.

# build a simple model on bad states
d$bad_status <- d$Status %in% c("ERROR", "FAIL", "WARN")
m <- glm(bad_status ~ nUsing,
           data = d,
           family = binomial)
summary(m)
```

    ## 
    ## Call:
    ## glm(formula = bad_status ~ nUsing, family = binomial, data = d)
    ## 
    ## Deviance Residuals: 
    ##     Min       1Q   Median       3Q      Max  
    ## -1.9634  -0.3788  -0.3408  -0.3064   2.4829  
    ## 
    ## Coefficients:
    ##             Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept) -3.03553    0.04611  -65.83   <2e-16 ***
    ## nUsing       0.10922    0.00654   16.70   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 6991.9  on 13920  degrees of freedom
    ## Residual deviance: 6745.4  on 13919  degrees of freedom
    ## AIC: 6749.4
    ## 
    ## Number of Fisher Scoring iterations: 5

``` r
d$bad_status <- d$Status %in% c("ERROR", "FAIL")
m <- glm(bad_status ~ nUsing,
         data = d,
         family = binomial)
summary(m)
```

    ## 
    ## Call:
    ## glm(formula = bad_status ~ nUsing, family = binomial, data = d)
    ## 
    ## Deviance Residuals: 
    ##     Min       1Q   Median       3Q      Max  
    ## -1.4290  -0.1895  -0.1691  -0.1597   2.9938  
    ## 
    ## Coefficients:
    ##              Estimate Std. Error z value Pr(>|z|)    
    ## (Intercept) -4.469923   0.085390  -52.35   <2e-16 ***
    ## nUsing       0.114645   0.009959   11.51   <2e-16 ***
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
    ## 
    ## (Dispersion parameter for binomial family taken to be 1)
    ## 
    ##     Null deviance: 2553.2  on 13920  degrees of freedom
    ## Residual deviance: 2453.1  on 13919  degrees of freedom
    ## AIC: 2457.1
    ## 
    ## Number of Fisher Scoring iterations: 7

``` r
# try an interpret
pred <- predict(m, newdata = d, type = "response")
d2 <- d
d2$nUsing <- d$nUsing + 1
pred_plus <- predict(m, newdata = d2, type = "response")

# bad status is rare (CRAN removes bad packages)
summary(d$bad_status)
```

    ##    Mode   FALSE    TRUE 
    ## logical   13665     256

``` r
# the absolute risk of each additional dependency is low
summary(pred_plus - pred)
```

    ##     Min.  1st Qu.   Median     Mean  3rd Qu.     Max. 
    ## 0.001358 0.001518 0.001697 0.002149 0.002118 0.028446

``` r
# the relative risk of each additional dependency is medium
summary(pred_plus / pred)
```

    ##    Min. 1st Qu.  Median    Mean 3rd Qu.    Max. 
    ##   1.041   1.119   1.120   1.119   1.120   1.120
