
.. code:: python

    from sympy import *
    import numpy
    from fractions import Fraction
    import scipy
    import scipy.optimize
    import operator as op
    
    
    # ncr from http://stackoverflow.com/questions/4941753/is-there-a-math-ncr-function-in-python
    def ncr(n, r):
        r = min(r, n-r)
        if r == 0: return 1
        numer = reduce(op.mul, xrange(n, n-r, -1))
        denom = reduce(op.mul, xrange(1, r+1))
        return numer//denom
    
    
    
    def numericSoln(si):
        return { k:complex(si[k]).real for k in si.keys() }
    
    def isRealSoln(si):
        return all([abs(complex(sij).imag)<1.0e-6 for sij in si.values()])
    
    def printsolnN(phis,soln):
       ns = numericSoln(soln)
       for phi in phis:
          if phi in soln:
             print '\t',phi,'\t',soln[phi],'\t',ns[phi]
    
                
                
    # for k flips of unknown coin solve for minimal max variance estimate schedule
    def solveForK(k):
       print '*******************'
       print k
       p = symbols('p')
       phis = [ symbols(str('phi_'+str(h) + '_' + str(k))) for h in range(k+1) ]
       poly = sum([ p**h * (1-p)**(k-h) * int(ncr(k,h)) * (phis[h]-p)**2 for h in range(k+1) ])
       # print poly
       # powers of p
       polyTerms = collect(expand(poly),p,evaluate=False)
       eqns = [ polyTerms[p**(pow+1)] for pow in range(len(polyTerms)-1) ]
       #print eqns
       soln1 = solve(eqns)
       #print soln1
       numSoln = [ numericSoln(si) for si in soln1 ]
       viol = [ max([ abs(expand(eij.subs(si))) for eij in eqns ]) for si in numSoln ]
       isReal = [ isRealSoln(si) for si in soln1 ]
       costs = { i:abs(expand(poly.subs(numSoln[i]).subs({p:0}))) for i in range(len(numSoln)) if isReal[i] and viol[i]<1.0e-8 }
       #print costs
       minCost = min(costs.values())
       index = [ i for i in costs.keys() if costs[i] <= minCost ][0]
       soln = soln1[index]
       printsolnN(phis,soln)
       print abs(complex(expand(poly.subs(soln).subs({p:0}))))
       print '*******************'
       ns = numericSoln(soln)
       return [ ns[phi] for phi in phis ]
    
    # solve numerically using Newton's zero finding method
    def solveForKN(k):
       p = symbols('p')
       phis = [ symbols(str('phi_'+str(h) + '_' + str(k))) for h in range(k+1) ]
       poly = sum([ p**h * (1.0-p)**(k-h) * float(ncr(k,h)) * (phis[h]-p)**2 for h in range(k+1) ])
       # print poly
       # powers of p
       polyTerms = collect(expand(poly),p,evaluate=False)
       eqns = [ polyTerms[p**(pow+1)] for pow in range(len(polyTerms)-1) ]
       jacobian = [ [ diff(eqi,phij) for phij in phis ] for eqi in eqns ]
       nSoln = { phis[i]:((i+0.5)/(k+1.0)) for i in range(len(phis)) }
       while True:
          checks = numpy.array([ float(expand(ei.subs(nSoln))) for ei in eqns ])
          if max([abs(ci) for ci in checks])<1.0e-12:
             break
          js = numpy.matrix([ [ float(expand(jij.subs(nSoln))) for jij in ji ] for ji in jacobian ])
          step = numpy.linalg.solve(js,checks)
          nSoln = { phis[i]:(nSoln[phis[i]]-step[i]) for i in range(len(phis)) }
          if max([abs(si) for si in step])<1.0e-12:
             break
       return [ nSoln[phi] for phi in phis ]
    
                
    # approximate l1 loss
    def l1Loss(phis):
        nps = 10000
        k = len(phis)-1
        kchoose = [ float(ncr(k,h)) for h in range(k+1) ]
        pseq = [ pi/float(nps) for pi in range(nps+1) ]
        def f(p):
            if p<0 or p>1:
                return float('inf')
            return -sum([ p**h * (1.0-p)**(k-h) * kchoose[h] * abs(phis[h]-p) for h in range(k+1) ])
        reg = max([ -f(p) for p in pseq ])
        return reg
    
        
.. code:: python

    k=2
    print 'analytic l2 solution for k=',k
    nSoln = solveForK(k)
    print nSoln
    print 'approximate numeric l1 solution for k=',k
    initialLoss = l1Loss(nSoln)
    print 'initial l1 loss',initialLoss
    nSoln[1] = 0.55
    print nSoln
    adjLoss = l1Loss(nSoln)
    print 'adjusted l1 loss',adjLoss
    print 'difference',initialLoss-adjLoss


