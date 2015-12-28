

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
estimateExpectedPrediction <- function(d,dEst,dTest,debug=FALSE) {
  # catch cases unsafe for glm
  if(all(d$y) || all(!d$y) || 
     ((max(dEst)-min(dEst))<=1.0e-5)) {
    return(dTest$est)
  }
  d$est <- dEst
  m <- glm(y~est,data=d,family=binomial(link='logit'))
  predict(m,newdata=dTest,type='response')
}


naiveModel <- function(d,dTest,debug=FALSE) {
  as.numeric(empiricalEst(d)[dTest$group])
}

jackknifeModel <- function(d,dTest,debug=FALSE) {
  p <- jackknifeEst(d,1)
  if(debug) {
    d$jEst <- p
    print('dTrain')
    print(d)
  }
  estimateExpectedPrediction(d,p,dTest,debug)
}

jackknifeModel2 <- function(d,dTest,debug=FALSE) {
  estimateExpectedPrediction(d,jackknifeEst(d,2),dTest)
}

#' Split train nested model.  Assumes design can be split in half
#'
#' Simulates the second stage of a 2-stage modeling process.
#' @param d data frame with y column and group column
#' @param dTest frame to score on has group and est columns
#' @return dTest predictions
splitEstimateExpectedPrediction <- function(d,dTest,debug=FALSE) {
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




#' evaluate a strategy by returning summary statistics
#'
#' @param d training data frame
#' @param dTest evaluation data frame
#' @param strat strategy to apply
#' @param what name of strategy
#' @return scores
evalModelingStrategy <- function(d,dTest,strat,what,
                                 debug=FALSE) {
  predExpectedMin <- 0
  predExpectedMean <- 0
  predExpectedMax <- 0
  probOn <- polynomial(c(0,1))  # polnomial x representing chance of y=TRUE
  # run through each possible realization of the training outcome
  # vector y.  Each situation is weigthed by the probability of 
  # seeing this y-vector (though the outcomes in the situation
  # are conditionally indpendent of this unknown probabilty 
  # given the realized y).
  ys <- expand.grid( rep( list(0:1), n))==1
  for(ii in seq_len(nrow(ys))) {
    y <- as.logical(ys[ii,])
    if(debug) {
      print("****")
      print(y)
    }
    d$y <- y
    py <- probOn^(sum(y))*(1-probOn)^(length(y)-sum(y))
    ee <- empiricalEst(d)
    if(debug) {
      d$empEst <- as.numeric(ee[d$group])
    }
    dTest$est <- as.numeric(ee[dTest$group])
    pred <- strat(d,dTest,debug)
    if(debug) {
      dTest$pred <- pred
      print('dTest')
      print(dTest)
    }
    predExpectedMin <- predExpectedMin + min(pred)*py
    predExpectedMean <- predExpectedMean + mean(pred)*py
    predExpectedMax <- predExpectedMax + max(pred)*py
  }
  x <- seq(0,1,by=0.01)
  plotD <- data.frame(x=x,
                      what=what,
                      expectedMin=as.function(predExpectedMin)(x),
                      expectedMean=as.function(predExpectedMean)(x),
                      expectedMax=as.function(predExpectedMax)(x),
                      stringsAsFactors = FALSE)
  plotD$expectedRatioMin <- plotD$expectedMin/plotD$x
  plotD$expectedRatioMean <- plotD$expectedMean/plotD$x
  plotD$expectedRatioMax <- plotD$expectedMax/plotD$x
  list(
    plotD=plotD,
    predExpectedMin=predExpectedMin,
    predExpectedMean=predExpectedMean,
    predExpectedMax=predExpectedMax
  )
}



