
designVar <- function(vname,nlevs) {
  probs <- runif(nlevs)
  probs <- probs/sum(probs)
  cumprobs <- cumsum(probs)
  codes <- paste(vname,sprintf("c%03d",seq_len(nlevs)),sep='.')
  lpy <- rnorm(nlevs)
  list(vname=vname,
       probs=probs,
       cumprobs=cumprobs,
       codes=codes,
       lpy=lpy)
}

designNoiseVar <- function(vname,nlevs) {
  probs <- runif(nlevs)
  probs <- probs/sum(probs)
  cumprobs <- cumsum(probs)
  codes <- paste(vname,sprintf("c%03d",seq_len(nlevs)),sep='.')
  lpy <- numeric(nlevs)
  list(vname=vname,
       probs=probs,
       cumprobs=cumprobs,
       codes=codes,
       lpy=lpy)
}


generateExample <- function(vars,nrow) {
  y <- numeric(nrow)
  d <- data.frame(y=logical(nrow),
                  stringsAsFactors=FALSE)
  for(var in vars) {
    idxs <- 1+findInterval(runif(nrow),var$cumprobs)
    d[[var$vname]] <- var$codes[idxs]
    y <- y + var$lpy[idxs]
  }
  d$y <- (y+rnorm(nrow))>0
  d
}

# vars <- list(designVar('x1',10),designVar('x2',100),designVar('x3',1000))
# generateExample(vars,15)


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

