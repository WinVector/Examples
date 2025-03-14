PlotBass
================
2025-03-14

Re-plot the contents of [Bass_Stan.Rmd](Bass_Stan.Rmd).

Data from:

<https://stackoverflow.blog/2017/09/06/incredible-growth-python/>
<https://trends.stackoverflow.co/?tags=python>

``` r
library(wrapr)
library(ggplot2)
library(geomtextpath)
knitr::opts_chunk$set(fig.height = 6, fig.width = 9)
```

``` r
unpack[
  d_plot = d_plot, 
  d_predict = d_predict] := readRDS("Pandas_predictions_Bass.RDS")
```

``` r
d_predict[["what"]] <- paste0("model using data before ", gsub("Stan_pred_", "", d_predict$what, fixed = TRUE))
```

``` r
ggplot(mapping = aes(x = date, y = percent)) +
  geom_point(data = na.omit(d_plot)) +
  geom_line(
    data = na.omit(d_predict),
    mapping = aes(color = what, linetype = is_forecast)) +
  geom_textvline(
    data = data.frame(
      date = as.Date('2022-11-30'),
      label = 'ChatGPT release'
      ),
      mapping = aes(xintercept = date, label = label),
    ) + 
  ylab("% of Stack Overflow questions that month") + 
  ggtitle("projection of Pandas questions on Stack Overflow as a function of training date")
```

![](Plot_Bass_files/figure-gfm/unnamed-chunk-4-1.png)<!-- -->
