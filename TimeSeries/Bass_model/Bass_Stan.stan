
// Bass diffusion model
// https://en.wikipedia.org/wiki/Bass_diffusion_model#cite_note-Bass1969-2
// https://srdas.github.io/MLBook/productForecastingBassModel.html
data {
  int<lower=1> N;               // number of observations
  vector<lower=0>[N] s;         // observation values
  vector<lower=0>[N] cumsum_s;  // cumsum observation values
  real<lower=0> total_s;        // total mass of observations
}
parameters {
  real<lower=0> z;            // skipped mass
  real<lower=total_s> m;      // total possible mass
  real<lower=0, upper=1> p;   // coefficient of innovation
  real<lower=0, upper=1> q;   // coefficient of imitation
}
transformed parameters {
  vector[N] err_s;
  for (i in 1:N) {
    err_s[i] = s[i] - (p + q * (cumsum_s[i] + z) / m) * (m - (cumsum_s[i] + z));
  }
}
model {
  z ~ uniform(0, total_s);
  m ~ uniform(0, 100 * total_s);
  p ~ uniform(0, 1);
  q ~ uniform(0, 1);
  err_s ~ normal(0, 1.0);  // square error
}

