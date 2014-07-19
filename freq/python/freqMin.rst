
.. code:: python

    import sympy
    import numpy
    import scipy
    import scipy.special
    import scipy.optimize
    import cvxopt
    
    
    def ncr(n, r):
        s = scipy.special.binom(n,r)
        return int(round(s)) # scipy special function return is not always an integer
    
    
    
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
       p = sympy.symbols('p')
       phis = [ sympy.symbols(str('phi_'+str(h) + '_' + str(k))) for h in range(k+1) ]
       poly = sum([ p**h * (1-p)**(k-h) * ncr(k,h) * (phis[h]-p)**2 for h in range(k+1) ])
       # print poly
       # powers of p
       polyTerms = sympy.collect(sympy.expand(poly),p,evaluate=False)
       eqns = [ polyTerms[p**(pow+1)] for pow in range(len(polyTerms)-1) ]
       #print eqns
       soln1 = sympy.solve(eqns)
       #print soln1
       numSoln = [ numericSoln(si) for si in soln1 ]
       viol = [ max([ abs(sympy.expand(eij.subs(si))) for eij in eqns ]) for si in numSoln ]
       isReal = [ isRealSoln(si) for si in soln1 ]
       costs = { i:abs(sympy.expand(poly.subs(numSoln[i]).subs({p:0}))) for i in range(len(numSoln)) if isReal[i] and viol[i]<1.0e-8 }
       #print costs
       minCost = min(costs.values())
       index = [ i for i in costs.keys() if costs[i] <= minCost ][0]
       soln = soln1[index]
       printsolnN(phis,soln)
       print 'loss',abs(complex(sympy.expand(poly.subs(soln).subs({p:0}))))
       # check if gradient is p-free (or even zero) at our fixed point
       for phi in phis:
            print 'd',phi,sympy.expand(sympy.diff(poly,p).subs(soln))
       print '*******************'
       ns = numericSoln(soln)
       return [ ns[phi] for phi in phis ]
    
    # solve numerically using Newton's zero finding method
    def solveForKN(k):
       p = sympy.symbols('p')
       phis = [ sympy.symbols(str('phi_'+str(h) + '_' + str(k))) for h in range(k+1) ]
       poly = sum([ p**h * (1-p)**(k-h) * ncr(k,h) * (phis[h]-p)**2 for h in range(k+1) ])
       # print poly
       # powers of p
       polyTerms = sympy.collect(sympy.expand(poly),p,evaluate=False)
       eqns = [ polyTerms[p**(pow+1)] for pow in range(len(polyTerms)-1) ]
       jacobian = [ [ sympy.diff(eqi,phij) for phij in phis ] for eqi in eqns ]
       nSoln = { phis[i]:((i+0.5)/(k+1.0)) for i in range(len(phis)) }
       while True:
          checks = numpy.array([ float(sympy.expand(ei.subs(nSoln))) for ei in eqns ])
          if max([abs(ci) for ci in checks])<1.0e-12:
             break
          js = numpy.matrix([ [ float(sympy.expand(jij.subs(nSoln))) for jij in ji ] for ji in jacobian ])
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
.. code:: python

    for k in range(1,11):
        print
        print 'l1 solution to dice game for k-rolls:',k
        print solveL1Problem(k,(1/6.0,2/6.0,3/6.0,4/6.0,5/6.0))
        print

