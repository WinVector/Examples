from sympy import *

p = symbols('p')
simplify(p*(3/4.0-p)**2 + (1-p)*(1/4.0-p)**2)
phis = [ symbols('phi01'), symbols('phi11') ]
poly = p*(phis[1]-p)**2 + (1-p)*(phis[0]-p)**2
polyTerms = collect(expand(poly),p,evaluate=False)
eqns = [ polyTerms[p**(pow+1)] for pow in range(len(polyTerms)-1) ]
soln1 = solve(eqns)
print soln1
print exapnd(poly.subs(soln1[0]))
dcterm = polyTerms[p**0]
print expand(dcterm.subs(soln1[0]))


