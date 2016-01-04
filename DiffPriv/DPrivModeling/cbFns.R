

zapBad <- function(v) {
  v <- as.numeric(v)
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
    return(rep(1,nrow(dTest)))
  }
  if(all(!d$y)) {
    return(rep(0,nrow(dTest)))
  }
  oldw <- getOption("warn")
  options(warn = -1)
  f <- paste('y',paste(vars,collapse=' + '),sep=' ~ ')
  m <- glm(f,data=d,family=binomial(link='logit'))
  p <- predict(m,newdata=dTest,type='response')
  options(warn = oldw)
  p
}


naiveModel <- function(d,vars,dTest,stratarg) {
  coder <- trainBayesCoder(d,'y',vars,0)
  d2 <- coder$codeFrame(d)
  dTest2 <- coder$codeFrame(dTest)
  estimateExpectedPrediction(d2,vars,dTest2)
}

jackknifeModel <- function(d,vars,dTest,stratarg) {
  coder <- trainBayesCoder(d,'y',vars,0)
  d2 <- jackknifeBayesCode(d,'y',vars)
  dTest2 <- coder$codeFrame(dTest)
  estimateExpectedPrediction(d2,vars,dTest2)
}

#' @param stratarg sigma for the laplace noising
noisedModel <-  function(d,vars,dTest,stratarg) {
  coder <- trainBayesCoder(d,'y',vars,stratarg)
  d2 <- coder$codeFrame(d)
  dTest2 <- coder$codeFrame(dTest)
  estimateExpectedPrediction(d2,vars,dTest2)
}

splitModel <- function(d,vars,dTest,stratarg) {
  # can use deterministic split as rows are
  # in a random order in the intended example
  dSplit1 <- logical(nrow(d))
  dSplit1[seq_len(floor(nrow(d)/2))] <- TRUE
  coder <- trainBayesCoder(d[dSplit1,],'y',vars,0)
  d2 <- coder$codeFrame(d[!dSplit1,])
  dTest2 <- coder$codeFrame(dTest)
  estimateExpectedPrediction(d2,vars,dTest2)
}





mkNoisePlan <- function(d,vars,sigma) {
  noisePlan <- lapply(vars,function(vi) {
    levs <- sort(unique(d[[vi]]))
    nlevs <- length(levs)
    tn <- rlaplace(nlevs,sigma)
    names(tn) <- levs
    tf <- rlaplace(nlevs,sigma)
    names(tf) <- levs
    list(tn=tn,tf=tf)
  })
  names(noisePlan) <- vars
  noisePlan
}

mkNoisePlanConst <- function(d,vars,sigma) {
  noisePlan <- lapply(vars,function(vi) {
    levs <- sort(unique(d[[vi]]))
    nlevs <- length(levs)
    tn <- rep(sigma,nlevs)
    names(tn) <- levs
    tf <- rep(sigma,nlevs)
    names(tf) <- levs
    list(tn=tn,tf=tf)
  })
  names(noisePlan) <- vars
  noisePlan
}

noiseCountFixed <- function(orig,noise) {
  x <- zapBad(orig + noise[names(orig)])
  x <- pmax(x,1.0e-3)
  names(x) <- names(orig)
  x
}

#' Compute counts of rescol conditioned on level of vcol
#' 
#' @param vnam character name of independent variable
#' @param vcol character vector independent variable
#' @param rescol logical vector dependent variable
#' @param noisePlan pre-built noise plan
#' @return conditonal count structure
conditionalCountsFixed <- function(vnam,vcol,rescol,noisePlan) {
  # count queries
  nCandT <- noiseCountFixed(tapply(as.numeric(rescol),vcol,sum),
                            noisePlan[[vnam]]$tn)   #  sum of true examples for a given C (vector)
  nCandF <- noiseCountFixed(tapply(as.numeric(!rescol),vcol,sum),
                            noisePlan[[vnam]]$tf)  #  sum of false examples for a give C (vector)
  checkTwoNVecs(nCandT,nCandF)
  list(nCandT=as.list(nCandT),nCandF=as.list(nCandF))
}

#' Return a Bayes coding plan, with fixed noise
#' 
#' @param d data.frame
#' @param yName name of dependent variable
#' @param varnames names of independent variables
#' @param noisePlan pre-built noise plan
#' @return Bayes encoding plan
trainBayesCoderFixed <- function(d,yName,varNames,noisePlan) {
  coder <- trainCoder(d,yName,varNames,conditionalCountsFixed,bayesCode,noisePlan) 
  coder$what <- 'BayesCoder'
  coder$codeFrame <- function(df) codeFrame(df,coder,c())
  coder
}

#' @param stratarg noisePlan pre-built noise for the Laplace smoothing
noisedModelFixed <-  function(d,vars,dTest,stratarg) {
  coder <- trainBayesCoderFixed(d,'y',vars,stratarg)
  d2 <- coder$codeFrame(d)
  dTest2 <- coder$codeFrame(dTest)
  estimateExpectedPrediction(d2,vars,dTest2)
}

