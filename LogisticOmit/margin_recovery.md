Solving for Hidden Data
================
2023-08-29

## Introduction

Let’s continue along the lines discussed in [Omitted Variable Effects in
Logistic
Regression](https://win-vector.com/2023/08/18/omitted-variable-effects-in-logistic-regression/).

The issue is as follows. For logistic regression, omitted variables
cause parameter estimation bias. This is true *even for independent
variables*, which is not the case for more familiar linear regression.

This is a known problem with known mitigations:

- Rhian Daniel, Jingjing Zhang, Daniel Farewell, “Making apples from
  oranges: Comparing noncollapsible effect estimators and their standard
  errors after adjustment for different covariate sets”, Biometrical
  Journal, (2020), DOI: 10.1002/bimj.201900297.
- John M. Neuhaus, Nicholas P. Jewell, “A Geometric Approach to Assess
  Bias Due to Omitted Covariates in Generalized Linear Models”,
  Biometrika, Vol. 80, No. 4 (Dec. 1993), pp. 807-815.
- Zhang, Zhiwei, “Estimating a Marginal Causal Odds Ratio Subject to
  Confounding”, Communications in Statistics - Theory and Methods, 38:3,
  (2009), 309-321.

(Thank you, Tom Palmer and Robert Horton for the references!)

For this note, let’s work out how to directly try and overcome the
omitted variable bias by solving for the hidden or unobserved detailed
data. We will work our example in [`R`](https://www.r-project.org). We
will derive some deep results out of a simple set-up. We show how to
“un-marginalize” or “un-summarize” data.

## Our Example

For an example let’s set up a logistic regression on two explanatory
variables `X1` and `X2` . For simplicity we will take the case where
`X1` and `X2` only take on the values `0` and `1`.

Our data is then keyed by the values of these explanatory variables and
the dependent or outcome variable `Y`, which takes on only the values
`FALSE` and `TRUE`. The keying looks like the following.

| x1  | x2  | y     |
|:----|:----|:------|
| 0   | 0   | FALSE |
| 1   | 0   | FALSE |
| 0   | 1   | FALSE |
| 1   | 1   | FALSE |
| 0   | 0   | TRUE  |
| 1   | 0   | TRUE  |
| 0   | 1   | TRUE  |
| 1   | 1   | TRUE  |

Note: we are using upper case names for *random variables* and lower
case names for coresponding *values of these variables*.

### The Example Data

Let’s specify the joint probability distribution of our two explanatory
variables. We choose them as independent with the following expected
values.

``` r
# specify explanatory variable distribution 
`P(X1=1)` <- 0.3
`P(X2=1)` <- 0.8
`P(X1=0)` <- 1 - `P(X1=1)`
`P(X2=0)` <- 1 - `P(X2=1)`
```

Our data set can then be completely described by above explanatory
variable distribution *and* the conditional probability of the dependent
outcomes. For our logistic regression problem we set up our outcome
conditioning as `P(Y=TRUE) ~ sigmoid(c0 + b1 * x1 + b2 * x2)`. Our
example coefficients are as follows.

``` r
# 0.5772
(c0 <- -digamma(1))
```

    ## [1] 0.5772157

``` r
# 3.1415
(b1 <- pi)
```

    ## [1] 3.141593

``` r
# 27.182
(b2 <- -3 * exp(1))
```

    ## [1] -8.154845

Please remember these coefficients in this order for later.

``` r
# show constants in an order will see again
c(c0, b1, b2)
```

    ## [1]  0.5772157  3.1415927 -8.1548455

Using the methodology of [Replicating a Linear
Model](https://win-vector.com/2019/07/03/replicating-a-linear-model/) we
can build an example data set that obeys the specified explanatory
variable distribution and has specified outcome probabilities. This is
just us building a data set matching an assumed known answer. Our data
distribution is going to be determined by `P(X1=1)`, `P(X2=1)`, and
`P(Y=TRUE) ~ sigmoid(c0 + b1 * x1 + b2 * x2)`. Our inference task is to
recover the parameters `P(X1=1)`, `P(X2=1)`, `c0`, `b1`, and `b2` from
data, even in the situation where observers have omitted variable
issues.

The complete detailed data is generated as follows. The
`P(X1=x1, X2=c2, Y=y)` column is what proportion of a data set drawn
from this specified distribution matches the row keys `x1`, `x2`, `y`,
or is the joint probability of a given row type. We can derive all the
detailed probabilities as follows.

``` r
# get joint distribution of explanatory variables
detailed_frame["P(X1=x1, X2=x2)"] <- (
  ifelse(detailed_frame$x1 == 1, `P(X1=1)`, `P(X1=0)`)
  * ifelse(detailed_frame$x2 == 1, `P(X2=1)`, `P(X2=0)`)
)

# converting "links" to probabilities
sigmoid <- function(x) {1 / (1 + exp(-x))}

# get conditional probability of observed outcome
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

The following table relates `x1`, `x2`, `y` value combinations to the
`P(X1=x1, X2=c2, Y=y)` column (which shows how common each such row is).

|  x1 |  x2 | y     | P(X1=x1, X2=x2) | P(Y=y \| X1=x1, X2=x2) | P(X1=x1, X2=x2, Y=y) |
|----:|----:|:------|----------------:|-----------------------:|---------------------:|
|   0 |   0 | FALSE |            0.14 |              0.3595735 |            0.0503403 |
|   1 |   0 | FALSE |            0.06 |              0.0236881 |            0.0014213 |
|   0 |   1 | FALSE |            0.56 |              0.9994885 |            0.5597136 |
|   1 |   1 | FALSE |            0.24 |              0.9882958 |            0.2371910 |
|   0 |   0 | TRUE  |            0.14 |              0.6404265 |            0.0896597 |
|   1 |   0 | TRUE  |            0.06 |              0.9763119 |            0.0585787 |
|   0 |   1 | TRUE  |            0.56 |              0.0005115 |            0.0002864 |
|   1 |   1 | TRUE  |            0.24 |              0.0117042 |            0.0028090 |

For a logistic regression problem, the relation between `X1`, `X2` and
`Y` is encoded in the `P(X1=x1, X2=c2, Y=y)` distribution that gives the
joint expected frequency of each possible data row in a drawn sample.

### Inferring From Fully Observed Data

We can confirm this data set encodes the expected logistic relationship
by recovering the coefficients through fitting.

``` r
# suppressWarnings() to avoid fractional data weight complaint
correct_coef <- suppressWarnings(
  glm(
    y ~ x1 + x2,
    data = detailed_frame,
    weights = detailed_frame[["P(X1=x1, X2=x2, Y=y)"]],
    family = binomial()
  )$coef
)

correct_coef
```

    ## (Intercept)          x1          x2 
    ##   0.5772157   3.1415927  -8.1548455

Notice we recover the
`c0 + b1 * detailed_frame$x1 + b2 * detailed_frame$x2` form.

### The Nonlinear Invariant

There is an interesting non-linear invariant the `P(X1=x1, X2=c2, Y=y)`
column obeys. We will use this invariant later, so it is worth
establishing. The principle is: our solution disappears with respect to
certain test-vectors, which will help us re-identify it later.

Consider the following test vector.

``` r
test_vec <- (
  (-1)^detailed_frame$x1 
  * (-1)^detailed_frame$x2 
  * (-1)^detailed_frame$y)

test_vec
```

    ## [1]  1 -1 -1  1 -1  1  1 -1

`sum(test_vec * log(detailed_frame[["P(X1=x1, X2=x2, Y=y)"]]))` is
*always* zero when `detailed_frame[["P(X1=x1, X2=x2, Y=y)"])` is the row
probabilities from a logistic model of the form we have been working
with. Or `log(detailed_frame[["P(X1=x1, X2=x2, Y=y)"]])` is orthogonal
to `test_vec`. We can confirm this in our case, and derive this in the
appendix.

``` r
p_vec <- test_vec * log(detailed_frame[["P(X1=x1, X2=x2, Y=y)"]])
stopifnot(  # abort render if claim is not true
  abs(sum(p_vec)) < 1e-8)

sum(p_vec)
```

    ## [1] -2.553513e-15

Roughly: this is one check that the data is consistent with the
distributions a logistic regression with independent explanatory
variables can produce.

## The Problem

Now let’s get to our issue. Suppose we have two experimenters, each of
which only observes one of the explanatory variables. As we saw in
[Omitted Variable Effects in Logistic
Regression](https://win-vector.com/2023/08/18/omitted-variable-effects-in-logistic-regression/)
each of these experimenters will in fact estimate coefficients that are
**biased towards zero**, due to the non-collapsibility of the modeling
set up. This differs from linear regression, where for independent
explanatory variables (as we have here) we would expect each
experimenter to be able to get an unbiased estimate of the coefficient
for the explanatory variable available to them!

### The “Unobserved to Observed” Linear Mapping

Let’s build a linear operator that computes the margins the
experimenters actually observe. We or the experimenters can specify this
mapping, and its output. We just don’t (yet) have complete inforation on
the pre-image of this mapping.

``` r
knitr::kable(margin_transform, format = "html") |>
  kableExtra::kable_styling(font_size = 10)
```

<table class="table" style="font-size: 10px; margin-left: auto; margin-right: auto;">
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
P(X1=0, X2=1, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=1, X2=1, Y=FALSE)
</th>
<th style="text-align:right;">
P(X1=0, X2=0, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=1, X2=0, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=0, X2=1, Y=TRUE)
</th>
<th style="text-align:right;">
P(X1=1, X2=1, Y=TRUE)
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
1
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
1
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
P(X1=0, X2=1, Y=&ast;)
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
1
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
1
</td>
</tr>
</tbody>
</table>

The above matrix linearly maps our earlier `P(X1=x1, X2=c2, Y=y)`
columns to various interesting roll-ups or aggregations. Or, it is 12
linear checks we expect our 8 unobserved distribution parameters to
obey. Unfortunately the rank of this linear transform is only 7, so
there is redundancy among the checks and the linear relations do not
fully specify the unobserved distribution parameters. This is why we
need additional criteria to drive our solution.

``` r
# apply the linear operator to compute marginalized observations
actual_margins <- margin_transform %*% detailed_frame[["P(X1=x1, X2=x2, Y=y)"]]
```

<table>
<thead>
<tr>
<th style="text-align:left;">
</th>
<th style="text-align:left;">
x1
</th>
<th style="text-align:left;">
x2
</th>
<th style="text-align:left;">
y
</th>
<th style="text-align:right;">
actual_margins
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:left;">
P(X1=0, X2=&ast;, Y=FALSE)
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.6100538
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=&ast;, Y=FALSE)
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.2386123
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=0, X2=&ast;, Y=TRUE)
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0899462
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=&ast;, Y=TRUE)
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0613877
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=0, Y=FALSE)
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.0517616
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=1, Y=FALSE)
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.7969046
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=0, Y=TRUE)
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.1482384
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=1, Y=TRUE)
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0030954
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=0, X2=0, Y=&ast;)
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:right;">
0.1400000
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=0, Y=&ast;)
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:right;">
0.0600000
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=0, X2=1, Y=&ast;)
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:right;">
0.5600000
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=1, Y=&ast;)
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:right;">
0.2400000
</td>
</tr>
</tbody>
</table>

The above margin frame describes how the detailed experiment is
marginalized or censored down to what different experimenters see. In
our set-up experimenter 1 sees only the first four rows, and
experimenter 2 sees only the next 4 rows. We consider the rest of the
data “unobserved”.

### A Blind Spot

We also note that `margin_transform` is blind to variation in the
direction of our earlier `test_vec`. This can be confirmed as follows.

``` r
test_map <- margin_transform %*% test_vec

stopifnot(
  max(abs(test_map)) < 1e-8)
```

We know`log(detailed_frame[["P(X1=x1, X2=x2, Y=y)"]])` is orthogonal to
`test_vec`, but we don’t have an obvious linear relation between
`detailed_frame[["P(X1=x1, X2=x2, Y=y)"])` and `test_vec`.

Fortunately we can show (in an appendix) that the logistic regression is
also blind in this direction, so all of the indistinguishable data
pre-images give us the same logistic regression solution. Also, we can
use a maximum entropy principle to correctly recover the single actual
data distribution specified.

### Experimenter 1’s view

Let’s see what happens when an experimenter tries to perform inference
on their fraction of the data.

``` r
# select data available to d1
d1 <- margin_frame[
  margin_frame$x2 == asterisk_symbol, , drop = FALSE]

knitr::kable(d1)
```

<table>
<thead>
<tr>
<th style="text-align:left;">
</th>
<th style="text-align:left;">
x1
</th>
<th style="text-align:left;">
x2
</th>
<th style="text-align:left;">
y
</th>
<th style="text-align:right;">
actual_margins
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:left;">
P(X1=0, X2=&ast;, Y=FALSE)
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.6100538
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=&ast;, Y=FALSE)
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.2386123
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=0, X2=&ast;, Y=TRUE)
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0899462
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=&ast;, Y=TRUE)
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0613877
</td>
</tr>
</tbody>
</table>

``` r
# solve from d1's point of view
d1_est <- suppressWarnings(
  glm(
    y ~ x1,
    data = d1,
    weights = d1$actual_margins,
    family = binomial()
  )$coef
)

d1_est
```

    ## (Intercept)          x1 
    ##  -1.9143360   0.5567057

Notice experimenter 1 got a *much* too small estimate of the `X1`
coefficient of 0.5567057, whereas the correct value is 3.1415927. From
experimenter 1’s point of view, the effect of the omitted variable `X2`
is making `X1` hard to correctly infer.

### Experimenter 2’s view

Experimenter 2 has the following portion of data, which also is not
enough to get an unbiased coefficient estimate.

``` r
# select data available to d2
d2 <- margin_frame[
  margin_frame$x1 == asterisk_symbol, , drop = FALSE]

knitr::kable(d2)
```

<table>
<thead>
<tr>
<th style="text-align:left;">
</th>
<th style="text-align:left;">
x1
</th>
<th style="text-align:left;">
x2
</th>
<th style="text-align:left;">
y
</th>
<th style="text-align:right;">
actual_margins
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=0, Y=FALSE)
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.0517616
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=1, Y=FALSE)
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.7969046
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=0, Y=TRUE)
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.1482384
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=&ast;, X2=1, Y=TRUE)
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0030954
</td>
</tr>
</tbody>
</table>

### Our Point

From the original data set’s point of view: both experimenters have
wrong estimates of their respective coefficients. They do have correct
estimates for their limited view of columns, but this is not what we are
looking for when trying to infer causal effects. The question then is:
if the experimenters pool their effort can they infer the correct
coefficients?

## A Solution Strategy

Each experimenter knows a lot about the data. They known the
distribution of their explanatory variable, and even the joint
distribution of their explanatory and the dependent or outcome data.
Assuming the two explanatory variables are independent, the
experimenters can cooperate to estimate the joint distribution of the
explanatory variables. We will show how to use their combined
observations to estimate the hidden data elements. This data can then be
used for standard detailed analysis, like we showed on the original full
data set.

This isn’t the first time we have proposed a “guess at the original
data, as it wasn’t shared” as we played with this in [Checking claims in
published statistics
papers](https://win-vector.com/2013/04/08/checking-claims-in-published-statistics-papers/).

## Solution Steps

Our solutions strategy is as follows:

- Estimate the joint distribution of `X1` and `X2` from the observed
  marginal distributions of `X1` and `X2` plus an assumption of
  independence.
- Plug the above and other details in to the inverse of
  `margin_transform` to get a family of estimates of the original hidden
  data.
- Use the maximum entropy principle to pick a distinguished pre-image as
  the least surprising.
- Perform inference on this data to get coefficient estimates.

Note this strategy biases the data recovery to data sets that match our
modeling assumptions. If the original data met our modeling assumptions
this is in fact a useful inductive bias. If the original data did not
match the modeling assumptions, then this will (unfortunately) hide
issues.

### Estimating the `X1` and `X2` joint distribution

Neither experimenter observed the following part of the marginal frame:

``` r
# show x1 x2 distribution poriton of margin_frame
dx <- margin_frame[
  margin_frame$y == asterisk_symbol, , drop = FALSE]

knitr::kable(dx)
```

<table>
<thead>
<tr>
<th style="text-align:left;">
</th>
<th style="text-align:left;">
x1
</th>
<th style="text-align:left;">
x2
</th>
<th style="text-align:left;">
y
</th>
<th style="text-align:right;">
actual_margins
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:left;">
P(X1=0, X2=0, Y=&ast;)
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:right;">
0.14
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=0, Y=&ast;)
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:right;">
0.06
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=0, X2=1, Y=&ast;)
</td>
<td style="text-align:left;">
0
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:right;">
0.56
</td>
</tr>
<tr>
<td style="text-align:left;">
P(X1=1, X2=1, Y=&ast;)
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
1
</td>
<td style="text-align:left;">
&ast;
</td>
<td style="text-align:right;">
0.24
</td>
</tr>
</tbody>
</table>

However, under the independence assumption they can estimate it from
their pooled observations as follows.

``` r
# estimate x1 x2 distribution from d1 and d2
d1a <- aggregate(actual_margins ~ x1, data = d1, sum)
d2a <- aggregate(actual_margins ~ x2, data = d2, sum)
dxe <- merge(d1a, d2a, by = c())
dxe["estimated_margins"] <- (
  dxe$actual_margins.x * dxe$actual_margins.y)
dxe$actual_margins.x <- NULL
dxe$actual_margins.y <- NULL
dxe <- dxe[order(dxe$x2, dxe$x1), , drop = FALSE]

knitr::kable(dxe)
```

<table>
<thead>
<tr>
<th style="text-align:right;">
x1
</th>
<th style="text-align:right;">
x2
</th>
<th style="text-align:right;">
estimated_margins
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0.14
</td>
</tr>
<tr>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0.06
</td>
</tr>
<tr>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0.56
</td>
</tr>
<tr>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0.24
</td>
</tr>
</tbody>
</table>

Notice `dxe` is build only from `dx1` and `dx2` (plus the assumed
independence of `X1` and `X2`). At this point we have inferred the
`P(X1=x1, X2=x2)` parameters from the observed data.

### Combining Observations

We now combine all of our known data to get an estimate of the
(unobserved) summaries produced by `margin_transform`.

``` r
# put together experimenter 1 and 2's joint estimate of marginal proportions
# from data they have in their sub-experiments.
estimated_margins <- c(
  d1$actual_margins,
  d2$actual_margins,
  dxe$estimated_margins
)

estimated_margins
```

    ##  [1] 0.610053847 0.238612287 0.089946153 0.061387713 0.051761580 0.796904554
    ##  [7] 0.148238420 0.003095446 0.140000000 0.060000000 0.560000000 0.240000000

We see that the two experimenters have estimated the output of the
`margin_frame` transform. As they know the `margin_frame` output and the
`margin_frame` operator itself, they can try to estimate the pre-image
or input. This pre-image is the detailed distribution of data they are
actually interested in.

### Solving For the Full Joint Distribution

We use linear algebra to pull `estimated_margins` back through
`margin_transform` inverse to get a linear estimate of the unobserved
original data.

``` r
# typical solution (in the linear sense, signs not enforced)
# remember: estimated_margins = margin_transform %*% v
v <- solve(
  qr(margin_transform, LAPACK = TRUE), 
  estimated_margins)

v
```

    ## P(X1=0, X2=0, Y=FALSE) P(X1=1, X2=0, Y=FALSE) P(X1=0, X2=1, Y=FALSE) 
    ##            0.047964126            0.003797454            0.562089720 
    ## P(X1=1, X2=1, Y=FALSE)  P(X1=0, X2=0, Y=TRUE)  P(X1=1, X2=0, Y=TRUE) 
    ##            0.234814833            0.092035874            0.056202546 
    ##  P(X1=0, X2=1, Y=TRUE)  P(X1=1, X2=1, Y=TRUE) 
    ##           -0.002089720            0.005185167

Note this estimate has negative entries, so is not yet a sequence of
valid frequencies or probabilities. We will correct this by adding
elements that don’t change the forward mapping under `margin_transform`.
This means we need a linear algebra basis for `margin_transform`’s “null
space.” This is gotten as follows. The null space calculation is the
systematic way of finding blind-spots in the linear transform, without
requiring prior domain knowledge.

``` r
# our degree of freedom between solutions
ns <- MASS::Null(t(margin_transform))  # also uses QR decomposition, could combine
stopifnot(  # abort render if this claim is not true
  ncol(ns) == 1
)
```

``` r
# ns is invariant under scaling, pick first coordinate to be 1 for presentation
ns <- ns / ns[[1]]

ns
```

    ## [1]  1 -1 -1  1 -1  1  1 -1

In our case the null space was one dimensional, or spanned by a single
vector. This means all valid solutions are of the form `v + z * ns` for
scalars `z`. In fact all solutions are in an interval of `z` values. We
can solve for this interval.

Note, we have seen the direction we are varying (`ns`) before: it is
`test_vec`!

The range of recovered solutions to the (unknown to either
experimenter!) original data distribution details can be seen below as
the `recovered_distribution_*` columns.

<table>
<thead>
<tr>
<th style="text-align:right;">
x1
</th>
<th style="text-align:right;">
x2
</th>
<th style="text-align:left;">
y
</th>
<th style="text-align:right;">
P(X1=x1, X2=x2, Y=y)
</th>
<th style="text-align:right;">
recovered_distribution_1
</th>
<th style="text-align:right;">
recovered_distribution_2
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.0503403
</td>
<td style="text-align:right;">
0.0500538
</td>
<td style="text-align:right;">
0.0517616
</td>
</tr>
<tr>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.0014213
</td>
<td style="text-align:right;">
0.0017077
</td>
<td style="text-align:right;">
0.0000000
</td>
</tr>
<tr>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.5597136
</td>
<td style="text-align:right;">
0.5600000
</td>
<td style="text-align:right;">
0.5582923
</td>
</tr>
<tr>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.2371910
</td>
<td style="text-align:right;">
0.2369046
</td>
<td style="text-align:right;">
0.2386123
</td>
</tr>
<tr>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0896597
</td>
<td style="text-align:right;">
0.0899462
</td>
<td style="text-align:right;">
0.0882384
</td>
</tr>
<tr>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0585787
</td>
<td style="text-align:right;">
0.0582923
</td>
<td style="text-align:right;">
0.0600000
</td>
</tr>
<tr>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0002864
</td>
<td style="text-align:right;">
0.0000000
</td>
<td style="text-align:right;">
0.0017077
</td>
</tr>
<tr>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0028090
</td>
<td style="text-align:right;">
0.0030954
</td>
<td style="text-align:right;">
0.0013877
</td>
</tr>
</tbody>
</table>

The actual solution is in the convex hull of the two extreme solutions.
And the logistic regression is blind to changes in the `test_vec`
direction (shown in appendix). So we can recover the correct logistic
regression coefficients from any of these solutions.

``` r
for (soln_name in soln_names) {
  print(soln_name)
  suppressWarnings(
    soln_i <- glm(
      y ~ x1 + x2,
      data = detailed_frame,
      weights = detailed_frame[[soln_name]],
      family = binomial()
    )$coef
  )
  print(soln_i)
  stopifnot(  # abort render if this claim is not true
    max(abs(correct_coef - soln_i)) < 1e-6)
}
```

    ## [1] "recovered_distribution_1"
    ## (Intercept)          x1          x2 
    ##   0.5772157   3.1415927  -8.1548455 
    ## [1] "recovered_distribution_2"
    ## (Intercept)          x1          x2 
    ##   0.5772157   3.1415927  -8.1548455

We see, all recovered data distributions give the same correct estimates
of the logistic regression coefficients.

### Picking a point-estimate

The standard trick with an under-specified system is to add an
objective. A great choice is: maximize the entropy of (or flatness of)
the distribution we are solving for.

This works as follows.

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

``` r
# brute force solve for maximum entropy mix
# obviously this can be done a bit slicker
opt_soln <- optimize(
  function(z) {
    entropy(
      z * detailed_frame$recovered_distribution_1 + 
        (1 - z) * detailed_frame$recovered_distribution_2)},
  c(0, 1),
  maximum = TRUE)

z_opt <- opt_soln$maximum
detailed_frame["maxent_distribution"] <- (
  z_opt * detailed_frame$recovered_distribution_1 + 
    (1 - z_opt) * detailed_frame$recovered_distribution_2)
```

The recovered `maxent_distribution` obeys the additional non-linear
check to a high degree.

``` r
log(detailed_frame[["maxent_distribution"]]) %*% test_vec
```

    ##              [,1]
    ## [1,] 3.395224e-05

In fact, the recovered `maxent_distribution` *is* the original
unobserved original `P(X1=x1, X2=x2, Y=y)` to many digits.

<table>
<thead>
<tr>
<th style="text-align:right;">
x1
</th>
<th style="text-align:right;">
x2
</th>
<th style="text-align:left;">
y
</th>
<th style="text-align:right;">
P(X1=x1, X2=x2, Y=y)
</th>
<th style="text-align:right;">
maxent_distribution
</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.0503403
</td>
<td style="text-align:right;">
0.0503403
</td>
</tr>
<tr>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.0014213
</td>
<td style="text-align:right;">
0.0014213
</td>
</tr>
<tr>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.5597136
</td>
<td style="text-align:right;">
0.5597135
</td>
</tr>
<tr>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:left;">
FALSE
</td>
<td style="text-align:right;">
0.2371910
</td>
<td style="text-align:right;">
0.2371910
</td>
</tr>
<tr>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0896597
</td>
<td style="text-align:right;">
0.0896597
</td>
</tr>
<tr>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
0
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0585787
</td>
<td style="text-align:right;">
0.0585787
</td>
</tr>
<tr>
<td style="text-align:right;">
0
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0002864
</td>
<td style="text-align:right;">
0.0002865
</td>
</tr>
<tr>
<td style="text-align:right;">
1
</td>
<td style="text-align:right;">
1
</td>
<td style="text-align:left;">
TRUE
</td>
<td style="text-align:right;">
0.0028090
</td>
<td style="text-align:right;">
0.0028090
</td>
</tr>
</tbody>
</table>

And these are our estimated coefficients.

``` r
recovered_coef <- suppressWarnings(
  glm(
    y ~ x1 + x2,
    data = detailed_frame,
    weights = detailed_frame[["maxent_distribution"]],
    family = binomial()
  )$coef
)

recovered_coef
```

    ## (Intercept)          x1          x2 
    ##   0.5772157   3.1415927  -8.1548455

This matches the correct (c0=0.5772, b1=3.1416, b2=-8.1548). We have
correctly inferred the actual coefficient values from the observed data.
We have removed the bias.

### Why the Maximum Entropy Solution is So Good

Some calculus (in appendix) shows that the entropy function for this
problem is maximized where the logarithm of the joint distribution is
orthogonal to `ns` or `test_vec`. So the maximum entropy condition will
enforce the extra non-linear invariant we know from our assumed problem
structure.

The funny thing is, we don’t have to know exactly what the maximum
entropy objective was doing to actually benefit from it. It tends to be
a helpful objective in modeling. In practice we don’t usually derive
`test_vec` but just impose the maximum entropy objective and trust that
it will help.

## Conclusion

By pooling observations we can recover a good estimate of a joint
analysis on data that was not available to us. The strategy is: try to
estimate plausible pre-images of the data that formed the observations,
and then analyze that. This gives us a method to invert the bias
introduced by the omitted variables in logistic regression.

In machine learning the [maximum entropy
principle](https://en.wikipedia.org/wiki/Principle_of_maximum_entropy)
plays the role that the [stationary-action principle
action](https://en.wikipedia.org/wiki/Stationary-action_principle) plays
in classic mechanics. While *nature* isn’t forced to put equal
probabilities on different states, deterministic models *must* put equal
probabilities on model indistinguishable states. Maximum entropy pushes
solutions to such symmetries, unless there are variables to support
differences. And, [maximum entropy modeling is very related to logistic
regression
modeling](https://win-vector.com/2011/09/23/the-equivalence-of-logistic-regression-and-maximum-entropy-models/).

There is, however, a danger. A naive over-reliance on the [principle of
indifference](https://en.wikipedia.org/wiki/Principle_of_indifference)
can lead to incorrect modeling. Nature may be able to distinguish
between states that a given set of experimental variables can not. Also,
the general applicability of maximum entropy techniques isn’t an excuse
to not look for problem specific *reasons* why such an objective helps.
This is what we did in this note when developing the non-linear
orthogonality condition. This condition is a consequence of the fact
that the logit-linear form of the logistic regression *we*, as the
experimenter, imposed on the data. At some point we are observing the
regularity of our assumptions, not of the original unobserved data.

In the real world we would at best be looking at marginalizations of
different draws of related data. So we would not have exact matches we
can invert- but instead would have to estimate low-discrepancy
pre-images of the data. And, as we are now introducing a lot of
unobserved parameters, we could go to Bayesian graphical model methods
to sum this all out (instead of proposing a specific point-wise method
as we did here).

We have some notes on how this method applies in a more general case
[here](https://github.com/WinVector/Examples/blob/main/LogisticOmit/LargeSystem.md).

## Appendices

## Appendix: The Relation to Entropy

The maximum likelihood solution to a logistic regression problem is
equivalent picking a paramaterized distribution `q` close to the target
distribution `p` by minimizing the cross entropy below.

<pre>
  - sum<sub>i</sub> p<sub>i</sub> log q<sub>i</sub>
</pre>

When `q` gets close to `p` this looks a lot like the standard entropy
below.

<pre>
  - sum<sub>i</sub> p<sub>i</sub> log p<sub>i</sub>
</pre>

So we do expect entropy calculations to be relevant to logistic
regression structure. We will back up this claim with detailed
calculation.

## Appendix: `test_vec` is an Orthogonal Test

To show `sum(test_vec * log(P(X1=x1, X2=x2, Y=y)) = 0` when
`P(X1=x1, X2=x2, Y=y)` is the row probabilities matching a logistic
model, write `sum(test_vec * log(P(X1=x1, X2=x2, Y=y)))` as:

<pre>
sum<sub>x1=0,1</sub> sum<sub>x2=0,1</sub> sum<sub>y=F,T</sub> (
   (-1)<sup>x1</sup> * (-1)<sup>x2</sup> * (-1)<sup>y</sup> 
     * log(P(X1=x1, X2=x2) * p(Y=y | x1, x2))
   )
&#10; = sum<sub>x1=0,1</sub> sum<sub>x2=0,1</sub> (
    (-1)<sup>x1</sup> * (-1)<sup>x2</sup> * ( 
       log(P(X1=x1, X2=x2) * 
          (1 - 1 / (1 + exp(c0 + b1 * x1 + b2 * x2))))
      - log(P(X1=x1, X2=x2) * 
          1 / (1 + exp(c0 + b1 * x1 + b2 * x2)))
    ))
    &#10;
 = sum<sub>x1=0,1</sub> sum<sub>x2=0,1</sub> (
    (-1)<sup>x1</sup> * (-1)<sup>x2</sup> * ( 
        log(P(X1=x1, X2=x2) * 
           (exp(c0 + b1 * x1 + b2 * x2) / (1 + exp(c0 + b1 * x1 + b2 * x2))))
      - log(P(X1=x1, X2=x2) * 
           1 / (1 + exp(c0 + b1 * x1 + b2 * x2)))
    ))
&#10; = sum<sub>x1=0,1</sub> sum<sub>x2=0,1</sub> (
    (-1)<sup>x1</sup> * (-1)<sup>x2</sup> * log(exp(c0 + b1 * x1 + b2 * x2)))
&#10; = sum<sub>x1=0,1</sub> sum<sub>x2=0,1</sub> (
    (-1)<sup>x1</sup> * (-1)<sup>x2</sup> * (c0 + b1 * x1 + b2 * x2))
&#10; = 0
</pre>

This establishes that `sum(test_vec * log(P(X1=x1, X2=x2, Y=y))) = 0`
for any logistic regression solution, not just the optimal one. This
condition is true for our data set, as we designed it to have the
structure of a logistic regression. And this shows logistic regression
can not tell `P(X1=x1, X2=x2, Y=y) + z * test_vec` from
`P(X1=x1, X2=x2, Y=y)`, as it is blind to changes in that direction.
This is why all our data pre-images yield the same logistic regression
coefficients.

## Appendix: the Entropy Gradient Goes to Zero at our Check Position

We can show the entropy gradient is zero at our check-gradient position.
So, maximizing entropy picks the position where we meet our non-linear
orthogonal check condition.

To establish this, consider the entropy function we are maximizing
<code>f(z) = -sum<sub>i</sub> (p<sub>i</sub> + z \*
test_vec<sub>i</sub>) log(p<sub>i</sub> + z \*
test_vec<sub>i</sub>)</code>. We expect our maximum occurs where
<code>f(z)</code> has a zero derivative.

<pre>
(d / d z) f(z) [evaluated at z = 0]
&#10; = (d / d z) -sum<sub>i</sub> (
    p<sub>i</sub> + z * test_vec<sub>i</sub>) 
      * log(p<sub>i</sub> + z * test_vec<sub>i</sub>) 
    [evaluated at z = 0]
 &#10; = -sum<sub>i</sub> test_vec<sub>i</sub> (
    log(p<sub>i</sub> + z * test_vec<sub>i</sub>) + 1) 
    [evaluated at z = 0]
 &#10; = -sum<sub>i</sub> test_vec<sub>i</sub> (log(p<sub>i</sub>) + 1)
 &#10; = -sum<sub>i</sub> test_vec<sub>i</sub> log(p<sub>i</sub>)  
    [using -sum<sub>i</sub> test_vec<sub>i</sub> = 0]
</pre>

And this is zero exactly where the non-linear orthogonal check condition
is zero.

## Appendix: Links

The source code of this article is available
[here](https://github.com/WinVector/Examples/blob/main/LogisticOmit/margin_recovery.Rmd)
(plus render
[here](https://github.com/WinVector/Examples/blob/main/LogisticOmit/margin_recovery.md)).
