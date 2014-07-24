
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
        if not all([abs(complex(sij).imag)<1.0e-6 for sij in si.values()]):
            return False
        ns = numericSoln(si)
        return all([ nij>=0 and nij<=1.0 for nij in ns.values()])
    
    def printsolnN(phis,soln):
       ns = numericSoln(soln)
       for phi in phis:
          if phi in soln:
             print '\t',phi,'\t',soln[phi],'\t',ns[phi]
    
    
    # build equations to make polynomial p-free
    def prepareClearingEqns(p,phis,poly):
       polyTerms = sympy.collect(sympy.expand(poly),p,evaluate=False)
       eqns = [ polyTerms[k] for k in polyTerms.keys() if (not k==1) ]
       return eqns
    
    # crude numeric check of signs of poly
    def checkForSignsIn01(p,poly):
        sawPlus = False
        sawMinus = False
        scale = 20
        for i in range(scale+1):
           y = float(sympy.expand(poly.subs({p:i/float(scale)})))
           if y>0:
              sawPlus = True
           if y<0:
              sawMinus = True
           if sawPlus and sawMinus:
              break
        return ('+' if sawPlus else '') + ('-' if sawMinus else '')
    
    explicitGradientClearingEqns = False
    
    # for k flips of unknown coin solve for minimal max variance estimate schedule
    def solveForK(k):
       print '*******************'
       print k
       p = sympy.symbols('p')
       phis = [ sympy.symbols(str('phi_'+str(h) + '_' + str(k))) for h in range(k+1) ]
       poly = sum([ p**h * (1-p)**(k-h) * ncr(k,h) * (phis[h]-p)**2 for h in range(k+1) ])
       eqns = []
       if explicitGradientClearingEqns:
           for phi in phis:
               eqns.extend(prepareClearingEqns(p,phis,sympy.diff(poly,phi)))
       else:
            eqns = prepareClearingEqns(p,phis,poly)
       soln1 = sympy.solve(eqns,phis)
       soln1 = [ { phis[j]:si[j] for j in range(len(phis))} for si in soln1 ]
       numSoln = [ numericSoln(si) for si in soln1 ]
       viol = [ max([ abs(sympy.expand(eij.subs(si))) for eij in eqns ]) for si in numSoln ]
       isReal = [ isRealSoln(si) for si in soln1 ]
       costs = { i:abs(sympy.expand(poly.subs(numSoln[i]).subs({p:0}))) for i in range(len(numSoln)) if isReal[i] and viol[i]<1.0e-8 }
       print costs
       minCost = min(costs.values())
       index = [ i for i in costs.keys() if costs[i] <= minCost ][0]
       soln = soln1[index]
       printsolnN(phis,soln)
       print 'loss',abs(complex(sympy.expand(poly.subs(soln).subs({p:0}))))
       # check if gradient is p-free (or even zero) at our fixed point
       checks = []
       for phi in phis:
            checki = sympy.expand(sympy.diff(poly,phi).subs(soln))
            print 'd',phi,checki,checkForSignsIn01(p,checki)
            checks.append(checki)
       print sympy.solve(checks,p)
       print '*******************'
       ns = numericSoln(soln)
       return [ ns[phi] for phi in phis ]
    
    # solve numerically using Newton's zero finding method
    def solveForKN(k):
       p = sympy.symbols('p')
       phis = [ sympy.symbols(str('phi_'+str(h) + '_' + str(k))) for h in range(k+1) ]
       poly = sum([ p**h * (1-p)**(k-h) * ncr(k,h) * (phis[h]-p)**2 for h in range(k+1) ])
       eqns = prepareClearingEqns(p,phis,poly)
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
    
    
    # approximate l1 loss for using phis as our estimate when prob is one of pseq
    def l1Loss(phis,pseq=[ pi/float(1000) for pi in range(1001) ]):
        k = len(phis)-1
        kchoose = [ float(ncr(k,h)) for h in range(k+1) ]
        def f(p):
            if p<0 or p>1:
                return float('inf')
            return sum([ p**h * (1.0-p)**(k-h) * kchoose[h] * abs(phis[h]-p) for h in range(k+1) ])
        reg = max([ f(p) for p in pseq ])
        return reg
    
    # approximate l1 loss for using phis as our estimate when prob is one of pseq
    def l2Loss(phis,pseq):
        k = len(phis)-1
        kchoose = [ float(ncr(k,h)) for h in range(k+1) ]
        def f(p):
            if p<0 or p>1:
                return float('inf')
            return sum([ p**h * (1.0-p)**(k-h) * kchoose[h] * (phis[h]-p)**2 for h in range(k+1) ])
        reg = max([ f(p) for p in pseq ])
        return reg
    
    def solveL2Problem(k,pseq):
        start = solveForKN(k)
        def f(x):
            if not all([ p>=0 and p<=1 for p in x]):
                return float('inf')
            return l2Loss(x,pseq)
        opt = scipy.optimize.minimize(f,start,method='Powell')
        return opt['x']
    
    # Solve argmin_phi max_i sum_{j=0}^{k} (k choose j) p(i)^j (1-p(i))^{k-j} | p(i) - phi(j) |
    # Pick set of estimates (indexed by evidence) minimizing worse L1 loss expected for any p
    # k: number of flips
    # p: array of probabilities to check against
    def solveL1Problem(k,p):
       nphis = k+1
       nps = len(p)
       # encode argmin_phi max_i sum_{j=0}^{k} (k choose j) p(i)^j (1-p(i))^{k-j} | p(i) - phi(j) |
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
       cvxopt.solvers.options['show_progress'] = False
       sol = cvxopt.solvers.lp(cmat,gmat,hmat) # solve gmax * x <= hmat minimizing cmat
       return [ sol['x'][i] for i in range(nphis) ]
    
    # l1 cost on known ps
    def l1Cost(phis,ps):
        k = len(phis)-1
        choose = [ ncr(k,j) for j in range(len(phis)) ]
        def f(p):
            return sum([ choose[j] *  p**j * (1.0-p)**(k-j) * abs(phis[j]-p) for j in range(len(phis)) ])
        return max([ f(p) for p in ps ])
            
    # solve argmax_p sum_{j=0}^{k} (k choose j) p^j (1-p)^{k-j} | p - phi(j) | for 0<=p<=1
    def worstL1p(phis):
        k = len(phis)-1
        choose = [ ncr(k,j) for j in range(len(phis)) ]
        def f(p):
            return -sum([ choose[j] * p**j * (1-p)**(k-j) * abs(phis[j]-p) for j in range(len(phis)) ])
        cuts = set([0.0,1.0])
        for phi in phis:
            if phi>0.0 and phi<1.0:
                cuts.add(phi)
        cuts = sorted(cuts)
        optX = None
        optF = None
        for i in range(len(cuts)-1):
           opti = scipy.optimize.minimize_scalar(f,bounds=(cuts[i],cuts[i+1]),method='Bounded')
           xi = opti['x']
           fi = -f(xi)
           if (optX is None) or (fi>optF):
                optX = xi
                optF = fi
        return optX
    
    # solve L1 problem over 0<=p<=1 using crude column generation method
    def solveL1ProblemByCuts(k):
       ps = [0.0,0.5,1.0]
       done = False
       while not done:
          phis = solveL1Problem(k,ps)
          # print phis
          cost1 = l1Cost(phis,ps)
          newP = worstL1p(phis)
          ps.append(newP)
          cost2 = l1Cost(phis,ps)
          # print 'cost1,cost2',cost1,cost2
          if not cost1+1.0e-8<cost2:
             done = True
       return phis
    
                
    # Build the Bayes estimate of expected values from uniform priors
    # on the unknown probability pWin in the set phis
    # seen in kFlips trials
    def bayesMeansEstimates(phis,priors,kFlips):
      nphis = len(phis)
      if priors is None:
         priors = numpy.ones(nphis)
      else:
         priors = numpy.array(priors)
      priors = priors/sum(priors)
      e = numpy.zeros(kFlips+1)
      for winsSeen in range(kFlips+1):
        posteriorProbs = numpy.zeros(nphis)
        for i in range(nphis):
          pWin = phis[i]
          posteriorProbs[i] = priors[i]*ncr(kFlips,winsSeen) * \
             pWin**winsSeen * (1-pWin)**(kFlips-winsSeen)
        posteriorProbs = posteriorProbs/sum(posteriorProbs)
        e[winsSeen] = sum(posteriorProbs*phis)
      return numpy.array(e)

