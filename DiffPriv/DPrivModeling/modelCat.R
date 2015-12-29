

#' Compute counts of rescol conditioned on level of vcol
#' 
#' @param vcol character vector independent variable
#' @param rescol logical vector dependent variable
#' @param sigma scalar Laplze noise level to apply
#' @return conditonal count structure
conditionalCounts <- function(vcol,rescol,sigma) {
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
#' @param sigma degree of Laplace smoothing
trainCoder <- function(d,yName,varNames,maker,coder,sigma) {
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
#' @param sigma Laplace smoothing degree
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
#' @param sigma Laplace smoothing degree
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


