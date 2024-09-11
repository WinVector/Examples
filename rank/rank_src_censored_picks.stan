
data {
  int<lower=1> n_vars;  // number of variables per alternative
  int<lower=2> n_alternatives;  // number of items per presentation list
  int<lower=1> m_examples;  // number of examples
  array[m_examples] int<lower=0, upper=n_alternatives> pick_index;   // which item is picked, 0 means no pick
  array[n_alternatives] matrix[m_examples, n_vars] x;  // explanatory variables
}
parameters {
  real beta_0;  // model parameters
  vector[n_vars] beta;  // model parameters
}
transformed parameters {
  array[n_alternatives] vector[m_examples] link;  // link values
  for (sel_j in 1:n_alternatives) {
    link[sel_j] = beta_0 + x[sel_j] * beta;
  }
}
model {
    // basic priors
  beta_0 ~ normal(0, 10);
  beta ~ normal(0, 10);
    // log probability of observed situation
  for (row_i in 1:m_examples) {
    if (pick_index[row_i] <= 0) {
      for (sel_j in 1:n_alternatives) {
        target += log1m(inv_logit(link[sel_j][row_i]));  // non-activation odds
      }
    } else {
      for (sel_j in 1:n_alternatives) {
        if (sel_j == pick_index[row_i]) {
          target += log(inv_logit(link[pick_index[row_i]][row_i]));  // probability selection indicates
        } else {
          target += log1m(inv_logit(link[sel_j][row_i])  // probability potential spoiler indicates
                            // probability potential spoiler outscores selection
                            * (1 - normal_cdf(link[pick_index[row_i]][row_i] | link[sel_j][row_i], 0.1)));
        }
      }
    }
  }
}
