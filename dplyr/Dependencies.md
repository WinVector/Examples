Dependencies
================
Win-Vector LLC
11/30/2017

This is an example of an erroneous calculation in `dplyr` `0.7.4`, likely arising from expression to expression dependencies (which [we have written about before](http://www.win-vector.com/blog/2017/09/my-advice-on-dplyrmutate/)).

First we set up our example.

``` r
packageVersion("dplyr")
```

    ## [1] '0.7.4'

``` r
my_db <- DBI::dbConnect(RSQLite::SQLite(),
                        ":memory:")
d <- dplyr::copy_to(my_db, 
                    data.frame(valuesA = c("A", NA, NA),
                               valuesB = c("B", NA, NA),
                               canUseFix1 = c(TRUE, TRUE, FALSE),
                               fix1 = c('Fix_1_V1', "Fix_1_V2", "Fix_1_V3"),
                               canUseFix2 = c(FALSE, FALSE, TRUE),
                               fix2 = c('Fix_2_V1', "Fix_2_V2", "Fix_2_V3"),
                               stringsAsFactors = FALSE),
                    'd', 
                    temporary = TRUE, overwrite = TRUE)
knitr::kable(dplyr::collect(d))
```

| valuesA | valuesB |  canUseFix1| fix1       |  canUseFix2| fix2       |
|:--------|:--------|-----------:|:-----------|-----------:|:-----------|
| A       | B       |           1| Fix\_1\_V1 |           0| Fix\_2\_V1 |
| NA      | NA      |           1| Fix\_1\_V2 |           0| Fix\_2\_V2 |
| NA      | NA      |           0| Fix\_1\_V3 |           1| Fix\_2\_V3 |

For our example we are using `canUseFix1*` columns to find which positions of our `values*` columns can be replaced by the corresponding fix values. This is a common situation in data processing: where you have a column you wish to populate from a ordered sequence of alternate sources.

We could write this as nested `ifelse()` or coalesce. But suppose we had written the code as below.

``` r
fixed <- dplyr::mutate(d,
                       valuesA := ifelse(is.na(valuesA) & canUseFix1, 
                                         fix1, valuesA),
                       valuesA := ifelse(is.na(valuesA) & canUseFix2, 
                                         fix2, valuesA),
                       valuesB := ifelse(is.na(valuesB) & canUseFix1, 
                                         fix1, valuesB),
                       valuesB := ifelse(is.na(valuesB) & canUseFix2, 
                                         fix2, valuesB))

fixed ->.;
  dplyr::select(., valuesA, valuesB) ->.;
  dplyr::collect(.) ->.;
  knitr::kable(.)
```

| valuesA    | valuesB    |
|:-----------|:-----------|
| A          | B          |
| Fix\_1\_V2 | Fix\_1\_V2 |
| NA         | Fix\_2\_V3 |

Notice this *silently* failed! It gave a wrong answer, with no indicated error.

The third `valuesA` value remains at `NA` even though it should have been repaired by the fix 2 rule. This is not due to order of statements as the fix rules were deliberately chosen to apply to disjoint rows.

This has been filed as a [`dplyr` issue](https://github.com/tidyverse/dplyr/issues/3223), and the issue might be avoided by an [upcoming code change](https://github.com/tidyverse/dbplyr/commit/36a44cd4b5f70bc06fb004e7787157165766d091) (though we have not confirmed the relation/fix, and are not sure of the efficiency of that sort of transformation).

For our recommended current work-around, please see [here](http://winvector.github.io/FluidData/DplyrDependencies.html).
