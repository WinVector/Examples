Many of the object size estimation methods in `R` have different opinions as to whether they count environments, which can be a very large component of objects.

Some related articles:

-   [Trimming the Fat from glm Models in R](http://www.win-vector.com/blog/2014/05/trimming-the-fat-from-glm-models-in-r/)
-   [How and why to return functions in R](http://www.win-vector.com/blog/2015/04/how-and-why-to-return-functions-in-r/)

``` r
build1 <- function() {
  x <- 1:1e+7 # this variable will be in f's closure
  f = function(i) {
    print(x[[i]])
  }
  print(paste(
    "serialize size in construction environment",
    length(serialize(f, NULL))
  ))
  print(paste(
    "pryr::object_size in construction environment",
    pryr::object_size(f)
  ))
  print(paste(
    "utils::object.size in construction environment",
    utils::object.size(f)
  ))
  f
}

f <- build1()
```

    ## [1] "serialize size in construction environment 40014302"
    ## [1] "pryr::object_size in construction environment 19880"
    ## [1] "utils::object.size in construction environment 4608"

``` r
print(paste(
  "serialize size in global environment",
  length(serialize(f, NULL))
))
```

    ## [1] "serialize size in global environment 40014302"

``` r
print(paste(
  "pryr::object_size in global environment",
  pryr::object_size(f)
))
```

    ## [1] "pryr::object_size in global environment 40020144"

``` r
print(paste(
  "utils::object.size in global environment",
  utils::object.size(f)
))
```

    ## [1] "utils::object.size in global environment 4608"

(Filed as [pryr issue 37](https://github.com/hadley/pryr/issues/37), and closed.)
