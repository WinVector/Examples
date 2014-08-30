
Java code implementing the zero/one (or even/odd) integer solution counting technique from:

@article{CPC:54639,
author = {MOUNT,JOHN},
title = {Fast Unimodular Counting},
journal = {Combinatorics, Probability and Computing},
volume = {9},
issue = {03},
month = {5},
year = {2000},
issn = {1469-2163},
pages = {277--285},
numpages = {9},
doi = {null},
URL = {http://journals.cambridge.org/article_S0963548300004193},
}

A note on the run time:

The Zero/One Method claims a run-time of no more than 2^{O(m log n)} log B steps.  The way to establish this is as follows.  

For simplicity we are trying to find the number of non-negative integer solutions to A x = b where A is a non-negative totally unimodular matrix (with no zero columns).  Let m be the number of rows of our matrix and n the number of columns.  Let B = max(abs(b_i)).  

Let's look at what new right-hand sides b' the Zero/One method can generate as it recurses over its dynamic programming plan.  Each new b' is generate from an old b by subtracting of A z (for some 0/1 vector z) and then dividing by 2 (with integer results).   If we consider our new right hand side b' as being formed by b/2^k - sum_{i=1...k} (A z(i,j))/2_i + rounding.  We can get a crude bound on how many possible b' there are.  Clearly k doesn't get past log(B) (at which point b'=0 and we hit a base-case of one solution).   The second part is that the A z(i,j) are always no more than n (the number of columns of A) so sum_{i=1...k} (A z(i,j))/2_i (since it is an integer) is always a value between 0 and -n (n/2 + n/4 ... not exceeding n). 

So the vector b' is always composed of the vector b/2^k (which only has log B possible values) plus an m-vector of integer noise terms which all have absolute magnitude no more than n+1.  So the noising vector has at most (n+1)^m possible values and we only recurse to depth log B. So there is no way to form more than 2^m (n+2)^m log B possible combination so b/2^k minus sum_{i=1...k} (A z(i))/2_i even after taking rounding into account.

Each recursion step certainly inspects no more than 2^n new solution patterns so a run-time like 2^n 2^m (n+2)^m log B is certainly possible.  We can strengthen this by building a dynamic programming solution for the zero/one problems (in addition to the non-negative integer problems) replacing the 2^n term with possibly another n^m style term.  

The long and short of it is a run-time of c (n+2)^(2 m + a) m^b log B is easily achievable (a,b,c all being small constants, like 2).  The structure of this run-time is roughly 2^{O(m log n)} log B.  Which means we are exponential in the number of constraints being checked, pseudo-polynomial in the number of variables and linear in the logarithm of the largest number in the problem.  This is much stronger than naive methods which are going to be of complexity B^n (exponential in n, which tends to be larger than m for contingency tables and  polynomial in B for fixed n, not log B).  When we combined our result with our polyhedral cone techniques we can remove the dependence on B entirely (under a number of arithmetic steps model, allowing us to manipulate integers of magnitude B^n in unit time).

What we want to emphasize is these are very good run-times and not the same run-times as seen in some other work.