.. code:: python

    # crude column generation solution
    
    for k in range(1,11):
        print
        print 'l1 solution to dice game for k-rolls:',k
        phis = solveL1ProblemByCuts(k)
        print 'phis',phis
        print

.. parsed-literal::

    
    l1 solution to dice game for k-rolls: 1
    phis [0.24999999945491402, 0.7500000005450859]
    
    
    l1 solution to dice game for k-rolls: 2
    phis [0.19160259253220915, 0.5000000066330934, 0.808397407210937]
    
    
    l1 solution to dice game for k-rolls: 3
    phis [0.16204791073717284, 0.39658683603890227, 0.6034131780361844, 0.8379520868680799]
    
    
    l1 solution to dice game for k-rolls: 4
    phis [0.1437480499665423, 0.33414661331872003, 0.5000000108084859, 0.6658533974417459, 0.8562519506864422]
    
    
    l1 solution to dice game for k-rolls: 5
    phis [0.13098490336276158, 0.2920833484409374, 0.4312839950164908, 0.5687160143766172, 0.7079166382343058, 0.8690150967731374]
    
    
    l1 solution to dice game for k-rolls: 6
    phis [0.12142009485229471, 0.2614791473652508, 0.381968919790032, 0.5000000013880771, 0.6180310808444995, 0.7385208401419168, 0.8785799047877464]
    
    
    l1 solution to dice game for k-rolls: 7
    phis [0.11389668220373642, 0.23800677135528683, 0.34455955305729236, 0.4484262174837331, 0.5515737795175774, 0.6554404386257229, 0.761993226542064, 0.8861033175135918]
    
    
    l1 solution to dice game for k-rolls: 8
    phis [0.10776815910577336, 0.21931788597075733, 0.3150231044641331, 0.40802482807595886, 0.5000000178264737, 0.5919751551011433, 0.6849768906352142, 0.7806821441202999, 0.8922318393100427]
    
    
    l1 solution to dice game for k-rolls: 9
    phis [0.10264212621699102, 0.20401368743209025, 0.29100220820592976, 0.37535486781436966, 0.45856319881937446, 0.5414368060381072, 0.6246451289384446, 0.708997795691393, 0.7959863249607008, 0.8973578740006296]
    
    
    l1 solution to dice game for k-rolls: 10
    phis [0.098265268762728, 0.1912031284733685, 0.2710157596937475, 0.34829222852616387, 0.4243922542801517, 0.5000000411954196, 0.5756077287713842, 0.6517077467601304, 0.728984249803712, 0.808796889221568, 0.9017347317099305]
    


