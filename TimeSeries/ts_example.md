ts_example
================

R packages re-doing of [our nested model time series
example](https://github.com/WinVector/Examples/blob/main/TimeSeries/nested_model_example.ipynb).

``` r
# http://fable.tidyverts.org
library(fable)
library(tsibble)
library(tsibbledata)
library(lubridate)
library(dplyr)
library(ggplot2)
library(forecast)
library(jsonlite)
```

## The problem

We want to fit a time series with both durable and transient external
regressors.

First let’s show the generating parameters we are attempting to recover.

``` r
model_specification <- fromJSON("generating_params.json")

model_specification
```

    ## $b_auto_0
    ## [1] 1.280413
    ## 
    ## $b_imp_0
    ## [1] -10.4
    ## 
    ## $b_auto
    ## [1]  1.975377 -1.000000
    ## 
    ## $b_z
    ## [1] 14.2
    ## 
    ## $b_x
    ## [1] 16.1
    ## 
    ## $generating_lags
    ## [1] 1 2
    ## 
    ## $modeling_lags
    ## [1] 1 2
    ## 
    ## $error_scale
    ## [1] 3.2

What we hope is to find `b_x_dur ~ b_z` and `b_x_imp ~ b_x`.

The generating and modeling lags specify translate into ARIMA terms as
`p = 2, i = 0`. We take our own advice from [A Time Series
Apologia](https://github.com/WinVector/Examples/blob/main/TS/TS_example.md)
and pick `q = p`. So in ARIMAX terms we try fitting a `pdq(2, 0, 2)`
system.

We don’t have any way to specify the nature of external regressors, with
act as transient effects in the “regression with ARIMA residuals”
formulation favored by the fable and forecast packages. This will lead
to a degradation in fit quality and an inability to properly estimate
`b_z` (as we can’t specify the for of the effect we believe it has in
the data).

## Fitting with external regressors using the fable package

General Fable formulation:

<code> (1 - φ<sub>1</sub> B - … - φ<sub>p</sub> B<sup>p</sup>)(1 -
B)<sup>d</sup> y<sub>t</sub> = c + (1 - θ<sub>1</sub> B - … -
θ<sub>q</sub> B<sup>q</sup>) ε<sub>t</sub> </code>

where <code>B</code> is the shift operator such that <code>B
u<sub>t</sub> = u<sub>t-1</sub></code>, <code>μ</code> is the mean of
<code>(1 - B)<sup>d</sup> y<sub>t</sub></code> and <code>c = μ (1 -
φ<sub>1</sub> - … - φ<sub>p</sub>)</code>. We solve for
<code>ε<sub>t</sub></code> being small. We very much prefer calling the
<code>ε<sub>t</sub></code> “the external shocks”, and not calling them
“errors.”

In our `pdq(2, 0, 2)` case this specializes to:

<code> (1 - φ<sub>1</sub> B - φ<sub>2</sub> B<sup>2</sup>)</sup>
y<sub>t</sub> = c + (1 - θ<sub>1</sub> B - θ<sub>2</sub> B<sup>2</sup>)
ε<sub>t</sub> </code>

And knowing this is “regression with ARIMA residuals”, when we add the
external regressors this should be:

<code> (1 - φ<sub>1</sub> B - φ<sub>2</sub> B<sup>2</sup>)</sup>
(y<sub>t</sub> - β<sub>0</sub> - β<sub>x</sub> x<sub>t</sub> -
β<sub>z</sub> z<sub>t</sub>) = c + (1 - θ<sub>1</sub> B - θ<sub>2</sub>
B<sup>2</sup>) ε<sub>t</sub> </code>

Removing the <code>B</code> shift notation and assuming
<code>mean(y<sub>t</sub> - β<sub>0</sub> - β<sub>x</sub> x<sub>t</sub> -
β<sub>z</sub> z<sub>t</sub>)</code> is zero gives us.

<pre>
<code>
(y<sub>t</sub> - &beta;<sub>0</sub> - &beta;<sub>x</sub> x<sub>t</sub> - &beta;<sub>z</sub> z<sub>t</sub>)
- &phi;<sub>1</sub> (y<sub>t-1</sub> - &beta;<sub>0</sub> - &beta;<sub>x</sub> x<sub>t-1</sub> - &beta;<sub>z</sub> z<sub>t-1</sub>)
- &phi;<sub>2</sub> (y<sub>t-2</sub> - &beta;<sub>0</sub> - &beta;<sub>x</sub> x<sub>t-2</sub> - &beta;<sub>z</sub> z<sub>t-2</sub>)
= &epsilon;<sub>t</sub> - &theta;<sub>1</sub> &epsilon;<sub>t-1</sub> - &theta;<sub>2</sub> &epsilon;<sub>t-2</sub>
</code>
</pre>

This shows us the grace of the <code>B</code> shift notation. This
equation block is repeated for all <code>t</code> (with out of range
indices denoting zero values). For a <code>T</code> time step system we
get a system of <code>T</code> equalities in <code>T + 7</code>
equations (minimizing norm <code>ε</code>). This also shows us that
while the system is linear in the data, it is non-linear in the fit
coefficients.

All of the above is a long way of saying: “given the `pdq(2, 0, 2)`
specification and <code>y, x, z</code>, the modeling system then fits
for <code>φ, β, θ, ε</code> (with <code>ε</code> small norm).” I.e., we
don’t have to worry over the above transformations- that is the job of
the solver.

Note: I agree with the Prophet authors that the user has to be involved
in specifying `pdq(2, 0, 2)`. Many auto-ARIMA systems seem to silently
fail in presence of external regressors. Here is an example of “hey
let’s use auto-arima” failing for tides and even its own package help
example:
<https://github.com/WinVector/Examples/blob/main/Tides/TideR_ARIMA.md>.
All mean mean to say is: we can give ourselves permission to use
non-ARIMA methods (more on this in [“A Time Series
Apologia”](https://github.com/WinVector/Examples/blob/16f31262873a649af2ad8aaa4c01f550ee60e72f/TS/TS_example.md))
in addition to trying ARIMA methods. The additional ARIMA driven
concerns and checks (such as looking for unit roots, worrying about
co-linear regressors) are more to do with the solution formulation
(recursive equations) than the nature of forecast problems.

Normally, we don’t have to care so much about model structure- as we are
protected from that by calling `predict()` or `forecast()`. However, in
this case we are very concerned if model structure will or will not
allow us to express what we think the external regressors actually do
(i.e. model structure).

This is what we meant about the chosen package specifying the modeling
recurrence equations (i.e. taking that choice out of our hands). We can
specify modeling the total, but not unobserved sub-populations of the
system.

Frankly ARIMAX/SARIMAX can be a false path for business modelers. Time
series research didn’t actually stop at or actually consolidate on this
terminology. Instead, transfer function methods and other more further
developed systems are studied. Roughly: the scientific community is well
served by ARIMAX. The research community moved on from ARIMAX. And, the
business community *wishes* ARIMAX was in fact the dominant method, as
it is the dominant software offered.

An odd point in this direction is: ARIMA prediction of tides. In fact
tides are formed by external regressors: the gravitational attraction of
the sun and moon. However just giving the ARIMA the exact periodicities
of these regressors is enough for it to model the entire system
*without* those inputs.

``` r
# https://otexts.com/fpp3/regarima.html
d_train <- read.csv('d_train.csv', stringsAsFactors = FALSE)
d_test <- read.csv('d_test.csv', stringsAsFactors = FALSE)

fable_model <- (
  d_train %>%
    tsibble(index=time_tick) %>%
    model(
      ARIMA(y ~ 
              1  # turn off must specify constant warning
            + z_0   # external regressor (can also use xreg(z_0))
            + x_0   # external regressor (can also use xreg(x_0))
            + pdq(2, 0, 2)   # AR=MA=2, I=0
            + PDQ(0, 0, 0)   # turn off seasonality (help(ARIMA))
            )
    )
)
coef(fable_model)
```

    ## # A tibble: 7 × 6
    ##   .model                            term  estimate std.error statistic   p.value
    ##   <chr>                             <chr>    <dbl>     <dbl>     <dbl>     <dbl>
    ## 1 ARIMA(y ~ 1 + z_0 + x_0 + pdq(2,… ar1     1.92      0.0114  168.     0        
    ## 2 ARIMA(y ~ 1 + z_0 + x_0 + pdq(2,… ar2    -0.954     0.0112  -85.2    0        
    ## 3 ARIMA(y ~ 1 + z_0 + x_0 + pdq(2,… ma1    -0.996     0.0321  -31.0    9.55e-148
    ## 4 ARIMA(y ~ 1 + z_0 + x_0 + pdq(2,… ma2     0.319     0.0323    9.88   5.37e- 22
    ## 5 ARIMA(y ~ 1 + z_0 + x_0 + pdq(2,… z_0    -0.0135    1.05     -0.0128 9.90e-  1
    ## 6 ARIMA(y ~ 1 + z_0 + x_0 + pdq(2,… x_0    14.8       0.275    54.0    8.40e-296
    ## 7 ARIMA(y ~ 1 + z_0 + x_0 + pdq(2,… inte…  43.4       2.03     21.4    2.33e- 83

Notice we recovered good estimates of the autoregressive terms `b_auto`
(`ar1`, `ar2`), transient external effect coefficient `b_x` (`x_0`). We
did not get a good estimate of the durable external effect coefficient
`z_0` (`b_z`), so we did not infer how changes in this variable affect
results.

We would be able to forecast, as the auto-regressive terms dominate. We
would not be able to plan, as we don’t have a good estimate of `z_0`
(`b_z`).

``` r
model_specification
```

    ## $b_auto_0
    ## [1] 1.280413
    ## 
    ## $b_imp_0
    ## [1] -10.4
    ## 
    ## $b_auto
    ## [1]  1.975377 -1.000000
    ## 
    ## $b_z
    ## [1] 14.2
    ## 
    ## $b_x
    ## [1] 16.1
    ## 
    ## $generating_lags
    ## [1] 1 2
    ## 
    ## $modeling_lags
    ## [1] 1 2
    ## 
    ## $error_scale
    ## [1] 3.2

``` r
preds <-  (
  fable_model %>%
    forecast(new_data=tsibble(d_test, index=time_tick)) 
)
d_test['fable ARIMAX prediction'] = preds['.mean']

# Rsquared
sse <- sum((d_test[['y']] - d_test[['fable ARIMAX prediction']])**2)
sey <- sum((d_test[['y']] - mean(d_test[['y']]))**2)
rsq <- 1 - sse/sey
# RMSE
rmse <- sqrt(mean((d_test[['y']] - d_test[['fable ARIMAX prediction']])**2))

(
  ggplot(
    data=d_test,
    mapping=aes(x=time_tick)
  )
  + geom_step(mapping=aes(y=`fable ARIMAX prediction`), direction='mid', color='blue')
  + geom_point(mapping=aes(y=y, shape=ext_regressors, color=ext_regressors), size=2)
  + ggtitle(paste0("fable package on held out data, rmse: ", 
    sprintf('%.2f', rmse), ', rsq: ', sprintf('%.2f', rsq)))
) 
```

![](ts_example_files/figure-gfm/unnamed-chunk-5-1.png)<!-- -->

## Fitting with an external regressor using the forecast package

Forecast formulation:

<code> (1 - φ<sub>1</sub> B - … - φ<sub>p</sub> B<sup>p</sup>)
(y<sup>′</sup><sub>t</sub> - μ) = c + (1 - θ<sub>1</sub> B - … -
θ<sub>q</sub> B<sup>q</sup>) ε<sub>t</sub> </code>

where <code>y<sup>′</sup><sub>t</sub> = (1 - B)<sup>d</sup>
y<sub>t</sub></code>, <code>μ = mean(y<sup>′</sup><sub>t</sub>)</code>.

``` r
# https://otexts.com/fpp3/regarima.html
d_train <- read.csv('d_train.csv', stringsAsFactors = FALSE)
d_test <- read.csv('d_test.csv', stringsAsFactors = FALSE)
forecast_model <- Arima(
  ts(d_train[['y']], start=d_train[['time_tick']][1]), 
  order=c(2, 0, 2), 
  xreg=ts(d_train[, c('z_0', 'x_0')], start=d_train[['time_tick']][1])
  )

forecast_model
```

    ## Series: ts(d_train[["y"]], start = d_train[["time_tick"]][1]) 
    ## Regression with ARIMA(2,0,2) errors 
    ## 
    ## Coefficients:
    ##          ar1      ar2      ma1     ma2  intercept      z_0      x_0
    ##       1.9250  -0.9542  -0.9960  0.3194    43.3823  -0.0135  14.8366
    ## s.e.  0.0114   0.0112   0.0321  0.0323     2.0318   1.0531   0.2749
    ## 
    ## sigma^2 = 33.1:  log likelihood = -3104.38
    ## AIC=6224.76   AICc=6224.91   BIC=6263.86

Notice the recovered durable effect coefficient is way too low.

``` r
preds <- forecast(
  forecast_model, 
  xreg=ts(d_test[, c('z_0', 'x_0')], 
  start=d_test[['time_tick']][1]))
d_test['forecast ARIMAX'] <- as.numeric(preds$mean)

# Rsquared
sse <- sum((d_test[['y']] - d_test[['forecast ARIMAX']])**2)
sey <- sum((d_test[['y']] - mean(d_test[['y']]))**2)
rsq <- 1 - sse/sey

# RMSE
rmse <- sqrt(mean((d_test[['y']] - d_test[['forecast ARIMAX']])**2))

(
  ggplot(
    data=d_test,
    mapping=aes(x=time_tick)
  )
  + geom_step(mapping=aes(y=`forecast ARIMAX`), direction='mid', color='blue')
  + geom_point(mapping=aes(y=y, shape=ext_regressors, color=ext_regressors), size=2)
  + ggtitle(paste0(
    "forecast package on held out data, rmse: ", 
    sprintf('%.2f', rmse), ', rsq: ', sprintf('%.2f', rsq)))
) 
```

![](ts_example_files/figure-gfm/unnamed-chunk-7-1.png)<!-- -->
