
From:
http://mathoverflow.net/questions/177574/existence-of-solutions-of-a-polynomial-system

Fix :math:`k \in \mathbb{N}`, :math:`k \geq 1`. Let :math:`p \in [0,1]`
and :math:`x = (x_0, \ldots, x_k)` be a :math:`(k+1)`-dimensional *real*
vector, and define

.. math:: S_k(p,x) = -x_0^2 + \sum_{i=0}^k {k \choose i} p^i (1 - p)^{k - i} \cdot (x_i - p)^2.

Experiments show that for small values of :math:`k`

.. math:: \exists x \in \text{ interior of } [0,1]^{k+1} \,.\, \forall p \in [0,1] \,.\, S_k(p,x) = 0.

 In other words, there are :math:`x_i`'s such that :math:`S_k(x,p)` is
identically zero as a polynomial in :math:`p`.

For a given :math:`k` we can expand :math:`S_k(x,p)` as a polynomial in
:math:`p` and equate the coefficients to :math:`0`. For :math:`k = 2` we
get

.. raw:: latex

   \begin{align*}
    0&=0 \\
    -x_0^2-2 x_0+x_1^2&=0 \\
    2 x_0-2 x_1+1&=0 \\
   \end{align*}

and this has two real solutions:

.. math:: x = (\frac{1}{2} (-1-\sqrt{2}),\frac{1}{2},\frac{1}{2} (3+\sqrt{2}))

and

.. math:: x = (\frac{1}{2} (-1+\sqrt{2}),\frac{1}{2},\frac{1}{2} (3-\sqrt{2})).

One of which satisifies our conditions.

The problem arises in statistics, see `John Mount's blog
post <http://www.win-vector.com/blog/2014/07/frequenstist-inference-only-seems-easy/>`__
for background.

**Question:** Is there a solution for every :math:`k`?

**Addendum:** John says he wants soltions in the interor of
:math:`[0,1]^{k+1}`...

--------------


Solution submitted 8-4-2013 by me (John Mount), having a lot of trouble
with links and formatting. Enough of that, submitting it here.

This is some background to the question and the solution (minus one
check mentioned at the end).

Define

.. math:: S(k,p,x) = \sum_{i=0}^k {k \choose i} p^i (1-p)^{k-i} (x_i-p)^2.

Define

.. math:: f_k(k) = \mathrm{argmin}_x \max_p S(k,p,x).

 Then :math:`f_k(k)` is the minimax square-loss solution to trying to
estimate the win rate of a random process by observing :math:`k` results
(Wald wrote on this). The neat thing is: we can show if there is a real
solution :math:`x` in :math:`[0,1]^{k+1}` to :math:`S(k,p,x) = x_0^2`
then :math:`x=f_k(k)`. Meaning we avoided two nasty quantifiers. See
`this
file <https://github.com/WinVector/Examples/blob/master/freq/python/freqMin.rst>`__
for some experimental examples.

We know there is only one connected component of solutions in the
interior of the unit cube because these solutions represent extreme
points of the minimax estimation problem. We show that there is a
diversity of gradients by reflecting coordinates of :math:`x` around
:math:`p` (and thus we have an extreme point).

From the original problem we expect a lot of symmetries. Also, a change
of variables :math:`z = p/(1-p)` makes collecting terms easier. In fact
I now have a conjectured exact solution, I now only need a proof that it
always works (cancels the p's, is real and in the interior of
:math:`[0,1]^{k+1}`; I already have a proof that such a solution when it
exists solves the original estimation problem). The conjectured solution
for :math:`k>1` (for :math:`k=1` the solution is :math:`[1/4,3/4]`) is:

.. math::

    
   \begin{align}
   f_k(0) &= (\sqrt{k}-1)/(2 (k-1))  \\
   f_k(1) &= \sqrt{f_k(0)^2+2 f_k(0)/k}  \\
    &  \text{ for } h>1: \\
   f_k(h)^2 &= (k+2) (k+1) (f_k(0)^2)/((k+2-h) (k+1-h))  \\
     & + 2 h f_k(h-1) (1-f_k(h-1))/(k+1-h) \\
     & - h (h-1) ((f_k(h-2)-1)^2)/((k+2-h) (k+1-h)) 
   \end{align}

