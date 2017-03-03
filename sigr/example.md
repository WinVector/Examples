``` r
library('sigr')
help(sigr)
d <- data.frame(x=1:5)
d$y <- 2*d$x
```

``` r
cat(render(wrapFTest(d, 'x', 'y')))
```

**F Test** summary: (<i>R<sup>2</sup></i>=-0.38, *F*(1,3)=-0.82, *p*=n.s.).

``` r
cat(render(wrapCorTest(d, 'x', 'y')))
```

**Pearson's product-moment correlation**: (*r*=1, *p*&lt;1e-05).
