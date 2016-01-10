

#' Compute counts of rescol conditioned on level of vcol
#' 
#' @param vnam character name of independent variable
#' @param vcol character vector independent variable
#' @param rescol logical vector dependent variable
#' @param sigma scalar noise level to apply
#' @return conditonal count structure
conditionalCounts <- function(vnam,vcol,rescol,sigma) {
  # count queries
  nCandT <- noiseCount(tapply(as.numeric(rescol),vcol,sum),sigma)   #  sum of true examples for a given C (vector)
  nCandF <- noiseCount(tapply(as.numeric(!rescol),vcol,sum),sigma)  #  sum of false examples for a give C (vector)
  checkTwoNVecs(nCandT,nCandF)
  list(nCandT=as.list(nCandT),nCandF=as.list(nCandF))
}



#' Encode a categorical variable as a Bayes model
#'
#' @param vname independnet variable name
#' @param vcol depedent variable values
#' @param counts conditional count structure
#' @param rescol if not null the idependent column to Jackknife out of the counts
#' @param jackDen Jackknifing denominator, 1 = standard
#' @return encoded data frame
bayesCode <- function(vname,vcol,counts,rescol,jackDen=1) {
  smFactor <- 1.0e-3
  nCandT <- listLookup(vcol,counts$nCandT) #  sum of true examples for given C
  nCandF <- listLookup(vcol,counts$nCandF) #  sum of false examples for given C
  # dervived values
  nT <- rep(sum(as.numeric(counts$nCandT)),length(vcol)) #  sum of true examples (vector)
  nF <- rep(sum(as.numeric(counts$nCandF)),length(vcol))  #  sum of false examples (vector)
  if(!is.null(rescol)) {
    # Jackknife adjust entries by removing self from counts
    nCandT <- nCandT - ifelse(rescol,1,0)/jackDen
    nT <- nT - ifelse(rescol,1,0)/jackDen
    nCandF <- nCandF - ifelse(rescol,0,1)/jackDen
    nF <- nF - ifelse(rescol,0,1)/jackDen
  }
  # perform the Bayesian calculation, vectorized
  probT <- nT/pmax(nT+nF,1.0e-3)   # unconditional probabilty target is true
  pCgivenT <- (nCandT+probT*smFactor)/(nT+probT*smFactor)   # probability of a given evidence C, condition on outcome=T
  pCgivenF <- (nCandF+(1.0-probT)*smFactor)/(nF+(1.0-probT)*smFactor)  # probability of a given evidence C, condition on outcome=F
  pTgivenCunnorm <- pCgivenT*probT      # Bayes law, corret missing a /pC term (which we will normalize out)
  pFgivenCunnorm <- pCgivenF*(1-probT)  # Bayes law, corret missing a /pC term (which we will normalize out)
  pTgivenC <- pTgivenCunnorm/(pTgivenCunnorm+pFgivenCunnorm)
  logLift <- log(pTgivenC/probT)  # log probability ratio (so no effect is coded as zero)
  z <- data.frame(z=logLift,
                  stringsAsFactors = FALSE)
  colnames(z) <- vname
  z
}

#' Train a coder from examples
#' 
#' @param d data.frame
#' @param yName independent varaible name
#' @param varnames dependent variable names
#' @param maker
#' @param coder
#' @param param parameter for maker
trainCoder <- function(d,yName,varNames,maker,coder,param) {
  codes <- lapply(varNames,function(vnam) { maker(vnam,d[[vnam]],d[[yName]],param) })
  names(codes) <- varNames
  list(yName=yName,
       varNames=varNames,
       maker=maker,
       coder=coder,
       param=param,
       codes=codes)
}


#' Encode a data frame using a coding plan
#' 
#' @param d data.frame original data frame
#' @param codes coding plan
#' @param rescol optional dependent varaible to Jacknife out
#' @return encoded data frame
codeFrame <- function(d,codes,rescol) {
  nd <- c()
  if(codes$yName %in% colnames(d)) {
    nd <- data.frame(d[[codes$yName]],
                     stringsAsFactors = FALSE)
    colnames(nd) <- codes$yName
  }
  for(varName in names(codes$codes)) {
    nf <- codes$coder(varName,d[[varName]],codes$codes[[varName]],rescol)
    if(is.null(nd)) {
      nd <- nf
    } else {
      nd <- cbind(nd,nf)
    }
  }
  nd
}

#' Return a Bayes coding plan
#' 
#' @param d data.frame
#' @param yName name of dependent variable
#' @param varnames names of independent variables
#' @param sigma noising degree
#' @return Bayes encoding plan
trainBayesCoder <- function(d,yName,varNames,sigma) {
  coder <- trainCoder(d,yName,varNames,conditionalCounts,bayesCode,sigma) 
  coder$what <- 'BayesCoder'
  coder$codeFrame <- function(df) codeFrame(df,coder,c())
  coder
}



