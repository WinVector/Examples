
.. code:: python

    import sympy
    
    
    # expecting a dictionary solution
    def isGoodSoln(si):
       def isGoodVal(x):
          xn = complex(x)
          xr = xn.real
          xi = xn.imag
          return (abs(xi)<1.0e-6) and (xr>0.0) and (xr<1.0)
       return all([ isGoodVal(xi) for xi in si.values() ])
    
    
    # only good for k>=1
    def solveKz(k):
       vars = sympy.symbols(['phi' + str(i) for i in range((k+1)/2)])
       if k%2!=0:
          phis = vars + [1-varsi for varsi in reversed(vars) ]
       else:
          phis = vars + [sympy.Rational(1,2)] + [1-varsi for varsi in reversed(vars) ]
       z = sympy.symbols('z')
       poly = sum([ sympy.binomial(k,h) * z**h * ((1+z)*phis[h] -z)**2 for h in range(k+1)]) - phis[0]**2 * (1+z)**(k+2)
       polyTerms = poly.expand().collect(z,evaluate=False)
       eqns = [ polyTerms[ki] for ki in polyTerms.keys() if (not ki==1) ]
       solns = sympy.solve(eqns,vars,dict=True)
       soln1 = [ si for si in solns if isGoodSoln(si)][0]
       solnv = [ soln1[vi] for vi in vars ]
       if k%2!=0:
          xs = solnv + [1-solni for solni in reversed(solnv) ]
       else:
          xs = solnv + [sympy.Rational(1,2)] + [1-solni for solni in reversed(solnv) ]
       return xs
    
    # only good for k>=1
    def conjectureK(k,numeric=False):
       if k<=1:
          return [sympy.Rational(1,4),sympy.Rational(3,4)]
       phi = [ 0 for i in range(k+1) ]
       phi[0] = (sympy.sqrt(k)-1)/(2*(k-1))
       phi[1] = (sympy.sqrt((phi[0]**2+2*phi[0]/k).expand())).simplify()
       if numeric:
          for h in range(2):
             phi[h] = float(phi[h])
       for h in range(2,(k+1)):
          phi[h] = sympy.sqrt(( (k+2)*(k+1)*(phi[0]**2)/((k+2-h)*(k+1-h)) + 2*h*phi[h-1]*(1-phi[h-1])/(k+1-h) - h*(h-1)*((phi[h-2]-1)**2)/((k+2-h)*(k+1-h)) ))
       return phi
    
    
    
    p = sympy.symbols('p')
    for k in range(1,9):
       print
       print 'k',k
       solnk = solveKz(k)
       print 'soln       ',solnk
       poly = sum([ p**h * (1-p)**(k-h) * sympy.binomial(k,h) * (solnk[h]-p)**2 for h in range(k+1) ]).expand()
       print 'check poly',poly
       conjk = conjectureK(k,numeric=True)
       print 'conjecture:',conjk
       print 'max difference:',max([ abs(complex(solnk[i]-conjk[i])) for i in range(len(solnk)) ])
       print
    
    


.. parsed-literal::

    
    k 1
    soln        [1/4, 3/4]
    check poly 1/16
    conjecture: [1/4, 3/4]
    max difference: 0.0
    
    
    k 2
    soln        [-1/2 + sqrt(2)/2, 1/2, -sqrt(2)/2 + 3/2]
    check poly -sqrt(2)/2 + 3/4
    conjecture: [0.20710678118654752, 0.5, 0.792893218813452]
    max difference: 6.26858358953e-17
    
    
    k 3
    soln        [-1/4 + sqrt(3)/4, sqrt(3)/12 + 1/4, -sqrt(3)/12 + 3/4, -sqrt(3)/4 + 5/4]
    check poly -sqrt(3)/8 + 1/4
    conjecture: [0.18301270189221933, 0.39433756729740643, 0.605662432702594, 0.816987298107781]
    max difference: 2.50877105545e-17
    
    
    k 4
    soln        [1/6, 1/3, 1/2, 2/3, 5/6]
    check poly 1/36
    conjecture: [0.16666666666666666, 0.3333333333333333, 0.500000000000000, 0.666666666666667, 0.833333333333333]
    max difference: 1.11022302463e-16
    
    
    k 5
    soln        [-1/8 + sqrt(5)/8, 1/8 + 3*sqrt(5)/40, sqrt(5)/40 + 3/8, -sqrt(5)/40 + 5/8, -3*sqrt(5)/40 + 7/8, -sqrt(5)/8 + 9/8]
    check poly -sqrt(5)/32 + 3/32
    conjecture: [0.15450849718747373, 0.2927050983124842, 0.430901699437495, 0.569098300562505, 0.707294901687516, 0.845491502812527]
    max difference: 3.19486619378e-16
    
    
    k 6
    soln        [-1/10 + sqrt(6)/10, 1/10 + sqrt(6)/15, sqrt(6)/30 + 3/10, 1/2, -sqrt(6)/30 + 7/10, -sqrt(6)/15 + 9/10, -sqrt(6)/10 + 11/10]
    check poly -sqrt(6)/50 + 7/100
    conjecture: [0.14494897427831782, 0.2632993161855452, 0.381649658092773, 0.500000000000000, 0.618350341907227, 0.736700683814455, 0.855051025721682]
    max difference: 3.77994123684e-16
    
    
    k 7
    soln        [-1/12 + sqrt(7)/12, 1/12 + 5*sqrt(7)/84, sqrt(7)/28 + 1/4, sqrt(7)/84 + 5/12, -sqrt(7)/84 + 7/12, -sqrt(7)/28 + 3/4, -5*sqrt(7)/84 + 11/12, -sqrt(7)/12 + 13/12]
    check poly -sqrt(7)/72 + 1/18
    conjecture: [0.13714594258871587, 0.24081853042051135, 0.344491118252307, 0.448163706084102, 0.551836293915898, 0.655508881747693, 0.759181469579488, 0.862854057411286]
    max difference: 1.69186951436e-15
    
    
    k 8
    soln        [-1/14 + sqrt(2)/7, 1/14 + 3*sqrt(2)/28, sqrt(2)/14 + 3/14, sqrt(2)/28 + 5/14, 1/2, -sqrt(2)/28 + 9/14, -sqrt(2)/14 + 11/14, -3*sqrt(2)/28 + 13/14, -sqrt(2)/7 + 15/14]
    check poly -sqrt(2)/49 + 9/196
    conjecture: [0.1306019374818707, 0.22295145311140305, 0.315300968740935, 0.407650484370468, 0.500000000000000, 0.592349515629532, 0.684699031259065, 0.777048546888597, 0.869398062518130]
    max difference: 5.41301093293e-16
    

