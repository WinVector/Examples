

#' Compute counts of rescol conditioned on level of vcol, standard method.
#' 
#' @param vcol character vector independent variable
#' @param rescol logical vector dependent variable
#' @param sigma ignored, only for consistency of calling interface
#' @return conditonal count structure
moments <- function(vcol,rescol,sigma) {
  sumXY <- tapply(as.numeric(rescol),vcol,sum)
  sumX <- tapply(rep(1.0,length(rescol)),vcol,sum)
  checkTwoNVecs(sumX,sumXY)
  list(sumX=as.list(sumX),
       sumXY=as.list(sumXY))
}

#' Compute counts of rescol conditioned on level of vcol, Laplace noise added.
#' Inspired by differential privacy ideas
#' see Misha Bilenko, Principal Researcher in Microsoft Azure Machine Learning. http://blogs.technet.com/b/machinelearning/archive/2015/02/17/big-learning-made-easy-with-counts.aspx
#' 
#' @param vcol character vector independent variable
#' @param rescol logical vector dependent variable
#' @param sigma scalar Laplace noise level to apply
#' @return conditonal count structure
momentsLNoise <- function(vcol,rescol,sigma) {
  sumXY <- tapply(as.numeric(rescol),vcol,sum)
  sumX <- tapply(rep(1.0,length(rescol)),vcol,sum)
  denomNoise <- 0
  numNoise <- 0
  if(sigma>0) {
    denomNoise <- rlaplace(length(sumX),sigma)
    numNoise <- rlaplace(length(sumX),sigma)
#     # imitate adding a few observations with mean zero y 
#     numNoise <- numNoise*sqrt(pmax(0,denomNoise))
    denomNoise <- pmax(1.e-3,denomNoise)
  }
  namesX <- names(sumX)
  sumX <- pmax(1.0,sumX+denomNoise) # kills names
  names(sumX) <- namesX
  sumXY <- sumXY+numNoise
  names(sumXY) <- namesX
  checkTwoNVecs(sumX,sumXY)
  list(sumX=as.list(sumX),
       sumXY=as.list(sumXY))
}

#' Compute counts of rescol conditioned on level of vcol, Laplace smoothing
#' 
#' @param vcol character vector independent variable
#' @param rescol logical vector dependent variable
#' @param sigma scalar Laplace smoothing (added to denominator)
#' @return conditonal count structure
momentsLSmooth <- function(vcol,rescol,sigma) {
  # count queries
  sumX <- tapply(rep(1.0,length(rescol)),vcol,sum) 
  namesX <- names(sumX)
  sumX <- sumX + sigma
  names(sumX) <- namesX
  sumXY <- tapply(as.numeric(rescol),vcol,sum)
  checkTwoNVecs(sumX,sumXY)
  list(sumX=as.list(sumX),
       sumXY=as.list(sumXY))
}



