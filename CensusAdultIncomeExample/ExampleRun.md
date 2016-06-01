``` r
library('vtreat')
library('caret')
library('gbm')
library('doMC')
library('WVPlots') # see https://github.com/WinVector/WVPlots

# parallel for vtreat
ncores <- parallel::detectCores()
parallelCluster <- parallel::makeCluster(ncores)
# parallel for caret
registerDoMC(cores=ncores)
```

``` r
# load data
# data from: http://archive.ics.uci.edu/ml/machine-learning-databases/adult/
colnames <-
  c(
    'age',
    'workclass',
    'fnlwgt',
    'education',
    'education-num',
    'marital-status',
    'occupation',
    'relationship',
    'race',
    'sex',
    'capital-gain',
    'capital-loss',
    'hours-per-week',
    'native-country',
    'class'
  )
dTrain <- read.table(
  'adult.data.txt',
  header = FALSE,
  sep = ',',
  strip.white = TRUE,
  stringsAsFactors = FALSE,
  na.strings = c('NA', '?', '')
)
colnames(dTrain) <- colnames
dTest <- read.table(
  'adult.test.txt',
  skip = 1,
  header = FALSE,
  sep = ',',
  strip.white = TRUE,
  stringsAsFactors = FALSE,
  na.strings = c('NA', '?', '')
)
colnames(dTest) <- colnames
```

``` r
# define problem
yName <- 'class'
yTarget <- '>50K'
varNames <- setdiff(colnames,yName)


# build varible encoding plan and prepare simulated out of sample
# training fame (cross-frame) 
# http://www.win-vector.com/blog/2016/05/vtreat-cross-frames/
cd <- vtreat::mkCrossFrameCExperiment(dTrain,varNames,yName,yTarget,
                                      parallelCluster=parallelCluster)
treatmentPlan <- cd$treatments
scoreFrame <- treatmentPlan$scoreFrame
dTrainTreated <- cd$crossFrame
# pick our variables
newVars <- scoreFrame$varName[scoreFrame$sig<1/nrow(scoreFrame)]
dTestTreated <- vtreat::prepare(treatmentPlan,dTest,
                                pruneSig=NULL,varRestriction=newVars)

# train our model using caret
yForm <- as.formula(paste(yName,paste(newVars,collapse=' + '),sep=' ~ '))
# from: http://topepo.github.io/caret/training.html
fitControl <- trainControl(## 10-fold CV
  method = "cv",
  number = 3)
model <- train(yForm,
               data = dTrainTreated,
               method = "gbm",
               trControl = fitControl,
               verbose = FALSE)
print(model)
```

    ## Stochastic Gradient Boosting 
    ## 
    ## 32561 samples
    ##    64 predictor
    ##     2 classes: '<=50K', '>50K' 
    ## 
    ## No pre-processing
    ## Resampling: Cross-Validated (3 fold) 
    ## Summary of sample sizes: 21707, 21708, 21707 
    ## Resampling results across tuning parameters:
    ## 
    ##   interaction.depth  n.trees  Accuracy   Kappa    
    ##   1                   50      0.8476398  0.5091534
    ##   1                  100      0.8552869  0.5547989
    ##   1                  150      0.8572525  0.5679670
    ##   2                   50      0.8552562  0.5579513
    ##   2                  100      0.8607842  0.5865274
    ##   2                  150      0.8633333  0.5963652
    ##   3                   50      0.8589109  0.5741589
    ##   3                  100      0.8641626  0.5974681
    ##   3                  150      0.8657596  0.6061062
    ## 
    ## Tuning parameter 'shrinkage' was held constant at a value of 0.1
    ## 
    ## Tuning parameter 'n.minobsinnode' was held constant at a value of 10
    ## Accuracy was used to select the optimal model using  the largest value.
    ## The final values used for the model were n.trees = 150,
    ##  interaction.depth = 3, shrinkage = 0.1 and n.minobsinnode = 10.

``` r
# apply predictions and plot
dTest$pred <- predict(model,newdata=dTestTreated,type='prob')[,yTarget]
WVPlots::ROCPlot(dTest,'pred',yName,'predictions on test')
```

![](ExampleRun_files/figure-markdown_github/score-1.png)

``` r
WVPlots::DoubleDensityPlot(dTest,'pred',yName,'predictions on test')
```

![](ExampleRun_files/figure-markdown_github/score-2.png)

``` r
confusionMatrix <- table(truth=dTest[[yName]],pred=dTest$pred>=0.5)
print(confusionMatrix)
```

    ##         pred
    ## truth    FALSE  TRUE
    ##   <=50K. 11694   741
    ##   >50K.   1419  2427

``` r
testAccuarcy <- (confusionMatrix[1,1]+confusionMatrix[2,2])/sum(confusionMatrix)
testAccuarcy
```

    ## [1] 0.86733

Notice the achieved test accuarcy is in the ballpark of what was reported for this dataset.

    (From http://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.names )
    Error Accuracy reported as follows, after removal of unknowns from
     |    train/test sets):
     |    C4.5       : 84.46+-0.30
     |    Naive-Bayes: 83.88+-0.30
     |    NBTree     : 85.90+-0.28

``` r
# clean up
parallel::stopCluster(parallelCluster)
```
