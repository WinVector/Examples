```
%load_ext rpy2.ipython
```

    The rpy2.ipython extension is already loaded. To reload it, use:
      %reload_ext rpy2.ipython



```
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
grdevices = importr('grDevices')
r = ro.r

df = ro.DataFrame({'x': ro.FloatVector(x), \
                   'y': ro.FloatVector(y), \
                   'e': ro.FloatVector(e), \
                   'ymin': ro.FloatVector(y-e), \
                   'ymax': ro.FloatVector(y+e)})
rprint(df)
```

        y  x ymin   e ymax
    1  33  0 29.4 3.6 36.6
    2  68  3 64.1 3.9 71.9
    3  34  9 31.4 2.6 36.6
    4  34 14 30.6 3.4 37.4
    5  37 15 33.2 3.8 40.8
    6  71 19 67.2 3.8 74.8
    7  37 20 34.8 2.2 39.2
    8  44 21 41.9 2.1 46.1
    9  48 30 45.7 2.3 50.3
    10 49 35 45.2 3.8 52.8
    11 53 40 50.8 2.2 55.2
    12 49 41 46.2 2.8 51.8
    13 50 42 46.1 3.9 53.9
    14 48 43 44.9 3.1 51.1
    15 56 54 52.6 3.4 59.4
    16 60 56 57.4 2.6 62.6
    17 61 67 57.6 3.4 64.4
    18 63 69 59.3 3.7 66.7
    19 44 72 42.0 2.0 46.0
    20 71 88 67.5 3.5 74.5





    <DataFrame - Python:0x107e81b00 / R:0x7fe6f77f3d48>
    [ndarray, ndarray, ndarray, ndarray, ndarray]
      y: <type 'numpy.ndarray'>
      array([ 33.,  68.,  34.,  34.,  37.,  71.,  37.,  44.,  48.,  49.,  53.,
            49.,  50.,  48.,  56.,  60.,  61.,  63.,  44.,  71.])
      x: <type 'numpy.ndarray'>
      array([  0.,   3.,   9.,  14.,  15.,  19.,  20.,  21.,  30.,  35.,  40.,
            41.,  42.,  43.,  54.,  56.,  67.,  69.,  72.,  88.])
      ymin: <type 'numpy.ndarray'>
      array([ 29.4,  64.1,  31.4,  30.6,  33.2,  67.2,  34.8,  41.9,  45.7,
            45.2,  50.8,  46.2,  46.1,  44.9,  52.6,  57.4,  57.6,  59.3,
            42. ,  67.5])
      e: <type 'numpy.ndarray'>
      array([ 3.6,  3.9,  2.6,  3.4,  3.8,  3.8,  2.2,  2.1,  2.3,  3.8,  2.2,
            2.8,  3.9,  3.1,  3.4,  2.6,  3.4,  3.7,  2. ,  3.5])
      ymax: <type 'numpy.ndarray'>
      array([ 36.6,  71.9,  36.6,  37.4,  40.8,  74.8,  39.2,  46.1,  50.3,
            52.8,  55.2,  51.8,  53.9,  51.1,  59.4,  62.6,  64.4,  66.7,
            46. ,  74.5])




```r
%%R -i df
df <- as.data.frame(df)
gp <- ggplot(df) +
      aes_string(x='x', y='y', ymin='ymin', ymax='ymax') + 
     geom_point() + 
     geom_errorbar()
print(gp)
```


    
![png](lFit_files/lFit_2_0.png)
    



```
from scipy import optimize

def squared_loss(theta, x=x, y=y, e=e):
    dy = y - theta[0] - theta[1] * x
    return np.sum(0.5 * (dy / e) ** 2)

theta1 = optimize.fmin(squared_loss, [0, 0], disp=False)




# theta will be an array of length 2 + N, where N is the number of points
# theta[0] is the intercept, theta[1] is the slope,
# and theta[2 + i] is the weight g_i

from scipy.stats import beta

priorGS = beta(0.9,0.1) # prior: most weights should be near 1 (typical)

def log_prior(theta):
    #g_i needs to be between 0 and 1
    gs = theta[2:]
    if (all(gs > 0) and all(gs < 1)):
        intercept = theta[0]
        slope = theta[1]
        return -len(gs)*priorGS.logpdf(np.mean(gs)) - \
           0.01*intercept**2 - 0.01*slope**2  # unscaled very rough priors
        # faster than summing -logpdf() over the individual gs
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



ndim = 2 + len(x)  # number of parameters in the model
nwalkers = 2*ndim+6  # number of MCMC walkers
nburn = 10000   # "burn-in" period to let chains stabilize
nsteps = 15000  # number of MCMC steps to take
sigmaB = 50.0  # outlier sigma

# set theta near the maximum likelihood, with
np.random.seed(0)
starting_guesses = np.zeros((nwalkers, ndim))
starting_guesses[:, :2] = np.random.normal(theta1, 1, (nwalkers, 2))
starting_guesses[:, 2:] = np.random.normal(0.5, 0.1, (nwalkers, ndim - 2))
```


```
# Note that this step will take a few minutes to run!
import emcee
sampler = emcee.EnsembleSampler(nwalkers, ndim, log_posterior, args=[x, y, e, sigmaB])
sampler.run_mcmc(starting_guesses, nsteps)

sample = sampler.chain  # shape = (nwalkers, nsteps, ndim)
```


