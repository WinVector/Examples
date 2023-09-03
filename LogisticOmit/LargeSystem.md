Larger System
================
2023-09-03

## Introduction

We will work on a slightly larger version of [“Solving for Hidden
Data”](https://win-vector.com/2023/09/02/solving-for-hidden-data/).

## The Example

We define our detailed names frame frame.

We specify our (to be inferred) explanatory variable probabilities.

``` r
# specify explanatory variable distribution 
`P(X1=1)` <- 0.3
`P(X1=2)` <- 0.2
`P(X2=1)` <- 0.8
`P(X2=2)` <- 0.05
`P(X1=0)` <- 1 - (`P(X1=1)` + `P(X1=2)`)
`P(X2=0)` <- 1 - (`P(X2=1)` + `P(X2=2)`)
```

Define our conditional probability of outcome given explanatory
variables.

``` r
c0 = 0.5
b1 = 3.2
b2 = -1.1
```

We build up a data frame with row distribution defined as above.

``` r
# assign an example outcome or dependent variable
detailed_frame <- detailed_names
detailed_frame$x1 <- as.numeric(detailed_frame$x1)
detailed_frame$x2 <- as.numeric(detailed_frame$x2)

# get joint distribution of explanatory variables
detailed_frame["P(X1=x1, X2=x2)"] <- (
  ifelse(detailed_frame$x1 == 0, `P(X1=0)`, 
         ifelse(detailed_frame$x1 == 1, `P(X1=1)`, `P(X1=2)`))
  * ifelse(detailed_frame$x2 == 0, `P(X2=0)`,
           ifelse(detailed_frame$x1 == 1, `P(X2=1)`, `P(X2=2)`)))

# converting "links" to probabilities
sigmoid <- function(x) {1 / (1 + exp(-x))}

# get conditional probability of observed outcome
# could also consider categorical x1, x2 here
y_probability <- sigmoid(
  c0 + b1 * detailed_frame$x1 + b2 * detailed_frame$x2)

# record probability of observation
detailed_frame[["P(Y=y | X1=x1, X2=x2)"]] <- ifelse(
  detailed_frame$y, 
  y_probability, 
  1 - y_probability)

# compute joint explanatory plus outcome probability of each row
detailed_frame[["P(X1=x1, X2=x2, Y=y)"]] <- (
  detailed_frame[["P(X1=x1, X2=x2)"]] 
  * detailed_frame[["P(Y=y | X1=x1, X2=x2)"]])
```

``` r
knitr::kable(detailed_frame)
```

|  x1 |  x2 | y     | P(X1=x1, X2=x2) | P(Y=y \| X1=x1, X2=x2) | P(X1=x1, X2=x2, Y=y) |
|----:|----:|:------|----------------:|-----------------------:|---------------------:|
|   0 |   0 | FALSE |           0.075 |              0.3775407 |            0.0283156 |
|   1 |   0 | FALSE |           0.045 |              0.0241270 |            0.0010857 |
|   2 |   0 | FALSE |           0.030 |              0.0010068 |            0.0000302 |
|   0 |   1 | FALSE |           0.025 |              0.6456563 |            0.0161414 |
|   1 |   1 | FALSE |           0.240 |              0.0691384 |            0.0165932 |
|   2 |   1 | FALSE |           0.010 |              0.0030184 |            0.0000302 |
|   0 |   2 | FALSE |           0.025 |              0.8455347 |            0.0211384 |
|   1 |   2 | FALSE |           0.240 |              0.1824255 |            0.0437821 |
|   2 |   2 | FALSE |           0.010 |              0.0090133 |            0.0000901 |
|   0 |   0 | TRUE  |           0.075 |              0.6224593 |            0.0466844 |
|   1 |   0 | TRUE  |           0.045 |              0.9758730 |            0.0439143 |
|   2 |   0 | TRUE  |           0.030 |              0.9989932 |            0.0299698 |
|   0 |   1 | TRUE  |           0.025 |              0.3543437 |            0.0088586 |
|   1 |   1 | TRUE  |           0.240 |              0.9308616 |            0.2234068 |
|   2 |   1 | TRUE  |           0.010 |              0.9969816 |            0.0099698 |
|   0 |   2 | TRUE  |           0.025 |              0.1544653 |            0.0038616 |
|   1 |   2 | TRUE  |           0.240 |              0.8175745 |            0.1962179 |
|   2 |   2 | TRUE  |           0.010 |              0.9909867 |            0.0099099 |

## The unobserved to observed mapping

We show the linear operator that maps detailed probabilities to
summarized observed probabilities (where each view marginalizes out one
variable).

``` r
knitr::kable(margin_transform, format = "html") |>
  kableExtra::kable_styling(font_size = 8)
```

<table class="table" style="font-size: 8px; margin-left: auto; margin-right: auto;">
<thead>
<tr>
<th style="text-align:left;">
</th>
<th style="text-align:right;">
P(X1=0, X2=0, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=1, X2=0, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=2, X2=0, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=0, X2=1, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=1, X2=1, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=2, X2=1, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=0, X2=2, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=1, X2=2, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=2, X2=2, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=0, X2=0, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=1, X2=0, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=2, X2=0, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=0, X2=1, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=1, X2=1, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=2, X2=1, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=0, X2=2, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=1, X2=2, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=2, X2=2, Y=TRUE)
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:left;">
P(X1=0, X2=&ast;, Y=FALSE)
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=&ast;, Y=FALSE)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=2, X2=&ast;, Y=FALSE)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=0, X2=&ast;, Y=TRUE)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=&ast;, Y=TRUE)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=2, X2=&ast;, Y=TRUE)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=0, Y=FALSE)
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=1, Y=FALSE)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=2, Y=FALSE)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=0, Y=TRUE)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=1, Y=TRUE)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=2, Y=TRUE)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=0, X2=0, Y=&ast;)
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=0, Y=&ast;)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=2, X2=0, Y=&ast;)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=0, X2=1, Y=&ast;)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=1, Y=&ast;)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=2, X2=1, Y=&ast;)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=0, X2=2, Y=&ast;)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=2, Y=&ast;)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=2, X2=2, Y=&ast;)
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
</tr>
</tbody>
</table>

