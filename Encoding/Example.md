Model matrix does not store its "one-hot" plan anywhere, so you can not safely assume the same formula applied to two different data sets (say train and application or test) are using compatible encodings!

``` r
dTrain <- data.frame(x= c('a','b','c'), 
                     stringsAsFactors = FALSE)
stats::model.matrix(~x, dTrain)
```

    ##   (Intercept) xb xc
    ## 1           1  0  0
    ## 2           1  1  0
    ## 3           1  0  1
    ## attr(,"assign")
    ## [1] 0 1 1
    ## attr(,"contrasts")
    ## attr(,"contrasts")$x
    ## [1] "contr.treatment"

``` r
dTest <- data.frame(x= c('b','c'), 
                     stringsAsFactors = FALSE)
stats::model.matrix(~x, dTest)
```

    ##   (Intercept) xc
    ## 1           1  0
    ## 2           1  1
    ## attr(,"assign")
    ## [1] 0 1
    ## attr(,"contrasts")
    ## attr(,"contrasts")$x
    ## [1] "contr.treatment"

Let's try the Titanic data set to see encoding in action. `xgboost` requires a numeric matrix for its input, so unlike many `R` modeling methods we must manage the data encoding ourselves (instead of leaving that to `R` which often hides the encoding plan in the trained model).

``` r
library("titanic")
library("xgboost")
library("WVPlots")

data(titanic_train)
str(titanic_train)
```

    ## 'data.frame':    891 obs. of  12 variables:
    ##  $ PassengerId: int  1 2 3 4 5 6 7 8 9 10 ...
    ##  $ Survived   : int  0 1 1 1 0 0 0 0 1 1 ...
    ##  $ Pclass     : int  3 1 3 1 3 3 1 3 3 2 ...
    ##  $ Name       : chr  "Braund, Mr. Owen Harris" "Cumings, Mrs. John Bradley (Florence Briggs Thayer)" "Heikkinen, Miss. Laina" "Futrelle, Mrs. Jacques Heath (Lily May Peel)" ...
    ##  $ Sex        : chr  "male" "female" "female" "female" ...
    ##  $ Age        : num  22 38 26 35 35 NA 54 2 27 14 ...
    ##  $ SibSp      : int  1 1 0 1 0 0 0 3 0 1 ...
    ##  $ Parch      : int  0 0 0 0 0 0 0 1 2 0 ...
    ##  $ Ticket     : chr  "A/5 21171" "PC 17599" "STON/O2. 3101282" "113803" ...
    ##  $ Fare       : num  7.25 71.28 7.92 53.1 8.05 ...
    ##  $ Cabin      : chr  "" "C85" "" "C123" ...
    ##  $ Embarked   : chr  "S" "C" "S" "S" ...

``` r
summary(titanic_train)
```

    ##   PassengerId       Survived          Pclass          Name          
    ##  Min.   :  1.0   Min.   :0.0000   Min.   :1.000   Length:891        
    ##  1st Qu.:223.5   1st Qu.:0.0000   1st Qu.:2.000   Class :character  
    ##  Median :446.0   Median :0.0000   Median :3.000   Mode  :character  
    ##  Mean   :446.0   Mean   :0.3838   Mean   :2.309                     
    ##  3rd Qu.:668.5   3rd Qu.:1.0000   3rd Qu.:3.000                     
    ##  Max.   :891.0   Max.   :1.0000   Max.   :3.000                     
    ##                                                                     
    ##      Sex                 Age            SibSp           Parch       
    ##  Length:891         Min.   : 0.42   Min.   :0.000   Min.   :0.0000  
    ##  Class :character   1st Qu.:20.12   1st Qu.:0.000   1st Qu.:0.0000  
    ##  Mode  :character   Median :28.00   Median :0.000   Median :0.0000  
    ##                     Mean   :29.70   Mean   :0.523   Mean   :0.3816  
    ##                     3rd Qu.:38.00   3rd Qu.:1.000   3rd Qu.:0.0000  
    ##                     Max.   :80.00   Max.   :8.000   Max.   :6.0000  
    ##                     NA's   :177                                     
    ##     Ticket               Fare           Cabin             Embarked        
    ##  Length:891         Min.   :  0.00   Length:891         Length:891        
    ##  Class :character   1st Qu.:  7.91   Class :character   Class :character  
    ##  Mode  :character   Median : 14.45   Mode  :character   Mode  :character  
    ##                     Mean   : 32.20                                        
    ##                     3rd Qu.: 31.00                                        
    ##                     Max.   :512.33                                        
    ## 

``` r
shouldBeCategorical <- c('PassengerId', 'Pclass', 'Parch')
for(v in shouldBeCategorical) {
  titanic_train[[v]] <- as.factor(titanic_train[[v]])
}
outcome <- 'Survived'
tooDetailed <- c("Ticket", "Cabin", "Name", "PassengerId")
vars <- setdiff(colnames(titanic_train), c(outcome, tooDetailed))

set.seed(3425656)
crossValPlan <- vtreat::kWayStratifiedY(nrow(titanic_train), 
                                        10, 
                                        titanic_train, 
                                        outcome)

evaluateModelingProcedure <- function(xMatrix, outcomeV, crossValPlan) {
  preds <- rep(NA_real_, nrow(xMatrix))
  for(ci in crossValPlan) {
    model <- xgboost(data= xMatrix[ci$train, ],
                 label= outcomeV[ci$train],
                 objective= 'binary:logistic',
                 nrounds= 1000,
                 verbose= 0)
    preds[ci$app] <-  predict(model, xMatrix[ci$app, ])
  }
  preds
}
```

Our preferred way to encode data is to use the `vtreat` package either in the "no variables mode" shown below or in the "y aware" modes we usually teach.

