
Why dot-product is in fact a Mercer Kernel.

Here are some new notes on what is and what is not a Mercer Kernel style
function.

-   `abs(x dot y)` and `relu(x dot y)` are not in general Mercer Kernels
    <https://github.com/WinVector/Examples/blob/main/Mercer_kernel/Mercer_Kernel.md>.
-   How to check if a 3 by 3 matrix is positive (semi) definite
    <https://github.com/WinVector/Examples/blob/main/Mercer_kernel/Dets.ipynb>.
-   Why dot product is a Mercer Kernel
    <https://github.com/WinVector/Examples/blob/main/Mercer_kernel/dot.md>.


First this is almost by definition.  We can define a Mercer Kernel
in one of two equivalent manners.

  * A two argument map from `R^k` to `R` is a Mercer kernel if for any vectors `a1`, `a2`, ..., `an` the `n` by `n` Gram matrix `G` such that `G[i, j] = ai dot aj` is positive semi-definite.
  * There is a function phi from `R^k` to some (possibly infinite) vector space such that `K(a, b) = <phi(a), phi(b)>` (`<,>` being the inner product on the range space).

The equivalence being the content of Mercer's theorem and reproducing kernel Hilbert spaces.

Now the notation is so onerous, it becomes hard to see why the dot product itself is "obviously" a Mercer Kernel under the first definition (it is just a statement of the second definition, so that is considered "obvious").

Let's take moment to work through this.

The first definition check conditions are checking the sign of `transpose(x) G x` for all vectors in `R^n`. `G` itself is `transpose(A) A` where `A` is the `k`-row by `n`-columns matrix with the `j`-th column being the vector `aj`.

So we are interested in `transpose(x) transpose(A) A x`. But this is equal to `transpose(A x) . (A x)`. This in turn is just the 2-norm of `A x`, which is known to be non-negative.