``` r
margins <- 
   margin_transform %*% detailed_frame[["P(X1=x1, X2=x2, Y=y)"]]
```

## Reversing the mapping as a solution step

Let’s compute a linear pre-image of the marginalization.

``` r
(pre_image <- solve(
  qr(margin_transform, LAPACK = TRUE), 
  margins))
```

    ##                               [,1]
    ## P(X1=0, X2=0, Y=FALSE)  0.10175720
    ## P(X1=1, X2=0, Y=FALSE) -0.23758716
    ## P(X1=2, X2=0, Y=FALSE)  0.16526143
    ## P(X1=0, X2=1, Y=FALSE)  0.06465273
    ## P(X1=1, X2=1, Y=FALSE)  0.11428244
    ## P(X1=2, X2=1, Y=FALSE) -0.14617035
    ## P(X1=0, X2=2, Y=FALSE) -0.10081460
    ## P(X1=1, X2=2, Y=FALSE)  0.18476578
    ## P(X1=2, X2=2, Y=FALSE) -0.01894055
    ## P(X1=0, X2=0, Y=TRUE)  -0.02675720
    ## P(X1=1, X2=0, Y=TRUE)   0.28258716
    ## P(X1=2, X2=0, Y=TRUE)  -0.13526143
    ## P(X1=0, X2=1, Y=TRUE)  -0.03965273
    ## P(X1=1, X2=1, Y=TRUE)   0.12571756
    ## P(X1=2, X2=1, Y=TRUE)   0.15617035
    ## P(X1=0, X2=2, Y=TRUE)   0.12581460
    ## P(X1=1, X2=2, Y=TRUE)   0.05523422
    ## P(X1=2, X2=2, Y=TRUE)   0.02894055

Notice this does not obey sign constraints. We will use our degrees of
freedom in the pre-image process to both establish non-negativity
(moving to valid likelihoods/probabilities/frequencies) and maximize
entropy (under the assumption the actual solution is itself maximal
entropy).

## Fixing the linear solution

The the degrees of freedom in the pre-image process are given as
follows.

``` r
(ns <- MASS::Null(t(margin_transform)))
```

    ##               [,1]         [,2]        [,3]        [,4]
    ##  [1,] -0.291757032  0.005531517 -0.35514364 -0.10460619
    ##  [2,]  0.027416506 -0.100469560  0.36939730 -0.27371894
    ##  [3,]  0.264340526  0.094938042 -0.01425366  0.37832514
    ##  [4,]  0.292881367  0.323512407  0.11693140 -0.13457153
    ##  [5,]  0.137259622 -0.307789354 -0.30831951  0.11656247
    ##  [6,] -0.430140990 -0.015723053  0.19138811  0.01800907
    ##  [7,] -0.001124335 -0.329043924  0.23821224  0.23917773
    ##  [8,] -0.164676128  0.408258914 -0.06107778  0.15715648
    ##  [9,]  0.165800463 -0.079214990 -0.17713445 -0.39633420
    ## [10,]  0.291757032 -0.005531517  0.35514364  0.10460619
    ## [11,] -0.027416506  0.100469560 -0.36939730  0.27371894
    ## [12,] -0.264340526 -0.094938042  0.01425366 -0.37832514
    ## [13,] -0.292881367 -0.323512407 -0.11693140  0.13457153
    ## [14,] -0.137259622  0.307789354  0.30831951 -0.11656247
    ## [15,]  0.430140990  0.015723053 -0.19138811 -0.01800907
    ## [16,]  0.001124335  0.329043924 -0.23821224 -0.23917773
    ## [17,]  0.164676128 -0.408258914  0.06107778 -0.15715648
    ## [18,] -0.165800463  0.079214990  0.17713445  0.39633420

