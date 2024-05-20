Follow-up calculation for [How to Read Sourav Chatterjee’s Basic XICOR Definition](https://win-vector.com/2021/12/26/how-to-read-sourav-chatterjees-basic-xicor-defenition/).

## Solving for the sum


```python
import functools
import numpy
import pandas
import sklearn.linear_model
from sympy import *
from fractions import Fraction


def f(n):
    res = 0
    for a in range(n):
        for b in range(n):
            if b != a:
                res = res + numpy.abs(b - a)
    return res

d = pandas.DataFrame({
    'n': range(10)
})
d['f'] = [f(n) for n in d['n']]
d['n2'] = d['n'] * d['n']
d['n3'] = d['n'] * d['n2']
model = sklearn.linear_model.LinearRegression()
model.fit(d.loc[: , ['n', 'n2', 'n3']], d['f'])
```




    LinearRegression()




```python
model.intercept_
```




    5.684341886080802e-14




```python
def mk_rational(v):
    den_limit = 1000000
    rat = Fraction(v).limit_denominator(den_limit)
    return Rational(p=rat.numerator, q=rat.denominator)

intercept_rational = mk_rational(model.intercept_)

intercept_rational

```




$\displaystyle 0$




```python
model.coef_
```




    array([-3.33333333e-01,  2.88657986e-15,  3.33333333e-01])




```python
coef_rational = [mk_rational(c) for c in model.coef_]

coef_rational
```




    [-1/3, 0, 1/3]




```python
n = symbols('n')
terms = (
        [intercept_rational]
        + [coef_rational[i] * n ** (i+1) for i in range(len(coef_rational))]
)
formula = functools.reduce(lambda a, b: a + b, terms)

formula

```




$\displaystyle \frac{n^{3}}{3} - \frac{n}{3}$




```python
def g(n_value):
    return formula.subs(n, n_value)

del d['n2']
del d['n3']
d['g'] = [g(n) for n in d['n']]

d
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>n</th>
      <th>f</th>
      <th>g</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>2</td>
      <td>2</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>8</td>
      <td>8</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>20</td>
      <td>20</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>40</td>
      <td>40</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>70</td>
      <td>70</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>112</td>
      <td>112</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td>168</td>
      <td>168</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td>240</td>
      <td>240</td>
    </tr>
  </tbody>
</table>
</div>



## Solving the integral

Checking the value of E[|a-b|] is for a,b indepedently chosen uniformly at random in [0, 1]?


```python
a, b = symbols('a b')

integrate(integrate(a - b, (b, 0, a)) + integrate(b - a, (b, a, 1)), (a, 0, 1))
```




$\displaystyle \frac{1}{3}$



## Side question, what is E[(a-b)^2] for a,b indepedently chosen uniformly at random in [0, 1]?


```python
integrate(integrate((a - b)**2, (b, 0, 1)), (a, 0, 1))

```




$\displaystyle \frac{1}{6}$


