(author: John Mount)

Please Consider Using `wrapr::let()` for Replacement Tasks
==========================================================

From [`dplyr` issue 2916](https://github.com/tidyverse/dplyr/issues/2916).

The following *appears* to work.

``` r
suppressPackageStartupMessages(library("dplyr"))

COL <- "homeworld"
starwars %>%
  group_by(.data[[COL]]) %>%
  head(n=1)
```

    ## # A tibble: 1 x 14
    ## # Groups:   COL [1]
    ##             name height  mass hair_color skin_color eye_color birth_year
    ##            <chr>  <int> <dbl>      <chr>      <chr>     <chr>      <dbl>
    ## 1 Luke Skywalker    172    77      blond       fair      blue         19
    ## # ... with 7 more variables: gender <chr>, homeworld <chr>, species <chr>,
    ## #   films <list>, vehicles <list>, starships <list>, COL <chr>

Though notice it reports the grouping is by "`COL`", not by "`homeworld`". Also the data set now has `14` columns, not the original `13` from the `starwars` data set.

And this seemingly similar variation (currently) throws an exception:

``` r
homeworld <- "homeworld"

starwars %>%
  group_by(.data[[homeworld]]) %>% 
  head(n=1) 
```

    ## Error in mutate_impl(.data, dots): Evaluation error: Must subset with a string.

I know this will cost me what little community good-will I might have left (after already having raised this, unsolicited, many times), but *please* consider using our package `wrapr::let()` for tasks such as the above.

``` r
library("wrapr")

let(
  c(COL = "homeworld"),
  
  starwars %>%
    group_by(COL) %>%
    head(n=1)
)
```

    ## # A tibble: 1 x 13
    ## # Groups:   homeworld [1]
    ##             name height  mass hair_color skin_color eye_color birth_year
    ##            <chr>  <int> <dbl>      <chr>      <chr>     <chr>      <dbl>
    ## 1 Luke Skywalker    172    77      blond       fair      blue         19
    ## # ... with 6 more variables: gender <chr>, homeworld <chr>, species <chr>,
    ## #   films <list>, vehicles <list>, starships <list>

``` r
let(
  c(homeworld = "homeworld"),
  
  starwars %>%
    group_by(homeworld) %>% 
    head(n=1)
)
```

    ## # A tibble: 1 x 13
    ## # Groups:   homeworld [1]
    ##             name height  mass hair_color skin_color eye_color birth_year
    ##            <chr>  <int> <dbl>      <chr>      <chr>     <chr>      <dbl>
    ## 1 Luke Skywalker    172    77      blond       fair      blue         19
    ## # ... with 6 more variables: gender <chr>, homeworld <chr>, species <chr>,
    ## #   films <list>, vehicles <list>, starships <list>

Some explanation can be found [here](http://www.win-vector.com/blog/2017/06/wrapr-implementation-update/).
