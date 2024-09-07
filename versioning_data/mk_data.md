mk_data
================
2024-09-06

``` r
library(dplyr)
```

    ## 
    ## Attaching package: 'dplyr'

    ## The following objects are masked from 'package:stats':
    ## 
    ##     filter, lag

    ## The following objects are masked from 'package:base':
    ## 
    ##     intersect, setdiff, setequal, union

``` r
set.seed(2024)

d <- read.csv('Roxie_schedule_original.csv', strip.white = TRUE, stringsAsFactors = FALSE)
d$Date <- as.Date(d$Date, format='%Y-%B-%d')
d$EstimatedAttendance <- sample(c(233, 47), size=nrow(d), replace = TRUE)
d$Attendance <- round(d$EstimatedAttendance * runif(n = nrow(d)))
d$PopcornSales <- round(runif(n = nrow(d), min = 0.1, max = 0.2) * d$Attendance)

popcorn_sales <- d |>
  group_by(Date) |>
  summarize(PopcornSales = sum(PopcornSales)) |>
  ungroup() |>
  filter(format(Date, '%B') == 'August') |>
  as.data.frame()
write.csv(popcorn_sales, 'popcorn_sales.csv', row.names = FALSE)

knitr::kable(head(popcorn_sales))
```

| Date       | PopcornSales |
|:-----------|-------------:|
| 2024-08-01 |           25 |
| 2024-08-02 |          102 |
| 2024-08-03 |           76 |
| 2024-08-04 |           65 |
| 2024-08-05 |           13 |
| 2024-08-06 |           80 |

``` r
d$PopcornSales <- NULL

d$Attendance[format(d$Date, '%B') != 'August'] = d$EstimatedAttendance[format(d$Date, '%B') != 'August']

d_mixed <- d
d_mixed$EstimatedAttendance <- NULL
write.csv(d_mixed, 'Roxie_schedule_as_known_after_August.csv', row.names = FALSE)
knitr::kable(head(d_mixed))
```

| Date       | Movie                                                | Time    | Attendance |
|:-----------|:-----------------------------------------------------|:--------|-----------:|
| 2024-08-01 | Chronicles of a Wandering Saint                      | 6:40 pm |          6 |
| 2024-08-01 | Eno                                                  | 6:40 pm |         10 |
| 2024-08-01 | Longlegs                                             | 8:35 pm |        114 |
| 2024-08-01 | Staff Pick: Melvin and Howard (35mm)                 | 8:45 pm |         23 |
| 2024-08-02 | Made in England: The Films of Powell and Pressburger | 6:00 pm |        204 |
| 2024-08-02 | Lyd                                                  | 6:30 pm |        213 |

``` r
d_est <- d
d_est$Attendance <- NULL
write.csv(d_est, 'Roxie_schedule_as_known_before_August.csv', row.names = FALSE)
knitr::kable(head(d_est))
```

| Date       | Movie                                                | Time    | EstimatedAttendance |
|:-----------|:-----------------------------------------------------|:--------|--------------------:|
| 2024-08-01 | Chronicles of a Wandering Saint                      | 6:40 pm |                  47 |
| 2024-08-01 | Eno                                                  | 6:40 pm |                 233 |
| 2024-08-01 | Longlegs                                             | 8:35 pm |                 233 |
| 2024-08-01 | Staff Pick: Melvin and Howard (35mm)                 | 8:45 pm |                  47 |
| 2024-08-02 | Made in England: The Films of Powell and Pressburger | 6:00 pm |                 233 |
| 2024-08-02 | Lyd                                                  | 6:30 pm |                 233 |
