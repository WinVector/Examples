library(MASS)

# In all cases we are model the observed number of wins (winsSeen)
# found in flipping a coin kFlips times where the probability of
# winning on each flip is given by the probability pWin 
# (pWin in the set {1/nSides, ... (nSides-1)/nSides}).

# Write down the linear conditions that confirm a vector
# of estimates of length kFlips+1 where the entry winsSeen+1
# represents the estimated expected value of pWin give
# we observed winsSeen successes in kFlips trials.
# We are writing one check condition for each possible value
# of the unknown win probably pWin in the set {1/nSides, ... (nSides-1)/nSides}.
freqSystem <- function(nSides,kFlips,stepMult=1) {
  pSeq <- (1:(nSides-1))/nSides
  if(stepMult>1) {
     pSeq <- seq(1/nSides,(nSides-1)/nSides,by=1/(nSides*stepMult))
  }
  a <- matrix(data=0.0,nrow=length(pSeq),ncol=kFlips+1)
  rownames(a) <- paste('check for p=',pSeq,sep='')
  colnames(a) <- paste('observe ',0:kFlips,'heads')
  b <- matrix(data=0,nrow=length(pSeq),ncol=1)
  rownames(b) <- paste('check for p=',pSeq,sep='')
  colnames(b) <- c('p')
  i <- 1
  for(pWin in pSeq) {
    for(winsSeen in 0:kFlips) {
      a[i,winsSeen+1] <- choose(kFlips,winsSeen) * pWin^winsSeen * (1-pWin)^(kFlips-winsSeen)
    }
    b[i,1] <- pWin
    i <- i + 1
  }
  list(a=a,b=b)
}

nameBiasChecks <- function(x) {
  names(x) <- paste('bias for p=',1:length(x)/(length(x)+1),sep='')
  x
}

nameEstimates <- function(x) {
  names(x) <- paste('pest for',0:(length(x)-1),'heads')
  x
}

# Build the traditional frequentist empirical estimates of
# the expected value of the unknown quantity pWin
# for each possible observed outcome of number of wins
# seen in kFlips trials
empiricalMeansEstimates <- function(nSides,kFlips) {
  nameEstimates(c((0:kFlips)/kFlips))
}

# Build the Bayes estimate of expected values from uniform priors
# on the unknown probability pWin (in the set {1/nSides, ... (nSides-1)/nSides})
# seen in kFlips trials
bayesMeansEstimates <- function(nSides,kFlips) {
  e <- rep(0.0,kFlips+1)
  for(winsSeen in 0:kFlips) {
    posteriorProbs <- rep(0,nSides-1)
    for(i in 1:(nSides-1)) {
      pWin <- i/nSides
      posteriorProbs[i] <- choose(kFlips,winsSeen) * pWin^winsSeen * (1-pWin)^(kFlips-winsSeen)
    }
    posteriorProbs <- posteriorProbs/sum(posteriorProbs)
    e[winsSeen+1] <- sum(posteriorProbs*(1:(nSides-1))/nSides)
  }
  nameEstimates(e)
}

# Compute for a given assumed win probability pWin
# the expected loss (under outcomes distributed 
# as length(ests)-1 flips with probability Win)
# of the estimates ests.
lossFn <- function(pWin,ests) {
  kFlips <- length(ests)-1
  loss <- 0.0
  for(winsSeen in 0:kFlips) {
    probObservation <- choose(kFlips,winsSeen) * pWin^winsSeen * (1-pWin)^(kFlips-winsSeen)
    loss <- loss + probObservation*(ests[winsSeen+1]-pWin)^2
  }
  names(loss) <- paste('exp. sq. error for p=',pWin,sep='')
  loss
}

# Compute for all win probabilities
# pWin in the set {1/nSides, ... (nSides-1)/nSides}
# the expected loss (under outcomes distributed 
# as length(ests)-1 flips with probability Win)
# of the estimates ests.
losses <- function(nSides,ests) {
  sapply((1:(nSides-1))/nSides,function(pWin) lossFn(pWin,ests))
}

# return null vectors as columns of a matrix
nullVecs <- function(a) {
  Null(t(a))  # from MASS
}


