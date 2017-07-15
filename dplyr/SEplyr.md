dplyr 0.7 Made Simpler
======================

I have been writing *a lot* ([too much](http://www.win-vector.com/blog/2017/07/better-grouped-summaries-in-dplyr/)) on the [`R`](https://www.r-project.org) topics `dplyr`/`rlang`/`tidyeval` lately. The reason is: [major changes were recently announced](https://blog.rstudio.org/2017/06/13/dplyr-0-7-0/). If you are going to use `dplyr` well and correctly going forward you may need to understand some of the new issues (if you don't use `dplyr` you can safely skip all of this). I am trying to work out (publicly) how to best incorporate the new methods into:

-   real world analyses,
-   reusable packages,
-   and teaching materials.

I think some of the apparent discomfort on my part comes from my feeling that `dplyr` never really gave standard evaluation (SE) a fair chance. In my opinion: `dplyr` is based strongly on non-standard evaluation (NSE, originally through [`lazyeval`](https://CRAN.R-project.org/package=lazyeval) and now through [`rlang`/`tidyeval`](https://CRAN.R-project.org/package=rlang)) more by the taste and choice than by actual analyst benefit or need. `dplyr` isn't my package, so it isn't my choice to make; but I can still have an informed opinion, which I will discuss below.

`dplyr` itself is a very powerful collection of useful data analysis methods or "verbs." In some sense it is a fairly pure expression of how you organize data transformations in *functional programming* terms. (By the way: [`data.table`](https://CRAN.R-project.org/package=data.table) is probably an equally fundamental powerful formation in *object oriented* terms.)

In *my opinion* there are only two places where `dplyr` truly benefits from or actually needs the (often complicated and confusing) full power of non-standard evaluation: in the `dplyr::mutate()` and `dplyr::summarize()` verbs.

I admit: a system that can't accept an arbitrary functions or expressions from the user lacks expressive power. However, the only place you truly need this power is when creating a new derived column in a `data.frame`. If you can do this then you can drive all of the other important data wrangling functions (row selection, row ordering, grouping, joining, and so on).

When I teach `R`, I teach you are going to have to copy your data at some point. You are fighting the `R` language if you try to completely avoid copying as you would in other more reference oriented languages. This is likely one of the reasons [Nathan Stephens and Garrett Grolemund define "Big Data" as](https://github.com/rstudio/Strata2016/blob/master/solutions/02-Big-Data.Rmd):

> Big Data ~ ≥ 1/3 RAM.

Once you accept you are going to make copies (which is not part of all systems, but in my opinion is a part of `R`) then you should take advantage of the fact you are going to make copies. In particular you should land, materialize, or reify the results of complicated user expressions as actual data columns (i.e., propagate data forward, not propagate code forward). Doing this wastes some space, but can actually be easier to parellize, potentially faster, easier to document, and much easier to debug.

There is no reason to shun code of the form:

``` r
suppressPackageStartupMessages(library("dplyr"))

starwars %>% 
  mutate( want_row = height > mass ) %>%
  filter( want_row ) %>%
  select( -want_row )
```

    ## # A tibble: 58 x 13
    ##                  name height  mass    hair_color  skin_color eye_color
    ##                 <chr>  <int> <dbl>         <chr>       <chr>     <chr>
    ##  1     Luke Skywalker    172    77         blond        fair      blue
    ##  2              C-3PO    167    75          <NA>        gold    yellow
    ##  3              R2-D2     96    32          <NA> white, blue       red
    ##  4        Darth Vader    202   136          none       white    yellow
    ##  5        Leia Organa    150    49         brown       light     brown
    ##  6          Owen Lars    178   120   brown, grey       light      blue
    ##  7 Beru Whitesun lars    165    75         brown       light      blue
    ##  8              R5-D4     97    32          <NA>  white, red       red
    ##  9  Biggs Darklighter    183    84         black       light     brown
    ## 10     Obi-Wan Kenobi    182    77 auburn, white        fair blue-gray
    ## # ... with 48 more rows, and 7 more variables: birth_year <dbl>,
    ## #   gender <chr>, homeworld <chr>, species <chr>, films <list>,
    ## #   vehicles <list>, starships <list>

And say you really *need* to write the more succinct:

``` r
starwars %>% 
  filter( height > mass )
```

    ## # A tibble: 58 x 13
    ##                  name height  mass    hair_color  skin_color eye_color
    ##                 <chr>  <int> <dbl>         <chr>       <chr>     <chr>
    ##  1     Luke Skywalker    172    77         blond        fair      blue
    ##  2              C-3PO    167    75          <NA>        gold    yellow
    ##  3              R2-D2     96    32          <NA> white, blue       red
    ##  4        Darth Vader    202   136          none       white    yellow
    ##  5        Leia Organa    150    49         brown       light     brown
    ##  6          Owen Lars    178   120   brown, grey       light      blue
    ##  7 Beru Whitesun lars    165    75         brown       light      blue
    ##  8              R5-D4     97    32          <NA>  white, red       red
    ##  9  Biggs Darklighter    183    84         black       light     brown
    ## 10     Obi-Wan Kenobi    182    77 auburn, white        fair blue-gray
    ## # ... with 48 more rows, and 7 more variables: birth_year <dbl>,
    ## #   gender <chr>, homeworld <chr>, species <chr>, films <list>,
    ## #   vehicles <list>, starships <list>

The first form doesn't waste much space (it adds a single new column among many) and is much easier to characterize and debug. By landing our filter criteria in a column it becomes data. Data is something we can reason about and process:

``` r
starwars %>% 
  mutate( want_row = height > mass ) %>%
  group_by( want_row ) %>% 
  summarize( count = n() )
```

    ## # A tibble: 3 x 2
    ##   want_row count
    ##      <lgl> <int>
    ## 1    FALSE     1
    ## 2     TRUE    58
    ## 3       NA    28

To help demonstrate and explore the expressive power of standard evaluation interfaces I am distributing a new small `R` package called [`seplyr`](https://github.com/WinVector/seplyr) (standard evaluation dplyr). `seplyr` is based on `dplyr`/`rlang`/`tidyeval` and is a thin wrapper that exposes equivalent standard evaluation interfaces for some of the more fundamental `dplyr` verbs ( `group_by()`, `arrange()`, `rename()`, `select()`, and `distinct()` ) and adds some of its own advanced verbs. It is similar to `dplyr`'s now-deprecated "SE verbs", but with a more array and list oriented interface (de-emphasizing use of "`...`" in function arguments).

For example, we can take some of the code from the [`dplyr` 0.7.0 announcement](https://blog.rstudio.org/2017/06/13/dplyr-0-7-0/):

``` r
my_var <- quo(homeworld)
# or my_var <- rlang::sym("homeworld")

starwars %>%
  group_by(!!my_var) %>%
  summarise_at(vars(height:mass), mean, na.rm = TRUE)
```

    ## # A tibble: 49 x 3
    ##         homeworld   height  mass
    ##             <chr>    <dbl> <dbl>
    ##  1       Alderaan 176.3333  64.0
    ##  2    Aleen Minor  79.0000  15.0
    ##  3         Bespin 175.0000  79.0
    ##  4     Bestine IV 180.0000 110.0
    ##  5 Cato Neimoidia 191.0000  90.0
    ##  6          Cerea 198.0000  82.0
    ##  7       Champala 196.0000   NaN
    ##  8      Chandrila 150.0000   NaN
    ##  9   Concord Dawn 183.0000  79.0
    ## 10       Corellia 175.0000  78.5
    ## # ... with 39 more rows

And translate it into standard evaluation verbs:

``` r
# install.packages("seplyr")
library("seplyr")

my_var <- "homeworld"
summary_vars <- c("height", "mass")

starwars %>%
  select_se( c(my_var, summary_vars) ) %>%
  group_by_se( my_var ) %>%
  summarise_all( mean, na.rm = TRUE )
```

    ## # A tibble: 49 x 3
    ##         homeworld   height  mass
    ##             <chr>    <dbl> <dbl>
    ##  1       Alderaan 176.3333  64.0
    ##  2    Aleen Minor  79.0000  15.0
    ##  3         Bespin 175.0000  79.0
    ##  4     Bestine IV 180.0000 110.0
    ##  5 Cato Neimoidia 191.0000  90.0
    ##  6          Cerea 198.0000  82.0
    ##  7       Champala 196.0000   NaN
    ##  8      Chandrila 150.0000   NaN
    ##  9   Concord Dawn 183.0000  79.0
    ## 10       Corellia 175.0000  78.5
    ## # ... with 39 more rows

This standard evaluation interface isn't so much a "more limited" version of `dplyr`, but a "more disciplined" approach to working *with* `dplyr`. We are using `rlang`/`tidyeval`, but that doesn't mean the user has to see the `rlang`/`tidyeval` internals at all times.

For the most part we are passing work to `dplyr` using very small (and clear) functions. You can see how to use the new `dplyr`/`rlang`/`tidyeval` methods by printing the source code (for example: `print(group_by_se)`).

Also, in [the development version of `seplyr`](https://github.com/WinVector/seplyr) we are building up some exciting "complex standard evaluation verbs" such as `add_group_indices()` and `add_group_sub_indices()` which are best explained through their own documentation or an example:

``` r
# devtools::install_github('WinVector/seplyr')
library("seplyr")
groupingVars = c("cyl", "gear")

datasets::mtcars %>%
  tibble::rownames_to_column('CarName') %>%
  select_se(c('CarName', 'cyl', 'gear', 'hp', 'wt')) %>%
  add_group_indices(groupingVars = groupingVars,
                    indexColumn = 'groupID') %>%
  add_group_sub_indices(groupingVars = groupingVars,
                       arrangeTerms = c('desc(hp)', 'wt'),
                       orderColumn = 'orderInGroup') %>%
  arrange_se(c('groupID', 'orderInGroup'))
```

    ## # A tibble: 32 x 7
    ##           CarName   cyl  gear    hp    wt groupID orderInGroup
    ##             <chr> <dbl> <dbl> <dbl> <dbl>   <dbl>        <dbl>
    ##  1  Toyota Corona     4     3    97 2.465       1            1
    ##  2     Volvo 142E     4     4   109 2.780       2            1
    ##  3       Merc 230     4     4    95 3.150       2            2
    ##  4     Datsun 710     4     4    93 2.320       2            3
    ##  5      Fiat X1-9     4     4    66 1.935       2            4
    ##  6       Fiat 128     4     4    66 2.200       2            5
    ##  7 Toyota Corolla     4     4    65 1.835       2            6
    ##  8      Merc 240D     4     4    62 3.190       2            7
    ##  9    Honda Civic     4     4    52 1.615       2            8
    ## 10   Lotus Europa     4     5   113 1.513       3            1
    ## # ... with 22 more rows