#' Jacknife encode a dataframe through Bayes encoding.
#' 
#' @param d data.frame
#' @param yName name of dependent variable
#' @param varnames names of independent variables
#' @return Jackknife encoded frame
jackknifeBayesCode <- function(d,yName,varNames) {
  coder <- trainCoder(d,yName,varNames,conditionalCounts,bayesCode,0) 
  coder$what <- 'BayesCoder'
  codeFrame(d,coder,d[[yName]])
}


#' Encode a counts model see: 
#'   http://blogs.technet.com/b/machinelearning/archive/2015/02/17/big-learning-made-easy-with-counts.aspx
#'
#' @param vname independnet variable name
#' @param vcol depedent variable values
#' @param counts conditional count structure
#' @param rescol if not null the idependent column to Jacknife out of the counts
#' @return encoded data frame
countCode <- function(vname,vcol,codes,rescol) {
  eps <- 1.0e-3
  nPlus <- pmax(eps,listLookup(vcol,codes$nCandT))
  nMinus <- pmax(eps,listLookup(vcol,codes$nCandF))
  if(!is.null(rescol)) {
    # Jackknife adjust entries by removing self from counts
    nPlus <- pmax(eps,nPlus - ifelse(rescol,1,0))
    nMinus <- pmax(eps,nMinus - ifelse(rescol,0,1))
  }
  lg <- log(nPlus) - log(nMinus)
  isRest <- ifelse(pmax(nPlus,nMinus)<10,1,0)
  z <- data.frame(z1=nPlus,z2=nMinus,z3=lg,z4=isRest,
                  stringsAsFactors = FALSE)
  colnames(z) <- paste(vname,c('T','F','l','r'),sep='.')
  z
}


#' Return a count coding plan
#' 
#' @param d data.frame
#' @param yName name of dependent variable
#' @param varnames names of independent variables
#' @param sigma noising degree
#' @return count coding plan
trainCountCoder <- function(d,yName,varNames,sigma) {
  coder <- trainCoder(d,yName,varNames,conditionalCounts,countCode,sigma) 
  coder$what <- 'countCoder'
  coder$codeFrame <- function(df) codeFrame(df,coder,c())
  coder
}

#' Jacknife encode a dataframe through count code.
#' 
#' @param d data.frame
#' @param yName name of dependent variable
#' @param varnames names of independent variables
#' @return Jackknife encoded frame
jackknifeCountCode <- function(d,yName,varNames) {
  coder <- trainCoder(d,yName,varNames,conditionalCounts,countCode,0) 
  coder$what <- 'countCoder'
  codeFrame(d,coder,d[[yName]])
}

# standard logisticRegression
glmFitter <- function(yVar,
                      xVars,trainData,applicationData,
                     what='',
                     verbose=FALSE) {
  formulaL <- paste(yVar,paste(xVars,collapse=' + '),sep=' ~ ')
  modelL <- glm(formulaL,data=trainData,family=binomial)
  trainPred=predict(modelL,newdata=trainData,type='response')
  appPred=predict(modelL,newdata=applicationData,type='response')
  if(verbose) {
    print(paste(what,"fit model:"))
    print(summary(modelL))
  }
  list(trainPred=trainPred,
       appPred=appPred)
}


findSigmaC <- function(cl,
                       fnFitter,
                       yName,
                       yVars,
                       dTrain,
                       vars,
                       dCal,
                       sigmaTargets=(seq_len(41)-1)) {
  force(fnFitter)
  force(yName)
  force(yVars)
  force(dTrain)
  force(vars)
  force(dCal)
  bindToEnv(objNames=sourcedFns)
  worker <- function(sigma) {
    scoresB <- numeric(3)
    for(rep in seq_len(length(scoresB))) {
      bCoder <- trainBayesCoder(dTrain,yName,vars,sigma)
      dTrainB <- bCoder$codeFrame(dTrain)
      dCalB <- bCoder$codeFrame(dCal)
      varsB <- setdiff(colnames(dTrainB),yVars)
      preds <- fnFitter(yName,varsB,dTrainB,dCalB) 
      dCalB$pred <- preds$appPred
      scoresB[[rep]] <- meanDeviance(dCalB$pred,dCalB[[yName]])
    }
    list(scoreB=mean(scoresB),sigma=sigma)
  }
  
  if(!is.null(cl)) {
    results <- parallel::parLapplyLB(cl,sigmaTargets,worker)
  } else {
    results <- vector(mode='list',length=length(sigmaTargets))
    for(ii in seq_len(length(sigmaTargets))) {
      results[[ii]] <- worker(sigmaTargets[[ii]])
    }
  }
  
  bSigmaBest = 0
  bestB = Inf
  for(res in results) {
    sigma <- res$sigma
    scoreB <- res$scoreB
    if(scoreB<bestB) {
      bestB <- scoreB
      bSigmaBest <- sigma
    }
  }
  bSigmaBest
}