#' Encode a categorical variable as a expectation model
#'
#' @param vname independnet variable name
#' @param vcol depedent variable values
#' @param counts conditional count structure
#' @param rescol if not null the idependent column to Jackknife out of the counts
#' @param jackDen Jackknifing denominator, 1 = standard
#' @return encoded data frame
expectCode <- function(vname,vcol,counts,rescol,jackDen=1) {
  smFactor <- 1.0e-3
  sumX <- listLookup(vcol,counts$sumX)
  sumXY <- listLookup(vcol,counts$sumXY)
  sum1 <- rep(sum(as.numeric(counts$sumX)),
              length(vcol))
  sumY <- rep(sum(as.numeric(counts$sumXY)),
              length(vcol))
  if(!is.null(rescol)) {
    # Jackknife adjust entries by removing self from counts
    sumX <- sumX - 1/jackDen
    sumXY <- sumXY - rescol/jackDen
    sum1 <- sum1 - 1/jackDen
    sumY <- sumY - rescol/jackDen
  }
  # perform the expectation calculation, vectorized
  meanY <- sumY/sum1
  z <- data.frame(z=(sumXY+smFactor*meanY)/(sumX+smFactor*1) - meanY,
                  stringsAsFactors=FALSE)
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
#' @param sigma degree of Laplace smoothing
trainCoderR <- function(d,yName,varNames,maker,coder,sigma) {
  codes <- lapply(varNames,function(vnam) { maker(d[[vnam]],d[[yName]],sigma) })
  names(codes) <- varNames
  list(yName=yName,
       varNames=varNames,
       maker=maker,
       coder=coder,
       sigma=sigma,
       codes=codes)
}


#' Encode a data frame using a coding plan
#' 
#' @param d data.frame original data frame
#' @param codes coding plan
#' @param rescol optional dependent varaible to Jacknife out
#' @return encoded data frame
codeFrameR <- function(d,codes,rescol) {
  nd <- c()
  if(codes$yName %in% colnames(d)) {
    nd <- data.frame(z=d[[codes$yName]],
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

#' Return a expectation coding plan using Laplace noising
#' 
#' @param d data.frame
#' @param yName name of dependent variable
#' @param varnames names of independent variables
#' @param sigma Laplace smoothing degree
#' @return expectation encoding plan
trainEffectCoderR <- function(d,yName,varNames,sigma) {
  coder <- trainCoderR(d,yName,varNames,momentsLNoise,expectCode,sigma) 
  coder$what <- 'EffectCoder'
  coder$codeFrameR <- function(df) codeFrameR(df,coder,c())
  coder
}

#' Return a expectation coding plan using Laplace smoothing
#' 
#' @param d data.frame
#' @param yName name of dependent variable
#' @param varnames names of independent variables
#' @param sigma Laplace smoothing degree
#' @return expectation encoding plan
trainEffectCoderLSmooth <- function(d,yName,varNames,sigma) {
  coder <- trainCoderR(d,yName,varNames,momentsLSmooth,expectCode,sigma) 
  coder$what <- 'EffectCoder'
  coder$codeFrameR <- function(df) codeFrameR(df,coder,c())
  coder
}



#' Jackknife encode a dataframe through expectation encoding.
#' 
#' @param d data.frame
#' @param yName name of dependent variable
#' @param varnames names of independent variables
#' @return Jackknife encoded frame
jackknifeEffectCodeR <- function(d,yName,varNames) {
  coder <- trainCoderR(d,yName,varNames,moments,expectCode,0) 
  coder$what <- 'EffectCoder'
  codeFrameR(d,coder,d[[yName]])
}



# standard linear regression
lrFitter <- function(yVar,xVars,trainData,applicationData,
                     what='',
                     verbose=FALSE) {
  formulaL <- paste(yVar,paste(xVars,collapse=' + '),sep=' ~ ')
  modelL <- lm(formulaL,data=trainData)
  trainPred=predict(modelL,newdata=trainData)
  appPred=predict(modelL,newdata=applicationData)
  if(verbose) {
    print(paste(what,"fit model:"))
    print(summary(modelL))
    print(paste(" train rmse",
                rmse(trainPred,trainData[[yVar]])))
    print(paste(" application rmse",
                rmse(appPred,applicationData[[yVar]])))
  }
  list(trainPred=trainPred,
       appPred=appPred)
}

# diagonal fitter- assumes dc term zero and all variables 
# perfectly independent
dFitter <- function(yVar,xVars,trainData,applicationData,
                    what='',
                    verbose=FALSE) {
  trainPred <- numeric(nrow(trainData))
  appPred <- numeric(nrow(applicationData))
  betas <- numeric(length(xVars))
  for(ii in seq_len(length(xVars))) {
    xV <- xVars[[ii]]
    beta <- sum(trainData[[xV]]*trainData[[yVar]])/sum(trainData[[xV]]^2)
    if(is.nan(beta)||is.infinite(beta)||is.na(beta)) {
      beta <- 0.0
    }
    betas[[ii]] <- beta
    trainPred <- trainPred + beta*trainData[[xV]]
    appPred <- appPred + beta*applicationData[[xV]]
  }
  names(betas) <- xVars
  if(verbose) {
    print(paste(what,"fit model:"))
    print(betas)
    print(paste(" train rmse",
                rmse(trainPred,trainData[[yVar]])))
    print(paste(" application rmse",
                rmse(appPred,applicationData[[yVar]])))
  }
  list(trainPred=trainPred,
       appPred=appPred)
}



findSigmaR <- function(cl,
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
      bCoder <- trainEffectCoderR(dTrain,yName,vars,sigma)
      dTrainB <- bCoder$codeFrameR(dTrain)
      dCalB <- bCoder$codeFrameR(dCal)
      varsB <- setdiff(colnames(dTrainB),yVars)
      preds <- fnFitter(yName,varsB,dTrainB,dCalB) 
      dCalB$pred <- preds$appPred
      scoresB[[rep]] <- rmse(dCalB$pred,dCalB[[yName]])
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