``` r
library("vtreat")
set.seed(3425656)
tplan <- vtreat::designTreatmentsZ(titanic_train, vars, verbose=FALSE)
sf <- tplan$scoreFrame
newvars <- sf$varName[sf$code %in% c('clean', 'lev', 'isBad')]
trainVtreat <- as.matrix(vtreat::prepare(tplan, titanic_train, 
                                         varRestriction = newvars))
print(dim(trainVtreat))
```

    ## [1] 891  14

``` r
print(colnames(trainVtreat))
```

    ##  [1] "Pclass_lev_x.1"   "Pclass_lev_x.2"   "Pclass_lev_x.3"  
    ##  [4] "Sex_lev_x.female" "Sex_lev_x.male"   "Age_clean"       
    ##  [7] "SibSp_clean"      "Parch_lev_x.0"    "Parch_lev_x.1"   
    ## [10] "Parch_lev_x.2"    "Fare_clean"       "Embarked_lev_x.C"
    ## [13] "Embarked_lev_x.Q" "Embarked_lev_x.S"

``` r
titanic_train$predVtreatZ <- evaluateModelingProcedure(trainVtreat,
                                                       titanic_train[[outcome]]==1,
                                                       crossValPlan)
WVPlots::ROCPlot(titanic_train, 
                 'predVtreatZ', 
                 outcome, 1, 
                 'vtreat encoder performance')
```

![](Example_files/figure-markdown_github/vtreatZ-1.png)

Model matrix can perform similar encoding when we only have a single data set.

``` r
set.seed(3425656)
f <- paste('~ 0 + ', paste(vars, collapse = ' + '))
# model matrix skips rows with NAs by default,
# get control of this through an option
oldOpt <- getOption('na.action')
options(na.action='na.pass')
trainModelMatrix <- stats::model.matrix(as.formula(f), 
                                  titanic_train)
# note model.matrix does not conveniently store the encoding
# plan, so you may run into difficulty if you were to encode
# new data which didn't have all the levels seen in the training
# data.
options(na.action=oldOpt)
print(dim(trainModelMatrix))
```

    ## [1] 891  16

``` r
print(colnames(trainModelMatrix))
```

    ##  [1] "Pclass1"   "Pclass2"   "Pclass3"   "Sexmale"   "Age"      
    ##  [6] "SibSp"     "Parch1"    "Parch2"    "Parch3"    "Parch4"   
    ## [11] "Parch5"    "Parch6"    "Fare"      "EmbarkedC" "EmbarkedQ"
    ## [16] "EmbarkedS"

``` r
titanic_train$predModelMatrix <- evaluateModelingProcedure(trainModelMatrix,
                                                     titanic_train[[outcome]]==1,
                                                     crossValPlan)
WVPlots::ROCPlot(titanic_train, 
                 'predModelMatrix', 
                 outcome, 1, 
                 'model.matrix encoder performance')
```

![](Example_files/figure-markdown_github/modelmatrix-1.png)

`caret` supplies an encoding functionality properly split between training (`caret::dummyVars`) and application (called `predict()`).

``` r
library("caret")
```

    ## Loading required package: lattice

    ## Loading required package: ggplot2

``` r
set.seed(3425656)
f <- paste('~', paste(vars, collapse = ' + '))
encoder <- caret::dummyVars(as.formula(f), titanic_train)
trainCaret <- predict(encoder, titanic_train)
print(dim(trainCaret))
```

    ## [1] 891  19

``` r
print(colnames(trainCaret))
```

    ##  [1] "Pclass.1"  "Pclass.2"  "Pclass.3"  "Sexfemale" "Sexmale"  
    ##  [6] "Age"       "SibSp"     "Parch.0"   "Parch.1"   "Parch.2"  
    ## [11] "Parch.3"   "Parch.4"   "Parch.5"   "Parch.6"   "Fare"     
    ## [16] "Embarked"  "EmbarkedC" "EmbarkedQ" "EmbarkedS"

``` r
titanic_train$predCaret <- evaluateModelingProcedure(trainCaret,
                                                     titanic_train[[outcome]]==1,
                                                     crossValPlan)
WVPlots::ROCPlot(titanic_train, 
                 'predCaret', 
                 outcome, 1, 
                 'caret encoder performance')
```

![](Example_files/figure-markdown_github/caret-1.png)

You can also try y-aware encoding, but it isn't adding much in this situation.

``` r
set.seed(3425656)
# for y aware evaluation must cross-validate whole procedure, designing
# on data you intend to score on can leak information.
preds <- rep(NA_real_, nrow(titanic_train))
for(ci in crossValPlan) {
  cfe <- vtreat::mkCrossFrameCExperiment(titanic_train[ci$train, , drop=FALSE], 
                                     vars,
                                     outcome, 1)
  tplan <- cfe$treatments
  sf <- tplan$scoreFrame
  newvars <- sf$varName[sf$sig < 1/nrow(sf)]
  trainVtreat <- cfe$crossFrame[ , c(newvars, outcome), drop=FALSE]
  model <- xgboost(data= as.matrix(trainVtreat[, newvars, drop=FALSE]),
                   label= trainVtreat[[outcome]]==1,
                   objective= 'binary:logistic',
                   nrounds= 1000,
                   verbose= 0)
  appVtreat <- vtreat::prepare(tplan, 
                               titanic_train[ci$app, , drop=FALSE], 
                               varRestriction = newvars)
  preds[ci$app] <-  predict(model,
                            as.matrix(appVtreat[, newvars, drop=FALSE]))
}
titanic_train$predVtreatC <- preds
WVPlots::ROCPlot(titanic_train, 
                 'predVtreatC', 
                 outcome, 1, 
                 'vtreat y-aware encoder performance')
```

![](Example_files/figure-markdown_github/vtreatC-1.png)
