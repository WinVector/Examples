
# Examples for [Bad Bayes: an example of why you need hold-out testing](http://www.win-vector.com/blog/2014/02/bad-bayes-an-example-of-why-you-need-hold-out-testing/)

Document rendering command (in bash):
```
echo "library('knitr'); knit('BadBayesExample.Rmd')" | R --vanilla ; pandoc -o BadBayesExample.html BadBayesExample.md
```


```r
runExample <- function(rows,features,rareFeature=F,nSignal=0,trainer,predictor) {
   print(sys.call(0)) # print call and arguments
   set.seed(123525)   # make result deterministic
   yValues <- factor(c('A','B'))
   xValues <- factor(c('a','b','z'))
   yData = sample(yValues,replace=T,size=rows)
   d <- data.frame(y=yData,
                   group=sample(1:100,replace=T,size=rows))
   mkRandVar <- function() {
     if(rareFeature) {
         v <- rep(xValues[[3]],rows)
         signalIndices <- sample(1:rows,replace=F,size=2)
         v[signalIndices] <- sample(xValues[1:2],replace=T,size=2)
      } else {
         v <- sample(xValues[1:2],replace=T,size=rows)
      }
      if(nSignal>0) {
         goodIndices <- sample(1:rows,replace=F,size=nSignal)
         v[goodIndices] <- xValues[as.numeric(yData[goodIndices])]
      }
      v
   }
   varValues <- as.data.frame(replicate(features,mkRandVar()))
   varNames <- colnames(varValues)
   d <- cbind(d,varValues)
   dTrain <- subset(d,group<=50)
   dTest <- subset(d,group>50)
   model <- trainer(yName='y',varNames=varNames,yValues=yValues,
      data=dTrain)
   tabTrain <- table(truth=dTrain$y,
      predict=predictor(model,newdata=dTrain,yValues=yValues))
   print('train set results')
   print(tabTrain)
   print(fisher.test(tabTrain))
   tabTest <- table(truth=dTest$y,
      predict=predictor(model,newdata=dTest,yValues=yValues))
   print('hold-out test set results')
   print(tabTest)
   print(fisher.test(tabTest))
   list(yName='y',yValues=yValues,xValues=xValues,varNames=varNames,data=d,
      model=model,tabTrain=tabTrain,tabTest=tabTest)
}
```



```r
library(e1071)
```

```
## Loading required package: class
```

```r
res <- runExample(rows=200,features=400,rareFeature=T,
   trainer=function(yName,varNames,yValues,data) {
      formula <- as.formula(paste(yName,paste(varNames,collapse=' + '),
         sep=' ~ '))
      naiveBayes(formula,data) 
   },
   predictor=function(model,newdata,yValues) { 
      predict(model,newdata,type='class')
   }
)
```

```
## runExample(rows = 200, features = 400, rareFeature = T, trainer = function(yName, 
##     varNames, yValues, data) {
##     formula <- as.formula(paste(yName, paste(varNames, collapse = " + "), 
##         sep = " ~ "))
##     naiveBayes(formula, data)
## }, predictor = function(model, newdata, yValues) {
##     predict(model, newdata, type = "class")
## })
## [1] "train set results"
##      predict
## truth  A  B
##     A 45  2
##     B  0 49
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTrain
## p-value < 2.2e-16
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##  131.3   Inf
## sample estimates:
## odds ratio 
##        Inf 
## 
## [1] "hold-out test set results"
##      predict
## truth  A  B
##     A 17 41
##     B 14 32
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTest
## p-value = 1
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##  0.3753 2.4193
## sample estimates:
## odds ratio 
##     0.9482
```



```r
library(rpart)
res <- runExample(rows=200,features=400,rareFeature=F,
   trainer=function(yName,varNames,yValues,data) {
     formula <- as.formula(paste(yName,paste(varNames,collapse=' + '),
        sep=' ~ '))
     rpart(formula,data) 
   },
   predictor=function(model,newdata,yValues) { 
      predict(model,newdata,type='class')
   }
)
```