A Python implementation, demonstration and check of this solution up
through :math:`k=8` is `given
here <https://github.com/WinVector/Examples/blob/master/freq/python/explicitSolution.rst>`__.
So really all that is left to prove is the right hand side of
:math:`f_k(h)^2` is always positive and in the interior of :math:`[0,1]`
for all :math:`k,h`.

Note 8-4-2014: Vladimir Dotsenko `finished the
solution <http://mathoverflow.net/a/177820/56665>`__ by adding the
important insight that the :math:`f_k(h)` are evenly spaced when
:math:`k` is held constant. This lets him get a closed form solution for
each :math:`f_k(h)` (without having to refer to ealier :math:`h`).

--------------

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
.. code:: python

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
       print '1/k for scale:',1/float(k)
       print

.. parsed-literal::

    
    k 1
    soln        [1/4, 3/4]
    check poly 1/16
    conjecture: [1/4, 3/4]
    max difference: 0.0
    1/k for scale: 1.0
    
    
    k 2
    soln        [-1/2 + sqrt(2)/2, 1/2, -sqrt(2)/2 + 3/2]
    check poly -sqrt(2)/2 + 3/4
    conjecture: [0.20710678118654752, 0.5, 0.792893218813452]
    max difference: 6.26858358953e-17
    1/k for scale: 0.5
    
    
    k 3
    soln        [-1/4 + sqrt(3)/4, sqrt(3)/12 + 1/4, -sqrt(3)/12 + 3/4, -sqrt(3)/4 + 5/4]
    check poly -sqrt(3)/8 + 1/4
    conjecture: [0.18301270189221933, 0.39433756729740643, 0.605662432702594, 0.816987298107781]
    max difference: 2.50877105545e-17
    1/k for scale: 0.333333333333
    
    
    k 4
    soln        [1/6, 1/3, 1/2, 2/3, 5/6]
    check poly 1/36
    conjecture: [0.16666666666666666, 0.3333333333333333, 0.500000000000000, 0.666666666666667, 0.833333333333333]
    max difference: 1.11022302463e-16
    1/k for scale: 0.25
    
    
    k 5
    soln        [-1/8 + sqrt(5)/8, 1/8 + 3*sqrt(5)/40, sqrt(5)/40 + 3/8, -sqrt(5)/40 + 5/8, -3*sqrt(5)/40 + 7/8, -sqrt(5)/8 + 9/8]
    check poly -sqrt(5)/32 + 3/32
    conjecture: [0.15450849718747373, 0.2927050983124842, 0.430901699437495, 0.569098300562505, 0.707294901687516, 0.845491502812527]
    max difference: 3.19486619378e-16
    1/k for scale: 0.2
    
    
    k 6
    soln        [-1/10 + sqrt(6)/10, 1/10 + sqrt(6)/15, sqrt(6)/30 + 3/10, 1/2, -sqrt(6)/30 + 7/10, -sqrt(6)/15 + 9/10, -sqrt(6)/10 + 11/10]
    check poly -sqrt(6)/50 + 7/100
    conjecture: [0.14494897427831782, 0.2632993161855452, 0.381649658092773, 0.500000000000000, 0.618350341907227, 0.736700683814455, 0.855051025721682]
    max difference: 3.77994123684e-16
    1/k for scale: 0.166666666667
    
    
    k 7
    soln        [-1/12 + sqrt(7)/12, 1/12 + 5*sqrt(7)/84, sqrt(7)/28 + 1/4, sqrt(7)/84 + 5/12, -sqrt(7)/84 + 7/12, -sqrt(7)/28 + 3/4, -5*sqrt(7)/84 + 11/12, -sqrt(7)/12 + 13/12]
    check poly -sqrt(7)/72 + 1/18
    conjecture: [0.13714594258871587, 0.24081853042051135, 0.344491118252307, 0.448163706084102, 0.551836293915898, 0.655508881747693, 0.759181469579488, 0.862854057411286]
    max difference: 1.69186951436e-15
    1/k for scale: 0.142857142857
    
    
    k 8
    soln        [-1/14 + sqrt(2)/7, 1/14 + 3*sqrt(2)/28, sqrt(2)/14 + 3/14, sqrt(2)/28 + 5/14, 1/2, -sqrt(2)/28 + 9/14, -sqrt(2)/14 + 11/14, -3*sqrt(2)/28 + 13/14, -sqrt(2)/7 + 15/14]
    check poly -sqrt(2)/49 + 9/196
    conjecture: [0.1306019374818707, 0.22295145311140305, 0.315300968740935, 0.407650484370468, 0.500000000000000, 0.592349515629532, 0.684699031259065, 0.777048546888597, 0.869398062518130]
    max difference: 5.41301093293e-16
    1/k for scale: 0.125
    