.. parsed-literal::

    
    l1 solution to dice game for k-rolls: 1
         pcost       dcost       gap    pres   dres   k/t
     0:  0.0000e+00 -0.0000e+00  3e+00  3e+00  4e-17  1e+00
     1:  6.8365e-02  5.5415e-02  4e-01  4e-01  2e-16  1e-01
     2:  1.7186e-01  1.6067e-01  1e-01  9e-02  6e-16  2e-02
     3:  1.8929e-01  1.8708e-01  2e-02  2e-02  2e-16  4e-03
     4:  1.9966e-01  1.9935e-01  1e-03  1e-03  8e-16  1e-04
     5:  2.0000e-01  1.9999e-01  1e-05  1e-05  3e-16  1e-06
     6:  2.0000e-01  2.0000e-01  1e-07  1e-07  3e-16  1e-08
     7:  2.0000e-01  2.0000e-01  1e-09  1e-09  2e-16  1e-10
    Optimal solution found.
    [0.30000000025554363, 0.6999999997444563]
    
    
    l1 solution to dice game for k-rolls: 2
         pcost       dcost       gap    pres   dres   k/t
     0:  0.0000e+00  3.4694e-18  3e+00  3e+00  6e-17  1e+00
     1:  6.5039e-02  4.6507e-02  3e-01  3e-01  7e-17  1e-01
     2:  1.4330e-01  1.3491e-01  8e-02  7e-02  6e-16  2e-02
     3:  1.5546e-01  1.5396e-01  1e-02  1e-02  3e-16  2e-03
     4:  1.6152e-01  1.6147e-01  3e-04  3e-04  5e-16  4e-05
     5:  1.6162e-01  1.6161e-01  3e-06  3e-06  8e-16  4e-07
     6:  1.6162e-01  1.6162e-01  3e-08  3e-08  3e-16  4e-09
    Optimal solution found.
    [0.24242424302874568, 0.5000000000000001, 0.7575757569712543]
    
    
    l1 solution to dice game for k-rolls: 3
         pcost       dcost       gap    pres   dres   k/t
     0:  0.0000e+00 -0.0000e+00  3e+00  3e+00  2e-16  1e+00
     1:  6.2325e-02  3.9812e-02  3e-01  3e-01  2e-16  1e-01
     2:  1.3201e-01  1.2463e-01  5e-02  4e-02  4e-16  1e-02
     3:  1.4100e-01  1.3969e-01  9e-03  7e-03  2e-16  1e-03
     4:  1.4247e-01  1.4244e-01  2e-04  2e-04  1e-16  4e-05
     5:  1.4250e-01  1.4250e-01  2e-06  2e-06  3e-16  4e-07
     6:  1.4250e-01  1.4250e-01  2e-08  2e-08  2e-16  4e-09
    Optimal solution found.
    [0.2132637245687511, 0.405581333738664, 0.5944186662613359, 0.7867362754312489]
    
    
    l1 solution to dice game for k-rolls: 4
         pcost       dcost       gap    pres   dres   k/t
     0:  0.0000e+00 -0.0000e+00  3e+00  3e+00  2e-16  1e+00
     1:  6.0667e-02  3.5061e-02  3e-01  3e-01  4e-16  8e-02
     2:  1.1455e-01  1.0648e-01  6e-02  5e-02  3e-16  1e-02
     3:  1.1779e-01  1.1671e-01  8e-03  7e-03  2e-16  2e-03
     4:  1.1980e-01  1.1939e-01  3e-03  2e-03  2e-16  5e-04
     5:  1.2018e-01  1.2015e-01  1e-04  1e-04  6e-16  2e-05
     6:  1.2020e-01  1.2020e-01  1e-06  1e-06  3e-16  2e-07
     7:  1.2020e-01  1.2020e-01  1e-08  1e-08  7e-16  2e-09
    Optimal solution found.
    [0.18090056258036633, 0.33937246942223204, 0.4999999999999999, 0.6606275305777674, 0.8190994374196335]
    
    
    l1 solution to dice game for k-rolls: 5
         pcost       dcost       gap    pres   dres   k/t
     0:  0.0000e+00 -0.0000e+00  3e+00  3e+00  5e-17  1e+00
     1:  5.9402e-02  3.1387e-02  3e-01  2e-01  4e-17  7e-02
     2:  1.1087e-01  1.0344e-01  5e-02  4e-02  2e-16  9e-03
     3:  1.1615e-01  1.1552e-01  4e-03  3e-03  5e-16  7e-04
     4:  1.1723e-01  1.1721e-01  1e-04  1e-04  2e-16  2e-05
     5:  1.1726e-01  1.1726e-01  1e-06  1e-06  3e-16  2e-07
     6:  1.1726e-01  1.1726e-01  1e-08  1e-08  5e-16  2e-09
    Optimal solution found.
    [0.1666666679120836, 0.3136382568747281, 0.4388931407533864, 0.5611068592466137, 0.6863617431252721, 0.8333333320879167]
    
    
    l1 solution to dice game for k-rolls: 6
         pcost       dcost       gap    pres   dres   k/t
     0:  0.0000e+00 -0.0000e+00  3e+00  2e+00  6e-17  1e+00
     1:  5.7623e-02  2.8077e-02  3e-01  2e-01  3e-16  6e-02
     2:  1.0540e-01  9.8070e-02  4e-02  3e-02  2e-16  6e-03
     3:  1.0957e-01  1.0823e-01  7e-03  5e-03  6e-16  8e-04
     4:  1.0981e-01  1.0974e-01  3e-04  3e-04  5e-16  4e-05
     5:  1.0984e-01  1.0984e-01  2e-05  1e-05  6e-16  2e-06
     6:  1.0984e-01  1.0984e-01  2e-07  1e-07  5e-16  2e-08
     7:  1.0984e-01  1.0984e-01  2e-09  1e-09  5e-16  2e-10
    Optimal solution found.
    [0.16666666730865293, 0.2810765242229833, 0.3754580498073886, 0.5, 0.6245419501926115, 0.7189234757770168, 0.8333333326913472]
    
    
    l1 solution to dice game for k-rolls: 7
         pcost       dcost       gap    pres   dres   k/t
     0:  0.0000e+00 -3.4694e-18  3e+00  2e+00  2e-16  1e+00
     1:  5.6143e-02  2.5408e-02  3e-01  2e-01  2e-16  6e-02
     2:  9.7364e-02  8.8361e-02  6e-02  4e-02  3e-16  9e-03
     3:  1.0179e-01  1.0027e-01  9e-03  7e-03  7e-16  1e-03
     4:  1.0258e-01  1.0246e-01  7e-04  5e-04  5e-16  9e-05
     5:  1.0263e-01  1.0262e-01  2e-05  2e-05  4e-16  3e-06
     6:  1.0263e-01  1.0263e-01  9e-07  7e-07  4e-16  1e-07
     7:  1.0263e-01  1.0263e-01  9e-09  7e-09  5e-16  1e-09
    Optimal solution found.
    [0.16666667287996165, 0.25129079795016174, 0.3333333333253158, 0.4715996013407067, 0.5284003986592934, 0.6666666666746842, 0.7487092020498384, 0.8333333271200385]
    
    
    l1 solution to dice game for k-rolls: 8
         pcost       dcost       gap    pres   dres   k/t
     0:  0.0000e+00 -0.0000e+00  3e+00  2e+00  5e-17  1e+00
     1:  5.5087e-02  2.3295e-02  3e-01  2e-01  2e-16  5e-02
     2:  9.1334e-02  8.1445e-02  6e-02  5e-02  1e-16  1e-02
     3:  9.5502e-02  9.3153e-02  1e-02  1e-02  2e-16  2e-03
     4:  9.7543e-02  9.7053e-02  3e-03  2e-03  3e-16  4e-04
     5:  9.7710e-02  9.7684e-02  1e-04  1e-04  2e-16  2e-05
     6:  9.7726e-02  9.7725e-02  6e-06  5e-06  5e-16  8e-07
     7:  9.7727e-02  9.7727e-02  3e-07  2e-07  3e-16  4e-08
     8:  9.7727e-02  9.7727e-02  3e-09  2e-09  5e-16  4e-10
    Optimal solution found.
    [0.16666666883414585, 0.2167982497001821, 0.33333333372249996, 0.4063670201486247, 0.4999999999999999, 0.5936329798513751, 0.6666666662774997, 0.7832017502998178, 0.833333331165854]
    
    
    l1 solution to dice game for k-rolls: 9
         pcost       dcost       gap    pres   dres   k/t
     0:  0.0000e+00  5.5511e-16  1e+02  2e+00  1e+01  1e+00
     1:  9.7659e-01  8.9137e-01  8e+00  2e-01  1e+00  6e-03
     2:  2.6575e-01  2.5759e-01  5e-01  3e-02  2e-01  4e-03
     3:  1.1844e-01  1.1687e-01  1e-01  6e-03  3e-02  8e-04
     4:  9.2710e-02  9.2481e-02  1e-02  8e-04  5e-03  1e-04
     5:  9.0232e-02  9.0176e-02  3e-03  2e-04  1e-03  2e-05
     6:  8.9177e-02  8.9175e-02  9e-05  7e-06  4e-05  6e-07
     7:  8.9138e-02  8.9138e-02  2e-06  1e-07  7e-07  6e-09
     8:  8.9137e-02  8.9137e-02  2e-08  2e-09  1e-08  7e-11
    Optimal solution found.
    [0.16666666901939065, 0.17839485069204533, 0.3333333327163272, 0.3381984815899826, 0.4999999992904852, 0.500000000709515, 0.6618015184100173, 0.6666666672836729, 0.821605149307955, 0.8333333309806096]
    
    
    l1 solution to dice game for k-rolls: 10
         pcost       dcost       gap    pres   dres   k/t
     0:  0.0000e+00  2.2204e-16  2e+02  2e+00  2e+01  1e+00
     1:  1.0170e+00  9.2831e-01  9e+00  2e-01  1e+00  6e-03
     2:  2.8916e-01  2.7987e-01  7e-01  3e-02  2e-01  4e-03
     3:  1.2382e-01  1.2178e-01  1e-01  8e-03  5e-02  1e-03
     4:  9.4357e-02  9.3999e-02  2e-02  1e-03  8e-03  1e-04
     5:  8.8715e-02  8.8680e-02  2e-03  1e-04  7e-04  1e-05
     6:  8.8019e-02  8.8018e-02  4e-05  3e-06  2e-05  1e-07
     7:  8.7998e-02  8.7998e-02  7e-07  5e-08  3e-07  1e-09
     8:  8.7998e-02  8.7998e-02  9e-09  7e-10  4e-09  1e-11
    Optimal solution found.
    [0.16666666652773787, 0.1666666670780608, 0.3113782073030003, 0.3333333332017673, 0.43857086996118466, 0.4999999999999999, 0.561429130038815, 0.6666666667982325, 0.6886217926969996, 0.833333332921939, 0.833333333472262]
    


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
    loss 0.0428932188135
    d phi_0_2 0
    d phi_1_2 0
    d phi_2_2 0
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
    loss 0.0625
    d phi_0_1 0
    d phi_1_1 0
    *******************
    numeric l2 solution for k= 1
    [0.25, 0.75]
    
    
    analytic l2 solution for k= 2
    *******************
    2
    	phi_0_2 	-1/2 + sqrt(2)/2 	0.207106781187
    	phi_1_2 	1/2 	0.5
    	phi_2_2 	-sqrt(2)/2 + 3/2 	0.792893218813
    loss 0.0428932188135
    d phi_0_2 0
    d phi_1_2 0
    d phi_2_2 0
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
    loss 0.0334936490539
    d phi_0_3 0
    d phi_1_3 0
    d phi_2_3 0
    d phi_3_3 0
    *******************
    numeric l2 solution for k= 3
    [0.18301270189221974, 0.39433756729740699, 0.60566243270259423, 0.8169872981077817]
    
    
    analytic l2 solution for k= 4
    *******************
    4
    	phi_0_4 	1/6 	0.166666666667
    	phi_1_4 	1/3 	0.333333333333
    	phi_2_4 	1/2 	0.5
    	phi_3_4 	2/3 	0.666666666667
    	phi_4_4 	5/6 	0.833333333333
    loss 0.0277777777778
    d phi_0_4 0
    d phi_1_4 0
    d phi_2_4 0
    d phi_3_4 0
    d phi_4_4 0
    *******************
    numeric l2 solution for k= 4
    [0.16666666666666657, 0.33333333333333298, 0.49999999999999928, 0.66666666666666574, 0.83333333333333226]
    


