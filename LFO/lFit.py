
# adapted from http://jakevdp.github.io/blog/2014/06/06/frequentism-and-bayesianism-2-when-results-differ/

import numpy as np

x = np.array([ 0,  3,  9, 14, 15, 19, 20, 21, 30, 35,
              40, 41, 42, 43, 54, 56, 67, 69, 72, 88])
y = np.array([33, 68, 34, 34, 37, 71, 37, 44, 48, 49,
              53, 49, 50, 48, 56, 60, 61, 63, 44, 71])
e = np.array([ 3.6, 3.9, 2.6, 3.4, 3.8, 3.8, 2.2, 2.1, 2.3, 3.8,
               2.2, 2.8, 3.9, 3.1, 3.4, 2.6, 3.4, 3.7, 2.0, 3.5])

import math, datetime
import rpy2.robjects.lib.ggplot2 as ggplot2
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
rprint = ro.globalenv.get("print")
base = importr('base')
datasets = importr('datasets')
r = ro.r

df = ro.DataFrame({'x': ro.FloatVector(x), \
                   'y': ro.FloatVector(y), \
                   'e': ro.FloatVector(e), \
                   'ymin': ro.FloatVector(y-e), \
                   'ymax': ro.FloatVector(y+e)})
rprint(df)
gp = ggplot2.ggplot(df)
pp = gp + \
     ggplot2.aes_string(x='x', y='y', ymin='ymin', ymax='ymax') + \
     ggplot2.geom_point() + \
     ggplot2.geom_errorbar()
pp.plot()


from scipy import optimize

def squared_loss(theta, x=x, y=y, e=e):
    dy = y - theta[0] - theta[1] * x
    return np.sum(0.5 * (dy / e) ** 2)

theta1 = optimize.fmin(squared_loss, [0, 0], disp=False)




# theta will be an array of length 2 + N, where N is the number of points
# theta[0] is the intercept, theta[1] is the slope,
# and theta[2 + i] is the weight g_i

from scipy.stats import beta

priorGS = beta(0.1,0.9)

def log_prior(theta):
    #g_i needs to be between 0 and 1
    gs = theta[2:]
    if (all(gs > 0) and all(gs < 1)):
        intercept = theta[0]
        slope = theta[1]
        return -np.log(priorGS.pdf(np.mean(gs))) - 0.01*intercept**2 - 0.01*slope**2  # unscaled very rough priors
    else:
        return -np.inf  # recall log(0) = -inf

def log_likelihood(theta, x, y, e, sigma_B):
    dy = y - theta[0] - theta[1] * x
    g = np.clip(theta[2:], 0, 1)  # g<0 or g>1 leads to NaNs in logarithm
    logL1 = np.log(g) - 0.5 * np.log(2 * np.pi * e ** 2) - 0.5 * (dy / e) ** 2
    logL2 = np.log(1 - g) - 0.5 * np.log(2 * np.pi * sigma_B ** 2) - 0.5 * (dy / sigma_B) ** 2
    return np.sum(np.logaddexp(logL1, logL2))

def log_posterior(theta, x, y, e, sigma_B):
    return log_prior(theta) + log_likelihood(theta, x, y, e, sigma_B)




# Note that this step will take a few minutes to run!

ndim = 2 + len(x)  # number of parameters in the model
nwalkers = 50  # number of MCMC walkers
nburn = 10000   # "burn-in" period to let chains stabilize
nsteps = 15000  # number of MCMC steps to take
sigmaB = 50.0  # outlier sigma

# set theta near the maximum likelihood, with 
np.random.seed(0)
starting_guesses = np.zeros((nwalkers, ndim))
starting_guesses[:, :2] = np.random.normal(theta1, 1, (nwalkers, 2))
starting_guesses[:, 2:] = np.random.normal(0.5, 0.1, (nwalkers, ndim - 2))

import emcee
sampler = emcee.EnsembleSampler(nwalkers, ndim, log_posterior, args=[x, y, e, sigmaB])
sampler.run_mcmc(starting_guesses, nsteps)

sample = sampler.chain  # shape = (nwalkers, nsteps, ndim)

ests = [ np.mean(sample[:,:,j]) for j in range(ndim) ]
intercept = ests[0]
slope = ests[1]
gs = [ ests[j+2] for j in range(len(x)) ] cut = min(0.5,np.percentile(gs,15))
typical = [ g>=cut for g in gs ]


df = ro.DataFrame({'x': ro.FloatVector(x), \
                   'y': ro.FloatVector(y), \
                   'e': ro.FloatVector(e), \
                   'ymin': ro.FloatVector(y-e), \
                   'ymax': ro.FloatVector(y+e), \
                   'yest': ro.FloatVector(slope*x+intercept), \
                   'typical': ro.BoolVector(typical)})
rprint(df)
gp = ggplot2.ggplot(df)
pp = gp + \
   ggplot2.geom_point(ggplot2.aes_string(x='x', y='y',\
     color='typical',shape='typical'),size=5) + \
   ggplot2.geom_errorbar(ggplot2.aes_string(x='x', ymin='ymin', ymax='ymax')) +\
   ggplot2.geom_line(ggplot2.aes_string(x='x', y='yest'))
pp.plot()


