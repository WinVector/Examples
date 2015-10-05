

rlaplace <- function(n,sigma) {
  if(sigma<=0) {
    return(numeric(n))
  }
  rexp(n,rate = 1/sigma) - rexp(n,rate = 1/sigma)
}

noiseCount <- function(orig,sigma) {
  if(sigma>0) {
    x <- orig + rlaplace(length(orig),sigma)
  } else {
    x <- orig
  }
  x <- pmax(x,1.0e-3)
  x
}


#' @param vcol character vector
#' @param rescol logical vector
#' @param sigma scalar 
conditionalCounts <- function(vcol,rescol,sigma) {
  # count queries
  nCandT <- noiseCount(tapply(as.numeric(rescol),vcol,sum),sigma)   #  sum of true examples for a given C (vector)
  nCandF <- noiseCount(tapply(as.numeric(!rescol),vcol,sum),sigma)  #  sum of false examples for a give C (vector)
  list(nCandT=as.list(nCandT),nCandF=as.list(nCandF))
}



listLookup <- function(vcol,maplist) {
  vals <- numeric(length(vcol))
  seen <- vcol %in% names(maplist)
  if(length(seen)>0) {
     vals[seen] <- as.numeric(unlist(maplist[vcol[seen]]))
  }
  vals[!seen] <- 0
  vals
}



bayesCode <- function(vname,vcol,counts,rescol) {
  smFactor <- 1.0e-3
  nCandT <- listLookup(vcol,counts$nCandT) #  sum of true examples for given C
  nCandF <- listLookup(vcol,counts$nCandF) #  sum of false examples for given C
  # dervived values
  nT <- rep(sum(as.numeric(counts$nCandT)),length(vcol)) #  sum of true examples (vector)
  nF <- rep(sum(as.numeric(counts$nCandF)),length(vcol))  #  sum of false examples (vector)
  if(!is.null(rescol)) {
    # Jackknife adjust entries by removing self from counts
    nCandT <- nCandT - ifelse(rescol,1,0)
    nT <- nT - ifelse(rescol,1,0)
    nCandF <- nCandF - ifelse(rescol,0,1)
    nF <- nF - ifelse(rescol,0,1)
  }
  # perform the Bayesian calculation, vectorized
  probT <- nT/(nT+nF)   # unconditional probabilty target is true
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


codeFrame <- function(d,codes,rescol) {
  nd <- data.frame(d[[codes$yName]],
                   stringsAsFactors = FALSE)
  colnames(nd) <- codes$yName
  for(varName in names(codes$codes)) {
    nf <- codes$coder(varName,d[[varName]],codes$codes[[varName]],rescol)
    nd <- cbind(nd,nf)
  }
  nd
}


trainBayesCoder <- function(d,yName,varNames,sigma) {
  coder <- trainCoder(d,yName,varNames,conditionalCounts,bayesCode,sigma) 
  coder$what <- 'BayesCoder'
  coder$codeFrame <- function(df) codeFrame(df,coder,c())
  coder
}

jackknifeBayesCode <- function(d,yName,varNames) {
  coder <- trainCoder(d,yName,varNames,conditionalCounts,bayesCode,0) 
  coder$what <- 'BayesCoder'
  dc <- codeFrame(d,coder,d[[yName]])
}



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

trainCountCoder <- function(d,yName,varNames,sigma) {
  coder <- trainCoder(d,yName,varNames,conditionalCounts,countCode,sigma) 
  coder$what <- 'countCoder'
  coder$codeFrame <- function(df) codeFrame(df,coder,c())
  coder
}

jackknifeCountCode <- function(d,yName,varNames) {
  coder <- trainCoder(d,yName,varNames,conditionalCounts,countCode,0) 
  coder$what <- 'countCoder'
  dc <- codeFrame(d,coder,d[[yName]])
}


