
.. code:: python

    from sympy import *
    import numpy
    from fractions import Fraction
    
    # from http://stackoverflow.com/questions/4941753/is-there-a-math-ncr-function-in-python
    import operator as op
    
    def ncr(n, r):
        r = min(r, n-r)
        if r == 0: return 1
        numer = reduce(op.mul, xrange(n, n-r, -1))
        denom = reduce(op.mul, xrange(1, r+1))
        return numer//denom
    
    def numericSoln(si):
        return { k:complex(si[k]).real for k in si.keys() }
    
    def isRealSoln(si):
        return all([abs(complex(sij).imag)<1.0e-5 for sij in si.values()])
    
    def printsoln(phis,soln):
       ns = numericSoln(soln)
       for phi in phis:
          if phi in soln:
             print '\t',phi,'\t',soln[phi],'\t',ns[phi]
    
    p = symbols('p')
    floatPoly = False
    powerTerms = True
    
    def solveForK(k):
       print '*******************'
       print k
       print 'powerTerms',powerTerms
       phis = [ symbols(str('phi_'+str(h) + '_' + str(k))) for h in range(k+1) ]
       if floatPoly:
          poly = sum([ p**h * (1.0-p)**(k-h) * float(ncr(k,h)) * (phis[h]-p)**2 for h in range(k+1) ])
       else:
          poly = sum([ p**h * (1-p)**(k-h) * ncr(k,h) * (phis[h]-p)**2 for h in range(k+1) ])
       # print poly
       if powerTerms:
         # powers of p
         polyTerms = collect(expand(poly),p,evaluate=False)
         eqns = [ polyTerms[p**(pow+1)] for pow in range(len(polyTerms)-1) ]
       else:
         # different evaluations
         p0 = poly.subs({p:0})
         if floatPoly:
            eqns = [ poly.subs({p:(i+1.0/k+1.0)})-p0 for i in range(k+1) ]
         else:
            eqns = [ poly.subs({p:(simplify(Fraction(i+1,k+1)))})-p0 for i in range(k+1) ]
       #print eqns
       soln1 = solve(eqns)
       #print soln1
       numSoln = [ numericSoln(si) for si in soln1 ]
       isReal = [ isRealSoln(si) for si in soln1 ]
       #print isReal
       costs = { i:abs(expand(poly.subs(numSoln[i]).subs({p:0}))) for i in range(len(numSoln)) if isReal[i] }
       #print costs
       minCost = min(costs.values())
       index = [ i for i in costs.keys() if costs[i] <= minCost ][0]
       soln = soln1[index]
       printsoln(phis,soln)
       print abs(complex(expand(poly.subs(soln).subs({p:0}))))
       print '*******************'
       return soln
.. code:: python

    solveForK(1)

.. parsed-literal::

    *******************
    1
    powerTerms True
    	phi_0_1 	1/4 	0.25
    	phi_1_1 	3/4 	0.75
    0.0625
    *******************




.. parsed-literal::

    {phi_0_1: 1/4, phi_1_1: 3/4}



.. code:: python

    solveForK(2)

.. parsed-literal::

    *******************
    2
    powerTerms True
    	phi_0_2 	-1/2 + sqrt(2)/2 	0.207106781187
    	phi_1_2 	1/2 	0.5
    	phi_2_2 	-sqrt(2)/2 + 3/2 	0.792893218813
    0.0428932188135
    *******************




.. parsed-literal::

    {phi_2_2: -sqrt(2)/2 + 3/2, phi_0_2: -1/2 + sqrt(2)/2, phi_1_2: 1/2}



.. code:: python

    solveForK(3)

.. parsed-literal::

    *******************
    3
    powerTerms True
    	phi_0_3 	-1/4 + sqrt(3)/4 	0.183012701892
    	phi_1_3 	sqrt(3)/12 + 1/4 	0.394337567297
    	phi_2_3 	-sqrt(3)/12 + 3/4 	0.605662432703
    	phi_3_3 	-sqrt(3)/4 + 5/4 	0.816987298108
    0.0334936490539
    *******************




.. parsed-literal::

    {phi_3_3: -sqrt(3)/4 + 5/4,
     phi_1_3: sqrt(3)/12 + 1/4,
     phi_2_3: -sqrt(3)/12 + 3/4,
     phi_0_3: -1/4 + sqrt(3)/4}



.. code:: python

    solveForK(4)

.. parsed-literal::

    *******************
    4
    powerTerms True
    	phi_0_4 	1/6 	0.166666666667
    	phi_1_4 	1/3 	0.333333333333
    	phi_2_4 	1/2 	0.5
    	phi_3_4 	2/3 	0.666666666667
    	phi_4_4 	5/6 	0.833333333333
    0.0277777777778
    *******************




.. parsed-literal::

    {phi_0_4: 1/6, phi_2_4: 1/2, phi_4_4: 5/6, phi_1_4: 1/3, phi_3_4: 2/3}