.. code:: python

    for k in range(1,11):
        print
        print 'l1 solution to dice game for k-rolls:',k
        print solveL1Problem(k,(1/6.0,2/6.0,3/6.0,4/6.0,5/6.0))
        print

.. parsed-literal::

    
    l1 solution to dice game for k-rolls: 1
    [0.30000000025554363, 0.6999999997444564]
    
    
    l1 solution to dice game for k-rolls: 2
    [0.24242424302874574, 0.5000000000000002, 0.7575757569712546]
    
    
    l1 solution to dice game for k-rolls: 3
    [0.21326372456875112, 0.4055813337386642, 0.5944186662613361, 0.7867362754312492]
    
    
    l1 solution to dice game for k-rolls: 4
    [0.18090056258036644, 0.3393724694222323, 0.5000000000000001, 0.6606275305777679, 0.8190994374196339]
    
    
    l1 solution to dice game for k-rolls: 5
    [0.16666666791208357, 0.313638256874728, 0.4388931407533864, 0.5611068592466135, 0.686361743125272, 0.8333333320879165]
    
    
    l1 solution to dice game for k-rolls: 6
    [0.16666666730865295, 0.2810765242229833, 0.3754580498073887, 0.5000000000000001, 0.6245419501926115, 0.7189234757770169, 0.8333333326913474]
    
    
    l1 solution to dice game for k-rolls: 7
    [0.16666667287996165, 0.25129079795016174, 0.3333333333253158, 0.4715996013407066, 0.5284003986592933, 0.6666666666746843, 0.7487092020498383, 0.8333333271200385]
    
    
    l1 solution to dice game for k-rolls: 8
    [0.16666666883414594, 0.21679824970018224, 0.33333333372250007, 0.40636702014862486, 0.5000000000000002, 0.5936329798513754, 0.6666666662775, 0.7832017502998184, 0.8333333311658545]
    
    
    l1 solution to dice game for k-rolls: 9
    [0.16666666901939056, 0.17839485069204533, 0.3333333327163271, 0.3381984815899825, 0.49999999929048483, 0.5000000007095147, 0.6618015184100171, 0.6666666672836725, 0.8216051493079544, 0.8333333309806091]
    
    
    l1 solution to dice game for k-rolls: 10
    [0.1666666665277379, 0.1666666670780608, 0.31137820730300036, 0.33333333320176733, 0.43857086996118483, 0.49999999999999994, 0.5614291300388151, 0.6666666667982325, 0.6886217926969995, 0.833333332921939, 0.833333333472262]
    