```
## runExample(rows = 200, features = 400, rareFeature = F, trainer = function(yName, 
##     varNames, yValues, data) {
##     formula <- as.formula(paste(yName, paste(varNames, collapse = " + "), 
##         sep = " ~ "))
##     rpart(formula, data)
## }, predictor = function(model, newdata, yValues) {
##     predict(model, newdata, type = "class")
## })
## [1] "train set results"
##      predict
## truth  A  B
##     A 42  5
##     B 16 33
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTrain
## p-value = 7.575e-09
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##   5.273 64.713
## sample estimates:
## odds ratio 
##       16.7 
## 
## [1] "hold-out test set results"
##      predict
## truth  A  B
##     A 33 25
##     B 27 19
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTest
## p-value = 1
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##  0.3933 2.1839
## sample estimates:
## odds ratio 
##     0.9296
```



```r
# glm example
res <- runExample(rows=200,features=400,rareFeature=F,
   trainer=function(yName,varNames,yValues,data) {
      formula <- as.formula(paste(yName,paste(varNames,collapse=' + '),
         sep=' ~ '))
      glm(formula,data,family=binomial(link='logit')) 
   },
   predictor=function(model,newdata,yValues) { 
      pred <- predict(model,newdata=newdata,type='response')
      yValues[ifelse(pred>=0.5,2,1)]
   }
)
```

```
## runExample(rows = 200, features = 400, rareFeature = F, trainer = function(yName, 
##     varNames, yValues, data) {
##     formula <- as.formula(paste(yName, paste(varNames, collapse = " + "), 
##         sep = " ~ "))
##     glm(formula, data, family = binomial(link = "logit"))
## }, predictor = function(model, newdata, yValues) {
##     pred <- predict(model, newdata = newdata, type = "response")
##     yValues[ifelse(pred >= 0.5, 2, 1)]
## })
```

```
## Warning: prediction from a rank-deficient fit may be misleading
```

```
## [1] "train set results"
##      predict
## truth  A  B
##     A 47  0
##     B  0 49
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTrain
## p-value < 2.2e-16
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##  301.5   Inf
## sample estimates:
## odds ratio 
##        Inf
```

```
## Warning: prediction from a rank-deficient fit may be misleading
```

```
## [1] "hold-out test set results"
##      predict
## truth  A  B
##     A 35 23
##     B 25 21
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTest
## p-value = 0.5556
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##  0.5426 3.0070
## sample estimates:
## odds ratio 
##      1.275
```



```r
library(randomForest)
```

```
## randomForest 4.6-7
## Type rfNews() to see new features/changes/bug fixes.
```

```r
res <- runExample(rows=200,features=400,rareFeature=F,
   trainer=function(yName,varNames,yValues,data) {
      formula <- as.formula(paste(yName,paste(varNames,collapse=' + '),
         sep=' ~ '))
      randomForest(formula,data) 
   },
   predictor=function(model,newdata,yValues) { 
      predict(model,newdata,type='response')
   }
)
```

```
## runExample(rows = 200, features = 400, rareFeature = F, trainer = function(yName, 
##     varNames, yValues, data) {
##     formula <- as.formula(paste(yName, paste(varNames, collapse = " + "), 
##         sep = " ~ "))
##     randomForest(formula, data)
## }, predictor = function(model, newdata, yValues) {
##     predict(model, newdata, type = "response")
## })
## [1] "train set results"
##      predict
## truth  A  B
##     A 47  0
##     B  0 49
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTrain
## p-value < 2.2e-16
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##  301.5   Inf
## sample estimates:
## odds ratio 
##        Inf 
## 
## [1] "hold-out test set results"
##      predict
## truth  A  B
##     A 21 37
##     B 13 33
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTest
## p-value = 0.4095
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##  0.5794 3.6528
## sample estimates:
## odds ratio 
##      1.436
```



