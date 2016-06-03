It would be nice if the included `geom_step` example did not throw, but behaved more like the included `geom_line` example.

``` r
library('ggplot2')
d <- data.frame(x=1,y=1)
ggplot(data=d,aes(x=x,y=y)) + geom_point()
```

![](StepTrhow_files/figure-markdown_github/unnamed-chunk-1-1.png)

``` r
ggplot(data=d,aes(x=x,y=y)) + geom_line()
```

    ## geom_path: Each group consists of only one observation. Do you need to
    ## adjust the group aesthetic?

![](StepTrhow_files/figure-markdown_github/unnamed-chunk-1-2.png)

``` r
ggplot(data=d,aes(x=x,y=y)) + geom_step()
```

    ## Error in grid.Call.graphics(L_lines, x$x, x$y, index, x$arrow): invalid line type

![](StepTrhow_files/figure-markdown_github/unnamed-chunk-1-3.png)
