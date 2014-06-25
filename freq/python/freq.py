
from scipy.special import binom
from math import ceil
from numpy import matrix,zeros
import numpy
import scipy
import scipy.optimize
from rank_nullspace import rank,nullspace

# python freq.py > freq.txt

# In all cases we are model the observed number of wins (winsSeen)
# found in flipping a coin kFlips times where the probability of
# winning on each flip is given by the probility pWin
# (pWin in the set {1/nSides, ... (nSides-1)/nSides}).

def drangei(start, stop, step):
  d = []
  r = start
  while r <= stop:
    d.append(r)
    r += step
  return d


# Write down the linear conditions that confirm a vector
# of estimates of length kFlips+1 where the entry winsSeen
# represents the estimated expected value of pWin give
# we observed winsSeen successes in kFlips trials.
# We are writing one check condition for each possible value
# of the unknown win probably pWin in the
# set {1/nSides, ... (nSides-1)/nSides}.
def freqSystem(nSides,kFlips,stepMult=1):
  pSeq = [ j/float(nSides) for j in range(1,nSides)]
  if(stepMult>1):
     pSeq = drangei(1/float(nSides),(nSides-1)/float(nSides),\
        1/float(nSides*stepMult))
  a = matrix([[binom(kFlips,winsSeen) * pWin**winsSeen * \
      (1-pWin)**(kFlips-winsSeen) for winsSeen in range(kFlips+1)] \
      for pWin in pSeq])
  b = matrix([[pWin] for pWin in pSeq])
  return {'a':a,'b':b}


# Build the tradtinal frequentist emprical estimates of
# the expected value of the unknown quantity pWin
# for each possible observed outcome of number of wins
# seen in kFlips trials
def empiricalMeansEstimates(nSides,kFlips):
  return numpy.array([ j/float(kFlips) for j in range(kFlips+1) ])



# Build the Bayes estimate of expected values from uniform priors
# on the unknown probility pWin
# (in the set {1/nSides, ... (nSides-1)/nSides})
# seen in kFlips trials
def bayesMeansEstimates(nSides,kFlips):
  e = zeros(kFlips+1)
  for winsSeen in range(kFlips+1):
    posteriorProbs = zeros(nSides-1)
    for i in range(1,nSides):
      pWin = i/float(nSides)
      posteriorProbs[i-1] = binom(kFlips,winsSeen) * \
         pWin**winsSeen * (1-pWin)**(kFlips-winsSeen)
    posteriorProbs = posteriorProbs/sum(posteriorProbs)
    e[winsSeen] = sum(posteriorProbs*range(1,nSides))/float(nSides)
  return numpy.array(e)


# Compute for a given assumed win probabilty pWin
# the expected loss (under outcomes distributed
# as len(ests)-1 flips with probility Win)
# of the estimates ests.
def lossFn(pWin,ests):
  kFlips = len(ests)-1
  loss = 0.0
  for winsSeen in range(kFlips+1):
    probObservation = binom(kFlips,winsSeen) * pWin**winsSeen *\
       (1-pWin)**(kFlips-winsSeen)
    loss = loss + probObservation*(ests[winsSeen]-pWin)**2
  return loss



# Compute for all win probabilities
# pWin in the set {1/nSides, ... (nSides-1)/nSides}
# the expected loss (under outcomes distributed
# as len(ests)-1 flips with probility Win)
# of the estimates ests.
def losses(nSides,ests):
  return numpy.array([ lossFn(j/float(nSides),ests) for j in \
     range(1,nSides) ])


def flatten(x):
   return numpy.asarray(x).reshape(-1)

def matMulFlatten(a,x):
   return flatten(a * numpy.matrix(numpy.reshape(x,[a.shape[1],1])))

