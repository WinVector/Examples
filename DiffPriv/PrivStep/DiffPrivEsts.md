Worksheet showing additional calculations for:
   http://www.win-vector.com/blog/2015/10/a-simple-differentially-private-procedure/


```python
import sympy
```

We are going to run a simple experiment.  We have two data sets of size n.  One is all zeros (S0), and one is has one one (S1). We are returning "garbled" results and want to see how often an adversary sees the measurement on the set with a 1 as strictly larger than the set without the 1.

First we could estimate the parameters needed for differential privacy (a different and stronger condition) through adding Laplace noise.




```python
# Estimate the Laplace parameter needed to establish epsilon differential privacy
# (by adding Laplace noise) and see what variance this yields.
# Facts needed:
#  MaclaurinSeries (for estimates)
#  Definition of differential privacy 
#    http://www.win-vector.com/blog/2015/10/a-simpler-explanation-of-differential-privacy/
#  CDF and variance of Laplace distribution as a function of parameter "b"
#    https://en.wikipedia.org/wiki/Laplace_distribution
[n,bInv,epsilon] =  sympy.symbols(['n','bInv','epsilon'])

def MaclaurinSeries(expr,var):
    f0 = sympy.simplify(expr.subs(var,0))
    if((len(f0.free_symbols)==0) and (abs(float(f0))<1.0e-10)):
        f0 = 0
    f1 = sympy.simplify(sympy.diff(expr,var).subs(var,0))
    if((len(f1.free_symbols)==0) and (abs(float(f1))<1.0e-10)):
        f1 = 0
    return f0 + var*f1

# Set1 (n zeros) has expected frequency 0, Set2 has expected frequency 1/n
# So advesary places a cutpoint between these at 1/2n to try and observe the difference.
# We work out how often advesary s a difference.
cutpoint = 1/(2*n)
mu1 = 0
# cutpoint > mu
LaplaceCDF1 = 1 - 0.5*sympy.exp(-bInv*(cutpoint-mu1))
mu2 = 1/n
# cutpoint < mu
LaplaceCDF2 = 0.5*sympy.exp(-bInv*(mu2-cutpoint))
logRat = sympy.log(LaplaceCDF1/LaplaceCDF2)
#print(logRat)
pError = MaclaurinSeries(logRat,bInv)
#print(pError)
b = 1/sympy.solve(pError-epsilon,bInv)[0]
#print(b)
variance = 2*b*b
print(variance)
```

    2/(epsilon**2*n**2)


Or we could look at the Laplace noise to the counts before they are returned (the method used in differential privacy). We want to see P[count(S1) + NoiseA > count(S0) + NoiseB ] - P[count(S0) + NoiseA > count(S0) + NoiseB ] (very roughly how much leaking is going on).  This simplifies to P[1 + NoiseA > Noise B] - P[NoiseA > NoiseB]. Or if z = P[NoiseA==NoiseB]: ( (1-z)/2 + z ) - ((1-z)/2) = z.  For the Laplace distribution with mean zero and variance 2 b^2 we have z = (1/(4 b^2)) sum_{x=-inf}^{+inf} e^(-x^2/b) (the sum of the PDF squared).  We want a b such that this is equal to epsilon.  And then variance is 2*b^2 / n^2 (after scaling by 1/n to convert counts to factions).  From the normal distribution we know sum_{x=-inf}^{+inf} e^(-x^2/b) is approximately sqrt(pi b).  So z ~ (1/(4 b^2)) sqrt(pi b) ~ epsilon.  So b ~ (pi / (16 epsilon^2))^(1/3).  Or variance = (pi/16)^(2/3) epsilon^(-4/3) n^(-2). 

Another method is bootstrapping.  It may establish some sort of indistinguishableness, but not differential privacy. has the disadvantage of only returning "indistinguishable" or "correct difference" (never returning a reversed order, which would help hide things).


```python
# Estimate the sample size needed to work an indistinguishability example 
# by Bootstrap methods, and the variance of that method.
#   facts from http://www.win-vector.com/blog/2015/10/a-simple-differentially-private-procedure/
[n,Z,epsilon] = sympy.symbols(['n','Z','epsilon'])
# we draw (with replacement) n/Z samples from a set of size n that has n-1 zeros and 1 one.
# Error if we draw the 1 one or more times (which would allow an advesary to see a differenece between this set and
# an all zeros set). 
# The expected number of 1s in the draw is (n/Z)*(1/n) = 1/Z
# By Markov's inequality this gives us pError <= 1/Z
pError = 1/Z
Z = sympy.solve(pError-epsilon,Z)[0]
#print(Z)
# The process of counting how many 1s show up in the Bootstrap (with replacement) 
# sample is Poisson with intensity equal to the mean.  The mean is 1/Z (above).
# So the count is a mean 1/Z variance 1/Z random variable.  We actually return
# frequency which is count/bootStrapSize = count/(n/Z).  Variance scales as a square
# so the new variance is (1/Z)/(n/Z)**2.  And we are done.
var = (1/Z)/(n/Z)**2
print(var)
```

    1/(epsilon*n**2)