```r
## recognizes no fit
library(gbm)
```

```
## Loading required package: survival
## Loading required package: splines
## Loading required package: lattice
## Loading required package: parallel
## Loaded gbm 2.1
```

```r
for (nSignal in c(0,50)) { 
   print('##################')
   print(paste('nSignal:',nSignal))
   print('')
   res <- runExample(rows=200,features=400,rareFeature=T,nSignal=nSignal,
      trainer=function(yName,varNames,yValues,data) {
         yTerm <- paste('ifelse(',yName,'=="',yValues[[1]],'",1,0)',sep='')
         formula <- as.formula(paste(yTerm,paste(varNames,collapse=' + '),
            sep=' ~ '))
         gbm(formula,data=data,distribution='bernoulli',n.trees=100,
            interaction.depth=3) 
      },
      predictor=function(model,newdata,yValues) { 
         pred <- predict(model,newdata,n.trees=100,type='response')
         yValues[ifelse(pred>=0.5,1,2)]
      }
   )
   print('##################')
}
```

```
## [1] "##################"
## [1] "nSignal: 0"
## [1] ""
## runExample(rows = 200, features = 400, rareFeature = T, nSignal = nSignal, 
##     trainer = function(yName, varNames, yValues, data) {
##         yTerm <- paste("ifelse(", yName, "==\"", yValues[[1]], 
##             "\",1,0)", sep = "")
##         formula <- as.formula(paste(yTerm, paste(varNames, collapse = " + "), 
##             sep = " ~ "))
##         gbm(formula, data = data, distribution = "bernoulli", 
##             n.trees = 100, interaction.depth = 3)
##     }, predictor = function(model, newdata, yValues) {
##         pred <- predict(model, newdata, n.trees = 100, type = "response")
##         yValues[ifelse(pred >= 0.5, 1, 2)]
##     })
## [1] "train set results"
##      predict
## truth  A  B
##     A  0 47
##     B  0 49
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTrain
## p-value = 1
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##    0 Inf
## sample estimates:
## odds ratio 
##          0 
## 
## [1] "hold-out test set results"
##      predict
## truth  A  B
##     A  0 58
##     B  0 46
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTest
## p-value = 1
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##    0 Inf
## sample estimates:
## odds ratio 
##          0 
## 
## [1] "##################"
## [1] "##################"
## [1] "nSignal: 50"
## [1] ""
## runExample(rows = 200, features = 400, rareFeature = T, nSignal = nSignal, 
##     trainer = function(yName, varNames, yValues, data) {
##         yTerm <- paste("ifelse(", yName, "==\"", yValues[[1]], 
##             "\",1,0)", sep = "")
##         formula <- as.formula(paste(yTerm, paste(varNames, collapse = " + "), 
##             sep = " ~ "))
##         gbm(formula, data = data, distribution = "bernoulli", 
##             n.trees = 100, interaction.depth = 3)
##     }, predictor = function(model, newdata, yValues) {
##         pred <- predict(model, newdata, n.trees = 100, type = "response")
##         yValues[ifelse(pred >= 0.5, 1, 2)]
##     })
## [1] "train set results"
##      predict
## truth  A  B
##     A 46  1
##     B  0 49
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTrain
## p-value < 2.2e-16
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##  181.9   Inf
## sample estimates:
## odds ratio 
##        Inf 
## 
## [1] "hold-out test set results"
##      predict
## truth  A  B
##     A 19 39
##     B  0 46
## 
## 	Fisher's Exact Test for Count Data
## 
## data:  tabTest
## p-value = 3.71e-06
## alternative hypothesis: true odds ratio is not equal to 1
## 95 percent confidence interval:
##  4.999   Inf
## sample estimates:
## odds ratio 
##        Inf 
## 
## [1] "##################"
```