naiveModel <- function(d,yName,vars,dTest,stratarg) {
  coder <- trainBayesCoder(d,yName,vars,0)
  d2 <- coder$codeFrame(d)
  dTest2 <- coder$codeFrame(dTest)
  estimateExpectedPrediction(d2,yName,vars,dTest2)
}

jackknifeModel <- function(d,yName,vars,dTest,stratarg) {
  coder <- trainBayesCoder(d,yName,vars,0)
  d2 <- jackknifeBayesCode(d,yName,vars)
  dTest2 <- coder$codeFrame(dTest)
  estimateExpectedPrediction(d2,yName,vars,dTest2)
}

#' @param stratarg sigma for the noising
noisedModel <-  function(d,yName,vars,dTest,stratarg) {
  coder <- trainBayesCoder(d,yName,vars,stratarg)
  d2 <- coder$codeFrame(d)
  dTest2 <- coder$codeFrame(dTest)
  estimateExpectedPrediction(d2,yName,vars,dTest2)
}

splitModel <- function(d,yName,vars,dTest,stratarg) {
  # can use deterministic split as rows are
  # in a random order in the intended example
  dSplit1 <- logical(nrow(d))
  dSplit1[seq_len(floor(nrow(d)/2))] <- TRUE
  coder <- trainBayesCoder(d[dSplit1,],yName,vars,0)
  d2 <- coder$codeFrame(d[!dSplit1,])
  dTest2 <- coder$codeFrame(dTest)
  estimateExpectedPrediction(d2,yName,vars,dTest2)
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

#' @param stratarg noisePlan pre-built noise for the noising
noisedModelFixed <-  function(d,yName,vars,dTest,stratarg) {
  coder <- trainBayesCoderFixed(d,yName,vars,stratarg)
  d2 <- coder$codeFrame(d)
  dTest2 <- coder$codeFrame(dTest)
  estimateExpectedPrediction(d2,yName,vars,dTest2)
}

#' one fit on averged data frame
#' @param stratarg list of noisePlans pre-built noise for the noising
noisedModelFixedV1 <-  function(d,yName,vars,dTest,stratarg) {
  d2 <- c()
  dTest2 <- c()
  for(si in stratarg) {
    coder <- trainBayesCoderFixed(d,yName,vars,si)
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
  d2[[yName]] <- d[[yName]]
  dTest2 <- dTest2/length(stratarg)
  dTest2[[yName]] <- dTest[[yName]]
  estimateExpectedPrediction(d2,yName,vars,dTest2)
}

#' many fits, average prediction
#' @param stratarg list of noisePlans pre-built noise for the noising
noisedModelFixedV2 <-  function(d,yName,vars,dTest,stratarg) {
  pred <- c()
  for(si in stratarg) {
    coder <- trainBayesCoderFixed(d,yName,vars,si)
    d2 <- coder$codeFrame(d)
    dTest2 <- coder$codeFrame(dTest)
    pi <- estimateExpectedPrediction(d2,yName,vars,dTest2)
    if(is.null(pred)) {
      pred <- pi
    } else {
      pred <- pred+pi
    }
  }
  pred/length(stratarg)
}


# const model
constModel <-  function(d,yName,vars,dTest,stratarg) {
  rep(mean(d[[yName]]),nrow(dTest))
}

#' Fit a glm() on top of the dEstimate column to the d$y column, then apply this model to dTest
#'
#' Simulates the second stage of a 2-stage modeling process.
#' @param d data frame with vars and y column
#' @param yName name of y variable
#' @param vars
#' @param dTest frame to score on has group and est columns
#' @return dTest predictions
estimateExpectedPrediction <- function(d,yName,vars,dTest) {
  # catch cases unsafe for glm
  if(all(d[[yName]])) {
    return(rep(1,nrow(dTest)))
  }
  if(all(!d[[yName]])) {
    return(rep(0,nrow(dTest)))
  }
  vars <- setdiff(vars,yName)  # just in case
  oldw <- getOption("warn")
  options(warn = -1)
  f <- paste(yName,paste(vars,collapse=' + '),sep=' ~ ')
  m <- glm(f,data=d,family=binomial(link='logit'))
  p <- predict(m,newdata=dTest,type='response')
  options(warn = oldw)
  p
}