.. code:: python

    for k in range(1,11):
        print
        print 'l1 solution to dice game for k-rolls:',k
        print solveL1Problem(k,(0.0,1/6.0,2/6.0,3/6.0,4/6.0,5/6.0,1.0))
        print

.. parsed-literal::

    
    l1 solution to dice game for k-rolls: 1
    [0.24999999853385094, 0.7500000014661489]
    
    
    l1 solution to dice game for k-rolls: 2
    [0.19047619124888182, 0.49999999999999994, 0.8095238087511182]
    
    
    l1 solution to dice game for k-rolls: 3
    [0.15942028957279653, 0.40096618707100723, 0.5990338129289925, 0.8405797104272034]
    
    
    l1 solution to dice game for k-rolls: 4
    [0.12938596398639352, 0.33388157302807536, 0.5, 0.6661184269719247, 0.8706140360136065]
    
    
    l1 solution to dice game for k-rolls: 5
    [0.12703422407959558, 0.29969912001362736, 0.43419229359646666, 0.5658077064035332, 0.7003008799863724, 0.8729657759204041]
    
    
    l1 solution to dice game for k-rolls: 6
    [0.1177319181084499, 0.26291915433968766, 0.3691554524108885, 0.4999999999999999, 0.6308445475891111, 0.7370808456603123, 0.88226808189155]
    
    
    l1 solution to dice game for k-rolls: 7
    [0.10966835454129048, 0.22969219064568033, 0.3333333329765895, 0.4646774792892003, 0.5353225207107996, 0.6666666670234105, 0.7703078093543196, 0.8903316454587094]
    
    
    l1 solution to dice game for k-rolls: 8
    [0.10274348658975836, 0.19215456358040856, 0.3333333327777123, 0.3995628622843814, 0.4999999999999999, 0.6004371377156181, 0.6666666672222875, 0.8078454364195915, 0.8972565134102415]
    
    
    l1 solution to dice game for k-rolls: 9
    [0.0944265249343173, 0.1666666668526303, 0.3192592679376938, 0.3333333332932396, 0.4979289642365647, 0.5020710357634353, 0.6666666667067602, 0.680740732062306, 0.8333333331473697, 0.9055734750656828]
    
    
    l1 solution to dice game for k-rolls: 10
    [0.09281162245587529, 0.16666666708620176, 0.28805014521964334, 0.3333333332684214, 0.43218436047564174, 0.5000000000000001, 0.5678156395243583, 0.6666666667315787, 0.7119498547803568, 0.8333333329137985, 0.9071883775441248]
    


.. code:: python

    for k in range(1,11):
        print
        print 'l1 solution to dice game for k-rolls:',k
        print solveL1Problem(k,(0.0,0.5,1.0))
        print

.. parsed-literal::

    
    l1 solution to dice game for k-rolls: 1
    [0.24999999945491402, 0.7500000005450859]
    
    
    l1 solution to dice game for k-rolls: 2
    [0.1666666568485795, 0.5000000000000001, 0.8333333431514207]
    
    
    l1 solution to dice game for k-rolls: 3
    [0.09999999969515637, 0.5000000000000001, 0.5000000000000001, 0.9000000003048437]
    
    
    l1 solution to dice game for k-rolls: 4
    [0.05555552934981534, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.9444444706501847]
    
    
    l1 solution to dice game for k-rolls: 5
    [0.02941168066781756, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.9705883193321826]
    
    
    l1 solution to dice game for k-rolls: 6
    [0.015151464835256744, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.9848485351647435]
    
    
    l1 solution to dice game for k-rolls: 7
    [0.007692283124038655, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.9923077168759615]
    
    
    l1 solution to dice game for k-rolls: 8
    [0.003875857178041267, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.996124142821959]
    
    
    l1 solution to dice game for k-rolls: 9
    [0.0019448294819158865, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.9980551705180841]
    
    
    l1 solution to dice game for k-rolls: 10
    [0.0009745043896464365, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.9990254956103537]
    


