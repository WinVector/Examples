
#' Compute counts of rescol conditioned on level of vcol
#' 
#' @param vcol character vector independent variable
#' @param rescol logical vector dependent variable
#' @param sigma scalar Laplze noise level to apply
#' @return conditonal count structure
moments <- function(vcol,rescol,sigma) {
  # count queries
  sumX <- noiseCount(tapply(rep(1.0,length(rescol)),vcol,sum),sigma)
  sumXY <- noiseExpectation(tapply(as.numeric(rescol),vcol,sum),sigma)
  list(sumX=as.list(sumX),
       sumXY=as.list(sumXY))
}



#' Encode a categorical variable as a expectation model
#'
#' @param vname independnet variable name
#' @param vcol depedent variable values
#' @param counts conditional count structure
#' @param rescol if not null the idependent column to Jacknife out of the counts
#' @return encoded data frame
expectCode <- function(vname,vcol,counts,rescol) {
  smFactor <- 1.0e-3
  sumX <- listLookup(vcol,counts$sumX)
  sumXY <- listLookup(vcol,counts$sumXY)
  sum1 <- rep(sum(as.numeric(counts$sumX)),
              length(vcol))
  sumY <- rep(sum(as.numeric(counts$sumX)*as.numeric(counts$sumXY)),
              length(vcol))
  if(!is.null(rescol)) {
    # Jackknife adjust entries by removing self from counts
    sumX <- sumX - 1
    sumXY <- sumXY - rescol
    sum1 <- sum1 - 1
    sumY <- sumY - rescol
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
  nd <- data.frame(z=d[[codes$yName]],
                   stringsAsFactors = FALSE)
  colnames(nd) <- codes$yName
  for(varName in names(codes$codes)) {
    nf <- codes$coder(varName,d[[varName]],codes$codes[[varName]],rescol)
    nd <- cbind(nd,nf)
  }
  nd
}

#' Return a expectation coding plan
#' 
#' @param d data.frame
#' @param yName name of dependent variable
#' @param varnames names of independent variables
#' @param sigma Laplace smoothing degree
#' @return expectation encoding plan
trainEffectCoderR <- function(d,yName,varNames,sigma) {
  coder <- trainCoderR(d,yName,varNames,moments,expectCode,sigma) 
  coder$what <- 'EffectCoder'
  coder$codeFrameR <- function(df) codeFrameR(df,coder,c())
  coder
}

#' Jacknife encode a dataframe through expectation encoding.
#' 
#' @param d data.frame
#' @param yName name of dependent variable
#' @param varnames names of independent variables
#' @return Jackknife encoded frame
jackknifeEffectCodeR <- function(d,yName,varNames) {
  coder <- trainCoderR(d,yName,varNames,moments,expectCode,0) 
  coder$what <- 'EffectCoder'
  dc <- codeFrameR(d,coder,d[[yName]])
}


