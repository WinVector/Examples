``` r
print(head(dTrain))
```

    ##          x1      x2      x3      x4 y
    ## 77  lev_008 lev_004 lev_007 lev_011 0
    ## 41  lev_016 lev_015 lev_019 lev_012 0
    ## 158 lev_007 lev_019 lev_001 lev_015 4
    ## 69  lev_010 lev_017 lev_018 lev_009 0
    ## 6   lev_003 lev_014 lev_016 lev_017 0
    ## 18  lev_004 lev_015 lev_014 lev_007 0

``` r
# default ranger model, treat categoricals as ordered (a very limiting treatment)
m1 <- ranger(y~x1+x2+x3+x4,data=dTrain, write.forest=TRUE)
print(m1)
```

    ## Ranger result
    ## 
    ## Call:
    ##  ranger(y ~ x1 + x2 + x3 + x4, data = dTrain, write.forest = TRUE) 
    ## 
    ## Type:                             Regression 
    ## Number of trees:                  500 
    ## Sample size:                      100 
    ## Number of independent variables:  4 
    ## Mtry:                             2 
    ## Target node size:                 5 
    ## Variable importance mode:         none 
    ## OOB prediction error:             3.880332 
    ## R squared:                        0.01640494

``` r
dTest$rangerDefaultPred <- predict(m1,data=dTest)$predictions
WVPlots::ScatterHist(dTest,'rangerDefaultPred','y',
                     'ranger default prediction on test',
                     smoothmethod='identity',annot_size=3)
```

![](RangerExample_files/figure-markdown_github/rangerDafault-1.png)

``` r
# default ranger model, set categoricals to unordered, now limited to 63 levels
m2 <- ranger(y~x1+x2+x3+x4,data=dTrain,  write.forest=TRUE,
             respect.unordered.factors=TRUE)
```

    ## Growing trees.. Progress: 12%. Estimated remaining time: 3 minutes, 43 seconds.
    ## Growing trees.. Progress: 25%. Estimated remaining time: 3 minutes, 8 seconds.
    ## Growing trees.. Progress: 38%. Estimated remaining time: 2 minutes, 31 seconds.
    ## Growing trees.. Progress: 51%. Estimated remaining time: 2 minutes, 2 seconds.
    ## Growing trees.. Progress: 63%. Estimated remaining time: 1 minute, 30 seconds.
    ## Growing trees.. Progress: 77%. Estimated remaining time: 57 seconds.
    ## Growing trees.. Progress: 88%. Estimated remaining time: 29 seconds.

``` r
print(m2)
```

    ## Ranger result
    ## 
    ## Call:
    ##  ranger(y ~ x1 + x2 + x3 + x4, data = dTrain, write.forest = TRUE,      respect.unordered.factors = TRUE) 
    ## 
    ## Type:                             Regression 
    ## Number of trees:                  500 
    ## Sample size:                      100 
    ## Number of independent variables:  4 
    ## Mtry:                             2 
    ## Target node size:                 5 
    ## Variable importance mode:         none 
    ## OOB prediction error:             1.998252 
    ## R squared:                        0.4934786

``` r
dTest$rangerUnorderedPred <- predict(m2,data=dTest)$predictions
WVPlots::ScatterHist(dTest,'rangerUnorderedPred','y',
                     'ranger unordered prediction on test',
                     smoothmethod='identity',annot_size=3)
```

![](RangerExample_files/figure-markdown_github/rangerUnordered-1.png)

``` r
# vtreat re-encoded model
ct <- vtreat::mkCrossFrameNExperiment(dTrain,c('x1','x2','x3','x4'),'y')
newvars <- ct$treatments$scoreFrame$varName[(ct$treatments$scoreFrame$code=='catN') &
                                            (ct$treatments$scoreFrame$sig<1)]
m3 <- ranger(paste('y',paste(newvars,collapse=' + '),sep=' ~ '),data=ct$crossFrame,
              write.forest=TRUE)
print(m3)
```

    ## Ranger result
    ## 
    ## Call:
    ##  ranger(paste("y", paste(newvars, collapse = " + "), sep = " ~ "),      data = ct$crossFrame, write.forest = TRUE) 
    ## 
    ## Type:                             Regression 
    ## Number of trees:                  500 
    ## Sample size:                      100 
    ## Number of independent variables:  4 
    ## Mtry:                             2 
    ## Target node size:                 5 
    ## Variable importance mode:         none 
    ## OOB prediction error:             1.125285 
    ## R squared:                        0.7147603

``` r
dTestTreated <- vtreat::prepare(ct$treatments,dTest,
                                pruneSig=c(),varRestriction=newvars)
dTest$rangerNestedPred <- predict(m3,data=dTestTreated)$predictions
WVPlots::ScatterHist(dTest,'rangerNestedPred','y',
                     'ranger vtreat nested prediction on test',
                     smoothmethod='identity',annot_size=3)
```

![](RangerExample_files/figure-markdown_github/rangervtreat-1.png)
