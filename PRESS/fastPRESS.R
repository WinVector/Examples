# weighted PRESS statistic of a weighted mean
# so in this case it is sum((y_i - meanAllBut(y,i))^) where mean is computed of all but the i'th datum
# y numeric, no NAs/NULLS
# wts numeric, non-negative, no NAs/NULLs at least two positive positions, vector can be null
# all vectors same length
hold1OutMeans <- function(y,wts=c()) {
  # get per-datum hold-1 out grand means
  if(is.null(wts)) {
    wts <- rep(1.0,length(y))
  }
  sumY <- sum(y*wts)
  sumW <- sum(wts)
  meanP <- (sumY - y*wts)/(sumW - wts)
  meanP[is.na(meanP)] <- 0.5
  meanP
}

hold1OutLMPreds <- function(formula,data,wts=c()) {
  formula <- as.formula(formula)
  nRows <- dim(data)[[1]]
  if(is.null(wts)) {
    wts <- rep(1.0,nRows)
  }
  x <- model.matrix(formula,data=data)
  nVars <- dim(x)[[2]]
  terms <- terms(formula)
  yvarName <- as.character(as.list((attr(terms,'variables')))[[attr(terms,'response')+1]])
  y <- data[,yvarName]
  xTx <- t(x) %*% ( wts * x ) + 1.0e-5*diag(nVars)
  xTy <- t(x) %*% ( wts * y )
  pi <- function(i) {
    xTxi <- xTx - wts[i] * (x[i,] %o% x[i,])
    xTyi <- xTy - wts[i] * (x[i,] * y[i])
    betai <- solve(xTxi,xTyi)
    predi <- as.numeric(x[i,] %*% betai)
  }
  preds <- sapply(1:nRows,pi)
  preds
}

# Example of calculating PRESS, and related statistics
# y is the actual y column
# press statistic is sum(y_i - f_i)^2, f_i hold-i-out prediction
PRESSstats.lm = function(fmla, dframe, y) {
  n = length(y)
  hopreds = hold1OutLMPreds(fmla, dframe)
  homeans = hold1OutMeans(y)
  devs = y-hopreds
  PRESS = sum(devs^2)
  rmPRESS = sqrt(mean(devs^2))
  dely = y-homeans
  PRESS.r2= 1 - (PRESS/sum(dely^2))
  data.frame(PRESS=PRESS, rmPRESS=rmPRESS, PRESS.r.squared=PRESS.r2)
}


# example:
# set.seed(25325)
# d <- data.frame(y=rnorm(10),x=rnorm(10))
# d$h1pred <- hold1OutLMPreds(y~x,d)
# d$h1predCheck <- sapply(1:(dim(d)[[1]]),function(i) { predict(lm(y~x,data=d[-i,]),newdata=d[i,]) })
# print('confirm h1pred')
# print(sum(d$h1pred-d$h1predCheck)^2)  # 1.370424e-11
# d$h1mean <- hold1OutMeans(d$y)
# d$h1meanCheck <- sapply(1:(dim(d)[[1]]),function(i) { mean(d$y[-i]) })
# print('confirm h1mean')
# print(sum(d$h1mean-d$h1meanCheck)^2)  # 4.930381e-32
# d$lmpred <- predict(lm(y~x,data=d))
# print(PRESSstats.lm("y~x", d, d$y))
# #     PRESS   rmPRESS PRESS.r.squared
# #  2.196021 0.4686172     -0.02146757

# d$mean <- mean(d$y)
# print("in-sample R^2")
# print(1-sum((d$lmpred-d$y)^2)/sum((d$mean-d$y)^2))   # R^2 : 0.1378046
# print("in-sample hold-out 1 R^2 normal total variation")
# print(1-sum((d$h1pred-d$y)^2)/sum((d$mean-d$y)^2))   # h1 R^2 form 1 : -0.2610711
# print("in-sample hold-out 1 R^2 hold-out 1 total variation")
# print(1-sum((d$h1pred-d$y)^2)/sum((d$h1mean-d$y)^2)) # h1 R^2 form 2 : -0.02146757
