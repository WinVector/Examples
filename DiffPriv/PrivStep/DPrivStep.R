

rlaplace <- function(n,sigma) {
  rexp(n,rate = 1/sigma) - rexp(n,rate = 1/sigma)
}


mkData <- function(coefs,nRow) {
  y <- ifelse(runif(nRow)>0.5,1.0,-1.0)
  d <- matrix(data=0,
              nrow=nRow,ncol=length(coefs))
  for(i in seq_len(nRow)) {
    for(j in seq_len(length(coefs))) {
      d[i,j] <- rnorm(1,
                      mean=0.1*coefs[[j]]*y[[i]],
                      sd=1)
    }
  }
  d <- data.frame(d)
  colnames(d) <- names(coefs)
  d$y <- y>0
  d
}

accuracy <- function(y,pred) {
  sum(y==(pred>=0.5))/length(y)
}

mkModel <- function(varList,dat) {
  formula <- paste('y',paste(varList,collapse=' + '),sep=' ~ ')
  glm(formula,data=dat,family=binomial(link='logit'))
}

scoreModel <- function(model,dat) {
  pred <- predict(model,newdata=dat,type='response')
  accuracy(dat$y,pred)
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






