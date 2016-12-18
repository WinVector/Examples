# Implement model fitters for several different algorithms (in this case, GLM, GAM, and Random Forest (ranger)).

library(tidyr)
library(dplyr)
library(replyr)
library(sigr)
library(ranger)
library(mgcv) # nmle (called by mgcv) also has a function called gapply


#
# Predictor factories for various algorithms
#

glm_predictor = function(yvar, varlist, traindata) {
  fmla = paste(yvar, "~", paste(varlist, collapse=" + "))
  model = glm(fmla, traindata, family=binomial)
  rm(list="traindata") # try not to leak extra copies of the training data
  function(newdata) {
    predict(model, newdata=newdata, type="response")
  }
}

#
# Need to test this. hmmm. still takes a long time
#
gam_predictor = function(yvar, varlist, traindata) {
  summ = replyr_summary(train[, varlist])
  sfilter = summ$class %in% c("integer", "numeric") & summ$nunique > 10
  svars = summ$column[sfilter]
  rvars = setdiff(varlist, svars)

  srhs = paste("s(",svars,")")
  rhs = c(rvars, srhs)
  fmla = paste(yvar, "~", paste(rhs, collapse=" + "))
  model = gam(as.formula(fmla), data=traindata,
              family=binomial)
  rm(list="traindata")
  function(newdata) {
    predict(model, newdata=newdata, type="response")
  }
}

ranger_predictor = function(yvar, varlist, traindata) {
  fmla = paste("as.factor(", yvar, ") ~", paste(varlist, collapse=" + "))
  model = ranger(as.formula(fmla), traindata, probability=TRUE)
  rm(list="traindata")
  function(newdata) {
    predictions = predict(model, data=newdata, type="response")$predictions
    predictions[, "TRUE"]
  }
}

# fit the models (resulting list should have the same names)
fit_models = function(algolist, yvar, varlist, train) {
  predictors = lapply(algolist, FUN=function(algo){algo(yvar, varlist, train)})
  predictors
}

# take a list of predictors and a test set, and make predictions
# return results in a long frame
make_predictions = function(predictorlist, test, yvar) {
  pnames = names(predictorlist)
  for(predictor in pnames)
    test[[predictor]] = predictors[[predictor]](test)

  # gather a long frame of predictions
  tidyr::gather_(test, key_col="model", value_col="pred", pnames) %>%
    dplyr::select(one_of(c(yvar, "model", "pred")))
}
