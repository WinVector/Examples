```python
import pandas as pd
from vtreat.stats_utils import xicor

peas = pd.read_csv('peas.tsv', sep='\t')
peas

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
      <th>parent</th>
      <th>child</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>21</td>
      <td>14.67</td>
    </tr>
    <tr>
      <th>1</th>
      <td>21</td>
      <td>14.67</td>
    </tr>
    <tr>
      <th>2</th>
      <td>21</td>
      <td>14.67</td>
    </tr>
    <tr>
      <th>3</th>
      <td>21</td>
      <td>14.67</td>
    </tr>
    <tr>
      <th>4</th>
      <td>21</td>
      <td>14.67</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>695</th>
      <td>15</td>
      <td>18.77</td>
    </tr>
    <tr>
      <th>696</th>
      <td>15</td>
      <td>18.77</td>
    </tr>
    <tr>
      <th>697</th>
      <td>15</td>
      <td>18.77</td>
    </tr>
    <tr>
      <th>698</th>
      <td>15</td>
      <td>19.77</td>
    </tr>
    <tr>
      <th>699</th>
      <td>15</td>
      <td>19.77</td>
    </tr>
  </tbody>
</table>
<p>700 rows × 2 columns</p>
</div>



### Replicate The Peas Experiment from the XICOR paper

The `xicor` call returns the mean estimated XI coefficient, and the standard error of the estimate.


```python
# xi(X, Y)
xicor(peas.parent, peas.child, n_reps=10000)
```




    (0.11088906234252008, 0.0002359534732067584)




```python
# xi(Y, X)
xicor(peas.child, peas.parent, n_reps=10000)
```




    (0.9224999999999998, 2.220446049250313e-18)




```python

```
