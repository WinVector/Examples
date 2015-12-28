

#' compute the direct expected value of y per group
#'
#' @param v categorical variable
#' @param y outcome
#' @return named vector with grouped y-means
empiricalEst <- function(v,y) {
  d <- data.frame(group=v,y=y,one=1.0)
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
#' @param v categorical variable
#' @param y outcome
#' @param jackDenom denominator of current observation to pull off in estimate, 1 is standard jackknife, 2 is one half jackknife
#' @return named vector with jackknifed grouped y-means
jackknifeEst <- function(v,y,jackDenom=1) {
  d <- data.frame(group=v,y=y,one=1.0)
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
#' @param d data frame with vars and y column
#' @param vars
#' @param dTest frame to score on has group and est columns
#' @return dTest predictions
estimateExpectedPrediction <- function(d,vars,dTest) {
  # catch cases unsafe for glm
  if(all(d$y)) {
    rep(1,length(d$y))
  }
  if(all(!d$y)) {
    rep(0,length(d$y))
  }
  f <- paste('y',paste(vars,collapse=' + '),sep=' ~ ')
  m <- glm(f,data=d,family=binomial(link='logit'))
  predict(m,newdata=dTest,type='response')
}


naiveModel <- function(d,vars,dTest) {
  d2 <- data.frame(y=d$y,
                   stringsAsFactors=FALSE)
  dTest2 <- dTest
  for(vi in vars) {
    ei <- empiricalEst(d[[vi]],d$y)
    d2[[vi]] <- as.numeric(ei[d[[vi]]])
    dTest2[[vi]] <- as.numeric(ei[dTest[[vi]]])
  }
  estimateExpectedPrediction(d2,vars,dTest2)
}

jackknifeModel <- function(d,vars,dTest) {
  d2 <- data.frame(y=d$y,
                   stringsAsFactors=FALSE)
  dTest2 <- dTest
  for(vi in vars) {
    ei <- empiricalEst(d[[vi]],d$y)
    d2[[vi]] <- jackknifeEst(d[[vi]],d$y,1)
    dTest2[[vi]] <- as.numeric(ei[dTest[[vi]]])
  }
  estimateExpectedPrediction(d2,vars,dTest2)
}

jackknifeModel2 <- function(d,vars,dTest) {
  d2 <- data.frame(y=d$y,
                   stringsAsFactors=FALSE)
  dTest2 <- dTest
  for(vi in vars) {
    ei <- empiricalEst(d[[vi]],d$y)
    d2[[vi]] <- jackknifeEst(d[[vi]],d$y,2)
    dTest2[[vi]] <- as.numeric(ei[dTest[[vi]]])
  }
  estimateExpectedPrediction(d2,vars,dTest2)
}



#' Evaluate probability of y given each row
#' 
#' @param d data frame
#' @param signalGroupLevels groups
pYgivenRow <- function(d,signalGroupLevels) {
  arity <- match(d$group,signalGroupLevels) %% 2
  probs <- list(polynomial(c(0,1)),polynomial(c(1,-1)))
  probs[arity+1]
}

#' Evaluate probability of y vector given x
#' 
#' @param d data frame
#' @param y observed ys
#' @param signalGroupLevels groups
pYsgivenRows <- function(d,y,signalGroupLevels) {
  pYs <- pYgivenRow(d,signalGroupLevels)
  pObs <- ifelse(y,pYs,lapply(pYs,function(x){1-x}))
  Reduce(function(a,b){a*b},pObs)
}


#' evaluate a strategy by returning summary statistics
#'
#' @param d training data frame
#' @param dTest evaluation data frame
#' @param signalGroupLevels signal group levels (group named group)
#' @param noiseGroups noise group variable names
#' @param strat strategy to apply
#' @param what name of strategy
#' @return scores
evalModelingStrategy <- function(d,dTest,signalGroupLevels,noiseGroups,
                                 strat,what) {
  expectedMeanSquareDiff <- 0
  totalProbCheck <- 0
  pTestPy <- pYgivenRow(dTest,signalGroupLevels)
  allVars <- union("group",noiseGroups)
  # run through each possible realization of the training outcome
  # vector y.  Each situation is weigthed by the probability of 
  # seeing this y-vector (though the outcomes in the situation
  # are conditionally indpendent of this unknown probabilty 
  # given the realized y).
  ys <- expand.grid( rep( list(0:1), n),stringsAsFactors=FALSE)==1
  for(ii in seq_len(nrow(ys))) {
    y <- as.logical(ys[ii,])
    d$y <- y
    pTrainYs <- pYsgivenRows(d,y,signalGroupLevels)
    ee <- empiricalEst(d$group,d$y)
    dTest$est <- as.numeric(ee[dTest$group])
    predTest <- strat(d,allVars,dTest)
    sqDiffs <- lapply(seq_len(length(pTestPy)),
                      function(i){(predTest[[i]]-pTestPy[[i]])^2})
    meanSqDiff <- Reduce(function(a,b){a+b},sqDiffs)/length(sqDiffs)
    expectedMeanSquareDiff <- expectedMeanSquareDiff + pTrainYs*meanSqDiff
    totalProbCheck <- totalProbCheck + pTrainYs
  }
  x <- seq(0,1,by=0.01)
  plotD <- data.frame(x=x,
                      what=what,
                      expectedMeanSquareDiff=as.function(expectedMeanSquareDiff)(x),
                      stringsAsFactors = FALSE)
  list(
    plotD=plotD,
    totalProbCheck=totalProbCheck,
    expectedMeanSquareDiff=expectedMeanSquareDiff
  )
}



