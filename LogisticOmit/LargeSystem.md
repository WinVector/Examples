Large System
================
2023-09-03

Work a slightly larger version of [“Solving for Hidden
Data”](https://win-vector.com/2023/09/02/solving-for-hidden-data/).

Define our frame.

Define our explanatory variable probabilities.

``` r
# specify explanatory variable distribution 
`P(X1=1)` <- 0.3
`P(X1=2)` <- 0.2
`P(X2=1)` <- 0.8
`P(X1=0)` <- 1 - (`P(X1=1)` + `P(X1=2)`)
`P(X2=0)` <- 1 - `P(X2=1)`
```

Define our condidtional probability of outcome given explanatory
variables.

``` r
c0 = 0.5
b1 = 3.2
b2 = -11.1
```

Build up a data frame with row distribution defined as above.

``` r
# assign an example outcome or dependent variable
detailed_frame <- detailed_names
detailed_frame$x1 <- as.numeric(detailed_frame$x1)
detailed_frame$x2 <- as.numeric(detailed_frame$x2)

# get joint distribution of explanatory variables
detailed_frame["P(X1=x1, X2=x2)"] <- (
  ifelse(detailed_frame$x1 == 0, `P(X1=0)`, 
         ifelse(detailed_frame$x1 == 1, `P(X1=1)`, `P(X1=2)`))
  * ifelse(detailed_frame$x2 == 0, `P(X2=0)`, `P(X2=1)`)
)

# converting "links" to probabilities
sigmoid <- function(x) {1 / (1 + exp(-x))}

# get conditional probability of observed outcome
# could treat x1 as categorical here
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
|   0 |   0 | FALSE |            0.10 |              0.3775407 |            0.0377541 |
|   1 |   0 | FALSE |            0.06 |              0.0241270 |            0.0014476 |
|   2 |   0 | FALSE |            0.04 |              0.0010068 |            0.0000403 |
|   0 |   1 | FALSE |            0.40 |              0.9999751 |            0.3999900 |
|   1 |   1 | FALSE |            0.24 |              0.9993891 |            0.2398534 |
|   2 |   1 | FALSE |            0.16 |              0.9852260 |            0.1576362 |
|   0 |   0 | TRUE  |            0.10 |              0.6224593 |            0.0622459 |
|   1 |   0 | TRUE  |            0.06 |              0.9758730 |            0.0585524 |
|   2 |   0 | TRUE  |            0.04 |              0.9989932 |            0.0399597 |
|   0 |   1 | TRUE  |            0.40 |              0.0000249 |            0.0000100 |
|   1 |   1 | TRUE  |            0.24 |              0.0006109 |            0.0001466 |
|   2 |   1 | TRUE  |            0.16 |              0.0147740 |            0.0023638 |

Build the linear operator that maps detailed probabilities to summarized
observed probabilities (where each view marginalizes out one variable).

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
1
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
1
</td>
</tr>
</tbody>
</table>

``` r
(margins <- 
   margin_transform %*% detailed_frame[["P(X1=x1, X2=x2, Y=y)"]])
```

    ##                                   [,1]
    ## P(X1=0, X2=&ast;, Y=FALSE) 0.437744101
    ## P(X1=1, X2=&ast;, Y=FALSE) 0.241301010
    ## P(X1=2, X2=&ast;, Y=FALSE) 0.157676426
    ## P(X1=0, X2=&ast;, Y=TRUE)  0.062255899
    ## P(X1=1, X2=&ast;, Y=TRUE)  0.058698990
    ## P(X1=2, X2=&ast;, Y=TRUE)  0.042323574
    ## P(X1=&ast;, X2=0, Y=FALSE) 0.039241959
    ## P(X1=&ast;, X2=1, Y=FALSE) 0.797479578
    ## P(X1=&ast;, X2=0, Y=TRUE)  0.160758041
    ## P(X1=&ast;, X2=1, Y=TRUE)  0.002520422
    ## P(X1=0, X2=0, Y=&ast;)     0.100000000
    ## P(X1=1, X2=0, Y=&ast;)     0.060000000
    ## P(X1=2, X2=0, Y=&ast;)     0.040000000
    ## P(X1=0, X2=1, Y=&ast;)     0.400000000
    ## P(X1=1, X2=1, Y=&ast;)     0.240000000
    ## P(X1=2, X2=1, Y=&ast;)     0.160000000

Show a linear pre-image of the marginalization.

``` r
(pre_image <- solve(
  qr(margin_transform, LAPACK = TRUE), 
  margins))
```

    ##                                [,1]
    ## P(X1=0, X2=0, Y=FALSE)  0.025706513
    ## P(X1=1, X2=0, Y=FALSE) -0.005139468
    ## P(X1=2, X2=0, Y=FALSE)  0.018674914
    ## P(X1=0, X2=1, Y=FALSE)  0.412037588
    ## P(X1=1, X2=1, Y=FALSE)  0.246440478
    ## P(X1=2, X2=1, Y=FALSE)  0.139001512
    ## P(X1=0, X2=0, Y=TRUE)   0.074293487
    ## P(X1=1, X2=0, Y=TRUE)   0.065139468
    ## P(X1=2, X2=0, Y=TRUE)   0.021325086
    ## P(X1=0, X2=1, Y=TRUE)  -0.012037588
    ## P(X1=1, X2=1, Y=TRUE)  -0.006440478
    ## P(X1=2, X2=1, Y=TRUE)   0.020998488

Notice this does not obey sign constraints. We will use our degrees of
freedom in the pre-image process to both establish non-negativity
(moving to valid likelihoods/probabilities/frequencies) and maximize
entropy (under the assumption the actual solution is itself maximal
entropy).

Show the degrees of freedom in the pre-image process.

``` r
(ns <- MASS::Null(t(margin_transform)))
```

    ##             [,1]       [,2]
    ##  [1,] -0.2886751 -0.2886751
    ##  [2,]  0.3943376 -0.1056624
    ##  [3,] -0.1056624  0.3943376
    ##  [4,]  0.2886751  0.2886751
    ##  [5,] -0.3943376  0.1056624
    ##  [6,]  0.1056624 -0.3943376
    ##  [7,]  0.2886751  0.2886751
    ##  [8,] -0.3943376  0.1056624
    ##  [9,]  0.1056624 -0.3943376
    ## [10,] -0.2886751 -0.2886751
    ## [11,]  0.3943376 -0.1056624
    ## [12,] -0.1056624  0.3943376

The above null vectors include the [Kronecker
product](https://en.wikipedia.org/wiki/Kronecker_product) of the
per-variable null spaces. Each of the per-variable null spaces are just
a basis for the orthogonal complement of an all ones vector of length
equal to the number of values the variable takes. So *if* we establish
that these are *all* of the null-vectors, we expect the null space to be
of dimension the product of each variables number of levels each
minus 1. That would be why in [“Solving for Hidden
Data”](https://win-vector.com/2023/09/02/solving-for-hidden-data/) the
null space is rank 1, and here it is rank 2.

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

Solve: maximize `entropy(pre_image + ns * z)` subject to
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
recovered0 <- ns %*% z0 + pre_image
stopifnot(
  all(recovered0 >= 0)
)
stopifnot(
  max(abs(margins - margin_transform %*% recovered0)) < 1e-6
)

recovered0
```

    ##                                [,1]
    ## P(X1=0, X2=0, Y=FALSE) 3.780972e-02
    ## P(X1=1, X2=0, Y=FALSE) 1.366626e-03
    ## P(X1=2, X2=0, Y=FALSE) 6.561601e-05
    ## P(X1=0, X2=1, Y=FALSE) 3.999344e-01
    ## P(X1=1, X2=1, Y=FALSE) 2.399344e-01
    ## P(X1=2, X2=1, Y=FALSE) 1.576108e-01
    ## P(X1=0, X2=0, Y=TRUE)  6.219028e-02
    ## P(X1=1, X2=0, Y=TRUE)  5.863337e-02
    ## P(X1=2, X2=0, Y=TRUE)  3.993438e-02
    ## P(X1=0, X2=1, Y=TRUE)  6.561601e-05
    ## P(X1=1, X2=1, Y=TRUE)  6.561601e-05
    ## P(X1=2, X2=1, Y=TRUE)  2.389190e-03

``` r
entropy(recovered0)
```

    ## [1] 2.332883

Solve the constrained optimization problem.

``` r
# maximize entropy in constrained region
soln1 <- constrOptim(
  theta = z0,
  f = function(z) {-entropy(ns %*% z + pre_image)},
  grad = NULL,
  ui = ns,
  ci = -pre_image,
)
z1 <- soln1$par
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
    ## P(X1=0, X2=0, Y=FALSE) 3.775406e-02
    ## P(X1=1, X2=0, Y=FALSE) 1.448321e-03
    ## P(X1=2, X2=0, Y=FALSE) 3.957397e-05
    ## P(X1=0, X2=1, Y=FALSE) 3.999900e-01
    ## P(X1=1, X2=1, Y=FALSE) 2.398527e-01
    ## P(X1=2, X2=1, Y=FALSE) 1.576369e-01
    ## P(X1=0, X2=0, Y=TRUE)  6.224594e-02
    ## P(X1=1, X2=0, Y=TRUE)  5.855168e-02
    ## P(X1=2, X2=0, Y=TRUE)  3.996043e-02
    ## P(X1=0, X2=1, Y=TRUE)  9.963032e-06
    ## P(X1=1, X2=1, Y=TRUE)  1.473110e-04
    ## P(X1=2, X2=1, Y=TRUE)  2.363148e-03

``` r
entropy(recovered1)
```

    ## [1] 2.333035

Show this solution is very close to the original (unobserved)
distribution. I.e.: we have solved the problem.

``` r
(residuals <- 
  detailed_frame[["P(X1=x1, X2=x2, Y=y)"]] - recovered1)
```

    ##                                 [,1]
    ## P(X1=0, X2=0, Y=FALSE)  3.123745e-09
    ## P(X1=1, X2=0, Y=FALSE) -6.999854e-07
    ## P(X1=2, X2=0, Y=FALSE)  6.968617e-07
    ## P(X1=0, X2=1, Y=FALSE) -3.123745e-09
    ## P(X1=1, X2=1, Y=FALSE)  6.999854e-07
    ## P(X1=2, X2=1, Y=FALSE) -6.968617e-07
    ## P(X1=0, X2=0, Y=TRUE)  -3.123745e-09
    ## P(X1=1, X2=0, Y=TRUE)   6.999854e-07
    ## P(X1=2, X2=0, Y=TRUE)  -6.968617e-07
    ## P(X1=0, X2=1, Y=TRUE)   3.123745e-09
    ## P(X1=1, X2=1, Y=TRUE)  -6.999854e-07
    ## P(X1=2, X2=1, Y=TRUE)   6.968617e-07

``` r
stopifnot(
  max(abs(residuals)) < 1e-6
)
```

What we want to show is that the distribution given is highest entropy
with respect to the variations of the specified adjustment vectors. If
this is the case, then we *always* recover the actual pre-image
distribution through these methods.
