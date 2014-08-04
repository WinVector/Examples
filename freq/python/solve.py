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
for k in range(1,21):
   print
   print 'k',k
#   solnk = solveKz(k)
#   print 'soln       ',solnk
#   poly = sum([ p**h * (1-p)**(k-h) * sympy.binomial(k,h) * (solnk[h]-p)**2 for h in range(k+1) ]).expand()
#   print 'check poly',poly
   conjk = conjectureK(k,numeric=True)
   print 'conjecture:',conjk
   polyc = sum([ p**h * (1-p)**(k-h) * sympy.binomial(k,h) * (conjk[h]-p)**2 for h in range(k+1) ]).expand()
   print 'conjecture check poly',polyc
#   print 'max difference:',max([ abs(complex(solnk[i]-conjk[i])) for i in range(len(solnk)) ])
   print '1/k for scale:',1/float(k)
   print



