Inferring From Individuals
================
John Mount
12/4/24

Joseph Rickert and I put together an experiment trying to both run a
standard meta-analysis and then reproduce similar results directly using
Bayesian methods. I think it came out really interesting and we share it
here at [R Works](https://rworks.dev/posts/meta-analysis/) and also
[here on
Github](https://github.com/WinVector/Examples/blob/main/MetaAnalysis/Amlodipine/ExaminingMetaAnalysis.md).

In this note we examine how inference would work *if studies shared the
data* instead of sharing summary statistics.

When mean and variance are [sufficient
statistics](https://en.wikipedia.org/wiki/Sufficient_statistic) the
theory tells us: the inference from summaries should be best possible.
That is the inference made off summaries should be the same as made off
of individuals. Let’s confirm this for our example by performing an
analysis from summaries and simulating an analysis from individuals.

## Example

Let’s begin: load the required required packages and read in the data.

<details>
<summary>Show the code</summary>

``` r
library(wrapr)

angina <- read.csv(
  file = "AmlodipineData.csv", 
  strip.white = TRUE, 
  stringsAsFactors = FALSE)

angina |>
  knitr::kable()
```

</details>

| Protocol |  nE |  meanE |   varE |  nC |   meanC |   varC |
|---------:|----:|-------:|-------:|----:|--------:|-------:|
|      154 |  46 | 0.2316 | 0.2254 |  48 | -0.0027 | 0.0007 |
|      156 |  30 | 0.2811 | 0.1441 |  26 |  0.0270 | 0.1139 |
|      157 |  75 | 0.1894 | 0.1981 |  72 |  0.0443 | 0.4972 |
|      162 |  12 | 0.0930 | 0.1389 |  12 |  0.2277 | 0.0488 |
|      163 |  32 | 0.1622 | 0.0961 |  34 |  0.0056 | 0.0955 |
|      166 |  31 | 0.1837 | 0.1246 |  31 |  0.0943 | 0.1734 |
|      303 |  27 | 0.6612 | 0.7060 |  27 | -0.0057 | 0.9891 |
|      306 |  46 | 0.1366 | 0.1211 |  47 | -0.0057 | 0.1291 |

The data set contains eight rows each representing the measured effects
of treatment and control on different groups. The column definitions
are:

-   `Protocol` id number of the study the row is summarizing.
-   `nE` number of patients in the treatment group.
-   `meanE` mean treatment effect observed.
-   `varE` variance of treatment effect observed.
-   `nC` number of patients in the control group.
-   `meanC` mean control effect observed.
-   `varC` variance of control effect observed.

## Bayesian analysis from sufficient summary statistics

Let’s re-run the Bayesian analysis, this time capturing plausible
example data.

<details>
<summary>Show the code</summary>

``` r
# attach packages
library(ggplot2)
library(rstan)
library(digest)
source("define_Stan_model.R")

n_studies = nrow(angina)
# make strings for later use
descriptions = vapply(
  seq(n_studies),
  function(i) { paste0(
    'Protocol ', angina[i, 'Protocol'], ' (',
    'nE=', angina[i, 'nE'], ', meanE=', angina[i, 'meanE'],
    ', nC=', angina[i, 'nC'], ', meanC=', angina[i, 'meanC'],
    ')') },
  character(1))

unpack[
  analysis_src_joint_Stan = src_Stan, 
  analysis_src_joint_Latex = src_Latex
  ] := define_Stan_model(n_studies = n_studies, model_style = "per group means")

stan_data = list(
  n_studies = n_studies,
  nE = array(angina$nE, dim = n_studies),  # deal with length 1 arrays confused with scalars in JSON path
  meanE = array(angina$meanE, dim = n_studies),
  varE = array(angina$varE, dim = n_studies), 
  nC = array(angina$nC, dim = n_studies), 
  meanC = array(angina$meanC, dim = n_studies), 
  varC = array(angina$varC, dim = n_studies))
```

</details>
<details>
<summary>Show the code</summary>

``` r
whole_job_fn <- function() {
  # run the sampling procedure
  fit_joint <- stan(
    model_code = analysis_src_joint_Stan,  # Stan program
    data = stan_data,           # named list of data
    chains = 4,                 # number of Markov chains
    warmup = 2000,              # number of warmup iterations per chain
    iter = 4000,                # total number of iterations per chain
    cores = 4,                  # number of cores (could use one per chain)
    refresh = 0,                # no progress shown
    pars = c("lp__",  # parameters to bring back
           "inferred_grand_treatment_mean", "inferred_grand_control_mean", 
           "inferred_between_group_stddev",
           "inferred_group_treatment_mean", "inferred_group_control_mean",
           "inferred_in_group_stddev", 
           "sampled_meanE", "sampled_varE",
           "sampled_meanC", "sampled_varC",
           paste0('treatment_subject_', seq(n_studies)),
           paste0('control_subject_', seq(n_studies)))
    )
  # extract the results.
  # primary inference
  fit_joint <- fit_joint |>
    as.data.frame() 
  fit_joint['delta'] <- (
    fit_joint['inferred_grand_treatment_mean'] 
    - fit_joint['inferred_grand_control_mean'])
  inference <- fit_joint |>
    (`[`)(c(
      "inferred_grand_treatment_mean", 
      "inferred_grand_control_mean", 
      "inferred_between_group_stddev",
      "delta")) |>
    colMeans() |>
    as.list() |>
    data.frame()
  # extract enough to plot
  plt_frame <- fit_joint[ 
    , 
    c('inferred_grand_treatment_mean', 
      'inferred_grand_control_mean',
      'delta')]
  # extract a sample of individual subject data
  subject_column_names <- colnames(fit_joint)[
    grep('_subject_', colnames(fit_joint))]
  individual_sample <- fit_joint[1, subject_column_names]
  vector_names <- sort(unique(gsub('\\[.+\\]', '', subject_column_names)))
  vectors <- lapply(
    vector_names,
    function(nm) as.numeric(individual_sample[
      1,
      colnames(individual_sample)[grep(nm, colnames(individual_sample))]
    ]))
  names(vectors) <- vector_names
  return(list(
    inference = inference,
    plt_frame = plt_frame,
    vectors = vectors
  ))
}


unpack[    
  inference = inference,
  plt_frame = plt_frame,
  vectors = vectors] := run_cached(
  whole_job_fn,
  list(),
  prefix="Amlodipine_joint_summaries"
)
```

</details>
<details>
<summary>Show the code</summary>

``` r
# show primary inference
inference |>
  knitr::kable()
```

</details>

| inferred_grand_treatment_mean | inferred_grand_control_mean | inferred_between_group_stddev |     delta |
|---------------------:|--------------------:|---------------------:|-------:|
|                     0.1995232 |                   0.0392875 |                      0.064698 | 0.1602357 |

We can plot the estimated distribution effects in the treatment and
control groups.

<details>
<summary>Show the code</summary>

``` r
# plot the grand group inferences 
dual_density_plot(
  plt_frame, 
  c1 = 'inferred_grand_treatment_mean', 
  c2 = 'inferred_grand_control_mean',
  title = 'effect estimates, hierarchical model dependent means and independent variances')
```

</details>

![](InferringFromIndividuals.markdown_github_files/figure-markdown_github/unnamed-chunk-5-1.png)

We also plot the estimated net difference in treatment and control
effects.

<details>
<summary>Show the code</summary>

``` r
# plot the grand group inferences 
sd_t <- sd(plt_frame[['delta']])
ggplot(
  data = plt_frame,
  mapping = aes(x=delta),
  ) +
  geom_density(fill='green', alpha=0.5) +
  geom_vline(
    xintercept = inference['delta'][[1]], 
    linetype=2,
    alpha=0.8) +
  ggtitle("estimated distribution of treatment minus control effect",
          subtitle = paste0("( sd=", sprintf('%5.3f', sd_t), ")"))
```

</details>

![](InferringFromIndividuals.markdown_github_files/figure-markdown_github/unnamed-chunk-6-1.png)

## Bayesian analysis from simulated individual level data.

Let’s extract some sampled individuals to simulate how the analysis
would work if the individual outcomes had been shared. We don’t expect
we have de-censored or guessed the actual individual data. However we
know by our sampling specification these example are considered similar
to the actual data conditioned on the shared summary statistics. So if
we *pretend* these were the data we can estimate uncertainty that would
have been present when estimated parameters from this data and then
compare that to the uncertainty we just plotted when trying to estimate
parameters from statistical summaries.

The modified Stan source code to infer from individual level data is
[here](analysis_src_individuals_Stan.txt). We can play with some things,
such as specifying a Cauchy distribution for the individual
measurements.

<details>
<summary>Show the code</summary>

``` r
stan_src_i <- readLines('analysis_src_individuals_Stan.txt')
stan_src_i <- paste0(stan_src_i, collapse = "\n")
stan_data_i = list(
  n_studies = n_studies,
  nE = array(angina$nE, dim = n_studies),
  nC = array(angina$nC, dim = n_studies))
for(nm in names(vectors)) {
  vi <- as.numeric(vectors[[nm]])
  stan_data_i[[nm]] <- array(vi, dim = length(vi))
}
fit_joint_i <- run_cached(
  stan,
  list(
    model_code = stan_src_i,    # Stan program
    data = stan_data_i,         # named list of data
    chains = 4,                 # number of Markov chains
    warmup = 2000,              # number of warmup iterations per chain
    iter = 4000,                # total number of iterations per chain
    cores = 4,                  # number of cores (could use one per chain)
    refresh = 0,                # no progress shown
    pars = c("lp__",  # parameters to bring back
           "inferred_grand_treatment_mean", "inferred_grand_control_mean", 
           "inferred_between_group_stddev",
           "inferred_group_treatment_mean", "inferred_group_control_mean",
           "inferred_in_group_stddev")
    ),
    prefix="Amlodipine_joint_individuals"
  )
fit_joint_i <- fit_joint_i |>
  as.data.frame() 
fit_joint_i['delta'] <- (
  fit_joint_i['inferred_grand_treatment_mean'] 
  - fit_joint_i['inferred_grand_control_mean'])
inference_i <- fit_joint_i |>
  (`[`)(c(
    "inferred_grand_treatment_mean", 
    "inferred_grand_control_mean", 
    "inferred_between_group_stddev",
    "delta")) |>
  colMeans() |>
  as.list() |>
  data.frame()
```

</details>
<details>
<summary>Show the code</summary>

``` r
knitr::kable(inference_i)
```

</details>

| inferred_grand_treatment_mean | inferred_grand_control_mean | inferred_between_group_stddev |     delta |
|---------------------:|--------------------:|---------------------:|-------:|
|                     0.2037177 |                   0.0351755 |                     0.0648825 | 0.1685422 |

<details>
<summary>Show the code</summary>

``` r
# plot the grand group inferences 
dual_density_plot(
  fit_joint_i, 
  c1 = 'inferred_grand_treatment_mean', 
  c2 = 'inferred_grand_control_mean',
  title = 'effect estimates, hierarchical model with known individual observations')
```

</details>

![](InferringFromIndividuals.markdown_github_files/figure-markdown_github/unnamed-chunk-9-1.png)

<details>
<summary>Show the code</summary>

``` r
# plot the grand group inferences 
sd_t_i <- sd(fit_joint_i[['delta']])
ggplot(
  data = fit_joint_i,
  mapping = aes(x=delta),
  ) +
  geom_density(fill='green', alpha=0.5) +
  geom_vline(
    xintercept = inference_i['delta'][[1]], 
    linetype=2,
    alpha=0.8) +
  ggtitle("estimated distribution of treatment minus control effect (individual data)",
          subtitle = paste0("( sd=", sprintf('%5.3f', sd_t_i), ")"))
```

</details>

![](InferringFromIndividuals.markdown_github_files/figure-markdown_github/unnamed-chunk-10-1.png)

## Conclusion

And we confirm: there was no real loss of power in running the inference
from summaries instead of from individual data.