.. parsed-literal::

    analytic l2 solution for k= 2
    *******************
    2
    	phi_0_2 	-1/2 + sqrt(2)/2 	0.207106781187
    	phi_1_2 	1/2 	0.5
    	phi_2_2 	-sqrt(2)/2 + 3/2 	0.792893218813
    0.0428932188135
    *******************
    [0.20710678118654752, 0.5, 0.7928932188134524]
    approximate numeric l1 solution for k= 2
    initial l1 loss 0.207106781187
    [0.20710678118654752, 0.55, 0.7928932188134524]
    adjusted l1 loss 0.207106781187
    difference 0.0


.. code:: python

    for k in range(1,5):
        print
        print 'analytic l2 solution for k=',k
        solveForK(k)
        print 'numeric l2 solution for k=',k
        nSoln = solveForKN(k)
        print nSoln
        print

.. parsed-literal::

    
    analytic l2 solution for k= 1
    *******************
    1
    	phi_0_1 	1/4 	0.25
    	phi_1_1 	3/4 	0.75
    0.0625
    *******************
    numeric l2 solution for k= 1
    [0.25, 0.75]
    
    
    analytic l2 solution for k= 2
    *******************
    2
    	phi_0_2 	-1/2 + sqrt(2)/2 	0.207106781187
    	phi_1_2 	1/2 	0.5
    	phi_2_2 	-sqrt(2)/2 + 3/2 	0.792893218813
    0.0428932188135
    *******************
    numeric l2 solution for k= 2
    [0.20710678118654738, 0.49999999999999983, 0.79289321881345221]
    
    
    analytic l2 solution for k= 3
    *******************
    3
    	phi_0_3 	-1/4 + sqrt(3)/4 	0.183012701892
    	phi_1_3 	sqrt(3)/12 + 1/4 	0.394337567297
    	phi_2_3 	-sqrt(3)/12 + 3/4 	0.605662432703
    	phi_3_3 	-sqrt(3)/4 + 5/4 	0.816987298108
    0.0334936490539
    *******************
    numeric l2 solution for k= 3
    [0.18301270189221974, 0.39433756729740699, 0.60566243270259434, 0.81698729810778192]
    
    
    analytic l2 solution for k= 4
    *******************
    4
    	phi_0_4 	1/6 	0.166666666667
    	phi_1_4 	1/3 	0.333333333333
    	phi_2_4 	1/2 	0.5
    	phi_3_4 	2/3 	0.666666666667
    	phi_4_4 	5/6 	0.833333333333
    0.0277777777778
    *******************
    numeric l2 solution for k= 4
    [0.16666666666666768, 0.33333333333333431, 0.50000000000000111, 0.66666666666666807, 0.83333333333333526]
    


.. code:: python

    for k in range(5,11):
        print 'numeric l2 solution for k=',k
        print solveForKN(k)

.. parsed-literal::

    numeric l2 solution for k= 5
    [0.15450849718749685, 0.29270509831249786, 0.43090169943749879, 0.56909830056249966, 0.70729490168750031, 0.84549150281250052]
    numeric l2 solution for k= 6
    [0.14494897427875741, 0.26329931618583946, 0.38164965809292156, 0.500000000000004, 0.61835034190708682, 0.73670068381417098, 0.85505102572125735]
    numeric l2 solution for k= 7
    [0.13714594258870841, 0.24081853042050264, 0.34449111825229645, 0.44816370608408934, 0.55183629391588074, 0.65550888174766897, 0.75918146957945176, 0.86285405741122756]
    numeric l2 solution for k= 8
    [0.1306019374818575, 0.22295145311138789, 0.31530096874091768, 0.40765048437044638, 0.49999999999997313, 0.59234951562949656, 0.68469903125901432, 0.77704854688852543, 0.86939806251803797]
    numeric l2 solution for k= 9
    [0.12500000000008105, 0.20833333333342519, 0.29166666666677243, 0.37500000000012412, 0.45833333333348275, 0.5416666666668527, 0.62500000000024392, 0.70833333333367521, 0.79166666666717644, 0.87500000000077582]
    numeric l2 solution for k= 10
    [0.12012653667575041, 0.19610122934051302, 0.27207592200526709, 0.34805061467000892, 0.42402530733473265, 0.4999999999994279, 0.57597469266407486, 0.65194938532863334, 0.72792407799301684, 0.80389877065702275, 0.87987346332016558]