#' one fit on averged data frame
#' @param stratarg list of noisePlans pre-built noise for the Laplace smoothing
noisedModelFixedV1 <-  function(d,vars,dTest,stratarg) {
  d2 <- c()
  dTest2 <- c()
  for(si in stratarg) {
    coder <- trainBayesCoderFixed(d,'y',vars,si)
    d2i <- coder$codeFrame(d)
    dTest2i <- coder$codeFrame(dTest)
    if(is.null(d2)) {
      d2 <- d2i
      dTest2 <- dTest2i
    } else {
      d2 <- d2 + d2i
      dTest2 <- dTest2 + dTest2i
    }
  }
  d2 <- d2/length(stratarg)
  d2$y <- d$y
  dTest2 <- dTest2/length(stratarg)
  dTest2$y <- dTest$y
  estimateExpectedPrediction(d2,vars,dTest2)
}

#' many fits, average prediction
#' @param stratarg list of noisePlans pre-built noise for the Laplace smoothing
noisedModelFixedV2 <-  function(d,vars,dTest,stratarg) {
  pred <- c()
  for(si in stratarg) {
    coder <- trainBayesCoderFixed(d,'y',vars,si)
    d2 <- coder$codeFrame(d)
    dTest2 <- coder$codeFrame(dTest)
    pi <- estimateExpectedPrediction(d2,vars,dTest2)
    if(is.null(pred)) {
      pred <- pi
    } else {
      pred <- pred+pi
    }
  }
  pred/length(stratarg)
}




#' Evaluate probability of y given each row
#' 
#' @param d data frame
#' @param signalGroupLevels groups
pEachYgivenRow <- function(d,xs,signalGroupLevels) {
  arity <- match(d$group,signalGroupLevels) %% 2
  probs <- list(xs,1-xs)
  probs[arity+1]
}

#' Evaluate probability of y vector given x
#' 
#' @param d data frame
#' @param y observed ys
#' @param signalGroupLevels groups
pJointYsgivenRows <- function(d,xs,y,signalGroupLevels) {
  pYs <- pEachYgivenRow(d,xs,signalGroupLevels)
  pObs <- ifelse(y,pYs,lapply(pYs,function(x){1-x}))
  v <- Reduce(function(a,b){a*b},pObs)
  v
}


mkYList <- function(n) {
  ys <- expand.grid( rep( list(0:1), n),stringsAsFactors=FALSE)==1
  yList <- lapply(seq_len(nrow(ys)),
                  function(ii) { as.logical(ys[ii,]) })
  yList
}

extractSum <- function(vlist,vname) {
  vs <- lapply(vlist,function(vi) { vi[[vname]] })
  v <- Reduce(function(a,b){a+b},vs)
  v
}

#' evaluate a strategy by returning summary statistics
#'
#' @param d training data frame
#' @param dTest evaluation data frame
#' @param signalGroupLevels signal group levels (group named group)
#' @param noiseGroups noise group variable names
#' @param strat strategy to apply
#' @param stratarg an extra argument for the strategy
#' @param what name of strategy
#' @param parallelCluster cluster to run on
#' @param commonFns names of functions needed to run
#' @return scores
evalModelingStrategy <- function(d,dTest,signalGroupLevels,noiseGroups,
                                 strat,stratarg,what,
                                 parallelCluster,commonFns) {
  xs <- seq(0,1,by=0.01)
  pTestPy <- pEachYgivenRow(dTest,xs,signalGroupLevels)
  allVars <- union("group",noiseGroups)
  # run through each possible realization of the training outcome
  # vector y.  Each situation is weigthed by the probability of 
  # seeing this y-vector (though the outcomes in the situation
  # are conditionally indpendent of this unknown probabilty 
  # given the realized y).
  mkWorker <- function() {
    bindToEnv(d,signalGroupLevels,allVars,dTest,pTestPy,strat,stratarg,
              objNames=commonFns)
    function(y) {
      d$y <- y
      pTrainYs <- pJointYsgivenRows(d,xs,y,signalGroupLevels)
      predTest <- strat(d,allVars,dTest,stratarg)
      # deviance score
      scores <- lapply(seq_len(length(pTestPy)),
                       function(i) {
                         eps <- 1.e-5
                         pYi <- pTestPy[[i]]
                         predi <- predTest[[i]]
                         -2*(pYi*log2(pmax(eps,predi)) + 
                               (1-pYi)*log2(pmax(eps,1-predi)))
                       })
      meanScore <- Reduce(function(a,b){a+b},scores)/length(scores)
      list(expectedDeviance=pTrainYs*meanScore,
           totalProbCheck=pTrainYs)
    }
  }
  
  yList <-  mkYList(n)
  worker <-  mkWorker()
  if(!is.null(parallelCluster)) {
    resList <- parallel::parLapply(parallelCluster,yList,worker)
  } else {
    resList <- vector('list',length(yList))
    for(iii in seq_len(length(yList))) {
      resList[[iii]] <- worker(yList[[iii]])
    }
  }
  
  expectedDeviance <- extractSum(resList,'expectedDeviance')
  totalProbCheck <- extractSum(resList,'totalProbCheck')

  plotD <- data.frame(x=xs,
                      what=what,
                      expectedDeviance=expectedDeviance,
                      stringsAsFactors = FALSE)
  list(
    plotD=plotD,
    totalProbCheck=totalProbCheck,
    expectedDeviance=expectedDeviance
  )
}