.. code:: python

    pTrue = (0.0,0.5,1.0)
    for k in range(1,11):
        print
        print 'uniform Bayes solution to coingame (all-heads, fair, or all-tails):',k
        bmSoln = bayesMeansEstimates(pTrue,None,k)
        print bmSoln
        print 'l1 solution to coingame (all-heads, fair, or all-tails):',k
        l1Soln = solveL1Problem(k,pTrue)
        print 'l1Soln',l1Soln
        print 'l1 loss',l1Loss(l1Soln,pTrue)
        print 'l2 loss',l2Loss(l1Soln,pTrue)
        def eP(z):
             return bayesMeansEstimates(pTrue,(z, 1-2.0*z, z ),k)[0] - l1Soln[0]
        z = scipy.optimize.brentq(eP,0.0,0.5)
        effectivePriors = (z, 1-2.0*z, z)
        print 'effective priors l1',effectivePriors
        print 'Bayes check l1',bayesMeansEstimates(pTrue,effectivePriors,k)
        l2Soln = solveL2Problem(k,pTrue)
        print 'l2Soln',l2Soln
        print 'l1 loss',l1Loss(l2Soln,pTrue)
        print 'l2 loss',l2Loss(l2Soln,pTrue)
        def gP(z):
             return bayesMeansEstimates(pTrue,(z, 1-2.0*z, z ),k)[0] - l2Soln[0]
        z = scipy.optimize.brentq(gP,0.0,0.5)
        effectivePriors2 = (z, 1-2.0*z, z)
        print 'effective priors l2',effectivePriors2
        print 'Bayes check l2',bayesMeansEstimates(pTrue,effectivePriors2,k)


