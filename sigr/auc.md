##### Setup.

``` r
library("dplyr")
```

    ## 
    ## Attaching package: 'dplyr'

    ## The following objects are masked from 'package:stats':
    ## 
    ##     filter, lag

    ## The following objects are masked from 'package:base':
    ## 
    ##     intersect, setdiff, setequal, union

``` r
library("plotly")
```

    ## Loading required package: ggplot2

    ## 
    ## Attaching package: 'plotly'

    ## The following object is masked from 'package:ggplot2':
    ## 
    ##     last_plot

    ## The following object is masked from 'package:stats':
    ## 
    ##     filter

    ## The following object is masked from 'package:graphics':
    ## 
    ##     layout

``` r
library("WVPlots")  # needs dev version from Github
library("microbenchmark")

set.seed(224)

mkData <- function(n) {
  d <- data.frame(x= runif(n),   # predictor
                  y= rnorm(n)>=0 # outcome/truth
  )
  d$cx <- 1-d$x # complement of x
  d$ny <- !d$y  # not y
  d
}
d <- mkData(5)
print(d)
```

    ##           x     y         cx    ny
    ## 1 0.7538008 FALSE 0.24619925  TRUE
    ## 2 0.5867451 FALSE 0.41325491  TRUE
    ## 3 0.3844693  TRUE 0.61553066 FALSE
    ## 4 0.9483048 FALSE 0.05169519  TRUE
    ## 5 0.6525606  TRUE 0.34743940 FALSE

The effect
----------

We are looking at the facts that `AUC(prediction, outcome) + AUC(1-prediction, outcome) == 1` and `AUC(prediction, outcome) + AUC(prediction, !outcome) == 1`.

``` r
plotlyROC <- function(predictions, target, title) {
  rocFrame <- WVPlots::graphROC(predictions, target)
  plot_ly(rocFrame$pointGraph, x = ~FalsePositiveRate, y = ~TruePositiveRate, 
        type='scatter', mode='lines+markers', hoverinfo= 'text', 
        text= ~ paste('threshold:', model, 
                      '</br>FalsePositiveRate:', FalsePositiveRate,
                      '</br>TruePositiveRate:', TruePositiveRate)) %>%
    layout(title= title)
}

plotlyROC(d$x, d$y, 'interactive version of base plot (when rendered to html)')
```

<!--html_preserve-->

