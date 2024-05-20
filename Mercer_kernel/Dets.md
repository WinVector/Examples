Notes in support of [https://win-vector.com/2020/12/25/abs-and-relu-are-not-mercer-kernels/](https://win-vector.com/2020/12/25/abs-and-relu-are-not-mercer-kernels/).

Here are some new notes on what is and what is not a Mercer Kernel style function.

  * `abs(x dot y)` and `relu(x dot y)` are not in general Mercer Kernels [https://github.com/WinVector/Examples/blob/main/Mercer_kernel/Mercer_Kernel.md](https://github.com/WinVector/Examples/blob/main/Mercer_kernel/Mercer_Kernel.md).
  * How to check if a 3 by 3 matrix is positive (semi) definite [https://github.com/WinVector/Examples/blob/main/Mercer_kernel/Dets.ipynb](https://github.com/WinVector/Examples/blob/main/Mercer_kernel/Dets.ipynb).
  * Why dot product is a Mercer Kernel [https://github.com/WinVector/Examples/blob/main/Mercer_kernel/dot.md](https://github.com/WinVector/Examples/blob/main/Mercer_kernel/dot.md).


I've written before on Kernel methods (in the context of support vector machines).
 
  * [https://win-vector.com/2011/10/07/kernel-methods-and-support-vector-machines-de-mystified/](https://win-vector.com/2011/10/07/kernel-methods-and-support-vector-machines-de-mystified/)
  * [https://win-vector.com/2015/02/14/how-sure-are-you-that-large-margin-implies-low-vc-dimension/](https://win-vector.com/2015/02/14/how-sure-are-you-that-large-margin-implies-low-vc-dimension/)

Here we will show how to check a 3 by 3 matrix for positive definiteness and positive semi-definiteness.

Recreating [A.Γ.](https://math.stackexchange.com/users/253273/a-Γ)'s demonstration ([https://math.stackexchange.com/questions/1355088/is-the-absolute-value-of-a-p-d-s-matrix-p-d-s#comment2758302_1355088](https://math.stackexchange.com/questions/1355088/is-the-absolute-value-of-a-p-d-s-matrix-p-d-s#comment2758302_1355088)) that the absolute value of a 3 by 3 real symmetric positive semi-definite matrix is also positive semi-definite.

First we write down such a matrix, using capitals for positions known to be positive or non-negative (depending if we are checking positive definiteness or positive semidefiniteness).


```python
import sympy
```


```python
sympy.init_printing(use_unicode=True)
```


```python
A, B, C, d, e, f = sympy.symbols('A B C d e f')
```


```python
mat3 = sympy.Matrix([
    [A, d, f], 
    [d, B, e], 
    [f, e, C]])
mat3
```




$\displaystyle \left[\begin{matrix}A & d & f\\d & B & e\\f & e & C\end{matrix}\right]$



Now we use Sylvester's criterion ([https://en.wikipedia.org/wiki/Sylvester%27s_criterion](https://en.wikipedia.org/wiki/Sylvester%27s_criterion)), which states such a matrix is positive definite iff all leading pricipal minors have positive determinant.

First we check the positive definite case. Here we assume `A`, `B`, and `C` are positive and only need to check the initial principal minors.


```python
mat1 = sympy.Matrix([
    [mat3[0,0]]])
mat1
```




$\displaystyle \left[\begin{matrix}A\end{matrix}\right]$




```python
mat2 = sympy.Matrix([
    [mat3[0, 0], mat3[0, 1]], 
    [mat3[1, 0], mat3[1, 1]]])
mat2
```




$\displaystyle \left[\begin{matrix}A & d\\d & B\end{matrix}\right]$




```python
[mat1.det(), mat2.det(), mat3.det()]
```




$\displaystyle \left[ A, \  A B - d^{2}, \  A B C - A e^{2} - B f^{2} - C d^{2} + 2 d e f\right]$



The positive definite case is proved as follows. By assumption all of these terms are positve, we are asking if replacing the symbols `d`, `e`, and `f` with their absolute values (`|d|`, `|e|`, and `|f|`) can cause any of these terms to become non-positive (`A`, `B` and `C` are already known to be positive in this case, so they don't have an interesting replacement). By inspection the only term that can change is the `2 d e f` term, and it at most could only be made larger.

Now let's try the semi-definite case. 

We want to apply

> Prussing, John E. (1986), "The Principal Minor Test for Semidefinite Matrices" ([PDF](https://web.archive.org/web/20170107084552/http://prussing.ae.illinois.edu/semidef.pdf)), Journal of Guidance, Control, and Dynamics, 9 (1): 121–122, archived from the original ([PDF](http://prussing.ae.illinois.edu/semidef.pdf)).

So we change our assumptions from positive to non-negative and have to check more principal minors.


```python
mat1b = sympy.Matrix([
    [mat3[1,1]]])
mat1c = sympy.Matrix([
    [mat3[2,2]]])
mat2b = sympy.Matrix([
    [mat3[0, 0], mat3[0, 2]], 
    [mat3[2, 0], mat3[2, 2]]])
mat2c = sympy.Matrix([
    [mat3[1, 1], mat3[1, 2]], 
    [mat3[2, 1], mat3[2, 2]]])
```

The determinants of the additional pricipal minors are as follows.


```python
[mat1b.det(), mat1c.det(),
 mat2b.det(), mat2c.det()]
```




$\displaystyle \left[ B, \  C, \  A C - f^{2}, \  B C - e^{2}\right]$



By assumption these terms are non-netative. We need to if replacing the symbols `d`, `e`, and `f` with their absolute values (`|d|`, `|e|`, and `|f|`) preserves the non-negativity. The non-negativity of these additional minors follows quickly from the non-negativity of `A`, `B`, and `C`. And we have completed the arguments.


```python

```
