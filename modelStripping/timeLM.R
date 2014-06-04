
library(ggplot2)
set.seed(2325235)

synthFrame <- function(nrows) {
   d <- data.frame(xN=rnorm(nrows),
      xC=sample(c('a','b'),size=nrows,replace=TRUE))
   d$y <- (d$xN + ifelse(d$xC=='a',0.2,-0.2) + rnorm(nrows))
   d
}


# see if step() is working off (X^T X, X^T y) or re-scanning data
# answer: it has a run time proportional to the data size, not just
# a function of (X^T X, X^T y).
dTrainB <- synthFrame(100)
timeStep <- function(n) {
  dTraini <- c()
  for(i in 1:(n/dim(dTrainB)[[1]])) {
     dTraini <- rbind(dTraini,dTrainB)
  }
  nreps <- 5
  modeli <- lm(y~xN+xC,data=dTraini)
  stepResF <- step(modeli,trace=0) # run once to make sure data frame is ready
  duration <- system.time(
     for(i in 1:nreps) {
        stepResI <- step(modeli,trace=0)
     })
  duration['elapsed']/nreps
}
plotFrameStep <- data.frame(n=seq(100,10000,100))
plotFrameStep$stepTimeSeconds <- sapply(plotFrameStep$n,timeStep)
ggplot(data=plotFrameStep,aes(x=n,y=stepTimeSeconds)) + geom_line()
ggsave(filename='lmstepTimes.png')