<script type="application/json" data-for="htmlwidget-8a7b5a583a69569c54dd">{"x":{"layout":{"margin":{"b":40,"l":60,"t":25,"r":10},"title":"interactive version of base plot (when rendered to html)","xaxis":{"domain":[0,1],"title":"FalsePositiveRate"},"yaxis":{"domain":[0,1],"title":"TruePositiveRate"},"hovermode":"closest"},"source":"A","config":{"modeBarButtonsToAdd":[{"name":"Collaborate","icon":{"width":1000,"ascent":500,"descent":-50,"path":"M487 375c7-10 9-23 5-36l-79-259c-3-12-11-23-22-31-11-8-22-12-35-12l-263 0c-15 0-29 5-43 15-13 10-23 23-28 37-5 13-5 25-1 37 0 0 0 3 1 7 1 5 1 8 1 11 0 2 0 4-1 6 0 3-1 5-1 6 1 2 2 4 3 6 1 2 2 4 4 6 2 3 4 5 5 7 5 7 9 16 13 26 4 10 7 19 9 26 0 2 0 5 0 9-1 4-1 6 0 8 0 2 2 5 4 8 3 3 5 5 5 7 4 6 8 15 12 26 4 11 7 19 7 26 1 1 0 4 0 9-1 4-1 7 0 8 1 2 3 5 6 8 4 4 6 6 6 7 4 5 8 13 13 24 4 11 7 20 7 28 1 1 0 4 0 7-1 3-1 6-1 7 0 2 1 4 3 6 1 1 3 4 5 6 2 3 3 5 5 6 1 2 3 5 4 9 2 3 3 7 5 10 1 3 2 6 4 10 2 4 4 7 6 9 2 3 4 5 7 7 3 2 7 3 11 3 3 0 8 0 13-1l0-1c7 2 12 2 14 2l218 0c14 0 25-5 32-16 8-10 10-23 6-37l-79-259c-7-22-13-37-20-43-7-7-19-10-37-10l-248 0c-5 0-9-2-11-5-2-3-2-7 0-12 4-13 18-20 41-20l264 0c5 0 10 2 16 5 5 3 8 6 10 11l85 282c2 5 2 10 2 17 7-3 13-7 17-13z m-304 0c-1-3-1-5 0-7 1-1 3-2 6-2l174 0c2 0 4 1 7 2 2 2 4 4 5 7l6 18c0 3 0 5-1 7-1 1-3 2-6 2l-173 0c-3 0-5-1-8-2-2-2-4-4-4-7z m-24-73c-1-3-1-5 0-7 2-2 3-2 6-2l174 0c2 0 5 0 7 2 3 2 4 4 5 7l6 18c1 2 0 5-1 6-1 2-3 3-5 3l-174 0c-3 0-5-1-7-3-3-1-4-4-5-6z"},"click":"function(gd) { \n        // is this being viewed in RStudio?\n        if (location.search == '?viewer_pane=1') {\n          alert('To learn about plotly for collaboration, visit:\\n https://cpsievert.github.io/plotly_book/plot-ly-for-collaboration.html');\n        } else {\n          window.open('https://cpsievert.github.io/plotly_book/plot-ly-for-collaboration.html', '_blank');\n        }\n      }"}],"modeBarButtonsToRemove":["sendDataToCloud"]},"data":[{"x":[0.333333333333333,0.666666666666667,0.666666666666667,1,1],"y":[0,0,0.5,0.5,1],"mode":"lines+markers","hoverinfo":"text","text":["threshold: 0.948304814752191 \u003c/br>FalsePositiveRate: 0.333333333333333 \u003c/br>TruePositiveRate: 0","threshold: 0.753800751408562 \u003c/br>FalsePositiveRate: 0.666666666666667 \u003c/br>TruePositiveRate: 0","threshold: 0.652560597518459 \u003c/br>FalsePositiveRate: 0.666666666666667 \u003c/br>TruePositiveRate: 0.5","threshold: 0.586745094507933 \u003c/br>FalsePositiveRate: 1 \u003c/br>TruePositiveRate: 0.5","threshold: 0.384469341253862 \u003c/br>FalsePositiveRate: 1 \u003c/br>TruePositiveRate: 1"],"type":"scatter","line":{"fillcolor":"rgba(31,119,180,1)","color":"rgba(31,119,180,1)"},"xaxis":"x","yaxis":"y"}],"base_url":"https://plot.ly"},"evals":["config.modeBarButtonsToAdd.0.click"],"jsHooks":[]}</script>
<!--/html_preserve-->
``` r
WVPlots::ROCPlot(d,'x','y',TRUE,'base plot')
```

![](auc_files/figure-markdown_github/WVPlots-1.png)

``` r
WVPlots::ROCPlot(d,'cx','y',TRUE,'complemented x')
```

![](auc_files/figure-markdown_github/WVPlots-2.png)

``` r
WVPlots::ROCPlot(d,'x','ny',TRUE,'negated y')
```

![](auc_files/figure-markdown_github/WVPlots-3.png)

##### `ModelMetrics`

``` r
ModelMetrics::auc(d$y, d$x) +
  ModelMetrics::auc(d$y, d$cx)
```

    ## [1] 1

``` r
ModelMetrics::auc(d$y, d$x) +
  ModelMetrics::auc(d$ny, d$x)
```

    ## [1] 1

##### `sigr`

``` r
sigr::calcAUC(d$x, d$y) + 
  sigr::calcAUC(d$cx, d$y)
```

    ## [1] 1

``` r
sigr::calcAUC(d$x, d$y) +
  sigr::calcAUC(d$x, d$ny)
```

    ## [1] 1

##### `ROCR`

``` r
aucROCR <- function(predictions, target) {
  pred <- ROCR::prediction(predictions,
                           target)
  perf_AUC <- ROCR::performance(pred,
                                "auc")
  perf_AUC@y.values[[1]]
}

aucROCR(d$x, d$y) + 
  aucROCR(d$cx, d$y)
```

    ## [1] 1

``` r
aucROCR(d$x, d$y) + 
  aucROCR(d$x, d$ny)
```

    ## [1] 1

##### `AUC`

