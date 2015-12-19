
designVar <- function(vname,nlevs) {
  probs <- rep(1,nlevs)/nlevs
  cumprobs <- cumsum(probs)
  codes <- paste(vname,sprintf("c%03d",seq_len(nlevs)),sep='.')
  lpy <- rnorm(nlevs)  # effects from this variable
  # some levels have no effect
  lpy[sample.int(nlevs,floor(nlevs/2))] <- 0.0
  list(vname=vname,
       probs=probs,
       cumprobs=cumprobs,
       codes=codes,
       lpy=lpy)
}

designNoiseVar <- function(vname,nlevs) {
  probs <- rep(1,nlevs)/nlevs
  cumprobs <- cumsum(probs)
  codes <- paste(vname,sprintf("c%03d",seq_len(nlevs)),sep='.')
  lpy <- rep(0.0,nlevs)  # all zeroes, no effect from this variable
  list(vname=vname,
       probs=probs,
       cumprobs=cumprobs,
       codes=codes,
       lpy=lpy)
}


generateExample <- function(vars,nrow) {
  y <- rnorm(nrow)
  d <- data.frame(yCat=logical(nrow),
                  stringsAsFactors=FALSE)
  for(var in vars) {
    idxs <- 1+findInterval(runif(nrow),var$cumprobs)
    d[[var$vname]] <- var$codes[idxs]
    y <- y + var$lpy[idxs]
  }
  d$yCat <- y>0
  d$yNumeric <- y
  d
}

# vars <- list(designVar('x1',10),designVar('x2',100),designVar('x3',1000))
# generateExample(vars,15)


