
R markdown or "knitr" files to produce the Win-Vector LLC articles:

 * [XonlyPCA.Rmd](XonlyPCA.Rmd) [Principal Components Regression, Pt. 1: The Standard Method](http://www.win-vector.com/blog/2016/05/pcr_part1_xonly/) 
 * [YAwarePCA.Rmd](YAwarePCA.Rmd) [Principal Components Regression, Pt. 2: Y-Aware Methods](http://www.win-vector.com/blog/2016/05/pcr_part2_yaware/) 
 * YAwarePCR_pickK.Rmd Principal Components Regression, Pt. 3: Picking the number of components  , coming soon

If you are trying to download the worksheets from [here](https://github.com/WinVector/Examples/tree/master/PCR) we have (with the help of reader feedback) worked on some instructions to help through the install process [http://www.win-vector.com/blog/2016/05/installing-wvplots-and-knitting-r-markdown/](http://www.win-vector.com/blog/2016/05/installing-wvplots-and-knitting-r-markdown/).


------------------------------------------------------------------------

Win-Vector LLC's Dr. Nina Zumel has a three part series on
Principal Components Regression that we think is well worth your time.

------------------------------------------------------------------------

You can read her first article
[part 1 here](http://www.win-vector.com/blog/2016/05/pcr_part1_xonly).
Principal Components Regression (PCR) is the use of Principal Components
Analysis (PCA) as a dimension reduction step prior to linear regression.
It is one of the best known dimensionality reduction techniques and a
staple procedure in many scientific fields. PCA is used because:

-   It can find important latent structure and relations.
-   It can reduce over fit.
-   It can ease the curse of dimensionality.
-   It is used in a ritualistic manner in many scientific disciplines.
    In some fields it is considered ignorant and uncouth to regress
    using original variables.

We often find ourselves having to often remind readers that this last
reason is not actually positive. The standard derivation of PCA involves
trotting out the math and showing the determination of eigenvector
directions. It yields visually attractive diagrams such as the
following.

[![GaussianScatterPCA
svg](http://www.win-vector.com/blog/wp-content/uploads/2016/05/GaussianScatterPCA.svg_.png "GaussianScatterPCA.svg.png")](https://en.wikipedia.org/wiki/Principal_component_analysis#/media/File:GaussianScatterPCA.svg)

Wikipedia: PCA

And this leads to a deficiency in much of the teaching of the method:
glossing over the operational consequences and outcomes of applying the
method. The mathematics is important to the extent it allows you to
reason about the appropriateness of the method, the consequences of the
transform, and the pitfalls of the technique. The mathematics is also
critical to the correct implementation, but that is what one hopes is
*already* supplied in a reliable analysis platform (such as
[R](https://cran.r-project.org)). Dr. Zumel uses the expressive and
graphical power of R to work through the *use* of Principal Components
Regression in an operational series of examples. She works through how
Principal Components Regression is typically mis-applied and continues
on to how to correctly apply it. Taking the extra time to work through
the all too common errors allows her to demonstrate and quantify the
benefits of correct technique. Dr. Zumel will soon follow [part
1](http://www.win-vector.com/blog/2016/05/pcr_part1_xonly) later with a
shorter part 2 article demonstrating important "*y*-aware" techniques
that squeeze much more modeling power out of your data in predictive
analytic situations (which is what regression actually is). Some of the
methods are already in the literature, but are still not used widely
enough. We hope the demonstrated techniques and included references will
give you a perspective to improve how you use or even teach Principal
Components Regression. Please read on
[here](http://www.win-vector.com/blog/2016/05/pcr_part1_xonly).

------------------------------------------------------------------------

In [part 2](http://www.win-vector.com/blog/2016/05/pcr_part2_yaware) of
her series on Principal Components Regression Dr. Nina Zumel illustrates
so-called *y*-aware techniques. These often neglected methods use the
fact that for predictive modeling problems we know the dependent
variable, outcome or *y*, so we can use this during data preparation *in
addition to* using it during modeling. Dr. Zumel shows the incorporation
of *y*-aware preparation into Principal Components Analyses can capture
more of the problem structure in fewer variables. Such methods include:

-   Effects based variable pruning
-   Significance based variable pruning
-   Effects based variable scaling.

This recovers more domain structure and leads to better models. Using
the foundation set in the first article Dr. Zumel quickly shows how to
move from a traditional *x*-only analysis that fails to preserve a
domain-specific relation of two variables to outcome to a *y*-aware
analysis that preserves the relation. Or in other words how to move away
from a middling result where different values of y (rendered as three
colors) are hopelessly intermingled when plotted against the first two
found latent variables as shown below.
![NewImage](http://www.win-vector.com/blog/wp-content/uploads/2016/05/NewImage-1.png "NewImage.png")
Dr. Zumel shows how to perform a decisive analysis where *y* is somewhat
sortable by the each of the first two latent variable *and* the first
two latent variables capture complementary effects, making them good
mutual candidates for further modeling (as shown below).
![NewImage](http://www.win-vector.com/blog/wp-content/uploads/2016/05/NewImage.png "NewImage.png")
Click [here (part 2 *y*-aware
methods)](http://www.win-vector.com/blog/2016/05/pcr_part2_yaware) for
the discussion, examples, and references. Part 1 (*x* only methods) can
be found [here](http://www.win-vector.com/blog/2016/05/pcr_part1_xonly).

------------------------------------------------------------------------

Part 3: picking the number of components is coming soon.