``` r
aucAUC <- function(predictions, target) {
  AUC::auc(AUC::roc(predictions, 
                  factor(ifelse(target, "1", "0"))))
}

aucAUC(d$x, d$y) +
  aucAUC(d$cx, d$y)
```

    ## [1] 1

``` r
aucAUC(d$x, d$y) +
  aucAUC(d$x, d$ny)
```

    ## [1] 1

##### `caret`

``` r
aucCaret <- function(predictions, target) {
  classes <- c("class1", "class2")
  df <- data.frame(obs= ifelse(target, 
                               "class1", 
                               "class2"),
                 pred = ifelse(predictions>0.5, 
                               "class1", 
                               "class2"),
                 class1 = predictions,
                 class2 = 1-predictions)
  caret::twoClassSummary(df, lev=classes)[['ROC']]
}


aucCaret(d$x, d$y) + 
  aucCaret(d$cx, d$y)
```

    ## [1] 1

``` r
aucCaret(d$x, d$y) + 
  aucCaret(d$x, d$ny)
```

    ## [1] 1

##### `pROC`

``` r
pROC::auc(y~x, d) + 
  pROC::auc(y~cx, d) # wrong
```

    ## [1] 1.666667

More tries with `pROC`.

From `help(roc)`

> direction
>
> in which direction to make the comparison? "auto" (default): automatically define in which group the median is higher and take the direction accordingly. "&gt;": if the predictor values for the control group are higher than the values of the case group (controls &gt; t &gt;= cases). "&lt;": if the predictor values for the control group are lower or equal than the values of the case group (controls &lt; t &lt;= cases).

``` r
pROC::auc(y~x, d, direction= '<') + 
  pROC::auc(y~cx, d, direction= '<')
```

    ## [1] 1

``` r
pROC::auc(y~x, d, direction= '<') +
  pROC::auc(ny~x, d, direction= '<')
```

    ## [1] 1

### Timing

``` r
dTime <- mkData(100)
ModelMetrics::auc(dTime$y, dTime$x)
```

    ## [1] 0.4248

``` r
sigr::calcAUC(dTime$x, dTime$y)
```

    ## [1] 0.4248

``` r
aucROCR(dTime$x, dTime$y)
```

    ## [1] 0.4248

``` r
aucAUC(dTime$x, dTime$y)
```

    ## [1] 0.4248

``` r
aucCaret(dTime$x, dTime$y)
```

    ## [1] 0.4248

``` r
pROC::auc(y~x, dTime, direction= '<')
```

    ## Area under the curve: 0.4248

``` r
sizes <- 2^(7:16)
rlist <- lapply(sizes,
                function(si) {
                  dTime <- mkData(si)
                  res <- microbenchmark(
                    ModelMetrics::auc(dTime$y, dTime$x),
                    sigr::calcAUC(dTime$x, dTime$y),
                    aucROCR(dTime$x, dTime$y),
                    aucAUC(dTime$x, dTime$y),
                    aucCaret(dTime$x, dTime$y),
                    pROC::auc(y~x, dTime, direction= '<'),
                    times=10L
                  )
                  res$size <- si
                  res
                })
res <- bind_rows(rlist)
# select down columns and control units
res %>% 
  group_by(expr,size) %>%
  mutate(time = time/1e9) %>% # move from NanoSeconds to seconds
  summarize(meanTimeS = mean(time), 
            q1 = quantile(time, probs=0.25),
            q2 = quantile(time, probs=0.5),
            q3 = quantile(time, probs=0.75)) %>%
  arrange(size,expr) -> plt
plt$expr <- reorder(plt$expr, -plt$q2)

# from: http://stackoverflow.com/a/22227846/6901725
base_breaks <- function(n = 10){
    function(x) {
        axisTicks(log10(range(x, na.rm = TRUE)), log = TRUE, n = n)
    }
}

ggplot(plt, aes(x=size, color=expr, fill=expr)) +
  geom_point(aes(y=meanTimeS)) +
  geom_line(aes(y=q2)) +
  geom_ribbon(aes(ymin=q1, ymax=q3), alpha=0.3, color=NA) +
  scale_x_log10(breaks= base_breaks()) + 
  scale_y_log10(breaks= base_breaks()) +
  ylab("time in seconds") +
  ggtitle("run times by AUC package and data size")
```

![](auc_files/figure-markdown_github/timing-1.png)
