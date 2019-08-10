NNS solution 2
================

Variation on [Fred Viole’s excellent NNS
solution](https://htmlpreview.github.io/?https://github.com/OVVO-Financial/NNS/blob/NNS-Beta-Version/examples/tides.html).

``` r
library(ggplot2)
library(NNS)  # CRAN version August 8, 2019
```

    ## Loading required package: doParallel

    ## Loading required package: foreach

    ## Loading required package: iterators

    ## Loading required package: parallel

``` r
packageVersion('NNS')
```

    ## [1] '0.4.4'

``` r
tides <- readRDS('tides.RDS')

base_date_time =  as.POSIXct('2001/01/01 00:00', tz = "UTC")
first_date_time =  as.POSIXct('2019/06/01 00:00', tz = "UTC")
cut_date_time = as.POSIXct('2019/07/15 00:00', tz = "UTC")

dtrain <- tides[tides$dt<cut_date_time, , drop = FALSE]
dtest <- tides[tides$dt>=cut_date_time, , drop = FALSE]

training_length <- dim(dtrain)[1] - dim(dtest)[1]
```

``` r
nns_periods <- NNS.seas(dtrain$tide_feet)
```

![](NNS_solution2_files/figure-gfm/unnamed-chunk-3-1.png)<!-- -->

``` r
nns_periods <- nns_periods$all.periods$Period
nns_periods_seconds <- (nns_periods * (6*60))
take_period <- nns_periods_seconds<86400*120
nns_periods_seconds <- nns_periods_seconds[take_period]
nns_periods_seconds <- nns_periods_seconds[1:100]

ggplot(data.frame(nns_periods_days = nns_periods_seconds/86400), 
       aes(x=nns_periods_days)) + 
  geom_density(adjust = 0.25)
```

![](NNS_solution2_files/figure-gfm/unnamed-chunk-4-1.png)<!-- -->

``` r
head(nns_periods_seconds)
```

    ## [1] 7065720 7065360 7065000 8272800 7064640 9391320

``` r
length(nns_periods_seconds)
```

    ## [1] 100

``` r
nns_periods_constrained <- nns_periods[take_period]


arma_parameters <- NNS.ARMA.optim(variable = dtrain$tide_feet,
                                  training.set = training_length,
                                  seasonal.factor = nns_periods_constrained[1:100])
```

    ## [1] "CURRNET METHOD: lin"
    ## [1] "COPY LATEST PARAMETERS DIRECTLY FOR NNS.ARMA() IF ERROR:"
    ## [1] "NNS.ARMA(... method =  'lin' , seasonal.factor =  c( 13166 ) ...)"
    ## [1] "CURRENT lin OBJECTIVE FUNCTION = 913.880531125"
    ## [1] "NNS.ARMA(... method =  'lin' , seasonal.factor =  c( 13166, 22980 ) ...)"
    ## [1] "CURRENT lin OBJECTIVE FUNCTION = 889.725433641414"
    ## [1] "NNS.ARMA(... method =  'lin' , seasonal.factor =  c( 13166, 22980, 13167 ) ...)"
    ## [1] "CURRENT lin OBJECTIVE FUNCTION = 838.358475782724"
    ## [1] "BEST method = 'lin', seasonal.factor = c( 13166, 22980, 13167)"
    ## [1] "BEST lin OBJECTIVE FUNCTION = 838.358475782724"
    ## [1] "CURRNET METHOD: nonlin"
    ## [1] "COPY LATEST PARAMETERS DIRECTLY FOR NNS.ARMA() IF ERROR:"
    ## [1] "NNS.ARMA(... method =  'nonlin' , seasonal.factor =  c( 13166, 22980, 13167 ) ...)"
    ## [1] "CURRENT nonlin OBJECTIVE FUNCTION = 2436.53305681041"
    ## [1] "BEST method = 'nonlin' PATH MEMBER = c( 13166, 22980, 13167)"
    ## [1] "BEST nonlin OBJECTIVE FUNCTION = 2436.53305681041"
    ## [1] "CURRNET METHOD: both"
    ## [1] "COPY LATEST PARAMETERS DIRECTLY FOR NNS.ARMA() IF ERROR:"
    ## [1] "NNS.ARMA(... method =  'both' , seasonal.factor =  c( 13166, 22980, 13167 ) ...)"
    ## [1] "CURRENT both OBJECTIVE FUNCTION = 1362.25491187278"
    ## [1] "BEST method = 'both' PATH MEMBER = c( 13166, 22980, 13167)"
    ## [1] "BEST both OBJECTIVE FUNCTION = 1362.25491187278"

``` r
nns_estimates <- NNS.ARMA(dtrain$tide_feet, 
                          h = dim(dtest)[1], 
                          method = arma_parameters$method,
                          seasonal.factor = arma_parameters$periods, 
                          weights = arma_parameters$weights,
                          negative.values = TRUE,
                          seasonal.plot = FALSE)
```

![](NNS_solution2_files/figure-gfm/unnamed-chunk-6-1.png)<!-- -->

``` r
r_squared <- function(est, y) {
  1- sum((y-est)^2)/sum((y-mean(y))^2)
}

r_squared(nns_estimates, dtest$tide_feet)
```

    ## [1] 0.9345191

``` r
dtest$nns_estimates <- nns_estimates
sigr::wrapFTest(dtest, 
                predictionColumnName = 'nns_estimates',
                yColumnName = 'tide_feet')
```

    ## [1] "F Test summary: (R2=0.9345, F(1,4078)=5.82e+04, p<1e-05)."

``` r
ggplot(aes(x=dt), data=dtest) +
  geom_line(aes(y=tide_feet), color='blue', alpha=0.5) + 
  geom_line(aes(y=nns_estimates), color='black', alpha=0.5) +
  ggtitle("prediction (blue) superimposed on actuals on test")
```

![](NNS_solution2_files/figure-gfm/unnamed-chunk-9-1.png)<!-- -->
