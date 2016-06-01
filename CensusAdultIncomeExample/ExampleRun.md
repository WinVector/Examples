Example showing vtreat varaible preperation followed by caret training.

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
print(newVars)
```

    ##  [1] "age_clean"                              
    ##  [2] "workclass_lev_NA"                       
    ##  [3] "workclass_lev_x.Federal.gov"            
    ##  [4] "workclass_lev_x.Local.gov"              
    ##  [5] "workclass_lev_x.Private"                
    ##  [6] "workclass_lev_x.Self.emp.inc"           
    ##  [7] "workclass_lev_x.Self.emp.not.inc"       
    ##  [8] "workclass_lev_x.State.gov"              
    ##  [9] "workclass_catP"                         
    ## [10] "workclass_catB"                         
    ## [11] "education_lev_x.10th"                   
    ## [12] "education_lev_x.11th"                   
    ## [13] "education_lev_x.Bachelors"              
    ## [14] "education_lev_x.HS.grad"                
    ## [15] "education_lev_x.Masters"                
    ## [16] "education_lev_x.Some.college"           
    ## [17] "education_catP"                         
    ## [18] "education_catB"                         
    ## [19] "education.num_clean"                    
    ## [20] "marital.status_lev_x.Divorced"          
    ## [21] "marital.status_lev_x.Married.civ.spouse"
    ## [22] "marital.status_lev_x.Never.married"     
    ## [23] "marital.status_lev_x.Separated"         
    ## [24] "marital.status_lev_x.Widowed"           
    ## [25] "marital.status_catP"                    
    ## [26] "marital.status_catB"                    
    ## [27] "occupation_lev_NA"                      
    ## [28] "occupation_lev_x.Adm.clerical"          
    ## [29] "occupation_lev_x.Exec.managerial"       
    ## [30] "occupation_lev_x.Farming.fishing"       
    ## [31] "occupation_lev_x.Handlers.cleaners"     
    ## [32] "occupation_lev_x.Machine.op.inspct"     
    ## [33] "occupation_lev_x.Other.service"         
    ## [34] "occupation_lev_x.Prof.specialty"        
    ## [35] "occupation_lev_x.Sales"                 
    ## [36] "occupation_lev_x.Tech.support"          
    ## [37] "occupation_lev_x.Transport.moving"      
    ## [38] "occupation_catP"                        
    ## [39] "occupation_catB"                        
    ## [40] "relationship_lev_x.Husband"             
    ## [41] "relationship_lev_x.Not.in.family"       
    ## [42] "relationship_lev_x.Other.relative"      
    ## [43] "relationship_lev_x.Own.child"           
    ## [44] "relationship_lev_x.Unmarried"           
    ## [45] "relationship_lev_x.Wife"                
    ## [46] "relationship_catP"                      
    ## [47] "relationship_catB"                      
    ## [48] "race_lev_x.Black"                       
    ## [49] "race_lev_x.White"                       
    ## [50] "race_catP"                              
    ## [51] "race_catB"                              
    ## [52] "sex_lev_x.Female"                       
    ## [53] "sex_lev_x.Male"                         
    ## [54] "capital.gain_clean"                     
    ## [55] "capital.loss_clean"                     
    ## [56] "hours.per.week_clean"                   
    ## [57] "native.country_lev_x.United.States"     
    ## [58] "native.country_catP"                    
    ## [59] "native.country_catB"

``` r
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
    ## Summary of sample sizes: 21707, 21707, 21708 
    ## Resampling results across tuning parameters:
    ## 
    ##   interaction.depth  n.trees  Accuracy   Kappa    
    ##   1                   50      0.8479776  0.5090206
    ##   1                  100      0.8559319  0.5561799
    ##   1                  150      0.8574368  0.5701893
    ##   2                   50      0.8557784  0.5585251
    ##   2                  100      0.8605080  0.5840380
    ##   2                  150      0.8629956  0.5946207
    ##   3                   50      0.8587267  0.5748698
    ##   3                  100      0.8636406  0.5970673
    ##   3                  150      0.8656061  0.6058856
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
    ##   <=50K. 11740   695
    ##   >50K.   1452  2394

``` r
testAccuarcy <- (confusionMatrix[1,1]+confusionMatrix[2,2])/sum(confusionMatrix)
testAccuarcy
```

    ## [1] 0.8681285

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
