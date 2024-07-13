Linear Model Transfer with Categorical Variables
================
Nina Zumel
2024-07-08

In our main article, we showed an example of transferring the weights
from one linear model to another one, without retraining on the original
data. In order to do that, we fit a new model to a full rank set of
rows, using the predictions of the original model on our new evaluation
set as the outcome.

When all the variables are continuous, then the number of rows we need
is the number of variables plus one, for the intercept. This is the
number of coefficients in the model. If $n_{var}$ is the number of
variables, then an easy evaluation matrix to use is the
$n_{var}$-dimensional identity matrix, with a row of all zeros appended
to “represent” the intercept. This representation assumes an implicit
all ones column for the intercept; if you are transferring the model to
a framework that needs the intercept column explicitly, you’d need to
add a column of all ones explicitly.

When some of the variables are categorical, the process is slightly more
involved.

``` r
library(Matrix)
```

## One categorical variable

For our first example, we’ll use the `iris` dataset and fit sepal length
as a function of sepal width, petal length, and species. There are three
species represented: *setosa*, *versicolor*, and *virginica*.

First let’s fit a model.

``` r
iris = iris
summary(iris)
```

    ##   Sepal.Length    Sepal.Width     Petal.Length    Petal.Width   
    ##  Min.   :4.300   Min.   :2.000   Min.   :1.000   Min.   :0.100  
    ##  1st Qu.:5.100   1st Qu.:2.800   1st Qu.:1.600   1st Qu.:0.300  
    ##  Median :5.800   Median :3.000   Median :4.350   Median :1.300  
    ##  Mean   :5.843   Mean   :3.057   Mean   :3.758   Mean   :1.199  
    ##  3rd Qu.:6.400   3rd Qu.:3.300   3rd Qu.:5.100   3rd Qu.:1.800  
    ##  Max.   :7.900   Max.   :4.400   Max.   :6.900   Max.   :2.500  
    ##        Species  
    ##  setosa    :50  
    ##  versicolor:50  
    ##  virginica :50  
    ##                 
    ##                 
    ## 

``` r
# fit on two continuous vars for now
model = lm(Sepal.Length ~ Sepal.Width + Petal.Length + Species, data=iris)
coef(model)
```

    ##       (Intercept)       Sepal.Width      Petal.Length Speciesversicolor 
    ##         2.3903891         0.4322172         0.7756295        -0.9558123 
    ##  Speciesvirginica 
    ##        -1.3940979

Now we want to transfer the weights from this model to another one,
without retraining on the original data. Since our model has 5
coefficients, we know we need 5 rows. But let’s count them out
explicitly.

- 1 row for the intercept
- 2 rows for the two continuous variables
- `nlevels(Species)` - 1 = 3 - 1 = 2 rows for the categorical variable
  `Species`

1 + 2 + 2 = 5.

In R (and in most other linear modeling frameworks), by default, one
level from each categorical variable is folded into the intercept term
as a “reference level”: sort of the categorical equivalent of the
origin. So rather than a reference row of all zeros to represent the
intercept, we need a row of all zeros (for the continuous variables),
*plus* the reference levels.

In R, you either specify the categorical levels directly, or build the
model matrix directly. In python, you’d need to use the appropriate
one-hot encoded representation, which (in R parlance) is building the
model matrix directly.

The reference level of a categorical variable is generally the
orthographically first one. This is true in R; you can use the
`relevel()` command to change it. In any event, make sure to use the
same reference levels as the original model.

In this case, *setosa* is the reference level for `Species`.

``` r
evalframe = wrapr::build_frame(
  'Sepal.Width', 'Petal.Length', 'Species' |
              0,              0,  'setosa' |  # intercept plus reference level
              1,              0,  'setosa' |
              0,              1,  'setosa' |
              0,              0,  'versicolor' |
              0,              0,  'virginica'
)

# attach predictions from the original model
evalframe$Sepal.Length = predict(model, newdata=evalframe)

# look at the model matrix and confirm it's full rank.
m = model.matrix(Sepal.Length ~ Sepal.Width + Petal.Length + Species, evalframe)
m
```

    ##   (Intercept) Sepal.Width Petal.Length Speciesversicolor Speciesvirginica
    ## 1           1           0            0                 0                0
    ## 2           1           1            0                 0                0
    ## 3           1           0            1                 0                0
    ## 4           1           0            0                 1                0
    ## 5           1           0            0                 0                1
    ## attr(,"assign")
    ## [1] 0 1 2 3 3
    ## attr(,"contrasts")
    ## attr(,"contrasts")$Species
    ## [1] "contr.treatment"

