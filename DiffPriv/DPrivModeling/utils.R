

rmse <- function(pred,truth) {
  sqrt(sum((pred-truth)^2)/length(truth))
}

errorRate <- function(pred,truth) {
  sum((pred>=0.5)!=truth)/length(truth)
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

listLookup <- function(vcol,maplist) {
  vals <- numeric(length(vcol))
  seen <- vcol %in% names(maplist)
  if(length(seen)>0) {
    vals[seen] <- as.numeric(unlist(maplist[vcol[seen]]))
  }
  vals[!seen] <- 0
  vals
}

# copy all objects into env and re-bind an functions lexical
# scope to env
bindToEnv <- function(env,...) {
  # get names of variables used as aguments in function call
  dnames <- sapply(substitute(list(...))[-1],deparse)
  # get the values
  dvalues <- list(...)
  # merge in any value (non "=") assigments as names
  if(!is.null(names(dvalues))) {
    blanks <- nchar(names(dvalues))<=0
    names(dvalues)[blanks] <- dnames[blanks]
  } else {
    names(dvalues) <- dnames
  }
  # now bind the values into environment
  # and switch any functions to this environment!
  for(var in names(dvalues)) {
    val <- dvalues[[var]]
    if(is.function(val)) {
      environment(val) <- env
    }
    assign(var,val,envir=env)
  }
}