```
ests = [ np.mean(sample[:,:,j]) for j in range(ndim) ]
intercept = ests[0]
slope = ests[1]
gs = [ ests[j+2] for j in range(len(x)) ]
print gs
cut = min(0.5,np.percentile(gs,15))
typical = [ g>=cut for g in gs ]


pdf = ro.DataFrame({'x': ro.FloatVector(x), \
                   'y': ro.FloatVector(y), \
                   'e': ro.FloatVector(e), \
                   'ymin': ro.FloatVector(y-e), \
                   'ymax': ro.FloatVector(y+e), \
                   'yest': ro.FloatVector(slope*x+intercept), \
                   'typical': ro.BoolVector(typical)})
rprint(pdf)
```

    [0.47208546838703519, 0.35994773593022261, 0.58080090835329634, 0.48019290214562654, 0.52389373707779618, 0.38257071352609107, 0.54861895514309222, 0.43203733480741774, 0.45367530872040196, 0.5308700876820599, 0.49858655728504886, 0.51749421806734186, 0.44359229957726398, 0.50193382337871095, 0.48978045277541277, 0.47403628685782928, 0.45770292999309642, 0.51715685728031402, 0.41664413328326638, 0.52066998728048186]
           yest   e ymax  y  x ymin typical
    1  32.17770 3.6 36.6 33  0 29.4    TRUE
    2  33.61852 3.9 71.9 68  3 64.1   FALSE
    3  36.50016 2.6 36.6 34  9 31.4    TRUE
    4  38.90152 3.4 37.4 34 14 30.6    TRUE
    5  39.38180 3.8 40.8 37 15 33.2    TRUE
    6  41.30289 3.8 74.8 71 19 67.2   FALSE
    7  41.78316 2.2 39.2 37 20 34.8    TRUE
    8  42.26344 2.1 46.1 44 21 41.9    TRUE
    9  46.58590 2.3 50.3 48 30 45.7    TRUE
    10 48.98726 3.8 52.8 49 35 45.2    TRUE
    11 51.38863 2.2 55.2 53 40 50.8    TRUE
    12 51.86890 2.8 51.8 49 41 46.2    TRUE
    13 52.34917 3.9 53.9 50 42 46.1    TRUE
    14 52.82945 3.1 51.1 48 43 44.9    TRUE
    15 58.11245 3.4 59.4 56 54 52.6    TRUE
    16 59.07300 2.6 62.6 60 56 57.4    TRUE
    17 64.35600 3.4 64.4 61 67 57.6    TRUE
    18 65.31655 3.7 66.7 63 69 59.3    TRUE
    19 66.75737 2.0 46.0 44 72 42.0   FALSE
    20 74.44174 3.5 74.5 71 88 67.5    TRUE





    <DataFrame - Python:0x107b83368 / R:0x7fe6f7477680>
    [ndarray, ndarray, ndarray, ..., ndarray, ndarray, ndarray]
      yest: <type 'numpy.ndarray'>
      array([ 32.1776996 ,  33.61851914,  36.50015822,  38.90152412,
            39.3817973 ,  41.30289002,  41.7831632 ,  42.26343638,
            46.585895  ,  48.9872609 ,  51.3886268 ,  51.86889998,
            52.34917316,  52.82944634,  58.11245132,  59.07299768,
            64.35600266,  65.31654902,  66.75736856,  74.44173944])
      e: <type 'numpy.ndarray'>
      array([ 3.6,  3.9,  2.6,  3.4,  3.8,  3.8,  2.2,  2.1,  2.3,  3.8,  2.2,
            2.8,  3.9,  3.1,  3.4,  2.6,  3.4,  3.7,  2. ,  3.5])
      ymax: <type 'numpy.ndarray'>
      array([ 36.6,  71.9,  36.6,  37.4,  40.8,  74.8,  39.2,  46.1,  50.3,
            52.8,  55.2,  51.8,  53.9,  51.1,  59.4,  62.6,  64.4,  66.7,
            46. ,  74.5])
      ...
      yest: <type 'numpy.ndarray'>
      array([  0.,   3.,   9.,  14.,  15.,  19.,  20.,  21.,  30.,  35.,  40.,
            41.,  42.,  43.,  54.,  56.,  67.,  69.,  72.,  88.])
      e: <type 'numpy.ndarray'>
      array([ 29.4,  64.1,  31.4,  30.6,  33.2,  67.2,  34.8,  41.9,  45.7,
            45.2,  50.8,  46.2,  46.1,  44.9,  52.6,  57.4,  57.6,  59.3,
            42. ,  67.5])
      ymax: <type 'numpy.ndarray'>
      array([1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1], dtype=int32)




```r
%%R -i pdf
pdf <- as.data.frame(pdf)
gpf <- ggplot(pdf) +
   geom_point(aes_string(x='x', y='y',
     color='typical',shape='typical'),size=5) + 
  geom_errorbar(aes_string(x='x', ymin='ymin', ymax='ymax')) +
  geom_line(aes_string(x='x', y='yest'))
print(gpf)

```


    
![png](lFit_files/lFit_6_0.png)
    

