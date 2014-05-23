
library(ggplot2)
library(mgcv)
library(reshape2)
set.seed(2325235)

synthFrame <- function(nrows) {
   d <- data.frame(xN1=rnorm(nrows),xN2=rnorm(nrows),
      xC=sample(c('a','b'),size=nrows,replace=TRUE))
   d$y <- d$xN1*abs(d$xN1) + d$xN2 + ifelse(d$xC=='a',0.2,-0.2) + rnorm(nrows)
   d
}

dTrain <- synthFrame(100000)
dTest <- synthFrame(100)
model <- gam(y~s(xN1)+xN2+xC,data=dTrain)

mLength <- length(serialize(model,NULL))
print(paste('orig size',mLength))

dTest$pred1 <- predict(model,newdata=dTest)

# ggplot(data=dTest) + geom_density(aes(x=pred1,color=y))
# one way to hunt for leaks: lapply(cm,function(o) { length(serialize(o,NULL)) })

stripGamR <- function(cm) {
   cm$residuals <- c()
   cm$fitted.values <- c()
   cm$family <- c()
   cm$linear.predictors <- c()
   cm$weights <- c()
   cm$prior.weights <- c()
   cm$y <- c()
   cm$hat <- c()
   cm$formula <- c()
   cm$model <- c()
   cm$pred.formula <- c()
   cm$offset <- c()
   attr(cm$terms,".Environment") <- c()
   attr(cm$pterms,".Environment") <- c()
   cm
}

cm <- stripGamR(model)
dTest$pred2 <- predict(cm,newdata=dTest)

loss <- sum(abs(dTest$pred1-dTest$pred2))
print(paste('error',loss))

cLength <- length(serialize(cm,NULL))
print(paste('reduced size',cLength))
print(paste('size ratio',cLength/mLength))

plotFrame <- data.frame(n=seq(100,10000,100),originalSize=0,strippedSize=0)
for(i in 1:dim(plotFrame)[[1]]) {
  n <- plotFrame[i,'n']
  dTraini <- synthFrame(n)
  modeli <- gam(y~s(xN1)+xN2+xC,data=dTraini)
  plotFrame[i,'originalSize'] <- length(serialize(modeli,NULL))  
  plotFrame[i,'strippedSize'] <- length(serialize(stripGamR(modeli),NULL))  
}

pf <- melt(plotFrame,id.vars='n',variable.name='treatment',value.name='model.size')
ggplot(data=pf,aes(x=n,y=model.size,color=treatment)) + geom_line()
