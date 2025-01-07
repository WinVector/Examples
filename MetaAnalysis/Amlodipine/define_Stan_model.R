
# Note:
# On OSX may need to add following to ~/.Renviron 
# PKG_CXXFLAGS=-I /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/usr/include/c++/v1



run_cached <- function(f, arg_list, prefix='') {
  assumed_fn_name <- as.character(substitute(f))  # really name of variable in calling scope
  key = digest(
    paste(c(assumed_fn_name, length(arg_list), as.character(names(arg_list)), as.character(arg_list)), collapse="\n"),
    algo="md5")
  path = paste0('cache_', prefix, '_', key, '.RDS')
  if(file.exists(path)) {
    return(readRDS(path))
  }
  result = do.call(f, args = arg_list)
  saveRDS(result, path)
  return(result)
}


# code to replicate code per-IDX
idx_blocks <- function(txt, n_studies) {
  paste0(vapply(
    seq(n_studies),
    function(i) {
      gsub("{IDX}",
           as.character(i),
           txt
           ,
           fixed = TRUE)
    },
    character(1)
  ), collapse="\n")
}


substitute_symbols <- function(src_str, subs_pairs) {
  for(p in subs_pairs) {
    src_str <- gsub(p[[1]], p[[2]], src_str, fixed = TRUE)
  }
  return(src_str)
}