The above null vectors include the [Kronecker
product](https://en.wikipedia.org/wiki/Kronecker_product) of the
per-variable null spaces. Each of the per-variable null spaces are just
a basis for the orthogonal complement of an all ones vector of length
equal to the number of values the variable takes.

All we need to do to establish that these are *all* of the null-vectors,
is to bound the rank of the null space that there are in. In [“Solving
for Hidden
Data”](https://win-vector.com/2023/09/02/solving-for-hidden-data/) the
null space is rank 1, and here it is rank 4. In both of these cases this
means the Kronecker product vectors are the entire null space. It turns
out this is enough to allow us to confirm the following recovery
procedure can find the original data set.

Define our “pick a good solution” objective function.

``` r
entropy <- function(v) {
  v <- v[v > 0]
  if (length(v) < 2) {
    return(0)
  }
  v <- v / sum(v)
  -sum(v * log2(v))
}
```

To solve: maximize `entropy(pre_image + ns * z)` subject to
`pre_image + ns * z >= 0`.

``` r
library(lpSolve)
```

Get an interior starting solution for the later optimizer.

``` r
# solve for possible interior solution by maximizing slack
# this call takes only non-negative variables, so we double
# the variables to simulate signed variables.
soln0 <- lp(
  direction = "max",
  objective.in = c(rep(0, ncol(ns) * 2), 1),
  const.mat = cbind(ns, -ns, -1),
  const.dir = rep(">=", nrow(ns)),
  const.rhs = -pre_image,
)
z0 <- soln0$solution[1:ncol(ns)] - soln0$solution[(1+ncol(ns)):(2*ncol(ns))]

z0
```

    ## [1] -0.1611108 -0.2284994  0.4067960 -0.2514544

``` r
recovered0 <- ns %*% z0 + pre_image
stopifnot(
  all(recovered0 > 0)
)
stopifnot(
  max(abs(margins - margin_transform %*% recovered0)) < 1e-6
)

recovered0
```

    ##                                [,1]
    ## P(X1=0, X2=0, Y=FALSE) 2.933112e-02
    ## P(X1=1, X2=0, Y=FALSE) 5.017342e-05
    ## P(X1=2, X2=0, Y=FALSE) 5.017342e-05
    ## P(X1=0, X2=1, Y=FALSE) 2.494983e-02
    ## P(X1=1, X2=1, Y=FALSE) 7.764813e-03
    ## P(X1=2, X2=1, Y=FALSE) 5.017342e-05
    ## P(X1=0, X2=2, Y=FALSE) 1.131438e-02
    ## P(X1=1, X2=2, Y=FALSE) 5.364608e-02
    ## P(X1=2, X2=2, Y=FALSE) 5.017342e-05
    ## P(X1=0, X2=0, Y=TRUE)  4.566888e-02
    ## P(X1=1, X2=0, Y=TRUE)  4.494983e-02
    ## P(X1=2, X2=0, Y=TRUE)  2.994983e-02
    ## P(X1=0, X2=1, Y=TRUE)  5.017342e-05
    ## P(X1=1, X2=1, Y=TRUE)  2.322352e-01
    ## P(X1=2, X2=1, Y=TRUE)  9.949827e-03
    ## P(X1=0, X2=2, Y=TRUE)  1.368562e-02
    ## P(X1=1, X2=2, Y=TRUE)  1.863539e-01
    ## P(X1=2, X2=2, Y=TRUE)  9.949827e-03

``` r
entropy(recovered0)
```

    ## [1] 2.848024

We then finish by solving the following constrained optimization
problem.

``` r
# maximize entropy in constrained region
f <- function(z) {-entropy(ns %*% z + pre_image)}
g <- function(z) {
  as.numeric(t((log(ns %*% z + pre_image) + 1) / log(2))  %*% ns)
}
soln1 <- constrOptim(
  theta = z0,
  f = f,
  grad = g,
  ui = ns,
  ci = -pre_image,
  outer.iterations = 1000,
  outer.eps = 1e-10,
  method = "CG"
)
z1 <- soln1$par

z1
```

    ## [1] -0.1599510 -0.2543812  0.4066426 -0.2458285

``` r
stopifnot(
  max(abs(g(z1))) < 1e-5
)
```

``` r
recovered1 <- ns %*% z1 + pre_image
stopifnot(
  all(recovered1 >= 0)
)
stopifnot(
  max(abs(margins - margin_transform %*% recovered1)) < 1e-6
)

recovered1
```

    ##                                [,1]
    ## P(X1=0, X2=0, Y=FALSE) 2.831555e-02
    ## P(X1=1, X2=0, Y=FALSE) 1.085715e-03
    ## P(X1=2, X2=0, Y=FALSE) 3.020314e-05
    ## P(X1=0, X2=1, Y=FALSE) 1.614140e-02
    ## P(X1=1, X2=1, Y=FALSE) 1.659323e-02
    ## P(X1=2, X2=1, Y=FALSE) 3.018418e-05
    ## P(X1=0, X2=2, Y=FALSE) 2.113838e-02
    ## P(X1=1, X2=2, Y=FALSE) 4.378212e-02
    ## P(X1=2, X2=2, Y=FALSE) 9.013295e-05
    ## P(X1=0, X2=0, Y=TRUE)  4.668445e-02
    ## P(X1=1, X2=0, Y=TRUE)  4.391428e-02
    ## P(X1=2, X2=0, Y=TRUE)  2.996980e-02
    ## P(X1=0, X2=1, Y=TRUE)  8.858600e-03
    ## P(X1=1, X2=1, Y=TRUE)  2.234068e-01
    ## P(X1=2, X2=1, Y=TRUE)  9.969816e-03
    ## P(X1=0, X2=2, Y=TRUE)  3.861625e-03
    ## P(X1=1, X2=2, Y=TRUE)  1.962179e-01
    ## P(X1=2, X2=2, Y=TRUE)  9.909867e-03

``` r
entropy(recovered1)
```

    ## [1] 2.901993

``` r
stopifnot(
  entropy(recovered1) >= entropy(recovered0)
)
```

This recovered entropy should be at least as high as the unobserved
actual solution (modulo optimization early stopping and numeric issues).
If they are equal they are the same solution.

``` r
entropy(detailed_frame[["P(X1=x1, X2=x2, Y=y)"]])
```

    ## [1] 2.901993

``` r
stopifnot(
  entropy(recovered1) - entropy(detailed_frame[["P(X1=x1, X2=x2, Y=y)"]]) > -1e-8
)
```

We show this solution is very close to the original (unobserved)
distribution. I.e.: we have solved the problem.

``` r
(residuals <- 
  detailed_frame[["P(X1=x1, X2=x2, Y=y)"]] - recovered1)
```

    ##                                 [,1]
    ## P(X1=0, X2=0, Y=FALSE) -4.623074e-10
    ## P(X1=1, X2=0, Y=FALSE)  4.810488e-10
    ## P(X1=2, X2=0, Y=FALSE) -1.874144e-11
    ## P(X1=0, X2=1, Y=FALSE)  7.253382e-09
    ## P(X1=1, X2=1, Y=FALSE) -7.233596e-09
    ## P(X1=2, X2=1, Y=FALSE) -1.978541e-11
    ## P(X1=0, X2=2, Y=FALSE) -6.791074e-09
    ## P(X1=1, X2=2, Y=FALSE)  6.752547e-09
    ## P(X1=2, X2=2, Y=FALSE)  3.852690e-11
    ## P(X1=0, X2=0, Y=TRUE)   4.623073e-10
    ## P(X1=1, X2=0, Y=TRUE)  -4.810489e-10
    ## P(X1=2, X2=0, Y=TRUE)   1.874137e-11
    ## P(X1=0, X2=1, Y=TRUE)  -7.253382e-09
    ## P(X1=1, X2=1, Y=TRUE)   7.233596e-09
    ## P(X1=2, X2=1, Y=TRUE)   1.978557e-11
    ## P(X1=0, X2=2, Y=TRUE)   6.791074e-09
    ## P(X1=1, X2=2, Y=TRUE)  -6.752547e-09
    ## P(X1=2, X2=2, Y=TRUE)  -3.852712e-11

``` r
stopifnot(
  max(abs(residuals)) < 1e-8
)
```

What we want to show is that the distribution given is highest entropy
with respect to the variations of the specified adjustment vectors. If
this is the case, then we *always* recover the actual pre-image
distribution through these methods.

## The Kronecker product null vectors are orthogonal to the log probabilities

The Kronecker product null vectors are orthogonal to the log
probabilities of the original data set. Once we know this we know the
solution method recovers the original data, as it picks a unique optimum
with the same the above as zero-gradient conditions.

To show this we just expand one such sum as follows. Write our Kronecker
product null vector as
`v<sub>x1, x2, y</sub> = f1(<sup>x1</sup>) * f2(<sup>x2</sup>) * (-1)<sup>y</sup>`,
where `fi(<sup>xi</sup>)` is orthogonal to the all ones vector for the
appropiate sums and sub-sums.

<pre>
sum<sub>x1</sub> sum<sub>x2</sub> sum<sub>y=F,T</sub> (
   f1(<sup>x1</sup>) * f2(<sup>x2</sup>) * (-1)<sup>y</sup> 
     * log(P(X1=x1, X2=x2, Y))
   )
   &#10; = sum<sub>x1</sub> sum<sub>x2</sub> sum<sub>y=F,T</sub> (
     f1(<sup>x1</sup>) * f2(<sup>x2</sup>) * (-1)<sup>y</sup> 
       * log(P(X1=x1, X2=x2) * p(Y=y | x1, x2))
     )
&#10; = sum<sub>x1</sub> sum<sub>x2</sub> (
    f1(<sup>x1</sup>) * f2(<sup>x2</sup>) * ( 
       log(P(X1=x1, X2=x2) * 
          (1 - 1 / (1 + exp(c0 + b1 * x1 + b2 * x2))))
      - log(P(X1=x1, X2=x2) * 
          1 / (1 + exp(c0 + b1 * x1 + b2 * x2)))
    ))
    &#10; = sum<sub>x1</sub> sum<sub>x2</sub> (
    f1(<sup>x1</sup>) * f2(<sup>x2</sup>) * ( 
        log(P(X1=x1, X2=x2) * 
           (exp(c0 + b1 * x1 + b2 * x2) / (1 + exp(c0 + b1 * x1 + b2 * x2))))
      - log(P(X1=x1, X2=x2) * 
           1 / (1 + exp(c0 + b1 * x1 + b2 * x2)))
    ))
