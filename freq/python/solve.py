import sympy


# expecting a dictionary solution
def isGoodSoln(si):
   def isGoodVal(x):
      xn = complex(x)
      xr = xn.real
      xi = xn.imag
      return (abs(xi)<1.0e-6) and (xr>0.0) and (xr<1.0)
   return all([ isGoodVal(xi) for xi in si.values() ])



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


for k in range(1,9):
   print
   print k
   print solveKz(k)
   print


