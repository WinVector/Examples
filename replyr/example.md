[`replyr`](https://github.com/WinVector/replyr) is an [`R`](https://cran.r-project.org) package that contains extensions, adaptions, and work-arounds to make remote `R` `dplyr` data sources (including big data systems such as `Spark`) behave more like local data. This allows the analyst to more easily develop and debug procedures that simultaneously work on a variety of data services (in-memory `data.frame`, `SQLite`, `PostgreSQL`, and `Spark2` currently being the primary supported platforms).

![](replyrs.png)

Example
-------

Suppose we had a large data set hosted on a `Spark` cluster that we wished to work with using `dplyr` and `sparklyr` (for this article we will simulate such using data loaded into `Spark` from the `nycflights13` package).

We will work a trivial example: taking a quick peek at your data. The analyst should always be able to and willing to look at the data.

It is easy to look at the top of the data, or any specific set of rows of the data.

Either through `print()` (which is much safter with `tbl_df` derived classes, than with base `data.frame`).

``` r
print(flts)
```

    ## Source:   query [3.368e+05 x 19]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##     year month   day dep_time sched_dep_time dep_delay arr_time
    ##    <int> <int> <int>    <int>          <int>     <dbl>    <int>
    ## 1   2013     1     1      517            515         2      830
    ## 2   2013     1     1      533            529         4      850
    ## 3   2013     1     1      542            540         2      923
    ## 4   2013     1     1      544            545        -1     1004
    ## 5   2013     1     1      554            600        -6      812
    ## 6   2013     1     1      554            558        -4      740
    ## 7   2013     1     1      555            600        -5      913
    ## 8   2013     1     1      557            600        -3      709
    ## 9   2013     1     1      557            600        -3      838
    ## 10  2013     1     1      558            600        -2      753
    ## # ... with 3.368e+05 more rows, and 12 more variables:
    ## #   sched_arr_time <int>, arr_delay <dbl>, carrier <chr>, flight <int>,
    ## #   tailnum <chr>, origin <chr>, dest <chr>, air_time <dbl>,
    ## #   distance <dbl>, hour <dbl>, minute <dbl>, time_hour <dbl>

Or with `dplyr::glimpse()`:

``` r
dplyr::glimpse(flts)
```

    ## Observations: 3.368e+05
    ## Variables: 19
    ## $ year           <int> 2013, 2013, 2013, 2013, 2013, 2013, 2013, 2013,...
    ## $ month          <int> 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,...
    ## $ day            <int> 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,...
    ## $ dep_time       <int> 517, 533, 542, 544, 554, 554, 555, 557, 557, 55...
    ## $ sched_dep_time <int> 515, 529, 540, 545, 600, 558, 600, 600, 600, 60...
    ## $ dep_delay      <dbl> 2, 4, 2, -1, -6, -4, -5, -3, -3, -2, -2, -2, -2...
    ## $ arr_time       <int> 830, 850, 923, 1004, 812, 740, 913, 709, 838, 7...
    ## $ sched_arr_time <int> 819, 830, 850, 1022, 837, 728, 854, 723, 846, 7...
    ## $ arr_delay      <dbl> 11, 20, 33, -18, -25, 12, 19, -14, -8, 8, -2, -...
    ## $ carrier        <chr> "UA", "UA", "AA", "B6", "DL", "UA", "B6", "EV",...
    ## $ flight         <int> 1545, 1714, 1141, 725, 461, 1696, 507, 5708, 79...
    ## $ tailnum        <chr> "N14228", "N24211", "N619AA", "N804JB", "N668DN...
    ## $ origin         <chr> "EWR", "LGA", "JFK", "JFK", "LGA", "EWR", "EWR"...
    ## $ dest           <chr> "IAH", "IAH", "MIA", "BQN", "ATL", "ORD", "FLL"...
    ## $ air_time       <dbl> 227, 227, 160, 183, 116, 150, 158, 53, 140, 138...
    ## $ distance       <dbl> 1400, 1416, 1089, 1576, 762, 719, 1065, 229, 94...
    ## $ hour           <dbl> 5, 5, 5, 5, 6, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5,...
    ## $ minute         <dbl> 15, 29, 40, 45, 0, 58, 0, 0, 0, 0, 0, 0, 0, 0, ...
    ## $ time_hour      <dbl> 2013, 2013, 2013, 2013, 2013, 2013, 2013, 2013,...

What `replyr` adds to the task of "looking at the data" is a rough equivalent to `base::summary()`: a few per-column statistics.

``` r
# using dev version of replyr https://github.com/WinVector/replyr
replyr::replyr_summary(flts, 
                       countUniqueNonNum= TRUE)
```

    ##            column index     class  nrows  nna nunique  min  max
    ## 1            year     1   integer 336776    0      NA 2013 2013
    ## 2           month     2   integer 336776    0      NA    1   12
    ## 3             day     3   integer 336776    0      NA    1   31
    ## 4        dep_time     4   integer 336776 8255      NA    1 2400
    ## 5  sched_dep_time     5   integer 336776    0      NA  106 2359
    ## 6       dep_delay     6   numeric 336776 8255      NA  -43 1301
    ## 7        arr_time     7   integer 336776 8713      NA    1 2400
    ## 8  sched_arr_time     8   integer 336776    0      NA    1 2359
    ## 9       arr_delay     9   numeric 336776 9430      NA  -86 1272
    ## 10        carrier    10 character 336776    0      16   NA   NA
    ## 11         flight    11   integer 336776    0      NA    1 8500
    ## 12        tailnum    12 character 336776    0    4044   NA   NA
    ## 13         origin    13 character 336776    0       3   NA   NA
    ## 14           dest    14 character 336776    0     105   NA   NA
    ## 15       air_time    15   numeric 336776 9430      NA   20  695
    ## 16       distance    16   numeric 336776    0      NA   17 4983
    ## 17           hour    17   numeric 336776    0      NA    1   23
    ## 18         minute    18   numeric 336776    0      NA    0   59
    ## 19      time_hour    19   numeric 336776    0      NA 2013 2013
    ##           mean          sd lexmin lexmax
    ## 1  2013.000000    0.000000   <NA>   <NA>
    ## 2     6.548510    3.414457   <NA>   <NA>
    ## 3    15.710787    8.768607   <NA>   <NA>
    ## 4  1349.109947  488.281791   <NA>   <NA>
    ## 5  1344.254840  467.335756   <NA>   <NA>
    ## 6    12.639070   40.210061   <NA>   <NA>
    ## 7  1502.054999  533.264132   <NA>   <NA>
    ## 8  1536.380220  497.457142   <NA>   <NA>
    ## 9     6.895377   44.633292   <NA>   <NA>
    ## 10          NA          NA     9E     YV
    ## 11 1971.923620 1632.471938   <NA>   <NA>
    ## 12          NA          NA   <NA>   <NA>
    ## 13          NA          NA    EWR    LGA
    ## 14          NA          NA    ABQ    XNA
    ## 15  150.686460   93.688305   <NA>   <NA>
    ## 16 1039.912604  733.233033   <NA>   <NA>
    ## 17   13.180247    4.661316   <NA>   <NA>
    ## 18   26.230100   19.300846   <NA>   <NA>
    ## 19 2013.000000    0.000000   <NA>   <NA>

Note: the above summary has problems with `NA` in `character` columns with `Spark`, and thus is mis-reporting the `NA` count in the `tailum` column. We are working on the issue. That is also one of the advantages of taking your work-arounds from a package: when they do improve you can easily incorporate bring the improvements into your own work by a mere package update.

As we see, `replyr` summary returns data in a data frame, and can deal with multiple column types.

We could also use `dplyr::summarize_each` for the task, but it has the minor downside of returning the data in a wide form.

``` r
# currently throws if tailnum left in column list 
flts %>% summarize_each(funs(min, max, mean, sd), 
                        -tailnum)
```

    ## Source:   query [1 x 72]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE
    ## 
    ##   year_min month_min day_min dep_time_min sched_dep_time_min dep_delay_min
    ##      <int>     <int>   <int>        <int>              <int>         <dbl>
    ## 1     2013         1       1            1                106           -43
    ## # ... with 66 more variables: arr_time_min <int>,
    ## #   sched_arr_time_min <int>, arr_delay_min <dbl>, carrier_min <chr>,
    ## #   flight_min <int>, origin_min <chr>, dest_min <chr>,
    ## #   air_time_min <dbl>, distance_min <dbl>, hour_min <dbl>,
    ## #   minute_min <dbl>, time_hour_min <dbl>, year_max <int>,
    ## #   month_max <int>, day_max <int>, dep_time_max <int>,
    ## #   sched_dep_time_max <int>, dep_delay_max <dbl>, arr_time_max <int>,
    ## #   sched_arr_time_max <int>, arr_delay_max <dbl>, carrier_max <chr>,
    ## #   flight_max <int>, origin_max <chr>, dest_max <chr>,
    ## #   air_time_max <dbl>, distance_max <dbl>, hour_max <dbl>,
    ## #   minute_max <dbl>, time_hour_max <dbl>, year_mean <dbl>,
    ## #   month_mean <dbl>, day_mean <dbl>, dep_time_mean <dbl>,
    ## #   sched_dep_time_mean <dbl>, dep_delay_mean <dbl>, arr_time_mean <dbl>,
    ## #   sched_arr_time_mean <dbl>, arr_delay_mean <dbl>, carrier_mean <dbl>,
    ## #   flight_mean <dbl>, origin_mean <dbl>, dest_mean <dbl>,
    ## #   air_time_mean <dbl>, distance_mean <dbl>, hour_mean <dbl>,
    ## #   minute_mean <dbl>, time_hour_mean <dbl>, year_sd <dbl>,
    ## #   month_sd <dbl>, day_sd <dbl>, dep_time_sd <dbl>,
    ## #   sched_dep_time_sd <dbl>, dep_delay_sd <dbl>, arr_time_sd <dbl>,
    ## #   sched_arr_time_sd <dbl>, arr_delay_sd <dbl>, carrier_sd <dbl>,
    ## #   flight_sd <dbl>, origin_sd <dbl>, dest_sd <dbl>, air_time_sd <dbl>,
    ## #   distance_sd <dbl>, hour_sd <dbl>, minute_sd <dbl>, time_hour_sd <dbl>

``` r
flts %>% summarize_each(funs(min, max, mean, sd))
```

    ## Source:   query [1 x 76]
    ## Database: spark connection master=local[4] app=sparklyr local=TRUE

    ## Error: Variables must be length 1 or 1.
    ## Problem variables: 'tailnum_min'

Special code for remote data is needed as none of the obvious "one liner" candidates (`base::summary()`, or `broom:glance()`) are not currently (as of March 4, 2017) intended to work with remote data sources.

``` r
summary(flts)
```

    ##     Length Class          Mode
    ## src 1      src_spark      list
    ## ops 3      op_base_remote list

``` r
str(flts)
```

    ## List of 2
    ##  $ src:List of 1
    ##   ..$ con:List of 11
    ##   .. ..$ master       : chr "local[4]"
    ##   .. ..$ method       : chr "shell"
    ##   .. ..$ app_name     : chr "sparklyr"
    ##   .. ..$ config       :List of 5
    ##   .. .. ..$ sparklyr.cores.local              : int 4
    ##   .. .. ..$ spark.sql.shuffle.partitions.local: int 4
    ##   .. .. ..$ spark.env.SPARK_LOCAL_IP.local    : chr "127.0.0.1"
    ##   .. .. ..$ sparklyr.csv.embedded             : chr "^1.*"
    ##   .. .. ..$ sparklyr.shell.driver-class-path  : chr ""
    ##   .. .. ..- attr(*, "config")= chr "default"
    ##   .. .. ..- attr(*, "file")= chr "/Library/Frameworks/R.framework/Versions/3.3/Resources/library/sparklyr/conf/config-template.yml"
    ##   .. ..$ spark_home   : chr "/Users/johnmount/Library/Caches/spark/spark-2.0.0-bin-hadoop2.7"
    ##   .. ..$ backend      :Classes 'sockconn', 'connection'  atomic [1:1] 6
    ##   .. .. .. ..- attr(*, "conn_id")=<externalptr> 
    ##   .. ..$ monitor      :Classes 'sockconn', 'connection'  atomic [1:1] 5
    ##   .. .. .. ..- attr(*, "conn_id")=<externalptr> 
    ##   .. ..$ output_file  : chr "/var/folders/7q/h_jp2vj131g5799gfnpzhdp80000gn/T//Rtmp71iVSp/filed928bfb6274_spark.log"
    ##   .. ..$ spark_context:Classes 'spark_jobj', 'shell_jobj' <environment: 0x7fd2cb0df230> 
    ##   .. ..$ java_context :Classes 'spark_jobj', 'shell_jobj' <environment: 0x7fd2cb063f08> 
    ##   .. ..$ hive_context :Classes 'spark_jobj', 'shell_jobj' <environment: 0x7fd2cc6d2140> 
    ##   .. ..- attr(*, "class")= chr [1:3] "spark_connection" "spark_shell_connection" "DBIConnection"
    ##   ..- attr(*, "class")= chr [1:3] "src_spark" "src_sql" "src"
    ##  $ ops:List of 3
    ##   ..$ src :List of 1
    ##   .. ..$ con:List of 11
    ##   .. .. ..$ master       : chr "local[4]"
    ##   .. .. ..$ method       : chr "shell"
    ##   .. .. ..$ app_name     : chr "sparklyr"
    ##   .. .. ..$ config       :List of 5
    ##   .. .. .. ..$ sparklyr.cores.local              : int 4
    ##   .. .. .. ..$ spark.sql.shuffle.partitions.local: int 4
    ##   .. .. .. ..$ spark.env.SPARK_LOCAL_IP.local    : chr "127.0.0.1"
    ##   .. .. .. ..$ sparklyr.csv.embedded             : chr "^1.*"
    ##   .. .. .. ..$ sparklyr.shell.driver-class-path  : chr ""
    ##   .. .. .. ..- attr(*, "config")= chr "default"
    ##   .. .. .. ..- attr(*, "file")= chr "/Library/Frameworks/R.framework/Versions/3.3/Resources/library/sparklyr/conf/config-template.yml"
    ##   .. .. ..$ spark_home   : chr "/Users/johnmount/Library/Caches/spark/spark-2.0.0-bin-hadoop2.7"
    ##   .. .. ..$ backend      :Classes 'sockconn', 'connection'  atomic [1:1] 6
    ##   .. .. .. .. ..- attr(*, "conn_id")=<externalptr> 
    ##   .. .. ..$ monitor      :Classes 'sockconn', 'connection'  atomic [1:1] 5
    ##   .. .. .. .. ..- attr(*, "conn_id")=<externalptr> 
    ##   .. .. ..$ output_file  : chr "/var/folders/7q/h_jp2vj131g5799gfnpzhdp80000gn/T//Rtmp71iVSp/filed928bfb6274_spark.log"
    ##   .. .. ..$ spark_context:Classes 'spark_jobj', 'shell_jobj' <environment: 0x7fd2cb0df230> 
    ##   .. .. ..$ java_context :Classes 'spark_jobj', 'shell_jobj' <environment: 0x7fd2cb063f08> 
    ##   .. .. ..$ hive_context :Classes 'spark_jobj', 'shell_jobj' <environment: 0x7fd2cc6d2140> 
    ##   .. .. ..- attr(*, "class")= chr [1:3] "spark_connection" "spark_shell_connection" "DBIConnection"
    ##   .. ..- attr(*, "class")= chr [1:3] "src_spark" "src_sql" "src"
    ##   ..$ x   :Classes 'ident', 'sql', 'character'  chr "flights"
    ##   ..$ vars: chr [1:19] "year" "month" "day" "dep_time" ...
    ##   ..- attr(*, "class")= chr [1:3] "op_base_remote" "op_base" "op"
    ##  - attr(*, "class")= chr [1:4] "tbl_spark" "tbl_sql" "tbl_lazy" "tbl"

``` r
packageVersion('broom')
```

    ## [1] '0.4.2'

``` r
broom::glance(flts)
```

    ## Error: glance doesn't know how to deal with data of class tbl_sparktbl_sqltbl_lazytbl

The source for the examples can be found [here](https://github.com/WinVector/Examples/blob/master/replyr/example.Rmd).

Conclusion
----------

`replyr_summary` is not the only service `replyr` supplies, `replyr` includes many more adaptions [including my own version of case-completion](http://www.win-vector.com/blog/2017/02/the-zero-bug/).

Roughly `replyr` is where I collect my adaptions so they don't infest application code. `replyr` a way you can use heavy-duty big-data machinery, while keeping you fingers out of the gears.