nSides <- 6
for(kFlips in (1:3)) {
  print('')
  print(paste('***** nSides =',nSides,'kFlips =',kFlips))
  # first check insisting on unbiasedness
  # completely determines the estimate for 
  # one flip from a nSides-slides system
  sNK = freqSystem(nSides,kFlips)
  # print(sNK)
  print('full rank')
  print(qr(sNK$a)$rank==kFlips+1)
  print('bias free determined solution')
  print(nameEstimates(as.numeric(qr.solve(sNK$a,sNK$b))))
  print('standard empirical solution')
  print(empiricalMeansEstimates(nSides,kFlips))
  print('losses for standard empirical solution')
  print(losses(nSides,empiricalMeansEstimates(nSides,kFlips)))
  
  # now show the Bayes solution has smaller loss
  bayesSoln <- bayesMeansEstimates(nSides,kFlips)
  print('Bayes solution')
  print(bayesSoln)
  print('losses for Bayes solution')
  print(losses(nSides,bayesSoln))
  print('Bayes max loss improvement')
  print(max(losses(nSides,empiricalMeansEstimates(nSides,kFlips))) - max(losses(nSides,bayesSoln)))
  print('Bayes solution bias check (failed)')
  print(nameBiasChecks(as.numeric(sNK$a %*% bayesSoln - sNK$b)))
  print('')
}

print('')
print('*****')
# now show a under-determined system allows more solutions
kFlips = 7
# confirm more probs would completely determine this situation (should by analogy to the moment curve)
print('')
print(paste('***** nSides =',nSides,'kFlips =',kFlips))
print(kFlips)
sU <- freqSystem(nSides,kFlips)
print('is full rank')
print(qr(sU$a)$rank==kFlips+1)
print('can extend to full rank')
sCheck = freqSystem(nSides,kFlips,stepMult=2)
print(qr(sCheck$a)$rank==kFlips+1)
wiggleRoom = nullVecs(sU$a)
print('confirm null vecs')
wiggleDim <- dim(wiggleRoom)[[2]]
print((dim(wiggleRoom)[[1]]==kFlips+1) && (wiggleDim + nSides-1==kFlips+1) &&
   (max(abs(sU$a %*% wiggleRoom))<1.0e-12))
baseSoln <- empiricalMeansEstimates(nSides,kFlips)
print('empirical solution')
print(baseSoln)
baseLosses <- losses(nSides,baseSoln)
print('empirical solution losses')
print(baseLosses)
wsoln <- function(x) {nameEstimates(baseSoln  + as.numeric(wiggleRoom %*% x))}
maxloss <- function(x) {max(losses(nSides,wsoln(x)))-max(baseLosses)}
opt <- optim(rep(0.0,wiggleDim),f=maxloss,method='BFGS')
newSoln <- wsoln(opt$par)
print('new solution')
print(newSoln)
print('new solution losses')
print(losses(nSides,newSoln))
print('new solution bias checks')
print(nameBiasChecks(as.numeric(sU$a %*% newSoln - sU$b)))
print('new solution max loss improvement')
print(max(baseLosses)-max(losses(nSides,newSoln)))
print('new solution individual loss changes')
print(baseLosses-losses(nSides,newSoln))
bayesSoln <- bayesMeansEstimates(nSides,kFlips)
bayesLosses <- losses(nSides,bayesSoln)
print('bayes solution')
print(bayesSoln)
print('bayes losses')
print(bayesLosses)
print('sum bayes losses')
print(sum(bayesLosses))
print('max bayes losses')
print(max(bayesLosses))

print('')
# see if we can improve on Bayes by max criterion
wsolnF <- function(x) {nameEstimates(bayesSoln + x)}
maxlossF <- function(x) {max(losses(nSides,wsolnF(x)))-max(bayesLosses)}
optM <- optim(rep(0.0,length(bayesSoln)),f=maxlossF,method='BFGS')
maxPolished <- wsolnF(optM$par)
print('polished max soln')
print(maxPolished)
print('polished max losses')
print(losses(nSides,maxPolished))
print('polished max losses max')
print(max(losses(nSides,maxPolished)))
print('polished max improvement')
print(max(bayesLosses)-max(losses(nSides,maxPolished)))

print('')
# see if we can improve on Bayes by max criterion
sumlossF <- function(x) {sum(losses(nSides,wsolnF(x)))-sum(bayesLosses)}
optS <- optim(rep(0.0,length(bayesSoln)),f=sumlossF,method='BFGS')
polishedSum <- wsolnF(optS$par)
print('polished sum soln')
print(polishedSum)
print('polished sum losses')
print(losses(nSides,polishedSum))
print('polished sum losses sum')
print(sum(losses(nSides,polishedSum)))
print('polished sum improvement')
print(sum(bayesLosses)-sum(losses(nSides,polishedSum)))

# # look into polished soln
# library(contfrac)
# conv <- convergents(as_cf(polished[[1]]))
# conv$A/conv$B
# # likely not near a simple fraction


