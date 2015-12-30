
# check that we have two numeric lists both with names
# and names in same order
checkTwoNVecs <- function(vec1,vec2) {
  if(!is.numeric(vec1)) {
    stop('vec1 not numeric')
  }
  if(!is.numeric(vec2)) {
    stop('vec2 not numeric')
  }
  n <- length(vec1)
  if(n!=length(vec2)) {
    stop('lengths do not match')
  }
  nm1 <- names(vec1)
  if(is.null(nm1)||(length(nm1)!=n)) {
    stop("names 1 not good")
  }
  nm2 <- names(vec2)
  if(is.null(nm2)||(length(nm2)!=n)) {
    stop("names 2 not good")
  }
  if(!all(nm1==nm2)) {
    stop("name mismatch")
  }
}

rmse <- function(pred,truth) {
  sqrt(sum((pred-truth)^2)/length(truth))
}

errorRate <- function(pred,truth) {
  sum((pred>=0.5)!=truth)/length(truth)
}

meanDeviance <- function(pred,pY) {
  eps <- 1.e-5
  -2*(pY*log2(pmax(eps,pred)) + 
        (1-pY)*log2(pmax(eps,1-pred)))
}


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

noiseExpectation <- function(orig,sigma) {
  if(sigma>0) {
    x <- orig + rlaplace(length(orig),sigma)
  } else {
    x <- orig
  }
  x
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



