
.. code:: python

    from sympy import *
    import numpy
    from fractions import Fraction
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
    
    def printsoln(phis,soln):
       for phi in phis:
          if phi in soln:
             print '\t',phi,'\t',soln[phi]
    
    
    def printsolnN(phis,soln):
       ns = numericSoln(soln)
       for phi in phis:
          if phi in soln:
             print '\t',phi,'\t',soln[phi],'\t',ns[phi]
    
                
                
    # for k flips of unknown coin solve for minimal max variance estimate schedule
    def solveForK(k):
       p = symbols('p')
       print '*******************'
       print k
       phis = [ symbols(str('phi_'+str(h) + '_' + str(k))) for h in range(k+1) ]
       poly = sum([ p**h * (1-p)**(k-h) * ncr(k,h) * (phis[h]-p)**2 for h in range(k+1) ])
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
       return { str(k):ns[k] for k in ns.keys() }
    
    # solve numerically using Newton's zero finding method
    def solveForKN(k):
       print '*******************'
       print k
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
       printsoln(phis,nSoln)
       return nSoln

.. code:: python

    solveForK(1)

.. parsed-literal::

    *******************
    1
    	phi_0_1 	1/4 	0.25
    	phi_1_1 	3/4 	0.75
    0.0625
    *******************




.. parsed-literal::

    {'phi_0_1': 0.25, 'phi_1_1': 0.75}



.. code:: python

    solveForKN(1)

.. parsed-literal::

    *******************
    1
    	phi_0_1 	0.25
    	phi_1_1 	0.75




.. parsed-literal::

    {phi_0_1: 0.25, phi_1_1: 0.75}



.. code:: python

    solveForK(2)

.. parsed-literal::

    *******************
    2
    	phi_0_2 	-1/2 + sqrt(2)/2 	0.207106781187
    	phi_1_2 	1/2 	0.5
    	phi_2_2 	-sqrt(2)/2 + 3/2 	0.792893218813
    0.0428932188135
    *******************




.. parsed-literal::

    {'phi_0_2': 0.20710678118654752, 'phi_1_2': 0.5, 'phi_2_2': 0.7928932188134524}



.. code:: python

    solveForKN(2)

.. parsed-literal::

    *******************
    2
    	phi_0_2 	0.207106781187
    	phi_1_2 	0.5
    	phi_2_2 	0.792893218813




.. parsed-literal::

    {phi_2_2: 0.79289321881345221,
     phi_0_2: 0.20710678118654738,
     phi_1_2: 0.49999999999999983}



.. code:: python

    solveForK(3)

.. parsed-literal::

    *******************
    3
    	phi_0_3 	-1/4 + sqrt(3)/4 	0.183012701892
    	phi_1_3 	sqrt(3)/12 + 1/4 	0.394337567297
    	phi_2_3 	-sqrt(3)/12 + 3/4 	0.605662432703
    	phi_3_3 	-sqrt(3)/4 + 5/4 	0.816987298108
    0.0334936490539
    *******************




.. parsed-literal::

    {'phi_0_3': 0.18301270189221933,
     'phi_1_3': 0.39433756729740643,
     'phi_2_3': 0.6056624327025936,
     'phi_3_3': 0.8169872981077807}



.. code:: python

    solveForKN(3)

.. parsed-literal::

    *******************
    3
    	phi_0_3 	0.183012701892
    	phi_1_3 	0.394337567297
    	phi_2_3 	0.605662432703
    	phi_3_3 	0.816987298108




.. parsed-literal::

    {phi_3_3: 0.81698729810778192,
     phi_1_3: 0.39433756729740699,
     phi_2_3: 0.60566243270259434,
     phi_0_3: 0.18301270189221974}



.. code:: python

    solveForK(4)

.. parsed-literal::

    *******************
    4
    	phi_0_4 	1/6 	0.166666666667
    	phi_1_4 	1/3 	0.333333333333
    	phi_2_4 	1/2 	0.5
    	phi_3_4 	2/3 	0.666666666667
    	phi_4_4 	5/6 	0.833333333333
    0.0277777777778
    *******************




.. parsed-literal::

    {'phi_0_4': 0.16666666666666666,
     'phi_1_4': 0.3333333333333333,
     'phi_2_4': 0.5,
     'phi_3_4': 0.6666666666666666,
     'phi_4_4': 0.8333333333333334}



.. code:: python

    solveForKN(4)

.. parsed-literal::

    *******************
    4
    	phi_0_4 	0.166666666667
    	phi_1_4 	0.333333333333
    	phi_2_4 	0.5
    	phi_3_4 	0.666666666667
    	phi_4_4 	0.833333333333




.. parsed-literal::

    {phi_0_4: 0.16666666666666768,
     phi_2_4: 0.50000000000000111,
     phi_4_4: 0.83333333333333526,
     phi_1_4: 0.33333333333333431,
     phi_3_4: 0.66666666666666807}



.. code:: python

    for k in range(5,11):
        solveForKN(k)

.. parsed-literal::

    *******************
    5
    	phi_0_5 	0.154508497187
    	phi_1_5 	0.292705098312
    	phi_2_5 	0.430901699437
    	phi_3_5 	0.569098300562
    	phi_4_5 	0.707294901688
    	phi_5_5 	0.845491502813
    *******************
    6
    	phi_0_6 	0.144948974279
    	phi_1_6 	0.263299316186
    	phi_2_6 	0.381649658093
    	phi_3_6 	0.5
    	phi_4_6 	0.618350341907
    	phi_5_6 	0.736700683814
    	phi_6_6 	0.855051025721
    *******************
    7
    	phi_0_7 	0.137145942589
    	phi_1_7 	0.240818530421
    	phi_2_7 	0.344491118252
    	phi_3_7 	0.448163706084
    	phi_4_7 	0.551836293916
    	phi_5_7 	0.655508881748
    	phi_6_7 	0.759181469579
    	phi_7_7 	0.862854057411
    *******************
    8
    	phi_0_8 	0.130601937482
    	phi_1_8 	0.222951453111
    	phi_2_8 	0.315300968741
    	phi_3_8 	0.40765048437
    	phi_4_8 	0.5
    	phi_5_8 	0.592349515629
    	phi_6_8 	0.684699031259
    	phi_7_8 	0.777048546889
    	phi_8_8 	0.869398062518
    *******************
    9
    	phi_0_9 	0.125
    	phi_1_9 	0.208333333333
    	phi_2_9 	0.291666666667
    	phi_3_9 	0.375
    	phi_4_9 	0.458333333333
    	phi_5_9 	0.541666666667
    	phi_6_9 	0.625
    	phi_7_9 	0.708333333334
    	phi_8_9 	0.791666666667
    	phi_9_9 	0.875000000001
    *******************
    10
    	phi_0_10 	0.120126536676
    	phi_1_10 	0.196101229341
    	phi_2_10 	0.272075922005
    	phi_3_10 	0.34805061467
    	phi_4_10 	0.424025307335
    	phi_5_10 	0.499999999999
    	phi_6_10 	0.575974692664
    	phi_7_10 	0.651949385329
    	phi_8_10 	0.727924077993
    	phi_9_10 	0.803898770657
    	phi_10_10 	0.87987346332

