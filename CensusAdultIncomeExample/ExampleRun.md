This article is a demonstration the use of the [R](https://cran.r-project.org) [vtreat](https://github.com/WinVector/vtreat) variable preparation package followed by [caret](http://topepo.github.io/caret/index.html) controlled training.

In previous writings we have gone to great lengths to [document, explain and motivate `vtreat`](http://winvector.github.io/vtreathtml/). That necessarily gets long and unnecessarily feels complicated.

In this example we are going to show what building a predictive model using `vtreat` best practices looks like assuming you were somehow already in the habit of using vtreat for your data preparation step. We are deliberately not going to explain any steps, but just show the small number of steps we advise routinely using. This is a simple schematic, but not a guide. Of course we do not advise use without understanding (and we work hard to teach the concepts in our writing), but want what small effort is required to add `vtreat` to your predictive modeling practice.

First we set things up: load libraries, initialize parallel processing.

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

The we load our data for analysis. We are going to build a model predicting an income level from other demographic features. The data is taken from [here](http://archive.ics.uci.edu/ml/machine-learning-databases/adult/) and you can perform all of the demonstrated steps if you download the contents of the [example git directory](https://github.com/WinVector/Examples/tree/master/CensusAdultIncomeExample). Obviously this has a lot of moving parts (R, R Markdown, Github, R packages, devtools)- but is very easy to do a second time (first time can be a bit of learning and preparation).

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

Now we use `vtreat` to prepare the data for analysis. The goal of vtreat is to ensure a ready-to-dance data frame in a statistically valid manner. We are respecting the test/train split and building our data preparation plan only on the training data (though we do apply it to the test data). This step helps with a huge number of potential problems through automated repairs:

-   re-encoding missing values
-   dealing with large cardinality categorical variables
-   dealing with novel levels
-   fixing variable/column names to be "R safe"
-   looking for strange column types

``` r
# define problem
yName <- 'class'
yTarget <- '>50K'
varNames <- setdiff(colnames,yName)

# build variable encoding plan and prepare simulated out of sample
# training fame (cross-frame) 
# http://www.win-vector.com/blog/2016/05/vtreat-cross-frames/
system.time({
  cd <- vtreat::mkCrossFrameCExperiment(dTrain,varNames,yName,yTarget,
                                        parallelCluster=parallelCluster)
  scoreFrame <- cd$treatments$scoreFrame
  dTrainTreated <- cd$crossFrame
  # pick our variables
  newVars <- scoreFrame$varName[scoreFrame$sig<1/nrow(scoreFrame)]
  dTestTreated <- vtreat::prepare(cd$treatments,dTest,
                                  pruneSig=NULL,varRestriction=newVars)
})
```

    ##    user  system elapsed 
    ##  11.340   2.760  30.872

``` r
#print(newVars)
```

Now we train our model. In this case we are using the caret package to tune parameters.

``` r
# train our model using caret
system.time({
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
  dTest$pred <- predict(model,newdata=dTestTreated,type='prob')[,yTarget]
})
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
    ##   1                   50      0.8476398  0.5083558
    ##   1                  100      0.8556555  0.5561726
    ##   1                  150      0.8577746  0.5699958
    ##   2                   50      0.8560855  0.5606650
    ##   2                  100      0.8593102  0.5810931
    ##   2                  150      0.8625042  0.5930111
    ##   3                   50      0.8593717  0.5789289
    ##   3                  100      0.8649919  0.6017707
    ##   3                  150      0.8660975  0.6073645
    ## 
    ## Tuning parameter 'shrinkage' was held constant at a value of 0.1
    ## 
    ## Tuning parameter 'n.minobsinnode' was held constant at a value of 10
    ## Accuracy was used to select the optimal model using  the largest value.
    ## The final values used for the model were n.trees = 150,
    ##  interaction.depth = 3, shrinkage = 0.1 and n.minobsinnode = 10.

    ##    user  system elapsed 
    ##  61.908   2.227  36.850

Finally we take a look at the results on the held-out test data.

``` r
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
    ##   <=50K. 11684   751
    ##   >50K.   1406  2440

``` r
testAccuarcy <- (confusionMatrix[1,1]+confusionMatrix[2,2])/sum(confusionMatrix)
testAccuarcy
```

    ## [1] 0.8675143

Notice the achieved test accuracy is in the ballpark of what was reported for this dataset.

    (From http://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.names )
    Error Accuracy reported as follows, after removal of unknowns from
     |    train/test sets):
     |    C4.5       : 84.46+-0.30
     |    Naive-Bayes: 83.88+-0.30
     |    NBTree     : 85.90+-0.28

We can also compare accuracy on the "complete cases":

``` r
dTestComplete <- dTest[complete.cases(dTest[,varNames]),]
confusionMatrixComplete <- table(truth=dTestComplete[[yName]],
                                 pred=dTestComplete$pred>=0.5)
print(confusionMatrixComplete)
```

    ##         pred
    ## truth    FALSE  TRUE
    ##   <=50K. 10618   742
    ##   >50K.   1331  2369

``` r
testAccuarcyComplete <- (confusionMatrixComplete[1,1]+confusionMatrixComplete[2,2])/
  sum(confusionMatrixComplete)
testAccuarcyComplete
```

    ## [1] 0.8623506

``` r
# clean up
parallel::stopCluster(parallelCluster)
```

This is consistent with our experience that missingness is often actually informative, so in addition to imputing missing values you would like to preserver some notation indicating the missingness (which `vtreat` does in fact do).

And that is all there is to this example. I'd like to emphasize that vtreat steps were only a few lines in one of the blocks of code. `vtreat` treatment can take some time, but it is usually bearable. By design it is easy to add vtreat to your predictive analytics projects.

The point is: we got competitive results on real world data, in a single try (using vtreat to prepare data and caret to tune parameters). The job of the data scientist is to actually work longer on a problem and do better. But having a good start helps.

The theory behind vtreat is fairly important to the correctness of our implementation, and we would love for you to read through some of it:

-   [vtreat: designing a package for variable treatment](http://www.win-vector.com/blog/2014/08/vtreat-designing-a-package-for-variable-treatment/)
-   [vtreat Cross Frames](http://www.win-vector.com/blog/2016/05/vtreat-cross-frames/)
-   [On Nested Models](http://www.win-vector.com/blog/2016/04/on-nested-models/)
-   [vtreat manuals](http://winvector.github.io/vtreathtml/)
-   [Preparing data for analysis using R](http://winvector.github.io/DataPrep/EN-CNTNT-Whitepaper-Data-Prep-Using-R.pdf)
-   [More on preparing data](http://www.win-vector.com/blog/2016/03/more-on-preparing-data/)
-   [vtreat on Cran](https://cran.r-project.org/package=vtreat)
-   [vtreat on Github](https://github.com/WinVector/vtreat)

But operationally, please think of `vtreat` as just adding a couple of lines to your analysis scripts. Again, the raw R markdown source can be found [here](https://github.com/WinVector/Examples/blob/master/CensusAdultIncomeExample/ExampleRun.Rmd) and a rendered copy (with results and graphs) [here](https://github.com/WinVector/Examples/blob/master/CensusAdultIncomeExample/ExampleRun.md).