.. parsed-literal::

    
    uniform Bayes solution to coingame (all-heads, fair, or all-tails): 1
    [ 0.16666667  0.83333333]
    l1 solution to coingame (all-heads, fair, or all-tails): 1
    l1Soln [0.24999999945491402, 0.7500000005450859]
    l1 loss 0.250000000545
    l2 loss 0.0625000002725
    effective priors l1 (0.250000000545086, 0.49999999890982805, 0.250000000545086)
    Bayes check l1 [ 0.25  0.75]
    l2Soln [ 0.25  0.75]
    l1 loss 0.25
    l2 loss 0.0625
    effective priors l2 (0.25, 0.5, 0.25)
    Bayes check l2 [ 0.25  0.75]
    
    uniform Bayes solution to coingame (all-heads, fair, or all-tails): 2
    [ 0.1  0.5  0.9]
    l1 solution to coingame (all-heads, fair, or all-tails): 2
    l1Soln [0.1666666568485795, 0.5000000000000001, 0.8333333431514207]
    l1 loss 0.166666671576
    l2 loss 0.0555555588283
    effective priors l1 (0.25000001104535186, 0.4999999779092963, 0.25000001104535186)
    Bayes check l1 [ 0.16666666  0.5         0.83333334]
    l2Soln [ 0.20710678  0.5         0.79289322]
    l1 loss 0.207106781187
    l2 loss 0.0428932188135
    effective priors l2 (0.2071067811865605, 0.585786437626879, 0.2071067811865605)
    Bayes check l2 [ 0.20710678  0.5         0.79289322]
    
    uniform Bayes solution to coingame (all-heads, fair, or all-tails): 3
    [ 0.05555556  0.5         0.5         0.94444444]
    l1 solution to coingame (all-heads, fair, or all-tails): 3
    l1Soln [0.09999999969515637, 0.5000000000000001, 0.5000000000000001, 0.9000000003048437]
    l1 loss 0.100000000076
    l2 loss 0.040000000061
    effective priors l1 (0.25000000047631815, 0.4999999990473637, 0.25000000047631815)
    Bayes check l1 [ 0.1  0.5  0.5  0.9]
    l2Soln [ 0.1830127   0.39433757  0.60566243  0.8169873 ]
    l1 loss 0.183012701892
    l2 loss 0.0334936490539
    effective priors l2 (0.1510847396257868, 0.6978305207484263, 0.1510847396257868)
    Bayes check l2 [ 0.1830127  0.5        0.5        0.8169873]
    
    uniform Bayes solution to coingame (all-heads, fair, or all-tails): 4
    [ 0.02941176  0.5         0.5         0.5         0.97058824]
    l1 solution to coingame (all-heads, fair, or all-tails): 4
    l1Soln [0.05555552934981534, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.9444444706501847]
    l1 loss 0.0555555588313
    l2 loss 0.0246913609364
    effective priors l1 (0.2500000663328986, 0.49999986733420276, 0.2500000663328986)
    Bayes check l1 [ 0.05555553  0.5         0.5         0.5         0.94444447]
    l2Soln [ 0.16666667  0.33333333  0.49999803  0.43466401  0.87277898]
    l1 loss 0.166666666667
    l2 loss 0.0277777777778
    effective priors l2 (0.10000000000011512, 0.7999999999997698, 0.10000000000011512)
    Bayes check l2 [ 0.16666667  0.5         0.5         0.5         0.83333333]
    
    uniform Bayes solution to coingame (all-heads, fair, or all-tails): 5
    [ 0.01515152  0.5         0.5         0.5         0.5         0.98484848]
    l1 solution to coingame (all-heads, fair, or all-tails): 5
    l1Soln [0.02941168066781756, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.9705883193321826]
    l1 loss 0.0294117699583
    l2 loss 0.0138408353932
    effective priors l1 (0.2500003794849061, 0.4999992410301878, 0.2500003794849061)
    Bayes check l1 [ 0.02941168  0.5         0.5         0.5         0.5         0.97058832]
    l2Soln [ 0.1545085   0.2927051   0.4309017   0.50118994  0.47529225  0.8454915 ]
    l1 loss 0.154508497187
    l2 loss 0.0238728757031
    effective priors l2 (0.06130893952188311, 0.8773821209562338, 0.06130893952188311)
    Bayes check l2 [ 0.1545085  0.5        0.5        0.5        0.5        0.8454915]
    
    uniform Bayes solution to coingame (all-heads, fair, or all-tails): 6
    [ 0.00769231  0.5         0.5         0.5         0.5         0.5
      0.99230769]
    l1 solution to coingame (all-heads, fair, or all-tails): 6
    l1Soln [0.015151464835256744, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.9848485351647435]
    l1 loss 0.0151515167239
    l2 loss 0.00734619068911
    effective priors l1 (0.25000042808198086, 0.4999991438360383, 0.25000042808198086)
    Bayes check l1 [ 0.01515146  0.5         0.5         0.5         0.5         0.5
      0.98484854]
    l2Soln [ 0.14494897  0.26329932  0.38164966  0.49999782  0.38634769  0.50469803
      0.92877359]
    l1 loss 0.144948974262
    l2 loss 0.0210102051397
    effective priors l2 (0.03555190165993658, 0.9288961966801268, 0.03555190165993658)
    Bayes check l2 [ 0.14494897  0.5         0.5         0.5         0.5         0.5
      0.85505103]
    
    uniform Bayes solution to coingame (all-heads, fair, or all-tails): 7
    [ 0.00387597  0.5         0.5         0.5         0.5         0.5         0.5
      0.99612403]
    l1 solution to coingame (all-heads, fair, or all-tails): 7
    l1Soln [0.007692283124038655, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.9923077168759615]
    l1 loss 0.00769230807619
    l2 loss 0.00378698262649
    effective priors l1 (0.2500004054730463, 0.4999991890539074, 0.2500004054730463)
    Bayes check l1 [ 0.00769228  0.5         0.5         0.5         0.5         0.5         0.5
      0.99230772]
    l2Soln [ 0.13714594  0.24081853  0.34449112  0.44816371  0.50089267  0.42350623
      0.75918147  0.93260792]
    l1 loss 0.137145942589
    l2 loss 0.0188090095685
    effective priors l2 (0.019849362180012965, 0.960301275639974, 0.019849362180012965)
    Bayes check l2 [ 0.13714594  0.5         0.5         0.5         0.5         0.5         0.5
      0.86285406]
    
    uniform Bayes solution to coingame (all-heads, fair, or all-tails): 8
    [ 0.00194553  0.5         0.5         0.5         0.5         0.5         0.5
      0.5         0.99805447]
    l1 solution to coingame (all-heads, fair, or all-tails): 8
    l1Soln [0.003875857178041267, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.996124142821959]
    l1 loss 0.0038759698658
    l2 loss 0.00192296222727
    effective priors l1 (0.25000363423216493, 0.49999273153567014, 0.25000363423216493)
    Bayes check l1 [ 0.00387586  0.5         0.5         0.5         0.5         0.5         0.5
      0.5         0.99612414]
    l2Soln [ 0.13060194  0.22295145  0.31530097  0.40765048  0.5         0.50159034
      0.45269638  0.77704855  0.93582357]
    l1 loss 0.130601937482
    l2 loss 0.017056866074
    effective priors l2 (0.010809680995590636, 0.9783806380088187, 0.010809680995590636)
    Bayes check l2 [ 0.13060194  0.5         0.5         0.5         0.5         0.5         0.5
      0.5         0.86939806]
    
    uniform Bayes solution to coingame (all-heads, fair, or all-tails): 9
    [  9.74658869e-04   5.00000000e-01   5.00000000e-01   5.00000000e-01
       5.00000000e-01   5.00000000e-01   5.00000000e-01   5.00000000e-01
       5.00000000e-01   9.99025341e-01]
    l1 solution to coingame (all-heads, fair, or all-tails): 9
    l1Soln [0.0019448294819158865, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.5000000000000001, 0.9980551705180841]
    l1 loss 0.00194552800984
    l2 loss 0.000968980284687
    effective priors l1 (0.2500448884146172, 0.4999102231707656, 0.2500448884146172)
    Bayes check l1 [ 0.00194483  0.5         0.5         0.5         0.5         0.5         0.5
      0.5         0.5         0.99805517]
    l2Soln [ 0.125       0.20833333  0.29166667  0.375       0.45833333  0.50071754
      0.39299734  0.47633068  0.79166667  0.93857631]
    l1 loss 0.124999999916
    l2 loss 0.0156249999791
    effective priors l2 (0.005791505796615287, 0.9884169884067694, 0.005791505796615287)
    Bayes check l2 [ 0.125  0.5    0.5    0.5    0.5    0.5    0.5    0.5    0.5    0.875]
    
    uniform Bayes solution to coingame (all-heads, fair, or all-tails): 10
    [  4.87804878e-04   5.00000000e-01   5.00000000e-01   5.00000000e-01
       5.00000000e-01   5.00000000e-01   5.00000000e-01   5.00000000e-01
       5.00000000e-01   5.00000000e-01   9.99512195e-01]
    l1 solution to coingame (all-heads, fair, or all-tails): 10
    l1Soln [0.0009745043896464365, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.9990254956103537]
    l1 loss 0.000974659171114
    l2 loss 0.000486379775916
    effective priors l1 (0.2500198522933954, 0.4999602954132092, 0.2500198522933954)
    Bayes check l1 [  9.74504390e-04   5.00000000e-01   5.00000000e-01   5.00000000e-01
       5.00000000e-01   5.00000000e-01   5.00000000e-01   5.00000000e-01
       5.00000000e-01   5.00000000e-01   9.99025496e-01]
    l2Soln [ 0.12012654  0.19610123  0.27207592  0.34805061  0.42402531  0.5
      0.50130835  0.41994673  0.49592142  0.80389877  0.87987346]
    l1 loss 0.120126536676
    l2 loss 0.0144303848138
    effective priors l2 (0.0030692053724265004, 0.993861589255147, 0.0030692053724265004)
    Bayes check l2 [ 0.12012654  0.5         0.5         0.5         0.5         0.5         0.5
      0.5         0.5         0.5         0.87987346]


