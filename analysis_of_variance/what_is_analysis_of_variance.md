What Good is Analysis of Variance?
================
2024-02-19

## Introduction

I’d like to demonstrate what “analysis of variance” (often abbreviated
as “anova” or “aov”) does for you as a data scientist or analyst. After
reading this note you should be able to determine how an analysis of
variance style calculation can or can not help with your project.

<center>
<img src="McB-01.jpg"/>
<p/>
(Orson Welles as Macbeth, a photo that will be made relevant in the
conclusion)
</center>

We will exhibit specific examples, in [`R`](https://www.r-project.org),
designed to trigger most of the issues we are worried about *all at the
same time*. In practice (for data sets with large meaningful signal,
relations, or correlations) not everything we are worried about tends to
fail at the same time. However, it is quite instructive to see
everything go wrong at the same time.

We will show the exact calculations performed, beyond saying “call
`aov()`”. This isn’t to discuss the implementation, which we trust, but
to make clear what the reported statistics are. This lets us confirm
that the current `R` `aov()` calculations do in fact organize the data
in the manner Fisher described (which is not in fact obvious from trying
to read the source code).

We will also discuss some of the difficulty in pinning down the intent
and meaning of analysis of variance in a discussion section.

## Analysis of Variance

Analysis of variance comes to many of us from works derived from R. A.
Fisher \*Statistical Methods for Research Workers(, Oliver and Boyd,
1925. In chapter VII “Intraclass Correlations and the Analysis of
Variance” Fisher writes:

> If `k` is the number in each class, then each set of `k` values will
> provide `k (k − 1)` values for the symmetrical table, which thus may
> contain an enormous number entries, and be very laborious to
> construct. To obviate this difficulty Harris introduced an abbreviated
> method of calculation by which the value of the correlation given by
> the symmetrical table may be obtained directly from two distributions.

Roughly, Fisher is saying that Harris (1916) suggests evaluating the
quality and significance of a model fit from a small number of summaries
or statistics. This is a more sensitive method than a common naive idea
of attempting to attribute model fit and model quality down to specific
levels of variables.

In such early examples we have:

- A regression problem, or a numeric valued variable we are trying to
  predict (called the dependent variable or outcome).
- One or more category or string-valued explanatory variables with a
  fixed set of values or levels. This reduces the numeric prediction or
  regression problem to a partitioning problem or evaluating clustering
  quality.
- The decision to use square error as a loss function. Larger square
  error is bad, and small square error is good.
- A single test statistic or summary. In this case the statistic is:
  measured reduction (as a ratio) of square error or variance. This
  statistic allows a calculation of significance of result through an
  [F-test](https://en.wikipedia.org/wiki/F-test).
- The decision to use adjustments of “in sample” statistics to determine
  model quality. This differs from the more general (though much more
  computationally expensive) practice of test data, hold out data, or
  [cross
  methods](https://win-vector.com/2020/03/10/cross-methods-are-a-leak-variance-trade-off/)
  (including cross validation). Such adjustments are reliable for linear
  models (where the [model over-fit is bounded by “degrees of
  freedom”](https://win-vector.com/2023/03/16/bounding-excess-generalization-error-for-linear-regression-models/),
  but are not always applicable to more general models (including trees
  and neural nets).

Analysis of variance quickly got generalized past the above to include
arbitrary nested models (instead of only categorical variables),
detailed attribution of model performance to groups of variables, and
classification models (through dispersion measures such as [statistical
deviance](https://en.wikipedia.org/wiki/Deviance_(statistics))).
However, key ideas and terminology originate in the categorical or
partitioning case.

### An Analysis of Variance Example, Where There is No Signal

Let’s try analysis of variance with current tools.

First we set up a data set with a dependent or outcome variable “`y`”
and a single categorical explanatory variable “`group`”. For this first
example we deliberately design the variable `group` to be useless and
generated independently of `y` (which we, through a very slight abuse of
terminology call “the null situation”).

``` r
# seed pseudo-random generator for replicability
set.seed(2024)
```

``` r
# pick our number of data rows
# this is a large number to dispel:
#  "you only run into statistical problems with small data"
m_row <- 100000
```

``` r
# pick the k=100 levels or values for our explanatory variable
# this is a small number in some applications
group_levels <- sprintf(
  "level_%03d", seq(100))
```

``` r
# build our data
d_null <- data.frame(
  group = sample(
    group_levels, 
    size = m_row, 
    replace = TRUE)
)
d_null$y <- 10 * rnorm(n = m_row)
```

``` r
# show a bit of our data
knitr::kable(head(d_null))
```

| group     |         y |
|:----------|----------:|
| level_066 | -3.523702 |
| level_037 | 16.144303 |
| level_045 |  6.997154 |
| level_060 | -3.063851 |
| level_017 |  5.519029 |
| level_032 | -2.761535 |

We are now ready to perform our analysis of variance.

``` r
summary(aov(
  y ~ group,
  data = d_null))
```

    ##                Df  Sum Sq Mean Sq F value Pr(>F)
    ## group          99    8638   87.25   0.872  0.813
    ## Residuals   99900 9991165  100.01

The above report has columns summarizing facts about:

- `Df`: the “degrees of freedom.” This is the unit of measure for
  examples, instances, and even coefficients and variables. We will
  include a small section on this concept later.
- `Sum sq`: the sum of squares, what is colloquially called the
  variances.
- `Mean Sq`: `(Sum Sq) / Df`. This is a “bias corrected” variance
  estimate.
- `F value`: the statistic mentioned by Fisher. In fact this is the
  F-statistic, a random variable that is distributed as we would expect
  the ratio of two variances to be distributed. Technically it is
  distributed as the ratio of two chi-square distributions
  ([ref](https://en.wikipedia.org/wiki/F-distribution)), which in turn
  are distributed as sums of squares of normally distributed random
  variables. All this machinery is to give us a distribution that lets
  us estimate if an observed ratio of two variances (or sums of squares)
  is considered large or small. We want this value to be above 1.
- `Pr(>F)`: the significance of the observed `F value`. Values near zero
  mean our observed F value is large enough to be *not* often produced
  by mere sampling phenomena. This is then taken as evidence of a good
  model fit. Be aware “highly significant” means a significance near
  zero, not a large one. Also, significance is merely the chance of
  seeing a signal as least as strong as observed, *assuming* the signal
  was due to sampling error. A significance is only the estimate
  probability of one type of error, and there are many more ways than
  one to go wrong in modeling. A significance is very much **NOT** one
  minus the chance we have a good fit!!!

The rows of the report show:

- `group`: our categorical variable.
  - `Df = 99`, means that `group` consumes 99 “degrees of freedom”. This
    comes from the fact that the 100 possible levels for the categorical
    variable `group` get expanded into 100 different numeric indicator
    variables during analysis. One is subtracted as there is a linear
    dependence in this re-encoding.
  - `Sum Sq = 8638` means the analysis of variance is crediting the
    variable `group` with 8638 units of variance explained. We want this
    to be large.
  - `F value = 0.872`. The F value is how much reduction in square
    difference or variance we are seeing. We want this to be greater
    than 1.
  - `Pr(>F) = 0.813` means a sampling process where there is no relation
    between `group` and `y` can produce an F value as large as observed
    81.3% of the time. This non-significance is the measure of how
    uninteresting this F value is.
- `Residuals`: the variation unexplained by the model.
  - `Df`: the number of example or instance rows in the data set minus
    the `Df` of all the variables (again minus 1). The idea is: each
    variable could be used to fix the answer of a single row, so this is
    how many somewhat novel rows our model was tried on. We want this to
    be large.
  - `Sum Sq`: the unexplained variance. We want this to be small.

The data set we analyzed has no relation, so the poor opinion on model
quality expressed by the analysis of variance is exactly the correct
determination.

#### Degrees of Freedom

“Degrees of freedom” is a unit of “how many examples is one looking at?”
Roughly think of degrees of freedom as: “number of opportunities to be
wrong.”

For a data set the degrees of freedom is the number of data rows or
example instances. We usually use the number of rows minus 1, as we are
usually assuming we start with an estimate of the average or mean of the
data (consuming 1 degree of freedom).

For a linear model: the degrees of freedom is the number of model
coefficients, which in turn corresponds to the number of *numeric*
variables. For categorical variables we get one degree of freedom per
level or possible categorical value, minus one (due to the linear
dependence in the usual method of expanding categorical variables to 0/1
indicator variables).

In linear models over data: we tend to lose one degree of freedom per
fitted coefficient in the model
([ref](https://win-vector.com/2023/03/16/bounding-excess-generalization-error-for-linear-regression-models/).
It is this *arbitrage* in counting that lets us use degrees of freedom
to count variables or coefficients in addition to instances.

Roughly: we get degrees of freedom by inspection. For data and linear
models, degrees of freedom is a matter of counting. Getting the number
exactly right (within `+-1`) can be a *very* contentious discussion.
Fortunately, for large data sets and large numbers of variables “close
is good enough” in specifying the degrees of freedom.

#### The Calculations

Let’s directly calculate all of the items in the analysis of variance
table. This code will be much less general than R’s `aov()`, but can
show us exactly what is going on in a simple “single categorical
variable” (or clustering) case.

``` r
# compute analysis of variance of dependent variable y
# clustered by categorical explanatory variable group
aov_by_hand <- function(y, group) {
  # get observed group means
  observed_effects <- aggregate(
    y,
    by = list(group),
    FUN = mean)
  # build a group to effect lookup table
  oe <- observed_effects[, 2, drop = TRUE]
  names(oe) <- observed_effects[, 1, drop = TRUE]
  # calculate components of analysis of variance table
  # declare degrees of freedom
  df_group <- length(oe) - 1
  df_residual <- length(y) - df_group - 1
  # get sums of square differences
  group_sq <- sum(  # what is traditional
    (oe[group] - mean(y))**2)  
  model_improvement <- ( # what we care about
    sum((y - mean(y))**2) - sum((y - oe[group])**2))  
  stopifnot(abs(group_sq - model_improvement) < 1e-8)  # confirm equal
  residual_sq <- sum((y - oe[group])**2)  # unexplained variation
  # get the averages, un-biasing the estimate by dividing by degrees
  # of freedom instead of number of instances
  group_mean_sq <- group_sq / df_group
  residual_mean_sq <- residual_sq / df_residual
  # calculate the test statistic
  F_value <- group_mean_sq / residual_mean_sq
  # compute the significance of the test statistic
  # this is essentially a table lookup or special function
  group_sig <- pf(
    F_value, 
    df_group, 
    df_residual, 
    lower.tail = FALSE)
  # wrap report into a data frame
  anova_table <- data.frame(
    `Df` = c(df_group, df_residual),
    `Sum Sq` = c(group_sq, residual_sq),
    `Mean Sq` = c(group_mean_sq, residual_mean_sq),
    `F value` = c(F_value, NA),
    `Pr(>F)` = c(group_sig, NA),
    check.names = FALSE
  )
  row.names(anova_table) <- c("group", "Residuals")
  return(anova_table)
}
```

``` r
# show our by hand analysis of variance
knitr::kable(
  aov_by_hand(d_null$y, d_null$group)
)
```

|           |    Df |     Sum Sq |   Mean Sq |   F value |   Pr(\>F) |
|:----------|------:|-----------:|----------:|----------:|----------:|
| group     |    99 |    8637.85 |  87.25101 | 0.8724083 | 0.8134564 |
| Residuals | 99900 | 9991165.48 | 100.01167 |        NA |        NA |

This agrees with our previous calculation.

``` r
aov_null <- summary(aov(
    y ~ group,
    data = d_null))[[1]]
knitr::kable(
  aov_null
)
```

|           |    Df |     Sum Sq |   Mean Sq |   F value |   Pr(\>F) |
|:----------|------:|-----------:|----------:|----------:|----------:|
| group     |    99 |    8637.85 |  87.25101 | 0.8724083 | 0.8134564 |
| Residuals | 99900 | 9991165.48 | 100.01167 |        NA |        NA |

``` r
# confirm calculates match
stopifnot(max(abs(
  aov_by_hand(d_null$y, d_null$group) - 
    summary(aov(y ~ group, data = d_null))[[1]]), na.rm = TRUE)
  < 1e-7)
```

### An Analysis of Variance Example, Where There is a Signal

Let’s repeat our analysis on a data set where there is a relation
between `group` and `y`.

We build our new data set. For some of the `group_levels` we are going
to add a bit of a level-effect to `y`. This is what we would be looking
for in either a linear model or in a clustering model. We are simulating
the common modeling situation where knowing the group label is sometimes
somewhat useful in predicting the outcome.

``` r
# start with no effect for any level 
group_effect <- rep(0, length(group_levels))
names(group_effect) <- group_levels
# add an effect to first 25 group levels
effect_levels <- group_levels[1:25]
for(level_name in effect_levels) {
  group_effect[level_name] <- (
    0.4 * ifelse(
      rbinom(n = 1, size = 1, prob = 0.5) > 0.5,
      1, -1))
}
# the new example data
d_effect <- d_null
d_effect$y <- d_null$y + group_effect[d_effect$group]
```

Now that we have our new data, let’s run an analysis of variance on it.

``` r
knitr::kable(
  summary(aov(
    y ~ group,
    data = d_effect))[[1]]
)
```

|           |    Df |     Sum Sq |  Mean Sq |  F value |  Pr(\>F) |
|:----------|------:|-----------:|---------:|---------:|---------:|
| group     |    99 |   14347.85 | 144.9277 | 1.449108 | 0.002359 |
| Residuals | 99900 | 9991165.48 | 100.0117 |       NA |       NA |

``` r
# confirm by hand calculation matches
stopifnot(max(abs(
  aov_by_hand(d_effect$y, d_effect$group) - 
    summary(aov(y ~ group, data = d_effect))[[1]]), na.rm = TRUE)
  < 1e-7)
```

It may not seem so, but this is in fact better. From the new analysis of
variance table we can see the `group` variable is explaining as a
`14347.85 / (14347.85 + 9991165.48) = 0.0014` fraction of the overall
variance. This is, unfortunately minuscule. However it *is* consistent
with a small real effect or relation between `group` and `y`. The large
F value and small significance confirm that this is a performance that
is unlikely *if we assume* no relation is present.

The analysis of variance is supplying at least three very valuable
services:

- It is estimating the overall quality of the model as an observed
  reduction in square error.
- It is computing a significance of the above estimated model quality.
- It can control what variables or sets of variables we attribute model
  quality to. In fact we can decompose the model’s performance into an
  (order dependent) sequence of sub models or groups of variables.

What this analysis shows: *is* there an effect among the variables or
variable levels. But this does not show if there are specific levels
responsible for the quality of the fit.

### What **NOT** To Do

Now that we have seen an analysis of variance, let’s use a much less
powerful naive ad-hoc analysis. This is what one might attempt without
analysis of variance type tools. The poor performance of this
alternative is one of the justifications for incorporating analysis of
variance into your workflow.

What the analysis of variance did well is: it assigned model quality to
all the levels of a categorical variable as a *single* modeling step.
What our inferior analysis will do is: attempt to assign model quality
to individual variable levels. In other words, we are trying to find a
best level explaining some fraction of model fit. This will,
unfortunately, split what little explanatory power the `group` variable
has across the levels. In addition this will invite in undesirable
[multiple comparison
issues](https://en.wikipedia.org/wiki/Multiple_comparisons_problem) as
one inspects the many estimated level effects. Together these issues
give a test of low sensitivity, not able to effectively detect weak (but
actual) effects or relations.

First let’s fit a linear model on our first (“null”) data.

``` r
m_null <- lm(
  y ~ 0 + group,
  data = d_null)
```

The “`0 +`” notation allows all levels of the categorical explanatory
variable `group` to be tracked (normally one level is suppressed as the
“reference” level). This fits a model that is a bit easier to explore.
However it is known to [ruin the summary
statistics](https://win-vector.com/2017/06/15/an-easy-way-to-accidentally-inflate-reported-r-squared-in-linear-regression-models/),
so we will we not use the summary statistics from this fit.

Without the “`0 +`” notation the `lm()` summary does contain the same
F-test as the analysis of variance. So the linear model *can* be used to
directly identify if there is a significant fit.

``` r
# show linear model F test
lm_f_test <- sigr::wrapFTest(
  lm(y ~ group, data = d_null))

cat(sigr::render(
  lm_f_test,
  pLargeCutoff=1, format='markdown'))
```

**F Test** summary: (<i>R<sup>2</sup></i>=0.0008638,
*F*(99,99900)=0.8724, *p*=0.8135).

``` r
# confirm same values
stopifnot(abs(lm_f_test$FValue - aov_null[1, 'F value']) < 1e-8)
stopifnot(abs(lm_f_test$pValue - aov_null[1, 'Pr(>F)']) < 1e-8)
```

The fault in this scheme is *not* the linear modeling, but in ignoring
the F-test and looking at the individual level fits too early. If all
you want is the F-test, you can usually get that from the linear fit
diagnostics without running an additional analysis of variance.

That being said: lets ignore the linear model F-test, and attempt (and
fail) to use significance to filter down to some interesting variable
levels.

``` r
# pick our "what is interesting" threshold
significance_threshold <- 0.05
```

``` r
# sort down to interesting coefficients or variables
null_coef <- data.frame(
  summary(m_null)$coefficients,
  significance_threshold = significance_threshold,
  check.names = FALSE
)

interesting_null_coef <- null_coef[
  null_coef[['Pr(>|t|)']] < significance_threshold,
  c("Pr(>|t|)", "significance_threshold"), 
  drop = FALSE]

stopifnot(nrow(interesting_null_coef) > 0)

knitr::kable(interesting_null_coef)
```

|                | Pr(\>\|t\|) | significance_threshold |
|:---------------|------------:|-----------------------:|
| grouplevel_012 |   0.0440619 |                   0.05 |
| grouplevel_047 |   0.0147498 |                   0.05 |
| grouplevel_056 |   0.0281266 |                   0.05 |
| grouplevel_060 |   0.0247010 |                   0.05 |
| grouplevel_066 |   0.0313065 |                   0.05 |

At first it appears that we have identified a few important variable
levels. However, we (deliberately) neglected that when we are sifting
through 100 variable levels looking for winners: we are subject to the
[multiple comparisons
problem](https://en.wikipedia.org/wiki/Multiple_comparisons_problem).
Even if all the variables are useless (as they in fact are here), after
inspecting 100 of them at a 5% significance we would expect to find
about 5 false positives. By coincidence that is how many we found. So
these “finds” are not numerous enough or strong enough to be considered
convincing evidence there is a relation between “group” and “y” (which
is just as well, as there is no such relation in this data set).

A correct procedure is to “apply a [Bonferroni
correction](https://en.wikipedia.org/wiki/Bonferroni_correction).” This
is just saying “if you are looking at 100 things, you have to tighten up
your significance criteria by a factor of 100.” Let’s do this.

``` r
# tighten the filter using the Bonferroni correction
interesting_null_coef['Bonferroni corrected threshold'] <- (
  interesting_null_coef["significance_threshold"] / 
    length(group_levels))
interesting_null_coef['still interesting'] <- (
  interesting_null_coef[['Pr(>|t|)']] <= 
    interesting_null_coef[['Bonferroni corrected threshold']])

knitr::kable(interesting_null_coef)
```

|                | Pr(\>\|t\|) | significance_threshold | Bonferroni corrected threshold | still interesting |
|:---------------|------------:|-----------------------:|-------------------------------:|:------------------|
| grouplevel_012 |   0.0440619 |                   0.05 |                          5e-04 | FALSE             |
| grouplevel_047 |   0.0147498 |                   0.05 |                          5e-04 | FALSE             |
| grouplevel_056 |   0.0281266 |                   0.05 |                          5e-04 | FALSE             |
| grouplevel_060 |   0.0247010 |                   0.05 |                          5e-04 | FALSE             |
| grouplevel_066 |   0.0313065 |                   0.05 |                          5e-04 | FALSE             |

There is no strong evidence of any relation between any `group` level
and `y`. This is what was designed into this data, so it is a correct
determination.

``` r
# confirm statement
stopifnot(all(interesting_null_coef[["still interesting"]] == FALSE))
```

### Why To Not Do What We Just Showed

The Bonferroni Correction is “correct” in that it helps suppress false
positive variables and variable levels. However, it sacrifices
sensitivity. In fact it is so insensitive that this analysis procedure
will fail to pick up small but true relations or effects in our other
example.

Let’s show the (bad) analysis on the data set where we *know* there is a
relation.

``` r
# repeat the previous per-level analysis on new data
m_effect <- lm(
  y ~ 0 + group, 
  data = d_effect)

effect_coef <- data.frame(
  summary(m_effect)$coefficients,
  check.names = FALSE
)

interesting_effect_coef <- effect_coef[
  ((effect_coef[['Pr(>|t|)']] < significance_threshold)) |
    (row.names(effect_coef) %in% paste0("group", effect_levels)),
  c("Pr(>|t|)"),
  drop = FALSE]
interesting_effect_coef['Bonferroni corrected threshold'] <- (
  significance_threshold / length(group_levels))
interesting_effect_coef['still interesting'] <- (
  interesting_effect_coef[['Pr(>|t|)']] <= 
    interesting_effect_coef[['Bonferroni corrected threshold']])

knitr::kable(interesting_effect_coef)
```

|                | Pr(\>\|t\|) | Bonferroni corrected threshold | still interesting |
|:---------------|------------:|-------------------------------:|:------------------|
| grouplevel_001 |   0.0754553 |                          5e-04 | FALSE             |
| grouplevel_002 |   0.2257353 |                          5e-04 | FALSE             |
| grouplevel_003 |   0.0982440 |                          5e-04 | FALSE             |
| grouplevel_004 |   0.2077323 |                          5e-04 | FALSE             |
| grouplevel_005 |   0.0933375 |                          5e-04 | FALSE             |
| grouplevel_006 |   0.8127896 |                          5e-04 | FALSE             |
| grouplevel_007 |   0.2694684 |                          5e-04 | FALSE             |
| grouplevel_008 |   0.8755393 |                          5e-04 | FALSE             |
| grouplevel_009 |   0.0013846 |                          5e-04 | FALSE             |
| grouplevel_010 |   0.1767863 |                          5e-04 | FALSE             |
| grouplevel_011 |   0.3034294 |                          5e-04 | FALSE             |
| grouplevel_012 |   0.0010999 |                          5e-04 | FALSE             |
| grouplevel_013 |   0.3760182 |                          5e-04 | FALSE             |
| grouplevel_014 |   0.0428443 |                          5e-04 | FALSE             |
| grouplevel_015 |   0.0752557 |                          5e-04 | FALSE             |
| grouplevel_016 |   0.8916944 |                          5e-04 | FALSE             |
| grouplevel_017 |   0.3126977 |                          5e-04 | FALSE             |
| grouplevel_018 |   0.0524820 |                          5e-04 | FALSE             |
| grouplevel_019 |   0.3188409 |                          5e-04 | FALSE             |
| grouplevel_020 |   0.0599345 |                          5e-04 | FALSE             |
| grouplevel_021 |   0.0582381 |                          5e-04 | FALSE             |
| grouplevel_022 |   0.6620659 |                          5e-04 | FALSE             |
| grouplevel_023 |   0.0294470 |                          5e-04 | FALSE             |
| grouplevel_024 |   0.0148508 |                          5e-04 | FALSE             |
| grouplevel_025 |   0.0021958 |                          5e-04 | FALSE             |
| grouplevel_047 |   0.0147498 |                          5e-04 | FALSE             |
| grouplevel_056 |   0.0281266 |                          5e-04 | FALSE             |
| grouplevel_060 |   0.0247010 |                          5e-04 | FALSE             |
| grouplevel_066 |   0.0313065 |                          5e-04 | FALSE             |

Notice: none of the variables (including those that were actually doing
something!) survived the Bonferroni corrected significance filter. The
ad-hoc per-variable analysis method is not sufficiently sensitive. And
this is why we suggest using analysis of variance instead of the
per-variable or per-level attribution idea.

``` r
# confirm statement
stopifnot(all(interesting_effect_coef[["still interesting"]] == FALSE))
```

If you want to evaluate model fit: directly evaluate model fit. And
analysis of variance directly evaluates a total model fit summary
statistic.

## Discussion

Analysis of variance can be tricky to pin down and describe. That being
said, let’s try to say some things about analysis of variance.

- “… the analysis of variance, which may perhaps be called a statistical
  method, because the term is an a very ambiguous one- is not a
  mathematical theorem, but rather a convenient method of arranging the
  arithmetic.” R. A Fisher 1934, as cited by Speed, “What is an Analysis
  of Variance?”, Special Invited Paper, The Annals of Statistics, 1987,
  Vol 15, No 3, pp. 885-910.
- Many good sources call the analysis of variance a generalization of a
  [t-test](https://en.wikipedia.org/wiki/Student%27s_t-test) to more
  than two group levels (Horst Langer, Susanna Falsaperla and Conny
  Hammer, “Advantages and Pitfalls of Pattern Recognition Selected Cases
  in Geophysics”, Volume 3 in Computational Geophysics 2020; Marc Kéry,
  in “Introduction to WinBUGS for Ecologists”, 2010; and others).
  Similar claims include: “just the case of regression for 0/1
  variables” or “just the case of regression for truly orthogonal
  variables (arising from proper experiment design).”
- The previous point itself is somewhat contradicted by claimed methods
  that appear to be mere applications of analysis of variance to
  clustering problems (analysis of variance’s actual original domain!).
  For example: the the [Calinski–Harabasz
  index](https://en.wikipedia.org/wiki/Calinski–Harabasz_index) from
  clustering is crypto-morphic to our friend the F-statistic.
- A key additional feature of the analysis of variance is the crediting
  of explained variance to chosen variables or groups of variables (or
  more precisely to nested models). The convention is that model
  improvement is calculated in terms of the square-difference in nested
  model predictions, instead of in terms of the square reduction of
  prediction residuals. Under mild model optimality assumptions: these
  two quantities are identical. The second quantity is the one
  practitioners are likely to care about. The form of the first quantity
  likely helps derive of the number of degrees of freedom as used in the
  calculation.
- The “variances” analyzed are possibly better described with less
  semantically loaded terms such as “dispersions” or “sums of square
  differences” (depending on the specialization). Speed, “What is an
  Analysis of Variance?”, Special Invited Paper, The Annals of
  Statistics, 1987, Vol 15, No 3, pp. 885-910 states: “But all of this
  is just sums of squares- quadratic forms in normal variates if you
  wish; the only variance in sight is the common σ<sup>2</sup> and that
  does not appear to be undergoing any analysis.”
- There is overlap and competition between analysis of variance (Harris,
  Fisher ~ 1916 - 1925) and multiple linear regression (Galton, Pearson,
  Bravias ~ 1846 - 1930), (Gauss ~ 1821, Markov ~ 1900).

## Attribution by Analysis of Variance

Analysis of variance becomes very useful when there are multiple
variables and we want to attribute model utility down to the variables.
This analysis depends on the order the variables are presented in, so it
is contingent on user choices. This is inevitable as [variable utility
is not
intrinsic](https://win-vector.com/2021/01/12/variable-utility-is-not-intrinsic/).

A simple example is given here.

We set up our data.

``` r
# build new data set
m_rows <- 10000
v_common <- rnorm(n = m_rows)
v_1 <- rnorm(n = m_rows)
v_2 <- rnorm(n = m_rows)
d <- data.frame(
  x_1 = v_common + v_1,
  x_2 = v_common + v_2,
  y = v_common + v_1 + 2 * v_2 + rnorm(n = m_rows)
)
```

We then perform an analysis of variance.

``` r
summary(aov(
  lm(y ~ x_1 + x_2, data = d)))
```

    ##               Df Sum Sq Mean Sq F value Pr(>F)    
    ## x_1            1  20150   20150    8654 <2e-16 ***
    ## x_2            1  25124   25124   10790 <2e-16 ***
    ## Residuals   9997  23278       2                   
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

It is important to note: one can get the “percent credit” for each
variable by checking what fraction of the “`Sum Sq`” column is
associated with a given variable’s row. In our case `x_2` is given more
credit than `x_1` (larger `Sum Sq`, larger `F value`). Some of the
credit assignment depends on user specified variable order, and not on
properties of the model or data.

Let’s confirm that.

``` r
summary(aov(
  lm(y ~ x_2 + x_1, data = d)))
```

    ##               Df Sum Sq Mean Sq F value Pr(>F)    
    ## x_2            1  43443   43443 18657.0 <2e-16 ***
    ## x_1            1   1831    1831   786.2 <2e-16 ***
    ## Residuals   9997  23278       2                   
    ## ---
    ## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

Now `x_2` is getting even more of the credit.

Which answer is “right” depends on “causal issues” that are domain
specific and can’t always be determined retrospectively from the data,
as they depend on the actual semantics of the process producing the
data. The “attribution depends on order” is an essential difficulty in
attribution (though it may express in different ways with different
tools). Roughly: the variable order is a very crude stand-in for a
causal network diagram.

The analysis of variance attribution is very useful. In fact it is much
more useful than model coefficient size, model coefficient significance,
or even term sizes (coefficient times variable). However it is dependent
on user specification of variable order, which can hinder
interpretation.

## Conclusion

Analysis of variance is an analysis of overall model quality in terms of
summed square differences. Under sufficient assumptions, it also gives a
significance of fit estimate for the overall model. This is *without
having to* attribute significance down to individual variables or
levels. This makes the method useful in large data situations where
model effects can often arise from a sum of small variable effects. In
addition, the method is good at attributing model quality to user chosen
variables or groups of variables (though in an order dependent manner).

Even for “something as simple as” linear models the analysis of variance
attributions are much more reliable on attributions made by coefficient
size, coefficient significance, or even so-called “terms” (`R` phrase
for: coefficient times individual variables). So there are good reasons
to consider analysis of variance style summaries.

The point of analysis of variance *can* be obscured by derivations that
show that the traditional calculation tracks how nested models *differ
from each other*, instead of directly tracking *how much nested models
improve residual variance*. The two quantities *are identical given the
usual orthogonality of residuals properties known to be true for linear
modeling*. The confusion being: the first quantity makes for easier
bookkeeping, while only the second quantity is inherently interesting to
the analyst or data scientist. The identity of these two quantities is
called out in the included example code at the “`confirm equal`”
comment. Due to historic practice, we have a situation where
implementations refer to “[The Scottish
Play](https://en.wikipedia.org/wiki/The_Scottish_play)”, when users
really want “Macbeth.”
