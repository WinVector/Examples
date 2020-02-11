# utility functions used by the KS Distance article and supplementary markdown
#
# Packages used in this file. Actual library() calls are in the calling .Rmd file
#
# library(ggplot2)
# library(wrapr)
# library(rqdatatable)
# library(cdata)
# library(Matching)

###########################
#
# Functions to compare distributions visually and with summary stats
#
###########################

#
# dframe: data frame holding both new and reference data
# column: name of column to be plotted
# gpcol: name of column designating new vs reference data
#
comparison_plot = function(dframe, column, gpcol) {
  suppressWarnings(ggplot(dframe, aes_string(x=column, color=gpcol)) +
    geom_density(adjust=0.5) +
    scale_color_brewer(palette="Dark2"))
}


pct_diff_calc = function(cur, ref) {
  100 * (cur - ref)/ref
}

#
# dframe: frame of summary statistics, by group (newdata vs reference)
# gpcol: name of column designating new vs reference data
# refval: the label of the reference group
#
pct_diff = function(dframe, gpcol, refval="reference") {
  ref_ix = match(refval, dframe[[gpcol]])
  cur_ix = ifelse(ref_ix==1,2,1)
  refcol_ix = match(gpcol, colnames(dframe))

  pdframe = lapply(dframe[-refcol_ix],
                   function(v) pct_diff_calc(v[cur_ix], v[ref_ix])) %.>%
    as.data.frame(.)

  pdframe[[gpcol]] = paste("% diff from", refval)

  # return the frame in the same order as the original frame
  pdframe[colnames(dframe)]
}

# summary statistics that remove NAs
# needed because rquery calls can't take named arguments
meann = function(x) mean(x, na.rm=TRUE)
sdn = function(x) sd(x, na.rm=TRUE)
mediann = function(x) median(as.numeric(x), na.rm=TRUE)
quantilen = function(x, probs) quantile(x, probs, na.rm=TRUE)

#
# Calculate summary statistics and % difference between newdata and reference
#
# dframe: data frame holding both new and reference data
# column: name of column to be plotted
# gpcol: name of column designating new vs reference data
# refval: label of the reference group
#
comparison_stats = function(dframe, column, gpcol, refval="reference") {
  column <- as.name(column)
  ops  = local_td(dframe) %.>%
    project(.,
            mean := meann(.(column)),
            sd := sdn(.(column)),
            median := mediann(.(column)),
            pctile25 := quantilen(.(column), 0.25),
            pctile75 := quantilen(.(column), 0.75),
            groupby = gpcol) %.>%
    extend(., IQR := pctile75 - pctile25) %.>%
    drop_columns(., qc(pctile25, pctile75))

  comparisons = dframe %.>% ops

  rbind(comparisons, pct_diff(comparisons, gpcol, refval))
}


#
# Plot empirical CDFs of current and reference data,
# along with (approximate) maximum gap between the two. The length
# of this gap is the KS distance.
#
# Note that refval must be a string, even if the actual grouping
# value is a number (for example, a year), so rather than
# "refval = 2001" say "refval = '2001'"
#
# dframe: data frame holding both new and reference data
# column: name of column to be plotted
# gpcol: name of column designating new vs reference data
# refval: a STRING marking the reference value.
#
compare_ecdfs = function(dframe, column, gpcol, refval="reference") {
  gps = as.character(unique(dframe[[gpcol]]))
  curval = setdiff(gps, refval)

  # split into the two frames and unpack
  unpack(split(dframe, dframe[[gpcol]]),
         reference = .(refval), current = .(curval))

  refecdf = ecdf(reference[[column]])
  curecdf = ecdf(current[[column]])

  x = knots(curecdf) # I should check for the finer grained one, but whatever

  ecdf_frame = data.frame(x=x)
  ecdf_frame[[refval]] = refecdf(x)
  ecdf_frame[[curval]] = curecdf(x)

  # now get the (approx) max distance, its x and ys
  diffv = abs(ecdf_frame[[refval]] - ecdf_frame[[curval]])
  max_ix = which.max(diffv) # get the index of the FIRST max

  maxframe = ecdf_frame[max_ix,]

  ecdf_wide = pivot_to_blocks(ecdf_frame,
                              nameForNewKeyColumn = "dataset",
                              nameForNewValueColumn = "CDF",
                              gps)

  # the y and yend of the geom_segment are numbers
  # I had to do that because sometimes refval/curval
  # are strings that parse to numbers, and ggplot gets confused
  suppressWarnings(
    ggplot(ecdf_wide, aes(x=x, y=CDF, color=dataset)) +
    geom_line(linetype = 2) +
    geom_segment(data=maxframe,
                 aes(x = x,
                     xend = x,
                     y = maxframe[[refval]],
                     yend = maxframe[[curval]]),
                 color="maroon") +
    scale_color_brewer(palette="Dark2")
  )
}

###########################
#
# Functions to run permutation on two distributions
#
###########################

# Get the KS distance between two distributions
get_D = function(curr_dist, ref_dist) {
  # ks.test gets cranky when there are ties in the data
  # we are only using D, so ignore the warnings
  suppressWarnings(ks.test(curr_dist, ref_dist)$statistic)
}

#
# Run one iteration of the permutation test. Returns KS distance
# between the resampled sets.
#
# joint_dist: the current and reference data, concatenated
# n_curr: size of current data sample
# n_ref: size of reference data sample
#
permutation_run = function(joint_dist, n_curr, n_ref) {
  n = n_curr + n_ref
  ix = sample.int(n, size=n, replace=FALSE)
  ix_curr = ix[1:n_curr]
  ix_ref = ix[(n_curr+1):n]

  get_D(joint_dist[ix_curr], joint_dist[ix_ref])

}

#
# Run the entire permutation test.
# It's called "boot_" because I informally use the word "bootstrap"
# for both sample with and without replacement
#
# currdist: current data
# refdist: reference data
# nboots: number of iterations
#
# Returns a list of:
#  D_actual: KS distance between currdist and refdist
#  D_threshold: Threshold from bootstrapping
#  D_dist: vector of distances from all bootstrapped iterations
#
boot_dist_compare = function(currdist, refdist, nboots) {
  ncurr = length(currdist)
  nref = length(refdist)
  jointdist = c(currdist, refdist)

  D_dist = vapply(1:nboots,
                  function(i) permutation_run(jointdist, ncurr, nref),
                  numeric(1))

  D_actual = get_D(currdist, refdist)

  p_est = sum(D_dist >= D_actual)/nboots


  as_named_list(D_actual, D_dist, p_est)

}

#
# Display the distribution of bootstrapped distances,
# compare it to the actual KS distance, and
# report whether or not it is greater than the threshold
#
# dcompare: output of boot_dist_compare()
#
display_dist_compare = function(dcompare, pthresh = 0.002, title="") {
  unpack(dcompare, D_actual, D_dist, p_est)
  mesg = paste0("D = ", format(D_actual, digits=3),
                "; estimated p = ", format(p_est, digits=3))

  if(p_est <= pthresh) {
    mesg = paste(mesg, "-- distributions appear different")
  } else {
    mesg = paste(mesg, "-- distributions do not appear different")
  }
  print(ggplot(data.frame(D=D_dist), aes(x=D)) +
          geom_density(adjust=0.5) +
          geom_vline(xintercept = D_actual,
                     color="maroon", linetype=2) +
          ggtitle(title, subtitle=mesg))
}




