Dependencies
================
Win-Vector LLC
11/29/2017

Set up our example.

``` r
packageVersion("dplyr")
```

    ## [1] '0.7.4'

``` r
my_db <- DBI::dbConnect(RSQLite::SQLite(),
                        ":memory:")
d <- dplyr::copy_to(my_db, 
                    data.frame(val = c(0, 5),
                               a_1 = "UNINITIALIZED",
                               a_2 = "UNINITIALIZED"), 
                    'd')
```

Run, and find a non-signalling data-mangle issue. For our example we are assigning paired columns `a_1` and `a_2` to complementary treatment and control groups. In this case we do this by simulating an if/else conditional assignment using `ifelse(,,)` value operators (we could have done this different ways, but this is one possible solution that could occur in practice).

``` r
# all values in a_1 and a_2 should
# be "treatment" or "control" after
# the following statement.  
# That is not the case.
dplyr::mutate(d,
              cond = val>2,
              a_1 = ifelse( cond, 
                            'treatment', 
                            a_1),
              a_2 = ifelse( cond, 
                            'control', 
                            a_2),
              a_1 = ifelse( !( cond ), 
                            'control', 
                            a_1),
              a_2 = ifelse( !( cond ), 
                            'treatment', 
                            a_2))
```

    ## # Source:   lazy query [?? x 4]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##     val           a_1  cond       a_2
    ##   <dbl>         <chr> <int>     <chr>
    ## 1     0       control     0 treatment
    ## 2     5 UNINITIALIZED     1   control

[`seplyr`](https://winvector.github.io/seplyr/) work-around: break up the steps into safe blocks ([announcement](http://www.win-vector.com/blog/2017/11/win-vector-llc-announces-new-big-data-in-r-tools/)).

``` r
library("seplyr")
```

    ## Loading required package: wrapr

``` r
plan <- if_else_device(
              testexpr = "val>2",
              thenexprs = c("a_1" := "'treatment'",
                            "a_2" := "'control'"),
              elseexprs = c("a_1" := "'control'",
                            "a_2" := "'treatment'")) %.>% 
  partition_mutate_se(.)

print(plan)
```

    ## $group00001
    ## ifebtest_yqzh5dmazi7c 
    ##               "val>2" 
    ## 
    ## $group00002
    ##                                                a_1 
    ## "ifelse( ifebtest_yqzh5dmazi7c, 'treatment', a_1)" 
    ##                                                a_2 
    ##   "ifelse( ifebtest_yqzh5dmazi7c, 'control', a_2)" 
    ## 
    ## $group00003
    ##                                                     a_1 
    ##   "ifelse( !( ifebtest_yqzh5dmazi7c ), 'control', a_1)" 
    ##                                                     a_2 
    ## "ifelse( !( ifebtest_yqzh5dmazi7c ), 'treatment', a_2)"

``` r
d %.>% 
  mutate_seb(., plan) %.>% 
  select_se(., grepdf("^ifebtest_", ., invert = TRUE))
```

    ## # Source:   lazy query [?? x 3]
    ## # Database: sqlite 3.19.3 [:memory:]
    ##     val       a_1       a_2
    ##   <dbl>     <chr>     <chr>
    ## 1     0   control treatment
    ## 2     5 treatment   control
