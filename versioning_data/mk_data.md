mk_data
================
2024-09-06

``` r
library(dplyr)
```

``` r
set.seed(2024)

d <- read.csv('Roxie_schedule_original.csv', strip.white = TRUE, stringsAsFactors = FALSE)
d$Date <- as.Date(d$Date, format='%Y-%B-%d')
d$EstimatedAttendance <- sample(c(233, 47), size=nrow(d), replace = TRUE)
d$Attendance <- round(d$EstimatedAttendance * runif(n = nrow(d)))
# some estimates are right
attendance_matches_indexes <- sort(sample.int(nrow(d), 0.05 * nrow(d), replace = FALSE))
d$Attendance[attendance_matches_indexes] <- d$EstimatedAttendance[attendance_matches_indexes]
match_table <- table(format(d$Date, format='%B'), d$EstimatedAttendance == d$Attendance)
stopifnot(sum(match_table > 0) == 4)

knitr::kable(match_table)
```

|           | FALSE | TRUE |
|:----------|------:|-----:|
| August    |    85 |    6 |
| September |   100 |    3 |

``` r
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
| 2024-08-01 |           28 |
| 2024-08-02 |           82 |
| 2024-08-03 |           65 |
| 2024-08-04 |           67 |
| 2024-08-05 |           15 |
| 2024-08-06 |           81 |

``` r
d$PopcornSales <- NULL

d$Attendance[format(d$Date, '%B') != 'August'] = d$EstimatedAttendance[format(d$Date, '%B') != 'August']

d_mixed <- d
d_mixed$EstimatedAttendance <- NULL
d_mixed <- d_mixed[-1, , drop = FALSE]
write.csv(d_mixed, 'Roxie_schedule_as_known_after_August.csv', row.names = FALSE)
knitr::kable(head(d_mixed))
```

|     | Date       | Movie                                                | Time    | Attendance |
|:----|:-----------|:-----------------------------------------------------|:--------|-----------:|
| 2   | 2024-08-01 | Eno                                                  | 6:40 pm |         10 |
| 3   | 2024-08-01 | Longlegs                                             | 8:35 pm |        114 |
| 4   | 2024-08-01 | Staff Pick: Melvin and Howard (35mm)                 | 8:45 pm |         23 |
| 5   | 2024-08-02 | Made in England: The Films of Powell and Pressburger | 6:00 pm |        204 |
| 6   | 2024-08-02 | Lyd                                                  | 6:30 pm |        213 |
| 7   | 2024-08-02 | The Red Shoes                                        | 8:45 pm |        230 |

``` r
d_est <- d
d_est$Attendance <- NULL
d_est <- d_est[-2, , drop = FALSE]
write.csv(d_est, 'Roxie_schedule_as_known_before_August.csv', row.names = FALSE)
knitr::kable(head(d_est))
```

|     | Date       | Movie                                                | Time    | EstimatedAttendance |
|:----|:-----------|:-----------------------------------------------------|:--------|--------------------:|
| 1   | 2024-08-01 | Chronicles of a Wandering Saint                      | 6:40 pm |                  47 |
| 3   | 2024-08-01 | Longlegs                                             | 8:35 pm |                 233 |
| 4   | 2024-08-01 | Staff Pick: Melvin and Howard (35mm)                 | 8:45 pm |                  47 |
| 5   | 2024-08-02 | Made in England: The Films of Powell and Pressburger | 6:00 pm |                 233 |
| 6   | 2024-08-02 | Lyd                                                  | 6:30 pm |                 233 |
| 7   | 2024-08-02 | The Red Shoes                                        | 8:45 pm |                 233 |
