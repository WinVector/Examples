

mk_data <- function(
  m,
  n_linear_vars = 20,
  n_noise = 20,
  n_interval_vars = 20,
  var_strength = 0.2) {
  
  y_fn <- function(x) {
    (x >= 0.375) & (x <= 0.875)
  }
  
  d <- data.frame(zero = numeric(m))
  y <- rnorm(m)
  for(i in seq_len(n_linear_vars)) {
    vn <- sprintf('lv_%03d', i)
    d[[vn]] <- runif(m)
    y <- y + var_strength * 2 * (d[[vn]] - 0.5)
  }
  for(i in seq_len(n_noise)) {
    vn <- sprintf('ln_%03d', i)
    d[[vn]] <- runif(m)
  }
  for(i in seq_len(n_interval_vars)) {
    vn <- sprintf('iv_%03d', i)
    d[[vn]] <- runif(m)
    y <- y + var_strength * ifelse(y_fn(d[[vn]]), +1, -1)
  }
  d$y <- y >= 0
  d$zero <- NULL
  return(d)
}


deviance_per_row <- function(
  pred,
  truth) {
  epsilon <- 1e-7
  mean(-2 * ifelse(
    truth, 
    log(pmax(pred, epsilon)), 
    log(pmax(1-pred, epsilon))))
}


glm_model_def <- list(
  fit = function(vars, outcome_name, d) {
    force(vars)
    force(outcome_name)
    force(d)
    f <- mk_formula(outcome = outcome_name, variables = vars)
    model <- glm(
      f,
      data = d,
      family = binomial())
    d <- NULL
    predict_fn = function(d) {
      predict(
        model,
        newdata = d,
        type = 'response')
    }
    list(
      model = model,
      vars = vars,
      outcome_name = outcome_name,
      model_name = 'glm',
      predict_proba = predict_fn)
  })


glmnet_cv_model_def <- list(
  fit = function(vars, outcome_name, d) {
    force(vars)
    force(outcome_name)
    force(d)
    model <- cv.glmnet(
      x = as.matrix(d[, vars, drop = FALSE]),
      y = d[[outcome_name]],
      family = 'binomial')
    d <- NULL
    predict_fn = function(d) {
      predict(
        model,
        newx = as.matrix(d[, vars, drop = FALSE]),
        type = 'response')[, 1]
    }
    list(
      model = model,
      vars = vars,
      outcome_name = outcome_name,
      model_name = 'glmnet_cv',
      predict = predict_fn)
    })


run_experiment <- function(model_def, m_train, m_test, simulated_pop) {
  d_train <- mk_data(m_train)
  
  outcome_name <- 'y'
  vars <- setdiff(colnames(d_train), outcome_name)
  
  model <- NULL
  tryCatch(
    model <- model_def$fit(
      vars = vars, 
      outcome_name = outcome_name, 
      d = d_train),
    error = function(e) {e}
  )
  if(is.null(model)) {
    return(NULL)
  }
  
  eval <- function(d) {
    preds <- model$predict(d)
    deviance_per_row(
      pred = preds, 
      truth = d[[outcome_name]])
  }
  
  return(data.frame(
    model_name = model$model_name,
    m_train = m_train,
    m_test = m_test,
    train_deviance = eval(d_train),
    test_deviance = eval(mk_data(m_test)),
    pop_deviance = eval(simulated_pop)
  ))
}