nSides = 6
for kFlips in range(1,4):
  print
  print '***** nSides =',nSides,'kFlips =',kFlips
  # first check insisting on unbiasedness
  # completely determines the estimate for
  # one flip from a nSides-slides system
  sNK = freqSystem(nSides,kFlips)
  # print sNK
  print 'full rank'
  print rank(sNK['a'].T * sNK['a'])==kFlips+1
  print 'bias free determined solution'
  print flatten(numpy.linalg.solve(sNK['a'].T * sNK['a'], \
     sNK['a'].T * sNK['b']))
  print 'standard empirical solution'
  print empiricalMeansEstimates(nSides,kFlips)
  print 'losses for standard empirical solution'
  print losses(nSides,empiricalMeansEstimates(nSides,kFlips))

  # now show the bayes solution has smaller loss
  bayesSoln = bayesMeansEstimates(nSides,kFlips)
  print 'Bayes solution'
  print bayesSoln
  print 'losses for Bayes solution'
  print losses(nSides,bayesSoln)
  print 'Bayes max loss improvement'
  print max(losses(nSides,empiricalMeansEstimates(nSides,kFlips))) - \
     max(losses(nSides,bayesSoln))
  print 'Bayes solution bias check (failed)'
  print matMulFlatten(sNK['a'],bayesSoln) - flatten(sNK['b'])
  print


print
print '*****'
# now show a underdetermined system allows more solutions
kFlips = 7
# confirm more probs would completely determine this situation
# (will be by analogy to the moment curve)
print '***** nSides =',nSides,'kFlips =',kFlips
sU = freqSystem(nSides,kFlips)
print 'is full rank'
print rank(sU['a'].T * sU['a'])==kFlips+1
print 'can extend to full rank'
sCheck = freqSystem(nSides,kFlips,stepMult=2)
print rank(sCheck['a'].T * sCheck['a'])==kFlips+1
wiggleRoom = nullspace(sU['a'])
print 'confirm null vecs'
wiggleDim = wiggleRoom.shape[1]
print (wiggleRoom.shape[0]==kFlips+1) & \
   (wiggleDim + nSides-1==kFlips+1) & \
   (numpy.matrix.max(abs(sU['a'] * wiggleRoom))<1.0e-12)
baseSoln = empiricalMeansEstimates(nSides,kFlips)
print 'empirical solution'
print baseSoln
baseLosses = losses(nSides,baseSoln)
print 'empirical solution losses'
print baseLosses

def wsoln(x):
   return baseSoln + matMulFlatten(wiggleRoom,x)

def maxloss(x):
   return max(losses(nSides,wsoln(x)))-max(baseLosses)

opt = scipy.optimize.minimize(maxloss,zeros(wiggleDim),method='Powell')
newSoln = wsoln(opt['x'])
print 'new solution'
print newSoln
print 'new solution losses'
print losses(nSides,newSoln)
print 'new solution bias checks'
print matMulFlatten(sU['a'],newSoln) - flatten(sU['b'])
print 'new solution max loss improvement'
print max(baseLosses)-max(losses(nSides,newSoln))
print 'new solution individual loss changes'
print baseLosses-losses(nSides,newSoln)
bayesSoln = bayesMeansEstimates(nSides,kFlips)
bayesLosses = losses(nSides,bayesSoln)
print 'bayes solution'
print bayesSoln
print 'bayes losses'
print bayesLosses
print 'sum bayes losses'
print sum(bayesLosses)
print 'max bayes losses'
print max(bayesLosses)
print

# see if we can improve on Bayes by max criterion
def wsolnF(x):
  return bayesSoln + x

def maxlossF(x):
  return max(losses(nSides,wsolnF(x)))-max(bayesLosses)

optM = scipy.optimize.minimize(maxlossF,zeros(len(bayesSoln)), \
   method='Powell')
maxPolished = wsolnF(optM['x'])
print 'polished max soln'
print maxPolished
print 'polished max losses'
print losses(nSides,maxPolished)
print 'polished max losses max'
print max(losses(nSides,maxPolished))
print 'polished max improvement'
print max(bayesLosses)-max(losses(nSides,maxPolished))

# see if we can improve on Bayes by max criterion
def sumlossF(x):
   return sum(losses(nSides,wsolnF(x)))-sum(bayesLosses)

optS = scipy.optimize.minimize(sumlossF,zeros(len(bayesSoln)),\
   method='Powell')
polishedSum = wsolnF(optS['x'])
print 'polished sum soln'
print polishedSum
print 'polished sum losses'
print losses(nSides,polishedSum)
print 'polished sum losses sum'
print sum(losses(nSides,polishedSum))
print 'polished sum improvement'
print sum(bayesLosses)-sum(losses(nSides,polishedSum))

