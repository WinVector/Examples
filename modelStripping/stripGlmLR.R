
library(plyr)
library(ggplot2)
library(reshape2)
set.seed(2325235)

synthFrame <- function(nrows) {
   d <- data.frame(xN=rnorm(nrows),
      xC=sample(c('a','b'),size=nrows,replace=TRUE))
   d$y <- (d$xN + ifelse(d$xC=='a',0.2,-0.2) + rnorm(nrows))>0.5
   d
}

dTrain <- synthFrame(100000)
dTest <- synthFrame(100)
model <- glm(y~xN+xC,data=dTrain,family=binomial(link='logit'))


mLength <- length(serialize(model,NULL))
print(paste('orig size',mLength))

dTest$pred1 <- predict(model,newdata=dTest,type='response')

# ggplot(data=dTest) + geom_density(aes(x=pred1,color=y))
# one way to hunt: lapply(cm,object.size)

stripGlmLR <- function(cm) {
   cm$residuals <- c()
   cm$fitted.values <- c()
   cm$y <- c()
   cm$data <- c()
   cm$model <- c()
   cm$linear.predictors <- c()
   cm$effects <- c()
   cm$weights <- c()
   cm$prior.weights <- c()
   cm$qr$qr <- c()
   attr(cm$formula,".Environment") <- c()
   cm$family$variance <- c()
   cm$family$dev.resids <- c()
   cm$family$aic <- c()
   cm$family$validmu <- c()
   cm$family$simulate <- c()
   attr(cm$terms,".Environment") <- c()
   cm
}

cm <- stripGlmLR(model)
dTest$pred2 <- predict(cm,newdata=dTest,type='response')

loss <- sum(abs(dTest$pred1-dTest$pred2))
print(paste('error',loss))

cLength <- length(serialize(cm,NULL))
print(paste('reduced size',cLength))
print(paste('size ratio',cLength/mLength))

# more leaks are found if the work is done in a function 
# which creates local environments
# preventing later changes from masking size changes
# confusing sizes
doWork <- function(n) {
  dTraini <- synthFrame(n)
  modeli <- glm(y~xN+xC,data=dTraini,family=binomial(link='logit'))
  data.frame(n=n,
     originalSize=length(serialize(modeli,NULL)),
     strippedSize=length(serialize(stripGlmLR(modeli),NULL)))
}

plotFrame <- adply(seq(100,10000,100),1,doWork)
plotFrame <- plotFrame[,setdiff(colnames(plotFrame),'X1')]

pf <- melt(plotFrame,id.vars='n',variable.name='treatment',value.name='model.size')
ggplot(data=pf,aes(x=n,y=model.size,color=treatment)) + geom_line()
ggsave(filename='glmLRmodelSizes.png')

# try glm.fit()
doWork2 <- function(n) {
  dTraini <- synthFrame(n)
  modeli <- glm.fit(y=dTraini$y,x=model.matrix(~xN+xC,dTraini),
     family=binomial(link='logit'))
  length(serialize(modeli,NULL))
}
plotFrame2 <- data.frame(n=seq(100,10000,100))
plotFrame2$fitSize <- sapply(plotFrame2$n,doWork2)
ggplot(data=plotFrame2,aes(x=n,y=fitSize)) + geom_line()
ggsave(filename='glmLRfitSizes.png')


