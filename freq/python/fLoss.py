from sympy import *
import numpy

# from http://stackoverflow.com/questions/4941753/is-there-a-math-ncr-function-in-python
import operator as op

def ncr(n, r):
    r = min(r, n-r)
    if r == 0: return 1
    numer = reduce(op.mul, xrange(n, n-r, -1))
    denom = reduce(op.mul, xrange(1, r+1))
    return numer//denom

def realsoln(si):
   return all([ abs(complex(sij).imag)<1.e-6 for sij in si.values() ])

p = symbols('p')

for k in [ k+1 for k in range(4) ]:
   print '*******************'
   print k
   phis = [ symbols(str('phi_'+str(h) + '_' + str(k))) for h in range(k+1) ]
   poly = sum([ p**h * (1-p)**(k-h) * ncr(k,h) * (phis[h]-p)**2 for h in range(k+1) ])
   polyTerms = collect(expand(poly),p,evaluate=False)
   eqns = [ polyTerms[p**(pow+1)] for pow in range(len(polyTerms)-1) ]
   soln1 = solve(eqns)
   dcterm = polyTerms[p**0]
   costs = { i:float(expand(dcterm.subs(soln1[i]))) for i in range(len(soln1)) if realsoln(soln1[i]) }
   minCost = min(costs.values())
   index = [ i for i in costs.keys() if costs[i] <= minCost ][0]
   soln = soln1[index]
   print soln
   print float(expand(dcterm.subs(soln)))
   numsoln = { k:float(soln[k]) for k in soln.keys() }
   print numsoln
   print '*******************'