.. code:: python

    p = sympy.symbols('p')
    for k in range(1,21):
       print
       print 'k',k
       conjk = conjectureK(k,numeric=True)
       print 'conjecture:',conjk
       polyc = sum([ p**h * (1-p)**(k-h) * sympy.binomial(k,h) * (conjk[h]-p)**2 for h in range(k+1) ]).expand()
       print 'conjecture check poly',polyc
       print '1/k for scale:',1/float(k)
       print

.. parsed-literal::

    
    k 1
    conjecture: [1/4, 3/4]
    conjecture check poly 1/16
    1/k for scale: 1.0
    
    
    k 2
    conjecture: [0.20710678118654752, 0.5, 0.792893218813452]
    conjecture check poly 2.22044604925031e-16*p**3 + 0.0428932188134525
    1/k for scale: 0.5
    
    
    k 3
    conjecture: [0.18301270189221933, 0.39433756729740643, 0.605662432702594, 0.816987298107781]
    conjecture check poly -1.33226762955019e-15*p**4 - 8.88178419700125e-16*p**3 + 5.55111512312578e-17*p + 0.0334936490538903
    1/k for scale: 0.333333333333
    
    
    k 4
    conjecture: [0.16666666666666666, 0.3333333333333333, 0.500000000000000, 0.666666666666667, 0.833333333333333]
    conjecture check poly -8.88178419700125e-16*p**5 + 1.77635683940025e-15*p**4 + 0.0277777777777778
    1/k for scale: 0.25
    
    
    k 5
    conjecture: [0.15450849718747373, 0.2927050983124842, 0.430901699437495, 0.569098300562505, 0.707294901687516, 0.845491502812527]
    conjecture check poly -7.105427357601e-15*p**6 + 7.105427357601e-15*p**4 - 3.5527136788005e-15*p**3 + 8.88178419700125e-16*p**2 - 5.55111512312578e-17*p + 0.0238728757031316
    1/k for scale: 0.2
    
    
    k 6
    conjecture: [0.14494897427831782, 0.2632993161855452, 0.381649658092773, 0.500000000000000, 0.618350341907227, 0.736700683814455, 0.855051025721682]
    conjecture check poly -1.37667655053519e-14*p**7 + 7.43849426498855e-15*p**6 - 1.77635683940025e-15*p**5 + 4.44089209850063e-16*p**2 - 5.55111512312578e-17*p + 0.0210102051443364
    1/k for scale: 0.166666666667
    
    
    k 7
    conjecture: [0.13714594258871587, 0.24081853042051135, 0.344491118252307, 0.448163706084102, 0.551836293915898, 0.655508881747693, 0.759181469579488, 0.862854057411286]
    conjecture check poly 2.22044604925031e-15*p**8 + 1.08801856413265e-13*p**7 - 1.13686837721616e-13*p**6 - 2.8421709430404e-14*p**4 + 7.105427357601e-15*p**3 + 5.55111512312578e-17*p + 0.0188090095685473
    1/k for scale: 0.142857142857
    
    
    k 8
    conjecture: [0.1306019374818707, 0.22295145311140305, 0.315300968740935, 0.407650484370468, 0.500000000000000, 0.592349515629532, 0.684699031259065, 0.777048546888597, 0.869398062518130]
    conjecture check poly 7.105427357601e-14*p**8 - 5.6843418860808e-14*p**7 - 1.27897692436818e-13*p**6 + 5.6843418860808e-14*p**5 - 1.4210854715202e-14*p**4 + 1.06581410364015e-14*p**3 - 8.88178419700125e-16*p**2 + 1.11022302462516e-16*p + 0.0170568660740185
    1/k for scale: 0.125
    
    
    k 9
    conjecture: [0.125, 0.20833333333333334, 0.291666666666667, 0.375000000000000, 0.458333333333333, 0.541666666666667, 0.625000000000000, 0.708333333333333, 0.791666666666667, 0.874999999999993]
    conjecture check poly 2.27373675443232e-13*p**8 - 4.54747350886464e-13*p**7 + 4.54747350886464e-13*p**6 + 5.6843418860808e-14*p**4 - 7.105427357601e-15*p**3 - 4.44089209850063e-16*p**2 + 5.55111512312578e-17*p + 0.015625
    1/k for scale: 0.111111111111
    
    
    k 10
    conjecture: [0.12012653667602108, 0.19610122934081686, 0.272075922005613, 0.348050614670408, 0.424025307335204, 0.500000000000000, 0.575974692664796, 0.651949385329591, 0.727924077994388, 0.803898770659182, 0.879873463323994]
    conjecture check poly -4.54747350886464e-13*p**10 - 7.95807864051312e-13*p**9 + 1.53477230924182e-12*p**8 + 5.82645043323282e-13*p**7 - 2.27373675443232e-13*p**5 + 1.13686837721616e-13*p**4 - 2.1316282072803e-14*p**3 + 1.77635683940025e-15*p**2 + 0.0144303848137754
    1/k for scale: 0.1
    
    
    k 11
    conjecture: [0.11583123951777, 0.18568010505999363, 0.255528970602217, 0.325377836144441, 0.395226701686665, 0.465075567228888, 0.534924432771112, 0.604773298313335, 0.674622163855559, 0.744471029397782, 0.814319894940009, 0.884168760482201]
    conjecture check poly -9.09494701772928e-13*p**12 - 1.81898940354586e-12*p**11 + 2.72848410531878e-12*p**10 + 1.36424205265939e-12*p**9 + 1.02318153949454e-12*p**8 + 4.59010607301025e-12*p**7 - 1.36424205265939e-12*p**6 + 4.40536496171262e-13*p**5 - 1.13686837721616e-13*p**4 + 2.8421709430404e-14*p**3 - 8.88178419700125e-16*p**2 - 5.55111512312578e-17*p + 0.013416876048223
    1/k for scale: 0.0909090909091
    
    
    k 12
    conjecture: [0.11200461886989793, 0.17667051572491493, 0.241336412579932, 0.306002309434949, 0.370668206289966, 0.435334103144983, 0.500000000000000, 0.564665896855017, 0.629331793710034, 0.693997690565051, 0.758663587420068, 0.823329484275084, 0.887995381130121]
    conjecture check poly -4.54747350886464e-13*p**13 - 3.63797880709171e-12*p**11 + 1.45519152283669e-11*p**10 - 1.45519152283669e-11*p**9 + 1.45519152283669e-11*p**8 - 7.27595761418343e-12*p**7 - 9.09494701772928e-13*p**5 + 5.6843418860808e-14*p**4 - 2.8421709430404e-14*p**3 + 3.5527136788005e-15*p**2 + 0.0125450346481911
    1/k for scale: 0.0833333333333
    
    
    k 13
    conjecture: [0.10856463647766622, 0.16878546163494834, 0.229006286792230, 0.289227111949513, 0.349447937106795, 0.409668762264077, 0.469889587421359, 0.530110412578641, 0.590331237735923, 0.650552062893205, 0.710772888050488, 0.770993713207768, 0.831214538365061, 0.891435363522209]
    conjecture check poly 1.81898940354586e-12*p**14 - 3.63797880709171e-12*p**13 - 1.45519152283669e-11*p**12 + 5.82076609134674e-11*p**11 + 1.45519152283669e-11*p**10 + 1.45519152283669e-11*p**9 - 1.45519152283669e-11*p**8 + 7.105427357601e-15*p**3 - 1.77635683940025e-15*p**2 + 5.55111512312578e-17*p + 0.0117862802935278
    1/k for scale: 0.0769230769231
    
    
    k 14
    conjecture: [0.10544836102976697, 0.1618128808826574, 0.218177400735548, 0.274541920588438, 0.330906440441329, 0.387270960294219, 0.443635480147110, 0.500000000000000, 0.556364519852890, 0.612729039705781, 0.669093559558672, 0.725458079411560, 0.781822599264458, 0.838187119117306, 0.894551638970746]
    conjecture check poly -3.63797880709171e-12*p**15 + 4.36557456851006e-11*p**14 - 4.36557456851006e-11*p**13 + 1.16415321826935e-10*p**12 + 1.45519152283669e-11*p**11 + 1.57342583406717e-10*p**10 - 8.5265128291212e-12*p**9 - 4.36557456851006e-11*p**8 + 7.27595761418343e-12*p**7 - 9.09494701772928e-13*p**6 + 1.36424205265939e-12*p**5 + 3.41060513164848e-13*p**4 + 0.0111193568438641
    1/k for scale: 0.0714285714286
    
    
    k 15
    conjecture: [0.10260654807883632, 0.1555923416683248, 0.208578135257813, 0.261563928847302, 0.314549722436790, 0.367535516026279, 0.420521309615767, 0.473507103205256, 0.526492896794744, 0.579478690384233, 0.632464483973721, 0.685450277563210, 0.738436071152698, 0.791421864742188, 0.844407658331663, 0.897393451921343]
    conjecture check poly -1.09139364212751e-11*p**16 + 5.82076609134674e-11*p**15 + 8.73114913702011e-11*p**14 + 7.27595761418343e-11*p**13 + 1.45519152283669e-10*p**12 + 1.60071067512035e-10*p**11 - 1.28466126625426e-10*p**10 + 9.25410859053954e-11*p**9 + 2.5465851649642e-11*p**7 + 1.02318153949454e-12*p**6 + 1.59161572810262e-12*p**5 + 1.4210854715202e-13*p**4 - 7.105427357601e-15*p**3 + 0.0105281037086545
    1/k for scale: 0.0666666666667
    
    
    k 16
    conjecture: [0.1, 0.15, 0.200000000000000, 0.250000000000000, 0.300000000000000, 0.350000000000000, 0.400000000000000, 0.450000000000000, 0.500000000000000, 0.550000000000000, 0.600000000000000, 0.650000000000000, 0.700000000000000, 0.749999999999999, 0.800000000000001, 0.849999999999987, 0.900000000000195]
    conjecture check poly -1.81898940354586e-11*p**17 - 1.01863406598568e-10*p**16 - 8.73114913702011e-11*p**15 + 1.60071067512035e-10*p**14 - 1.14960130304098e-9*p**13 + 1.8007995095104e-10*p**12 + 8.84483597474173e-11*p**11 - 1.32786226458848e-10*p**10 + 1.69166014529765e-10*p**9 - 4.00177668780088e-11*p**8 - 2.91038304567337e-11*p**7 - 5.91171556152403e-12*p**6 - 1.59161572810262e-12*p**5 + 1.70530256582424e-13*p**4 - 7.105427357601e-15*p**3 + 1.77635683940025e-15*p**2 - 5.55111512312578e-17*p + 0.01
    1/k for scale: 0.0625
    
    
    k 17
    conjecture: [0.0975970508005519, 0.14493857423578108, 0.192280097671010, 0.239621621106239, 0.286963144541469, 0.334304667976698, 0.381646191411927, 0.428987714847156, 0.476329238282385, 0.523670761717615, 0.571012285152844, 0.618353808588073, 0.665695332023302, 0.713036855458531, 0.760378378893763, 0.807719902328977, 0.855061425764318, 0.902402949197767]
    conjecture check poly 5.82076609134674e-11*p**18 - 3.49245965480804e-10*p**17 + 2.3283064365387e-10*p**16 - 3.14321368932724e-9*p**15 + 8.73114913702011e-10*p**14 - 2.56113708019257e-9*p**13 + 1.38243194669485e-10*p**12 + 2.20006768358871e-9*p**11 + 3.20142135024071e-10*p**10 + 1.16415321826935e-10*p**9 + 2.47382558882236e-10*p**8 + 2.18278728425503e-11*p**7 + 3.63797880709171e-12*p**6 - 9.09494701772928e-13*p**5 + 2.27373675443232e-13*p**4 - 2.8421709430404e-14*p**3 + 1.77635683940025e-15*p**2 - 1.11022302462516e-16*p + 0.00952518432496551
    1/k for scale: 0.0588235294118
    
    
    k 18
    conjecture: [0.0953717849152731, 0.14033047548024274, 0.185289166045212, 0.230247856610182, 0.275206547175152, 0.320165237740121, 0.365123928305091, 0.410082618870061, 0.455041309435030, 0.500000000000000, 0.544958690564970, 0.589917381129939, 0.634876071694909, 0.679834762259878, 0.724793452824850, 0.769752143389811, 0.814710833954823, 0.859669524519452, 0.904628215090205]
    conjecture check poly -8.02060640126001e-11*p**19 + 2.29277929975069e-10*p**18 - 1.90539140021428e-10*p**17 + 3.85398379876278e-9*p**16 - 9.00399754755199e-10*p**15 - 6.15546014159918e-9*p**14 + 4.82395989820361e-9*p**13 + 5.75528247281909e-9*p**12 + 2.21916707232594e-9*p**11 - 2.40834197029471e-9*p**10 + 8.14907252788544e-10*p**9 - 8.36735125631094e-11*p**8 + 5.45696821063757e-11*p**7 + 3.63797880709171e-12*p**6 - 4.54747350886464e-13*p**5 - 2.8421709430404e-13*p**4 - 2.8421709430404e-14*p**3 - 8.88178419700125e-16*p**2 + 0.00909577735792511
    1/k for scale: 0.0555555555556
    
    
    k 19
    conjecture: [0.09330274843168537, 0.1361129854388764, 0.178923222446067, 0.221733459453258, 0.264543696460449, 0.307353933467640, 0.350164170474831, 0.392974407482022, 0.435784644489213, 0.478594881496404, 0.521405118503595, 0.564215355510786, 0.607025592517978, 0.649835829525168, 0.692646066532360, 0.735456303539549, 0.778266540546746, 0.821076777553906, 0.863887014561363, 0.906697251563763]
    conjecture check poly 2.9849189786546e-10*p**20 + 9.40303834795486e-10*p**19 + 5.04905983689241e-9*p**18 - 1.49611878441647e-9*p**17 + 1.15578586701304e-8*p**16 - 9.6588337328285e-9*p**15 + 7.99627741798759e-9*p**14 + 7.93079379945993e-9*p**13 - 2.16823536902666e-9*p**12 - 7.56699591875076e-10*p**11 - 1.29512045532465e-9*p**10 - 6.54836185276508e-11*p**9 + 4.07453626394272e-10*p**8 - 9.09494701772928e-11*p**7 - 3.18323145620525e-12*p**5 + 5.6843418860808e-14*p**4 + 3.5527136788005e-14*p**3 - 8.88178419700125e-16*p**2 + 5.55111512312578e-17*p + 0.00870540286490637
    1/k for scale: 0.0526315789474
    
    
    k 20
    conjecture: [0.0913719988157784, 0.13223479893420056, 0.173097599052623, 0.213960399171045, 0.254823199289467, 0.295685999407889, 0.336548799526311, 0.377411599644734, 0.418274399763156, 0.459137199881578, 0.500000000000000, 0.540862800118422, 0.581725600236844, 0.622588400355266, 0.663451200473689, 0.704314000592110, 0.745176800710534, 0.786039600828950, 0.826902400947407, 0.867765201065522, 0.908628001189783]
    conjecture check poly -4.65661287307739e-10*p**21 + 3.72529029846191e-9*p**20 - 1.11758708953857e-8*p**19 + 2.98023223876953e-8*p**17 + 7.45058059692383e-8*p**15 - 2.98023223876953e-8*p**14 - 9.31322574615479e-9*p**13 + 3.25962901115417e-9*p**12 - 3.7325662560761e-9*p**10 + 6.98491930961609e-10*p**9 - 5.23868948221207e-10*p**8 + 1.8007995095104e-10*p**7 - 5.82076609134674e-11*p**6 + 3.63797880709171e-12*p**5 + 2.8421709430404e-14*p**3 - 8.88178419700125e-16*p**2 + 5.55111512312578e-17*p + 0.00834884216759061
    1/k for scale: 0.05
    


