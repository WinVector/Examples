

library(plyr)
library(ggplot2)
library(microbenchmark)
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
  dTraini <- adply(1:(n/dim(dTrainB)[[1]]),1,function(x) dTrainB)
  modeli <- lm(y~xN+xC,data=dTraini)
  stepResF <- step(modeli,trace=0) # run once to make sure data caches are hot
  microbenchmark(step(modeli,trace=0))$time
}
plotFrameStep <- adply(seq(1000,10000,1000),1,
   function(n) data.frame(n=n,stepTime=timeStep(n)))
uBr <- max(aggregate(stepTime~n,data=plotFrameStep,
   FUN=function(x) { quantile(x,0.9) })$stepTime)
lBr <- min(aggregate(stepTime~n,data=plotFrameStep,
   FUN=function(x) { quantile(x,0.1) })$stepTime)
uB <- uBr + (uBr-lBr)/10
lB <- max(0,lBr - (uBr-lBr)/10)
ggplot(data=plotFrameStep,aes(x=n,y=stepTime)) + 
   geom_boxplot(aes(group=n),outlier.size=0) + 
   coord_cartesian(ylim=c(lB,uB)) +
   geom_smooth()
ggsave(filename='lmstepTimes.png')
