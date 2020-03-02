**Python Data Science Tip: Don't use Default Cross Validation Settings**

Here is a quick, simple, and important tip for doing machine learning, data science, or statistics in Python: don't use the default cross validation settings. The default can default to a deterministic, and even ordered split, which is not in general what one wants or expects from a statistical point of view.  From a software engineering point of view the defaults may be sensible as since they don't touch the pseudo-random number generator they are repeatable, deterministic, and side-effect free.

This issue falls under "read the manual", but it is always frustrating when the defaults are not sufficiently generous.

To see what is going on, let's work an example.


First we import our packages/modules.


```python
import pandas
import numpy
import sklearn
import sklearn.model_selection
from sklearn.base import BaseEstimator, TransformerMixin

sklearn.__version__
```




    '0.21.3'



Now let's set up some simple example data.


```python
nrow = 15
cv = 3
d = pandas.DataFrame({
    'const': ['a'] * nrow,
    'r1': numpy.random.normal(size=nrow),
    'row_id': range(nrow)
})
y = [2**i for i in range(nrow)]

d
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>const</th>
      <th>r1</th>
      <th>row_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>a</td>
      <td>0.231771</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>a</td>
      <td>-0.643458</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>a</td>
      <td>-0.814504</td>
      <td>2</td>
    </tr>
    <tr>
      <th>3</th>
      <td>a</td>
      <td>-1.346967</td>
      <td>3</td>
    </tr>
    <tr>
      <th>4</th>
      <td>a</td>
      <td>2.123949</td>
      <td>4</td>
    </tr>
    <tr>
      <th>5</th>
      <td>a</td>
      <td>-1.543649</td>
      <td>5</td>
    </tr>
    <tr>
      <th>6</th>
      <td>a</td>
      <td>0.427300</td>
      <td>6</td>
    </tr>
    <tr>
      <th>7</th>
      <td>a</td>
      <td>0.376089</td>
      <td>7</td>
    </tr>
    <tr>
      <th>8</th>
      <td>a</td>
      <td>0.562063</td>
      <td>8</td>
    </tr>
    <tr>
      <th>9</th>
      <td>a</td>
      <td>0.503133</td>
      <td>9</td>
    </tr>
    <tr>
      <th>10</th>
      <td>a</td>
      <td>-0.693433</td>
      <td>10</td>
    </tr>
    <tr>
      <th>11</th>
      <td>a</td>
      <td>1.035914</td>
      <td>11</td>
    </tr>
    <tr>
      <th>12</th>
      <td>a</td>
      <td>1.054931</td>
      <td>12</td>
    </tr>
    <tr>
      <th>13</th>
      <td>a</td>
      <td>-0.193353</td>
      <td>13</td>
    </tr>
    <tr>
      <th>14</th>
      <td>a</td>
      <td>-0.145543</td>
      <td>14</td>
    </tr>
  </tbody>
</table>
</div>



We now use `sklearn.model_selection.cross_val_predict` to land some derived columns.  In this case we are going to land the global average the outcome `y` as our estimate.


```python
class CopyYMeanTransform(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.est = 0
        BaseEstimator.__init__(self)
        TransformerMixin.__init__(self)

    def fit(self, X, y):
        self.est = numpy.mean(y)
        return self

    def transform(self, X):
        return [self.est] * X.shape[0]

    def fit_transform(self, X, y):
        self.fit(X, y)
        return self.transform(X)

    def predict(self, X):
        return self.transform(X)

    def fit_predict(self, X, y):
        return self.fit_transform(X, y)

ests = sklearn.model_selection.cross_val_predict(CopyYMeanTransform(), d, y, cv=cv)

ests
```




    array([3273.6, 3273.6, 3273.6, 3273.6, 3273.6, 3177.5, 3177.5, 3177.5,
           3177.5, 3177.5,  102.3,  102.3,  102.3,  102.3,  102.3])



In the result we notice two things:
    
  * The estimate global average varies, it is not a constant.  This is a very important feature of cross validated methods, and something I intend to write more on later.
  * The results seem to be in orderly blocks.  This is implied by the help, but not what one wants or expects in cross validated work.  Structure in the input data may survive the block structure of this cross validation and spoil results.
    
Let's re-encode the output to see what is going on.  We deliberately chose the `y` values to be powers of 2 so `v*(nrow-nrow/cv)` should give us the exact rows used in each calculation as bit positions.  We can view this as follows.


```python
[format(int(v*(nrow-nrow/cv)), '#0' + str(nrow+2) + 'b') for v in ests]
```




    ['0b111111111100000',
     '0b111111111100000',
     '0b111111111100000',
     '0b111111111100000',
     '0b111111111100000',
     '0b111110000011111',
     '0b111110000011111',
     '0b111110000011111',
     '0b111110000011111',
     '0b111110000011111',
     '0b000001111111111',
     '0b000001111111111',
     '0b000001111111111',
     '0b000001111111111',
     '0b000001111111111']



The first row indicates it was derived from all rows except the first 5 (as the 5 lowest bit positions are zero).  In fact the first five rows are all calculated in this manner.  So we have 3-way cross validation (each row is calculated using 2/3rds of the data), but in consecutive blocks.

This happens because [`sklearn.model_selection.cross_val_predict`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.cross_val_predict.html) defaults to using one of [`klearn.model_selection.KFold.html`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.KFold.html#sklearn.model_selection.KFold) [`sklearn.model_selection.StratifiedKFold`](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedKFold.html#sklearn.model_selection.StratifiedKFold). These in turn both default to `shuffle=False`, which explains the observed behavior.

This is "as expected" in the sense it is clearly documented.  It is however, not how a statistician would expect k-fold cross validation to work for a small k.

The solution is, as documented, avoid the default by explicitly setting the cross validation strategy.  We demonstrate this here.


```python
cvstrat = sklearn.model_selection.KFold(shuffle=True, n_splits=3)
ests = sklearn.model_selection.cross_val_predict(CopyYMeanTransform(), d, y, cv=cvstrat)

[format(int(v*(nrow-nrow/cv)), '#0' + str(nrow+2) + 'b') for v in ests]
```




    ['0b111111101110000',
     '0b111111101110000',
     '0b111111101110000',
     '0b111111101110000',
     '0b111010010101111',
     '0b000101111011111',
     '0b111010010101111',
     '0b111111101110000',
     '0b111010010101111',
     '0b111010010101111',
     '0b000101111011111',
     '0b111010010101111',
     '0b000101111011111',
     '0b000101111011111',
     '0b000101111011111']



This is still a 3-fold cross validation strategy as there are only 3 distinct calculations made.  However the arrangement is now random subject to the important constraint that the `i`-th row is not in input to the `i`-th result.

We can also confirm that the shuffle option suffles the cross-validation plan, and not the data set rows.


```python
class CopyXTransform(BaseEstimator, TransformerMixin):
    def __init__(self):
        BaseEstimator.__init__(self)
        TransformerMixin.__init__(self)

    def fit(self, X, y):
        return self

    def transform(self, X):
        return X.copy()

    def fit_transform(self, X, y):
        self.fit(X, y)
        return self.transform(X)

    def predict(self, X):
        return self.transform(X)

    def fit_predict(self, X, y):
        return self.fit_transform(X, y)

sklearn.model_selection.cross_val_predict(CopyXTransform(), d, y, cv=cvstrat)
```




    array([['a', 0.2317708416646105, 0],
           ['a', -0.6434576761630608, 1],
           ['a', -0.8145042224405192, 2],
           ['a', -1.346967064864293, 3],
           ['a', 2.1239493751828085, 4],
           ['a', -1.543648551466407, 5],
           ['a', 0.42730030589837925, 6],
           ['a', 0.37608917089238997, 7],
           ['a', 0.5620629364384716, 8],
           ['a', 0.5031329594694133, 9],
           ['a', -0.6934327743260298, 10],
           ['a', 1.0359136201260202, 11],
           ['a', 1.0549306824041969, 12],
           ['a', -0.19335275803764576, 13],
           ['a', -0.14554310090071113, 14]], dtype=object)



The `CopyXTransform` copied out the input data in its original order, confirming shuffle shuffles the plan not the data rows.

And that concludes our tip: don't use default cross validation settings.


```python

```