``` r
# assert that the model is full rank
stopifnot(rankMatrix(m)[1] == nrow(m))
```

We’ve confirmed that the model matrix for the evaluation frame is full
rank. Now we fit another `lm` to the evaluation frame.

``` r
portmod = lm(Sepal.Length ~ Sepal.Width + Petal.Length + Species, data=evalframe)

data.frame(
  ported_model = coef(portmod),
  original_model = coef(model)
)
```

    ##                   ported_model original_model
    ## (Intercept)          2.3903891      2.3903891
    ## Sepal.Width          0.4322172      0.4322172
    ## Petal.Length         0.7756295      0.7756295
    ## Speciesversicolor   -0.9558123     -0.9558123
    ## Speciesvirginica    -1.3940979     -1.3940979

The coefficients are the same as the original model fit to the iris
data.

## More than one categorical variable

In this example, we’ll predict the ascorbic acid (vitamin C) content of
cabbages as a function of: their weight (continuous variable), their
cultivar (categorical with two values: `c39` and `c52`) and their
planting date (categorical with three values: `d16`, `d20`, `d21`).

``` r
library(MASS) # to get the data

cabbages = cabbages
summary(cabbages)
```

    ##   Cult     Date        HeadWt           VitC      
    ##  c39:30   d16:20   Min.   :1.000   Min.   :41.00  
    ##  c52:30   d20:20   1st Qu.:1.875   1st Qu.:50.75  
    ##           d21:20   Median :2.550   Median :56.00  
    ##                    Mean   :2.593   Mean   :57.95  
    ##                    3rd Qu.:3.125   3rd Qu.:66.25  
    ##                    Max.   :4.300   Max.   :84.00

``` r
model = lm(VitC ~ HeadWt + Date + Cult, data=cabbages)
coef(model)
```

    ## (Intercept)      HeadWt     Dated20     Dated21     Cultc52 
    ##   63.333953   -4.412292   -1.213111    4.186440   10.134964

To port the model, let’s walk through the number of rows we need:

- 1 for the intercept
- 1 for the continuous variable `HeadWt`
- `nlevels(Date)` - 1 = 3 - 1 = 2 for the categorical variable `Date`
  (the reference level is `d16`)
- `nlevels(Cult)` - 1 = 2 - 1 = 1 for the categorical variable `Cult`
  (the reference level is `c39`)

1 + 1 + 2 + 1 = 5.

``` r
evalframe = wrapr::build_frame(
  'Cult', 'Date', 'HeadWt' |
    'c39', 'd16',   0 |  # intercept plus reference levels
    'c39', 'd16',   1 |  # HeadWt is 1, everything else is "0"
    'c52', 'd16',   0 |  # Cultc52 is 1, everything else is "0"
    'c39', 'd20',   0 |  # Dated20 is 1, everything else is "0"
    'c39', 'd21',   0    # Dated21 is 1, everything else is "0"
)

# attach predictions from the original model
evalframe$VitC = predict(model, newdata=evalframe)

# look at the model matrix and confirm it's full rank.
m = model.matrix(VitC ~ HeadWt + Date + Cult, evalframe)
m
```

    ##   (Intercept) HeadWt Dated20 Dated21 Cultc52
    ## 1           1      0       0       0       0
    ## 2           1      1       0       0       0
    ## 3           1      0       0       0       1
    ## 4           1      0       1       0       0
    ## 5           1      0       0       1       0
    ## attr(,"assign")
    ## [1] 0 1 2 2 3
    ## attr(,"contrasts")
    ## attr(,"contrasts")$Date
    ## [1] "contr.treatment"
    ## 
    ## attr(,"contrasts")$Cult
    ## [1] "contr.treatment"

``` r
# assert that the model is full rank
stopifnot(rankMatrix(m)[1] == nrow(m))
```

The model matrix is full rank, so let’s fit another `lm` to the
evaluation frame.

``` r
portmod = lm(VitC ~ HeadWt + Date + Cult, data=evalframe)

data.frame(
  ported_model = coef(portmod),
  original_model = coef(model)
)
```

    ##             ported_model original_model
    ## (Intercept)    63.333953      63.333953
    ## HeadWt         -4.412292      -4.412292
    ## Dated20        -1.213111      -1.213111
    ## Dated21         4.186440       4.186440
    ## Cultc52        10.134964      10.134964

The coefficients of the ported model are the same as the original model
fit to the cabbages data.