.. parsed-literal::

    /System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/scipy/optimize/optimize.py:1605: RuntimeWarning: invalid value encountered in double_scalars
      tmp2 = (x - v)*(fx - fw)
    -c:262: RuntimeWarning: invalid value encountered in divide


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
    {0: 0.0428932188134525}
    	phi_0_2 	-1/2 + sqrt(2)/2 	0.207106781187
    	phi_1_2 	1/2 	0.5
    	phi_2_2 	-sqrt(2)/2 + 3/2 	0.792893218813
    loss 0.0428932188135
    d phi_0_2 -2*p**3 + sqrt(2)*p**2 + 3*p**2 - 2*sqrt(2)*p - 1 + sqrt(2) +-
    d phi_1_2 4*p**3 - 6*p**2 + 2*p +-
    d phi_2_2 -2*p**3 - sqrt(2)*p**2 + 3*p**2 +-
    []
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
    {0: 0.0625000000000000}
    	phi_0_1 	1/4 	0.25
    	phi_1_1 	3/4 	0.75
    loss 0.0625
    d phi_0_1 2*p**2 - 5*p/2 + 1/2 +-
    d phi_1_1 -2*p**2 + 3*p/2 +-
    []
    *******************
    numeric l2 solution for k= 1
    [0.25, 0.75]
    
    
    analytic l2 solution for k= 2
    *******************
    2
    {0: 0.0428932188134525}
    	phi_0_2 	-1/2 + sqrt(2)/2 	0.207106781187
    	phi_1_2 	1/2 	0.5
    	phi_2_2 	-sqrt(2)/2 + 3/2 	0.792893218813
    loss 0.0428932188135
    d phi_0_2 -2*p**3 + sqrt(2)*p**2 + 3*p**2 - 2*sqrt(2)*p - 1 + sqrt(2) +-
    d phi_1_2 4*p**3 - 6*p**2 + 2*p +-
    d phi_2_2 -2*p**3 - sqrt(2)*p**2 + 3*p**2 +-
    []
    *******************
    numeric l2 solution for k= 2
    [0.20710678118654738, 0.49999999999999983, 0.79289321881345221]
    
    
    analytic l2 solution for k= 3
    *******************
    3
    {2: 0.0334936490538903}
    	phi_0_3 	-1/4 + sqrt(3)/4 	0.183012701892
    	phi_1_3 	sqrt(3)/12 + 1/4 	0.394337567297
    	phi_2_3 	-sqrt(3)/12 + 3/4 	0.605662432703
    	phi_3_3 	-sqrt(3)/4 + 5/4 	0.816987298108
    loss 0.0334936490539
    d phi_0_3 2*p**4 - 11*p**3/2 - sqrt(3)*p**3/2 + 3*sqrt(3)*p**2/2 + 9*p**2/2 - 3*sqrt(3)*p/2 - p/2 - 1/2 + sqrt(3)/2 +-
    d phi_1_3 -6*p**4 + sqrt(3)*p**3/2 + 27*p**3/2 - 9*p**2 - sqrt(3)*p**2 + sqrt(3)*p/2 + 3*p/2 +-
    d phi_2_3 6*p**4 - 21*p**3/2 + sqrt(3)*p**3/2 - sqrt(3)*p**2/2 + 9*p**2/2 +-
    d phi_3_3 -2*p**4 - sqrt(3)*p**3/2 + 5*p**3/2 +-
    []
    *******************
    numeric l2 solution for k= 3
    [0.18301270189221974, 0.39433756729740699, 0.60566243270259423, 0.8169872981077817]
    
    
    analytic l2 solution for k= 4
    *******************
    4
    {3: 0.0277777777777778}
    	phi_0_4 	1/6 	0.166666666667
    	phi_1_4 	1/3 	0.333333333333
    	phi_2_4 	1/2 	0.5
    	phi_3_4 	2/3 	0.666666666667
    	phi_4_4 	5/6 	0.833333333333
    loss 0.0277777777778
    d phi_0_4 -2*p**5 + 25*p**4/3 - 40*p**3/3 + 10*p**2 - 10*p/3 + 1/3 +-
    d phi_1_4 8*p**5 - 80*p**4/3 + 32*p**3 - 16*p**2 + 8*p/3 +-
    d phi_2_4 -12*p**5 + 30*p**4 - 24*p**3 + 6*p**2 +-
    d phi_3_4 8*p**5 - 40*p**4/3 + 16*p**3/3 +-
    d phi_4_4 -2*p**5 + 5*p**4/3 +-
    []
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

