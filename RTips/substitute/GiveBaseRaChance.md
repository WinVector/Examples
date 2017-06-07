<!-- *.md is generated from *.Rmd. Please edit that file -->
From [*Advanced R* : substitute](http://adv-r.had.co.nz/Computing-on-the-language.html#substitute):

![](advrsubs.png)

We can confirm that code performs no substitution:

``` r
a <- 1
b <- 2
substitute(a + b + z)
```

    ## a + b + z

And it appears the effect is that substitute is designed to not take values from the global environment. So, as we see below, it isn't so much what environment we are running in that changes substitute's behavior, it is what environment the values are bound to that changes things.

``` r
(function() {
  a <- 1
  substitute(a + b + z, 
             environment())
})()
```

    ## 1 + b + z

We can in fact find many simple variations of substitute that work conveniently.

``` r
substitute(a + b + z, 
           list(a=1, b=2))
```

    ## 1 + 2 + z

``` r
substitute(a + b + z, 
           as.list(environment()))
```

    ## 1 + 2 + z

Often `R`'s documentation is a bit terse (or even incomplete) and functions (confusingly) change behavior based on type arguments and context. I say: always try a few variations to see if some simple alteration can make "base-R" work for you before giving up and delegating everything to an ad-on package.
