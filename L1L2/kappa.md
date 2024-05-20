Define $\kappa(\sigma_1, \sigma_2)$ as $\text{P}[(X + Y \ge 0) = (X \ge 0)]$ where $X$ is normal mean $0$ variance $\sigma_1^2$ and $Y$ is indpendent normal mean $0$ variance $\sigma_2^2$. $\kappa(,)$ is used in our note [here](https://github.com/WinVector/Examples/blob/main/L1L2/L1L2.ipynb). We prove the formula for $\kappa(,)$ [here](https://win-vector.com/2023/06/24/tilting-at-sign/).


```python
import numpy.random
import numpy as np
import pandas as pd
import sympy
from sympy import atan, cos, exp, factorial, gamma, loggamma, pi, sin, sqrt
```


```python
rng = numpy.random.default_rng(seed=12345678903141592653589793)

```


```python
def l1l2auc_empirical_a(n: int, *, nreps :int = 10000000) -> float:
    """
    Empirical estimate of L1L2 AUC.

    :param n: dimension we are working in
    :param nreps: number of repetitions to simulate, > 0
    :return: empirical estimate of kappa(s1, s2)
    """
    n = int(n)
    assert n > 0
    nreps = int(nreps)
    assert nreps > 0
    r_mean = float(sqrt(n - 1/2))
    r_std = float(sqrt(1/2))
    s_mean = float(sqrt(2 * n / pi))
    s_std = float(sqrt(1 - 3 / pi))
    r1 = rng.normal(size=nreps) * r_std + r_mean
    r2 = rng.normal(size=nreps) * r_std + r_mean
    s1 = rng.normal(size=nreps) * s_std + s_mean
    s2 = rng.normal(size=nreps) * s_std + s_mean
    return np.mean((r1 >= r2) == ((r1 * s1) >= (r2 * s2)))

```


```python
l1l2auc_empirical_a(n=20)
```




    0.8866973




```python
def l1l2auc_empirical_b(n: int, *, nreps :int = 10000000) -> float:
    """
    Empirical estimate of L1L2 AUC.

    :param n: dimension we are working in
    :param nreps: number of repetitions to simulate, > 0
    :return: empirical estimate of kappa(s1, s2)
    """
    n = int(n)
    assert n > 0
    nreps = int(nreps)
    assert nreps > 0
    u_mean = 0
    u_std = float(sqrt(1/(2*n)))
    u_shift = float(sqrt(1 - 1/(2*n)))
    v_mean = 0
    v_std = float(sqrt((1 - 3 / pi)/n))
    v_shift = float(sqrt(2 / pi))
    u1 = rng.normal(size=nreps) * u_std + u_mean
    u2 = rng.normal(size=nreps) * u_std + u_mean
    v1 = rng.normal(size=nreps) * v_std + v_mean
    v2 = rng.normal(size=nreps) * v_std + v_mean
    return np.mean(
        ((u1 + u_shift) >= (u2 + u_shift)) 
        == (((u1 + u_shift) * (v1 + v_shift)) >= ((u2 + u_shift) * (v2 + v_shift)))
    )

```


```python
l1l2auc_empirical_b(2000)
```




    0.8854421




```python
def l1l2auc_empirical_c(n: int, *, nreps :int = 10000000) -> float:
    """
    Empirical estimate of L1L2 AUC.

    :param n: dimension we are working in
    :param nreps: number of repetitions to simulate, > 0
    :return: empirical estimate of kappa(s1, s2)
    """
    n = int(n)
    assert n > 0
    nreps = int(nreps)
    assert nreps > 0
    u_mean = 0
    u_std = float(sqrt(1/(2*n)))
    u_shift = 1  # float(sqrt(1 - 1/(2*n)))
    v_mean = 0
    v_std = float(sqrt((1 - 3 / pi)/n))
    v_shift = float(sqrt(2 / pi))
    u1 = rng.normal(size=nreps) * u_std + u_mean
    u2 = rng.normal(size=nreps) * u_std + u_mean
    v1 = rng.normal(size=nreps) * v_std + v_mean
    v2 = rng.normal(size=nreps) * v_std + v_mean
    return np.mean(
        (u1 * v_shift - u2 * v_shift >= 0)
        == (u1 * v_shift - u2 * v_shift + v1 * u_shift - v2 * u_shift >= 0)
     )

```


```python
l1l2auc_empirical_c(2000)
```




    0.8854356




```python
def kappa_empirical(s1: float, s2: float, *, nreps :int = 100000000) -> float:
    """
    Empirical estimate of
    $\kappa(\sigma_1, \sigma_2)$ as $\text{P}[X + Y \ge 0 | X \ge 0]$ 
    where $X$ is normal mean $0$ variance $\sigma_1^2$ and $Y$ is 
    indpendent normal mean $0$ variance $\sigma_2^2$.

    :param s1: variance 1, > 0
    :param s2: variance 2, > 0
    :param nreps: number of repetitions to simulate, > 0
    :return: empirical estimate of kappa(s1, s2)
    """
    s1 = float(s1)
    s2 = float(s2)
    assert s1 > 0
    assert s2 > 0
    nreps = int(nreps)
    assert nreps > 0
    x = rng.normal(size=nreps) * s1
    y = rng.normal(size=nreps) * s2
    return np.mean((x + y >= 0) == (x >= 0))

```


```python
kappa_empirical(
    1,
    sqrt(pi - 3)
)
```




    0.88536252




```python
# kappa(1, 1) should limit out to 0.75
k_1_1_est = kappa_empirical(1, 1)
assert np.abs(k_1_1_est - 0.75) < 1e-3

k_1_1_est
```




    0.75004813




```python
# kappa(a, b) should equal kappa(s a, s b) for s > 0
k_10_10_est = kappa_empirical(10, 10)

assert np.abs(k_10_10_est - 0.75) < 1e-3

k_10_10_est
```




    0.75003899




```python
# kappa(1, b) should go to 1/2 as b gets large
k_1_large_est = kappa_empirical(1, 1e+5)
assert np.abs(k_1_large_est - 0.5) < 1e-3

k_1_large_est
```




    0.49998873




```python
# kappa(1, 1/b) should go to 1 as 1/b gets large
k_1_small_est = kappa_empirical(1, 1e-5)
assert np.abs(k_1_small_est - 1) < 1e-3

k_1_small_est
```




    0.99999679




```python
def kappa(s1, s2):
    """
    arctan solution of
    $\kappa(\sigma_1, \sigma_2)$ as $\text{P}[Y \ge -X | X \ge 0]$ 
    where $X$ is normal mean $0$ variance $\sigma_1^2$ and $Y$ is 
    indpendent normal mean $0$ variance $\sigma_2^2$.
    The idea is the s1/s2 affinte transform moves the comparison line.

    :param s1: variance 1, > 0
    :param s2: variance 2, > 0
    :return: heuristic estimate of kappa(s1, s2)
    """
    # get what fraction of the ellipse circumfrance is in the selection region
    return float(atan(float(s1 / s2)) / pi + 1/2)
```


```python
for b in (0.01, 0.1, 0.5, 1, 2, 10, 100):
    a_est = kappa(1, b)
    e_est = kappa_empirical(1, b)
    print()
    print(f"arctan        kappa(1, {b}) ~ {a_est}")
    print(f"empirical est kappa(1, {b}) ~ {e_est}")
```

    
    arctan        kappa(1, 0.01) ~ 0.9968170072350918
    empirical est kappa(1, 0.01) ~ 0.99682068
    
    arctan        kappa(1, 0.1) ~ 0.9682744825694465
    empirical est kappa(1, 0.1) ~ 0.9683078
    
    arctan        kappa(1, 0.5) ~ 0.8524163823495667
    empirical est kappa(1, 0.5) ~ 0.85244162
    
    arctan        kappa(1, 1) ~ 0.75
    empirical est kappa(1, 1) ~ 0.74994822
    
    arctan        kappa(1, 2) ~ 0.6475836176504333
    empirical est kappa(1, 2) ~ 0.64761174
    
    arctan        kappa(1, 10) ~ 0.5317255174305535
    empirical est kappa(1, 10) ~ 0.53172457
    
    arctan        kappa(1, 100) ~ 0.5031829927649083
    empirical est kappa(1, 100) ~ 0.50317939



```python
# our L1L2 AUC soln
kappa(1, sqrt(pi - 3))
```




    0.8854404657887897




```python
soln = 1/2 + atan(1/sqrt(pi - 3)) / pi

soln
```




$\displaystyle \frac{\operatorname{atan}{\left(\frac{1}{\sqrt{-3 + \pi}} \right)}}{\pi} + 0.5$




```python
float(soln)
```




    0.8854404657887897



$1/2 + \arctan(1/\sqrt{\pi - 3}) / \pi \approx 0.8854404657887897$