define_Stan_model <- function(
    n_studies,
    ...,
    model_style = c("per group means", "shared mean", "independent means")
    ) {
  wrapr:::stop_if_dot_args(substitute(list(...)), "define_Stan_model")
  model_style <- model_style[[1]]
# the Stan source code for combining multiple studies as a meta-analysis
src_Stan <- paste0("
// model_style: {model_style}
functions {
  vector shift_scale(vector v, real target_mean, real target_var) {
     // shift and scale v to match target mean and variances
     int n = dims(v)[1];
     real sumv = sum(v);
     real sumv2 = dot_product(v, v);
     real diff = n * sumv2 - sumv * sumv;
     real disc = sqrt(target_var * n * (n - 1) * diff);
     real scale = disc / diff;
     real shift = target_mean - sumv * disc / (n * diff);
     vector[n] vr = scale * v + shift;
     if ((abs(mean(vr) - target_mean) >= 1e-3) || (abs(variance(vr) - target_var) >= 1e-3)) {
        reject(\"shift/scale failed\");
     }
     return vr;
  }
}
data {
  int<lower=1> n_studies;  // number of studies
  array[n_studies] int<lower=1> nE;  // number treated examples
  vector[n_studies] meanE;  // mean observed treatment effect
  vector<lower=0>[n_studies] varE;  // observed treatment effect variance
  array[n_studies] int<lower=1> nC;  // number control examples
  vector[n_studies] meanC;  // mean observed control effect
  vector<lower=0>[n_studies] varC;  // observed control effect variance
}
parameters {
  {/grand_mean_decl_lines/}real inferred_grand_treatment_mean;  // unobserved expected treatment
  {/grand_mean_decl_lines/}real inferred_grand_control_mean;  // unobserved expected control effect
  {/group_means_lines/}real<lower=0> inferred_between_group_stddev; // standard distance between groups
  {/group_mean_def_lines/}vector[n_studies] inferred_group_treatment_mean;  // unobserved per-group ideal treatment effect
  {/group_mean_def_lines/}vector[n_studies] inferred_group_control_mean;  // unobserved per-group ideal treatment effect
  vector<lower=0>[n_studies] inferred_in_group_stddev;  // unobserved per-group treatment variance
",
idx_blocks("
  vector[nE[{IDX}]] treatment_subject_unscaled_{IDX};  // unobserved per-group and subject treatment effects (unscaled)
  vector[nC[{IDX}]] control_subject_unscaled_{IDX};  // unobserved per-group and subject control effects (unscaled)
", n_studies = n_studies),
"
}
transformed parameters {
  vector[n_studies] sampled_meanE_unscaled;
  vector<lower=0>[n_studies] sampled_varE_unscaled;
  vector[n_studies] sampled_meanC_unscaled;
  vector<lower=0>[n_studies] sampled_varC_unscaled;
",
idx_blocks("
  vector[nE[{IDX}]] treatment_subject_{IDX};  // unobserved per-group and subject treatment effects
  vector[nC[{IDX}]] control_subject_{IDX};  // unobserved per-group and subject control effects
", n_studies = n_studies),
idx_blocks("
  sampled_meanE_unscaled[{IDX}] = mean(treatment_subject_unscaled_{IDX});
  sampled_varE_unscaled[{IDX}] = variance(treatment_subject_unscaled_{IDX});
  sampled_meanC_unscaled[{IDX}] = mean(control_subject_unscaled_{IDX});
  sampled_varC_unscaled[{IDX}] = variance(control_subject_unscaled_{IDX}); 
  treatment_subject_{IDX} = shift_scale(treatment_subject_unscaled_{IDX}, meanE[{IDX}], varE[{IDX}]);
  control_subject_{IDX} = shift_scale(control_subject_unscaled_{IDX}, meanC[{IDX}], varC[{IDX}]);
", n_studies = n_studies),
"
}
model {
  // priors
  {/group_means_lines/}inferred_grand_treatment_mean ~ normal(0, 1);
  {/group_means_lines/}inferred_grand_control_mean ~ normal(0, 1);
  {/between_group_stddev_lines/}inferred_between_group_stddev ~ lognormal(0, 1);
  {/group_mean_def_lines/}inferred_group_treatment_mean ~ normal(0, 1);
  {/group_mean_def_lines/}inferred_group_control_mean ~ normal(0, 1);
  inferred_in_group_stddev ~ lognormal(0, 1);
  // more peaked/informative stuff
",
idx_blocks("
  // each group generates an unobserved treatment response 
  {/group_means_lines/}inferred_group_treatment_mean[{IDX}] ~ normal(inferred_grand_treatment_mean, inferred_between_group_stddev);
  // treatment subjects experience effects a function of unobserved group response
  // in the normal distribution case could avoid forming individual observations as we know
  // summary mean should be normally distributed and variance chi-square (with proper parameters and scaling)
  {/grouped_subject_mean_lines/}treatment_subject_{IDX} ~ normal(inferred_group_treatment_mean[{IDX}], inferred_in_group_stddev[{IDX}]);
  {/pooled_subject_mean_lines/}treatment_subject_{IDX} ~ normal(inferred_grand_treatment_mean, inferred_in_group_stddev[{IDX}]);
  // match observed summaries
  sampled_meanE_unscaled[{IDX}] ~ normal(meanE[{IDX}], 1);
  sampled_varE_unscaled[{IDX}] ~ normal(varE[{IDX}], 1);
  // each group generates an unobserved control response
  {/group_means_lines/}inferred_group_control_mean[{IDX}] ~ normal(inferred_grand_control_mean, inferred_between_group_stddev);
  // control subjects experience effects a function of unobserved group response
  // in the normal distribution case could avoid forming individual observations as we know
  // summary mean should be normally distributed and variance chi-square (with proper parameters and scaling)
  {/grouped_subject_mean_lines/}control_subject_{IDX} ~ normal(inferred_group_control_mean[{IDX}], inferred_in_group_stddev[{IDX}]);
  {/pooled_subject_mean_lines/}control_subject_{IDX} ~ normal(inferred_grand_control_mean, inferred_in_group_stddev[{IDX}]);
  // match observed summaries
  sampled_meanC_unscaled[{IDX}] ~ normal(meanC[{IDX}], 1);
  sampled_varC_unscaled[{IDX}] ~ normal(varC[{IDX}], 1);
", n_studies = n_studies),
"
}
")
  src_Stan <- substitute_symbols(src_Stan ,list(c("{model_style}", model_style)))
  if(model_style == "per group means") {
    src_Stan <- substitute_symbols(
      src_Stan,
      list(
        c("{/group_means_lines/}", ""),
        c("{/grand_mean_decl_lines/}", ""),
        c("{/between_group_stddev_lines/}", ""),
        c("{/group_mean_def_lines/}", ""),
        c("{/grouped_subject_mean_lines/}", ""),
        c("{/pooled_subject_mean_lines/}", "//#")))
    src_Latex <- "
\\begin{align*}
\\mu^{treatment}_{i} &\\sim N(\\mu^{treatment}, \\sigma^2) &\\# \\; \\text{trying to infer} \\; \\mu^{treatment} \\\\
\\mu^{control}_{i} &\\sim N(\\mu^{control}, \\sigma^2) &\\# \\; \\text{trying to infer} \\; \\mu^{control} \\\\
subject^{treatment}_{i,j} &\\sim N(\\mu^{treatment}_{i}, \\sigma_{i}^{2}) &\\# \\; \\text{unobserved} \\\\
subject^{control}_{i,j} &\\sim N(\\mu^{control}_{i}, \\sigma_{i}^{2}) &\\# \\; \\text{unobserved} \\\\
mean_j(subject^{treatment}_{i,j}) &= observed\\_mean^{treatment}_{i}  &\\# \\; \\text{force inferred to be near observed} \\\\
mean_j(subject^{control}_{i,j}) &= observed\\_mean^{control}_{i}  &\\# \\; \\text{force inferred near to be observed} \\\\
var_j(subject^{treatment}_{i,j}) &= observed\\_var^{treatment}_{i}  &\\# \\; \\text{force inferred to be near observed} \\\\
var_j(subject^{control}_{i,j}) &= observed\\_var^{control}_{i}  &\\# \\; \\text{force inferred near to be observed}
\\end{align*}
"
  } else if(model_style == "independent means") {
    src_Stan <- substitute_symbols(
      src_Stan,
      list(
        c("{/group_means_lines/}", "//#"),
        c("{/grand_mean_decl_lines/}", "//#"),
        c("{/group_mean_def_lines/}", ""),
        c("{/between_group_stddev_lines/}", "//#"),
        c("{/grouped_subject_mean_lines/}", ""),
        c("{/pooled_subject_mean_lines/}", "//#")))
    src_Latex <- "
\\begin{align*}
subject^{treatment}_{i,j} &\\sim N(\\mu^{treatment}_{i}, \\sigma_{i}^{2}) &\\# \\; \\text{trying to infer} \\; \\mu^{treatment}_{i} \\\\
subject^{control}_{i,j} &\\sim N(\\mu^{control}_{i}, \\sigma_{i}^{2}) &\\# \\; \\text{trying to infer} \\; \\mu^{control}_{i} \\\\
mean_j(subject^{treatment}_{i,j}) &= observed\\_mean^{treatment}_{i}  &\\# \\; \\text{force inferred to be near observed} \\\\
mean_j(subject^{control}_{i,j}) &= observed\\_mean^{control}_{i}  &\\# \\; \\text{force inferred near to be observed} \\\\
var_j(subject^{treatment}_{i,j}) &= observed\\_var^{treatment}_{i}  &\\# \\; \\text{force inferred to be near observed} \\\\
var_j(subject^{control}_{i,j}) &= observed\\_var^{control}_{i}  &\\# \\; \\text{force inferred near to be observed}
\\end{align*}
"
  } else if(model_style == "shared mean") {
    src_Stan <- substitute_symbols(
      src_Stan,
      list(
        c("{/group_means_lines/}", "//#"),
        c("{/grand_mean_decl_lines/}", ""),
        c("{/group_mean_def_lines/}", "//#"),
        c("{/between_group_stddev_lines/}", "//#"),
        c("{/grouped_subject_mean_lines/}", "//#"),
        c("{/pooled_subject_mean_lines/}", "")))
    src_Latex <- "
\\begin{align*}
subject^{treatment}_{i,j} &\\sim N(\\mu^{treatment}, \\sigma_{i}^{2}) &\\# \\; \\text{trying to infer} \\; \\mu^{treatment} \\\\
subject^{control}_{i,j} &\\sim N(\\mu^{control}, \\sigma_{i}^{2}) &\\# \\; \\text{trying to infer} \\; \\mu^{control} \\\\
mean_j(subject^{treatment}_{i,j}) &= observed\\_mean^{treatment}_{i}  &\\# \\; \\text{force inferred to be near observed} \\\\
mean_j(subject^{control}_{i,j}) &= observed\\_mean^{control}_{i}  &\\# \\; \\text{force inferred near to be observed} \\\\
var_j(subject^{treatment}_{i,j}) &= observed\\_var^{treatment}_{i}  &\\# \\; \\text{force inferred to be near observed} \\\\
var_j(subject^{control}_{i,j}) &= observed\\_var^{control}_{i}  &\\# \\; \\text{force inferred near to be observed}
\\end{align*}
"
  } else {
    stop('define_Stan_model(): expected model_style to be one of: c("per group means", "shared mean", "independent means")')
  }
  # strip out commented out lines, and regularize white space just a bit
  lines <- strsplit(src_Stan, "\n")[[1]]
  lines <- lines[grepl("#", lines, fixed=TRUE) == FALSE]
  lines <- lapply(lines, function(s) trimws(s, which = "right"))
  src_Stan <- paste0("\n", paste0(lines, collapse = "\n"), "\n")
  # return problem description
  return(list(src_Stan = src_Stan, src_Latex = src_Latex))
}


extract_dual_density_plot_data <- function(fit, c1, c2) {
  treatment_result <- data.frame(
    effect = as.data.frame(fit)[ , c1, drop=TRUE],
    estimate = c1)
  treatment_result['mean_effect'] <- mean(treatment_result[['effect']])
  treatment_result['sd_effect'] <- sd(treatment_result[['effect']])
  control_result <- data.frame(
    effect = as.data.frame(fit)[ , c2, drop=TRUE],
    estimate = c2)
  control_result['mean_effect'] <- mean(control_result[['effect']])
  control_result['sd_effect'] <- sd(control_result[['effect']])
  results <- rbind(treatment_result, control_result)
  results['z'] <- (treatment_result[1, 'mean_effect'] - control_result[1, 'mean_effect']) / 
    ( (treatment_result[1, 'sd_effect'] + control_result[1, 'sd_effect']) / 2 )
  return(results)
}


dual_density_plot <- function(fit, c1, c2, title, vlines=c()) {
  # show the inferred distribution of plausible results
  results <- extract_dual_density_plot_data(fit, c1, c2)
  z <- results[1, 'z']
  plt <- (
    ggplot(
      data = results,
      mapping = aes(x = effect, color = estimate, fill = estimate, linetype = estimate))
    + geom_density(alpha = 0.5)
    + geom_vline(
      mapping = aes(xintercept = mean_effect, color = estimate, linetype = estimate))
    + theme(legend.position="bottom")
    + ggtitle(
        title,
        subtitle=paste0('(z ~ ', sprintf('%5.2f', z), ')')
      )
  )
  if(length(vlines) > 0) {
    for(x in vlines) {
      plt <- (
        plt
          + geom_vline(xintercept = x,linetype = 3, color = "darkgray")
      )
    }
  }
  return(plt)
}


double_dual_density_plot <- function(fitA, fitB, c1, c2, title, vlines=c()) {
  # show the inferred distribution of plausible results
  resultsA <- extract_dual_density_plot_data(fitA, c1, c2)
  zA <- resultsA[1, 'z']
  resultsA['method'] <- paste0('independent estimate (z ~ ', sprintf('%5.2f', zA), ')')
  resultsB <- extract_dual_density_plot_data(fitB, c1, c2)
  zB <- resultsB[1, 'z']
  resultsB['method'] <- paste0('joint estimate (z ~ ', sprintf('%5.2f', zB), ')')
  results <- rbind(resultsA, resultsB)
  plt <- (
    ggplot(
      data = results,
      mapping = aes(x = effect, color = estimate, fill = estimate, linetype = estimate))
    + geom_density(alpha = 0.5)
    + geom_vline(
      mapping = aes(xintercept = mean_effect, color = estimate, linetype = estimate))
    + facet_wrap(~method, ncol=1)
    + theme(legend.position="bottom")
    + ggtitle(title)
  )
  if(length(vlines) > 0) {
    for(x in vlines) {
      plt <- (
        plt
        + geom_vline(xintercept = x, linetype = 3, color = "darkgray")
      )
    }
  }
  return(plt)
}
