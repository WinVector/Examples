

#' compute the direct expected value of y per group
#'
#' @param d data frame with y and group columns
#' @return named vector with grouped y-means
empiricalEst <- function(d) {
  d$one <- 1.0
  num <- aggregate(y~group,data=d,FUN=sum)
  den <- aggregate(one~group,data=d,FUN=sum)
  if(!all(all.equal(num$group,den$group)==TRUE)) {
    stop("name mismatch")
  }
  est <- num$y/den$one
  names(est) <- num$group
  est
}

#' compute the jackknifed expected value of y per group
#'
#' @param d data frame with y and group columns
#' @param jackDenom denominator of current observation to pull off in estimate, 1 is standard jackknife, 2 is one half jackknife
#' @return named vector with jackknifed grouped y-means
jackknifeEst <- function(d,jackDenom) {
  d$one <- 1.0
  num <- aggregate(y~group,data=d,FUN=sum)
  numM <- num$y
  names(numM) <- num$group
  numV <- numM[d$group]
  den <- aggregate(one~group,data=d,FUN=sum)
  denM <- den$one
  names(denM) <- den$group
  denV <- denM[d$group]
  if(!all(all.equal(num$group,den$group)==TRUE)) {
    stop("name mismatch")
  }
  v <- as.numeric((numV-d$y/jackDenom)/(denV-1/jackDenom))
  v[is.na(v)|is.infinite(v)|is.nan(v)] <- 0
  v
}

#' Fit a glm() on top of the dEstimate column to the d$y column, then apply this model to dTest
#'
#' Simulates the second stage of a 2-stage modeling process.
#' @param d data frame with y column
#' @param dEst numeric with one sub-model prediction per row of d
#' @param dTest frame to score on has group and est columns
#' @return dTest predictions
estimateExpectedPrediction <- function(d,dEst,dTest) {
  # catch cases unsafe for glm
  if(all(d$y) || all(!d$y) || 
     ((max(dEst)-min(dEst))<=1.0e-5)) {
    return(dTest$est)
  }
  d$est <- dEst
  m <- glm(y~est,data=d,family=binomial(link='logit'))
  predict(m,newdata=dTest,type='response')
}


naiveModel <- function(d,dTest) {
  as.numeric(empiricalEst(d)[dTest$group])
}

jackknifeModel <- function(d,dTest) {
  p <- jackknifeEst(d,1)
  estimateExpectedPrediction(d,p,dTest)
}

jackknifeModel2 <- function(d,dTest) {
  estimateExpectedPrediction(d,jackknifeEst(d,2),dTest)
}

#' Split train nested model.  Assumes design can be split in half
#'
#' Simulates the second stage of a 2-stage modeling process.
#' @param d data frame with y column and group column
#' @param dTest frame to score on has group and est columns
#' @return dTest predictions
splitEstimateExpectedPrediction <- function(d,dTest) {
  isA <- logical(nrow(d))
  isA[seq_len(floor(nrow(d)/2))] <- TRUE
  dA <- d[isA,]
  dB <- d[!isA,]
  if(!all(all.equal(sort(unique(dA$group)),
                    sort(unique(dB$group)))==TRUE)) {
    stop("bad split")
  }
  dB$est <- empiricalEst(dA)[dB$group]
  # catch cases unsafe for glm
  if(all(dB$y) || all(!dB$y) || 
     ((max(dB$est)-min(dB$est))<=1.0e-5)) {
    return(dTest$est)
  }
  m <- glm(y~0+est,data=dB,family=binomial(link='logit'))
  predict(m,newdata=dTest,type='response')
}



#' Evaluate probability of y given each row
#' 
#' @param d data frame
#' @param gGroups groups
pYgivenRow <- function(d,gGroups) {
  arity <- match(d$group,gGroups) %% 2
  probs <- list(polynomial(c(0,1)),polynomial(c(1,-1)))
  probs[arity+1]
}

#' Evaluate probability of y vector given x
#' 
#' @param d data frame
#' @param y observed ys
#' @param gGroups groups
pYsgivenRows <- function(d,y,gGroups) {
  pYs <- pYgivenRow(d,gGroups)
  pObs <- ifelse(y,pYs,lapply(pYs,function(x){1-x}))
  Reduce(function(a,b){a*b},pObs)
}


#' evaluate a strategy by returning summary statistics
#'
#' @param d training data frame
#' @param dTest evaluation data frame
#' @param gGroups groups
#' @param strat strategy to apply
#' @param what name of strategy
#' @return scores
evalModelingStrategy <- function(d,dTest,gGroups,strat,what) {
  expectedMeanSquareDiff <- 0
  expectedBias <- as.list(rep(0,nrow(dTest)))
  totalProbCheck <- 0
  pTestPy <- pYgivenRow(dTest,gGroups)
  # run through each possible realization of the training outcome
  # vector y.  Each situation is weigthed by the probability of 
  # seeing this y-vector (though the outcomes in the situation
  # are conditionally indpendent of this unknown probabilty 
  # given the realized y).
  ys <- expand.grid( rep( list(0:1), n))==1
  for(ii in seq_len(nrow(ys))) {
    y <- as.logical(ys[ii,])
    d$y <- y
    pTrainYs <- pYsgivenRows(d,y,gGroups)
    ee <- empiricalEst(d)
    dTest$est <- as.numeric(ee[dTest$group])
    predTest <- strat(d,dTest)
    sqDiffs <- lapply(seq_len(length(pTestPy)),function(i){(predTest[[i]]-pTestPy[[i]])^2})
    meanSqDiff <- Reduce(function(a,b){a+b},sqDiffs)/length(sqDiffs)
    expectedMeanSquareDiff <- expectedMeanSquareDiff + pTrainYs*meanSqDiff
    expectedBias <- lapply(seq_len(length(expectedBias)),
                           function(i){expectedBias[[i]] + pTrainYs*(predTest[[i]]-pTestPy[[i]])})
    totalProbCheck <- totalProbCheck + pTrainYs
  }
  x <- seq(0,1,by=0.01)
  plotD <- data.frame(x=x,
                      what=what,
                      expectedMeanSquareDiff=as.function(expectedMeanSquareDiff)(x),
                      stringsAsFactors = FALSE)
  for(ii in seq_len(nrow(dTest))) {
    obsName <- paste('expectedBias',dTest[ii,'group'],sep='.')
    plotD[[obsName]] <- as.function(expectedBias[[ii]])(x)
  }
  list(
    plotD=plotD,
    totalProbCheck=totalProbCheck,
    expectedMeanSquareDiff=expectedMeanSquareDiff,
    expectedBias=expectedBias
  )
}