.. code:: python

    for k in range(5,11):
        print 'numeric l2 solution for k=',k
        print solveForKN(k)

.. parsed-literal::

    numeric l2 solution for k= 5
    [0.15450849718749732, 0.29270509831249841, 0.43090169943749956, 0.56909830056250077, 0.70729490168750231, 0.84549150281250485]
    numeric l2 solution for k= 6
    [0.14494897427875081, 0.26329931618583163, 0.38164965809291207, 0.49999999999999173, 0.61835034190706983, 0.736700683814145, 0.85505102572121505]
    numeric l2 solution for k= 7
    [0.13714594258870808, 0.24081853042050227, 0.344491118252296, 0.44816370608408912, 0.55183629391588152, 0.65550888174767297, 0.75918146957946298, 0.86285405741124843]
    numeric l2 solution for k= 8
    [0.13060193748186366, 0.22295145311139491, 0.31530096874092589, 0.40765048437045631, 0.49999999999998584, 0.59234951562951332, 0.68469903125903675, 0.77704854688855263, 0.8693980625180614]
    numeric l2 solution for k= 9
    [0.12499999999993124, 0.20833333333325538, 0.29166666666657692, 0.37499999999989464, 0.45833333333320636, 0.54166666666650842, 0.62499999999979383, 0.70833333333304671, 0.79166666666622476, 0.87499999999922329]
    numeric l2 solution for k= 10
    [0.12012653667611538, 0.19610122934092272, 0.27207592200573305, 0.3480506146705476, 0.42402530733536842, 0.50000000000019862, 0.5759746926650432, 0.65194938532990943, 0.72792407799480374, 0.80389877065973081, 0.87987346332470762]

