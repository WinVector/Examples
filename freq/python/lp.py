import cvxopt
import sympy
import numpy
import scipy
import scipy.special
import scipy.optimize


def ncr(n, r):
    s = scipy.special.binom(n,r)
    return int(round(s)) # scipy special function return is not always an integer



# Pick set of estimates (indexed by evidence) minimizing worse L1 loss expected for any p
# k: number of flips
# p: array of probabilities to check against
def solveL1Problem(k,p):
   nphis = k+1
   nps = len(p)
   # solve a x <= b 
   # varibles: 
   #  phi (indices: 0 ... nphis-1)
   #  u (indices: nphis ... (1+nps)*nphis-1) 
   #   u(i,j) = var((i+1)*nphis+j) = abs(phi(j)-p(i)) i=0...nps-1, j=0...nphis-1
   #  s (index: (1+nps)*nphis )
   # eqns: 
   #  u(i,j) >= phi(j) - p(i)
   #  u(i,j) >= -(phi(j) - p(i))
   #  s >= sum_{j=0}^{k} (k choose j) p(i)^j (1-p(i))^{k-j} u(i,j)
   nvars = (1+nps)*nphis+1
   sindex = (1+nps)*nphis
   a = []
   b = []
   c = numpy.zeros(nvars)
   c[sindex] = 1.0
   for i in range(nps):
      arow = numpy.zeros(nvars)
      brow = 0.0
      # TODO: put poly coefs in terms of u's here
      arow[sindex] = -1.0
      for j in range(nphis):
         uindex = (i+1)*nphis+j
         arow[uindex] = ncr(k,j) * p[i]**j * (1-p[i])**(k-j)
      a.append(arow)
      b.append(brow)
      for j in range(nphis):
         uindex = (i+1)*nphis+j
         phiindex = j
         # u(i,j) >= phi(j) - p(i) : phi(j) - u(i,j) <= p(i)
         arow = numpy.zeros(nvars)
         arow[phiindex] = 1.0
         arow[uindex] = -1.0 
         brow = p[i]
         a.append(arow)
         b.append(brow)
         # u(i,j) >= -(phi(j) - p(i)) : -phi(j) - u(i,j) <= -p(i)
         arow = numpy.zeros(nvars)
         arow[phiindex] = -1.0
         arow[uindex] = -1.0 
         brow = -p[i]
         a.append(arow)
         b.append(brow)
   cmat = cvxopt.matrix(c)
   gmat = cvxopt.matrix(numpy.matrix(a))
   hmat = cvxopt.matrix(b)
   sol = cvxopt.solvers.lp(cmat,gmat,hmat) # solve gmax * x <= hmat minimizing cmat
   return [ sol['x'][i] for i in range(nphis) ]


print solveL1Problem(1,(1/6.0,2/6.0,3/6.0,4/6.0,5/6.0))
