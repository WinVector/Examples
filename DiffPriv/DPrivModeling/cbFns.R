


# y is hard-coded as "y" in this file







#' Evaluate probability of y given each row
#' 
#' @param d data frame
#' @param signalGroupLevels groups
pEachYgivenRow <- function(d,xs,signalGroupLevels) {
  arity <- match(d$group,signalGroupLevels) %% 2
  probs <- list(xs,1-xs)
  probs[arity+1]
}

#' Evaluate probability of y vector given x
#' 
#' @param d data frame
#' @param y observed ys
#' @param signalGroupLevels groups
pJointYsgivenRows <- function(d,xs,y,signalGroupLevels) {
  pYs <- pEachYgivenRow(d,xs,signalGroupLevels)
  pObs <- ifelse(y,pYs,lapply(pYs,function(x){1-x}))
  v <- Reduce(function(a,b){a*b},pObs)
  v
}


mkYList <- function(n) {
  ys <- expand.grid( rep( list(0:1), n),stringsAsFactors=FALSE)==1
  yList <- lapply(seq_len(nrow(ys)),
                  function(ii) { as.logical(ys[ii,]) })
  yList
}

extractSum <- function(vlist,vname) {
  vs <- lapply(vlist,function(vi) { vi[[vname]] })
  v <- Reduce(function(a,b){a+b},vs)
  v
}

#' evaluate a strategy by returning summary statistics
#'
#' @param d training data frame
#' @param dTest evaluation data frame
#' @param signalGroupLevels signal group levels (group named group)
#' @param noiseGroups noise group variable names
#' @param strat strategy to apply
#' @param stratarg an extra argument for the strategy
#' @param what name of strategy
#' @param parallelCluster cluster to run on
#' @param commonFns names of functions needed to run
#' @return scores
evalModelingStrategy <- function(d,dTest,signalGroupLevels,noiseGroups,
                                 strat,stratarg,what,
                                 parallelCluster,commonFns) {
  n <- nrow(d)
  xs <- seq(0,1,by=0.01)
  pTestPy <- pEachYgivenRow(dTest,xs,signalGroupLevels)
  allVars <- union("group",noiseGroups)
  # run through each possible realization of the training outcome
  # vector y.  Each situation is weigthed by the probability of 
  # seeing this y-vector (though the outcomes in the situation
  # are conditionally indpendent of this unknown probabilty 
  # given the realized y).
  mkWorker <- function() {
    bindToEnv(d,signalGroupLevels,allVars,dTest,pTestPy,strat,stratarg,
              objNames=commonFns)
    function(y) {
      d$y <- y
      pTrainYs <- pJointYsgivenRows(d,xs,y,signalGroupLevels)
      predTest <- strat(d,'y',allVars,dTest,stratarg)
      # deviance score
      scores <- lapply(seq_len(length(pTestPy)),
                       function(i) {
                         eps <- 1.e-5
                         pYi <- pTestPy[[i]]
                         predi <- predTest[[i]]
                         -2*(pYi*log2(pmax(eps,predi)) + 
                               (1-pYi)*log2(pmax(eps,1-predi)))
                       })
      meanScore <- Reduce(function(a,b){a+b},scores)/length(scores)
      list(expectedDeviance=pTrainYs*meanScore,
           totalProbCheck=pTrainYs)
    }
  }
  
  yList <-  mkYList(n)
  worker <-  mkWorker()
  if(!is.null(parallelCluster)) {
    resList <- parallel::parLapply(parallelCluster,yList,worker)
  } else {
    resList <- vector('list',length(yList))
    for(iii in seq_len(length(yList))) {
      resList[[iii]] <- worker(yList[[iii]])
    }
  }
  
  expectedDeviance <- extractSum(resList,'expectedDeviance')
  totalProbCheck <- extractSum(resList,'totalProbCheck')

  plotD <- data.frame(x=xs,
                      what=what,
                      expectedDeviance=expectedDeviance,
                      stringsAsFactors = FALSE)
  list(
    plotD=plotD,
    totalProbCheck=totalProbCheck,
    expectedDeviance=expectedDeviance
  )
}


# try to build an n-row sample where each level that occurs occurs exactly k times
# uses fact dSource is a complete design
tryFor1design <- function(n,vars,dSource) {
  idxSet <- c()
  while(length(idxSet)!=n) {
    idxSet <- c()
    canUse <- rep(TRUE,nrow(dSource))
    while(any(canUse)&&(length(idxSet)<n)) {
      possible <- as.list(seq_len(nrow(dSource))[canUse])
      # sample from a single number vector samples from a sequence up to that number
      # a but we avoid by wrapping our numbers in a list 
      idx <- as.numeric(sample(possible,1))
      idxSet <- c(idxSet,idx)
      for(v in vars) {
        canUse <- canUse & (dSource[[v]]!=dSource[[v]][idx])
      }
    }
  }
  dSource[idxSet,]
}

# try to build an n-row sample where each level that occurs occurs exactly k times
# uses fact dSource is a complete design
tryForkdesign <- function(n,k,vars,dSource) {
  if(k<=1) {
    return(tryFor1design(n,vars,dSource))
  }
  nvar <- length(vars)
  # pick symbols we are going to see
  targets <- lapply(vars,
                    function(v) {
                      sample(unique(dSource[[v]]),n/k,replace=FALSE)
                    })
  # reduce source to rows involving only those symbols
  wants <- lapply(seq_len(nvar),
                  function(i) {
                    dSource[[vars[[i]]]] %in% targets[[i]]
                  })
  want <- Reduce(function(a,b) {a&b},wants)
  dSource <- dSource[want,]
  deqk <- c()
  while(is.null(deqk)) {
    deqk <- dSource[sample.int(nrow(dSource),n,replace=TRUE),]
    for(v in allVars) {
      tab <- table(deqk[[v]])
      minV <- min(tab)
      maxV <- max(tab)
      if((minV!=maxV)||(maxV!=2)) {
        deqk <- c()
        break
      }
    }
  }
  deqk
}