&#10; = sum<sub>x1</sub> sum<sub>x2</sub> (
    f1(<sup>x1</sup>) * f2(<sup>x2</sup>) * log(exp(c0 + b1 * x1 + b2 * x2)))
&#10; = sum<sub>x1</sub> sum<sub>x2</sub> (
    f1(<sup>x1</sup>) * f2(<sup>x2</sup>) * (c0 + b1 * x1 + b2 * x2))
&#10; = (
   sum<sub>x1</sub> sum<sub>x2</sub> (
    f1(<sup>x1</sup>) * f2(<sup>x2</sup>) * (c0 + b1 * x1))
   +
   sum<sub>x1</sub> sum<sub>x2</sub> (
    f1(<sup>x1</sup>) * f2(<sup>x2</sup>) * (b2 * x2))
   )
&#10; = (
    sum<sub>x2</sub> f2(<sup>x2</sup>) * (
    sum<sub>x1</sub>f1(<sup>x1</sup>) * (c0 + b1 * x1))
   +
   sum<sub>x1</sub> f1(<sup>x1</sup>) * (
     sum<sub>x2</sub> f2(<sup>x2</sup>) * (b2 * x2))
   )
&#10; = (
   sum<sub>x2</sub> f2(<sup>x2</sup>) * C1
   +
   sum<sub>x1</sub> f1(<sup>x1</sup>) * C2
   )
   &#10; = 0
</pre>

In both cases we are using that
`sum<sub>xi</sub> f2(<sup>xi</sup>) 1 = 0`. This derivation also works
for categorica variables, if we write `mi(bi, xi)` in place of
`bi * xi*` throughout.

## Bounding the rank

All the remains is to check that a the rank of the linear operator
summing out (or marginalizing) a `u` by `v` by `2` 3-way contingency
table has a null space with rank no larger than `(u - 1) * (v - 1)`.
This finishes the problem as we can find `(u - 1) * (v - 1)` independent
Kroenker product null vectors, and if these are all of the solution
degrees of freedom then we know the maximum entropy solution is the
original unobserved data distribution we wished to solve for.

We have checked the rank condition in the two cases `(u, v)` is `(2, 2)`
and `(3, 3)`. What remains is to establish this in general.
