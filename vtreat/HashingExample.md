Example from [`FeatureHashing package`](https://CRAN.R-project.org/package=FeatureHashing).

``` r
library("FeatureHashing")
data(ipinyou)
f <- ~ IP + Region + City + AdExchange + Domain +
  URL + AdSlotId + AdSlotWidth + AdSlotHeight +
  AdSlotVisibility + AdSlotFormat + CreativeID +
  Adid + split(UserTag, delim = ",")
m.train <- hashed.model.matrix(f, ipinyou.train, 2^16)
m.test <- hashed.model.matrix(f, ipinyou.test, 2^16)

library(glmnet)
```

    ## Loading required package: Matrix

    ## Loading required package: foreach

    ## Loaded glmnet 2.0-5

``` r
cv.g.lr <- cv.glmnet(m.train, ipinyou.train$IsClick,
                     family = "binomial")#, type.measure = "auc")
p.lr <- predict(cv.g.lr, m.test, s="lambda.min")
auc(ipinyou.test$IsClick, p.lr)
```

    ## [1] 0.5187244

``` r
## Per-Coordinate FTRL-Proximal with $L_1$ and $L_2$ Regularization for Logistic Regression
# The following scripts use an implementation of the FTRL-Proximal for Logistic Regresion, # which is published in McMahan, Holt and Sculley et al. (2013), to predict the probability # (1-step prediction) and update the model simultaneously.
source(system.file("ftprl.R", package = "FeatureHashing"))
m.train <- hashed.model.matrix(f, ipinyou.train, 2^16, transpose = TRUE)
ftprl <- initialize.ftprl(0.1, 1, 0.1, 0.1, 2^16)
ftprl <- update.ftprl(ftprl, m.train, ipinyou.train$IsClick, predict = TRUE)
auc(ipinyou.train$IsClick, attr(ftprl, "predict"))
```

    ## [1] 0.5993447

`vtreat` version.

``` r
library("vtreat")
library("dplyr")
```

    ## 
    ## Attaching package: 'dplyr'

    ## The following objects are masked from 'package:stats':
    ## 
    ##     filter, lag

    ## The following objects are masked from 'package:base':
    ## 
    ##     intersect, setdiff, setequal, union

``` r
set.seed(232325)

splitRows <- function(d, var, sep= ',') {
  splits <- strsplit(d[[var]], sep)
  n <- nrow(d)
  rlist <- lapply(seq_len(n),
                  function(i) {
                    si <- splits[[i]]
                    di <- d[rep(i, max(1,length(si))), , drop=FALSE]
                    di$origRowNum <- i
                    di$weight <- 1/nrow(di)
                    di[[var]] <- NA
                    if(length(si)>0) {
                      di[[var]] <- si
                    }
                    di
                  })
  r <- dplyr::bind_rows(rlist)
  r
}

outcome <- 'IsClick'
vars <- c('IP', 'Region', 'City', 'AdExchange', 'Domain',
  'URL', 'AdSlotId', 'AdSlotWidth', 'AdSlotHeight', 
  'AdSlotVisibility', 'AdSlotFormat', 'CreativeID',
  'Adid', 'UserTag')

splitVar <- 'UserTag'
trainS <- splitRows(ipinyou.train, splitVar)
testS <- splitRows(ipinyou.test, splitVar)
f2 <- paste(outcome, 
            paste(vars, collapse = ' + '),
            sep = ' ~ ')
splitF <- makekWayCrossValidationGroupedByColumn('origRowNum')
cfe <- vtreat::mkCrossFrameCExperiment(trainS, 
                                       vars,
                                       splitFunction = splitF,
                                       weights = trainS$weight,
                                       outcome, TRUE)
treatmentPlan <- cfe$treatments
sf <- treatmentPlan$scoreFrame
train.v <- cfe$crossFrame
newvars <- unique(c(sf$varName[sf$sig<1/nrow(sf)], 'UserTag_catB'))
test.v <- prepare(treatmentPlan, testS, 
                 pruneSig= NULL, varRestriction = newvars)
cv.g.lr <- cv.glmnet(as.matrix(train.v[, newvars]), train.v$IsClick,
                     family = "binomial",
                     weights = cfe$crossWeights)
test.v$pred <- as.numeric(predict(cv.g.lr, 
                                  as.matrix(test.v[, newvars]), 
                                  s="lambda.min"))
test.v$weight <- testS$weight
test.v$origRowNum <- testS$origRowNum
test.v %>% 
  group_by(origRowNum) %>%
  summarize(pred = sum(pred*weight)/sum(weight)) %>%
  arrange(origRowNum) -> netPreds
auc(ipinyou.test$IsClick, netPreds$pred)
```

    ## [1] 0.6191087
