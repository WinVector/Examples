# Pandas/Polars Rosetta Stone

Polars equivalents of common pandas operations.

* [Handy polars reference](https://pola-rs.github.io/polars-book/user-guide/introduction.html).
* [Polars API reference](https://pola-rs.github.io/polars/py-polars/html/reference/index.html)


Thanks to [deanm0000](https://github.com/deanm0000) for helpful comments/corrections.


```python

import numpy as np
import pandas as pd
import polars as pl

from palmerpenguins import load_penguins
```


```python
print(f'pandas version {pd.__version__}')
print(f'polars version {pl.__version__}')
```

    pandas version 1.4.4
    polars version 0.17.0


## Load the data

Penguins dataset

### pandas


```python
peng_pd = load_penguins()
peng_pd
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
      <th>species</th>
      <th>island</th>
      <th>bill_length_mm</th>
      <th>bill_depth_mm</th>
      <th>flipper_length_mm</th>
      <th>body_mass_g</th>
      <th>sex</th>
      <th>year</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>39.1</td>
      <td>18.7</td>
      <td>181.0</td>
      <td>3750.0</td>
      <td>male</td>
      <td>2007</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>39.5</td>
      <td>17.4</td>
      <td>186.0</td>
      <td>3800.0</td>
      <td>female</td>
      <td>2007</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>40.3</td>
      <td>18.0</td>
      <td>195.0</td>
      <td>3250.0</td>
      <td>female</td>
      <td>2007</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2007</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>36.7</td>
      <td>19.3</td>
      <td>193.0</td>
      <td>3450.0</td>
      <td>female</td>
      <td>2007</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>339</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>55.8</td>
      <td>19.8</td>
      <td>207.0</td>
      <td>4000.0</td>
      <td>male</td>
      <td>2009</td>
    </tr>
    <tr>
      <th>340</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>43.5</td>
      <td>18.1</td>
      <td>202.0</td>
      <td>3400.0</td>
      <td>female</td>
      <td>2009</td>
    </tr>
    <tr>
      <th>341</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>49.6</td>
      <td>18.2</td>
      <td>193.0</td>
      <td>3775.0</td>
      <td>male</td>
      <td>2009</td>
    </tr>
    <tr>
      <th>342</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>50.8</td>
      <td>19.0</td>
      <td>210.0</td>
      <td>4100.0</td>
      <td>male</td>
      <td>2009</td>
    </tr>
    <tr>
      <th>343</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>50.2</td>
      <td>18.7</td>
      <td>198.0</td>
      <td>3775.0</td>
      <td>female</td>
      <td>2009</td>
    </tr>
  </tbody>
</table>
<p>344 rows × 8 columns</p>
</div>



### polars


```python
peng_pl = pl.from_pandas(peng_pd)
peng_pl
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (344, 8)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>island</th><th>bill_length_mm</th><th>bill_depth_mm</th><th>flipper_length_mm</th><th>body_mass_g</th><th>sex</th><th>year</th></tr><tr><td>str</td><td>str</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>str</td><td>i64</td></tr></thead><tbody><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.1</td><td>18.7</td><td>181.0</td><td>3750.0</td><td>&quot;male&quot;</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.5</td><td>17.4</td><td>186.0</td><td>3800.0</td><td>&quot;female&quot;</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>40.3</td><td>18.0</td><td>195.0</td><td>3250.0</td><td>&quot;female&quot;</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>36.7</td><td>19.3</td><td>193.0</td><td>3450.0</td><td>&quot;female&quot;</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.3</td><td>20.6</td><td>190.0</td><td>3650.0</td><td>&quot;male&quot;</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>38.9</td><td>17.8</td><td>181.0</td><td>3625.0</td><td>&quot;female&quot;</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.2</td><td>19.6</td><td>195.0</td><td>4675.0</td><td>&quot;male&quot;</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>34.1</td><td>18.1</td><td>193.0</td><td>3475.0</td><td>null</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>42.0</td><td>20.2</td><td>190.0</td><td>4250.0</td><td>null</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>37.8</td><td>17.1</td><td>186.0</td><td>3300.0</td><td>null</td><td>2007</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>37.8</td><td>17.3</td><td>180.0</td><td>3700.0</td><td>null</td><td>2007</td></tr><tr><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.2</td><td>16.6</td><td>191.0</td><td>3250.0</td><td>&quot;female&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>49.3</td><td>19.9</td><td>203.0</td><td>4050.0</td><td>&quot;male&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.2</td><td>18.8</td><td>202.0</td><td>3800.0</td><td>&quot;male&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.6</td><td>19.4</td><td>194.0</td><td>3525.0</td><td>&quot;female&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>51.9</td><td>19.5</td><td>206.0</td><td>3950.0</td><td>&quot;male&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>46.8</td><td>16.5</td><td>189.0</td><td>3650.0</td><td>&quot;female&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.7</td><td>17.0</td><td>195.0</td><td>3650.0</td><td>&quot;female&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>55.8</td><td>19.8</td><td>207.0</td><td>4000.0</td><td>&quot;male&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>43.5</td><td>18.1</td><td>202.0</td><td>3400.0</td><td>&quot;female&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>49.6</td><td>18.2</td><td>193.0</td><td>3775.0</td><td>&quot;male&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.8</td><td>19.0</td><td>210.0</td><td>4100.0</td><td>&quot;male&quot;</td><td>2009</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.2</td><td>18.7</td><td>198.0</td><td>3775.0</td><td>&quot;female&quot;</td><td>2009</td></tr></tbody></table></div>



## Inspect the data frame

### pandas


```python
print(peng_pd.shape)
print (peng_pd.columns)
peng_pd.describe()
```

    (344, 8)
    Index(['species', 'island', 'bill_length_mm', 'bill_depth_mm',
           'flipper_length_mm', 'body_mass_g', 'sex', 'year'],
          dtype='object')





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
      <th>bill_length_mm</th>
      <th>bill_depth_mm</th>
      <th>flipper_length_mm</th>
      <th>body_mass_g</th>
      <th>year</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>count</th>
      <td>342.000000</td>
      <td>342.000000</td>
      <td>342.000000</td>
      <td>342.000000</td>
      <td>344.000000</td>
    </tr>
    <tr>
      <th>mean</th>
      <td>43.921930</td>
      <td>17.151170</td>
      <td>200.915205</td>
      <td>4201.754386</td>
      <td>2008.029070</td>
    </tr>
    <tr>
      <th>std</th>
      <td>5.459584</td>
      <td>1.974793</td>
      <td>14.061714</td>
      <td>801.954536</td>
      <td>0.818356</td>
    </tr>
    <tr>
      <th>min</th>
      <td>32.100000</td>
      <td>13.100000</td>
      <td>172.000000</td>
      <td>2700.000000</td>
      <td>2007.000000</td>
    </tr>
    <tr>
      <th>25%</th>
      <td>39.225000</td>
      <td>15.600000</td>
      <td>190.000000</td>
      <td>3550.000000</td>
      <td>2007.000000</td>
    </tr>
    <tr>
      <th>50%</th>
      <td>44.450000</td>
      <td>17.300000</td>
      <td>197.000000</td>
      <td>4050.000000</td>
      <td>2008.000000</td>
    </tr>
    <tr>
      <th>75%</th>
      <td>48.500000</td>
      <td>18.700000</td>
      <td>213.000000</td>
      <td>4750.000000</td>
      <td>2009.000000</td>
    </tr>
    <tr>
      <th>max</th>
      <td>59.600000</td>
      <td>21.500000</td>
      <td>231.000000</td>
      <td>6300.000000</td>
      <td>2009.000000</td>
    </tr>
  </tbody>
</table>
</div>



### polars


```python
print(peng_pl.shape)
print(peng_pl.columns)
peng_pl.describe()
```

    (344, 8)
    ['species', 'island', 'bill_length_mm', 'bill_depth_mm', 'flipper_length_mm', 'body_mass_g', 'sex', 'year']





<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (7, 9)</small><table border="1" class="dataframe"><thead><tr><th>describe</th><th>species</th><th>island</th><th>bill_length_mm</th><th>bill_depth_mm</th><th>flipper_length_mm</th><th>body_mass_g</th><th>sex</th><th>year</th></tr><tr><td>str</td><td>str</td><td>str</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>str</td><td>f64</td></tr></thead><tbody><tr><td>&quot;count&quot;</td><td>&quot;344&quot;</td><td>&quot;344&quot;</td><td>344.0</td><td>344.0</td><td>344.0</td><td>344.0</td><td>&quot;344&quot;</td><td>344.0</td></tr><tr><td>&quot;null_count&quot;</td><td>&quot;0&quot;</td><td>&quot;0&quot;</td><td>2.0</td><td>2.0</td><td>2.0</td><td>2.0</td><td>&quot;11&quot;</td><td>0.0</td></tr><tr><td>&quot;mean&quot;</td><td>null</td><td>null</td><td>43.92193</td><td>17.15117</td><td>200.915205</td><td>4201.754386</td><td>null</td><td>2008.02907</td></tr><tr><td>&quot;std&quot;</td><td>null</td><td>null</td><td>5.459584</td><td>1.974793</td><td>14.061714</td><td>801.954536</td><td>null</td><td>0.818356</td></tr><tr><td>&quot;min&quot;</td><td>&quot;Adelie&quot;</td><td>&quot;Biscoe&quot;</td><td>32.1</td><td>13.1</td><td>172.0</td><td>2700.0</td><td>&quot;female&quot;</td><td>2007.0</td></tr><tr><td>&quot;max&quot;</td><td>&quot;Gentoo&quot;</td><td>&quot;Torgersen&quot;</td><td>59.6</td><td>21.5</td><td>231.0</td><td>6300.0</td><td>&quot;male&quot;</td><td>2009.0</td></tr><tr><td>&quot;median&quot;</td><td>null</td><td>null</td><td>44.45</td><td>17.3</td><td>197.0</td><td>4050.0</td><td>null</td><td>2008.0</td></tr></tbody></table></div>



## Select a column

### pandas

Selecting a column returns a `pandas.Series`


```python
# select a series
peng_pd['species']
```




    0         Adelie
    1         Adelie
    2         Adelie
    3         Adelie
    4         Adelie
             ...    
    339    Chinstrap
    340    Chinstrap
    341    Chinstrap
    342    Chinstrap
    343    Chinstrap
    Name: species, Length: 344, dtype: object



### polars

You can select with indexing, but expressions are the preferred way, because this allows lazy evaluation.


```python
peng_pl.select('species')
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (344, 1)</small><table border="1" class="dataframe"><thead><tr><th>species</th></tr><tr><td>str</td></tr></thead><tbody><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&quot;Adelie&quot;</td></tr><tr><td>&hellip;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td></tr></tbody></table></div>



## Select a subset

That is, rows and columns.

### pandas


```python
# select a subset
peng_pd.loc[peng_pd['species']=='Chinstrap', ['species', 'island','body_mass_g']].reset_index(drop=True, inplace=False)
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
      <th>species</th>
      <th>island</th>
      <th>body_mass_g</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>3500.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>3900.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>3650.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>3525.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>3725.0</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>63</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>4000.0</td>
    </tr>
    <tr>
      <th>64</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>3400.0</td>
    </tr>
    <tr>
      <th>65</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>3775.0</td>
    </tr>
    <tr>
      <th>66</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>4100.0</td>
    </tr>
    <tr>
      <th>67</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>3775.0</td>
    </tr>
  </tbody>
</table>
<p>68 rows × 3 columns</p>
</div>



### polars

This works, too:
```
peng_pl.filter(pl.col("species") == "Chinstrap").select(
    "species", "island", "body_mass_g"
)

```


```python
peng_pl.filter(pl.col('species')=='Chinstrap').select(['species', 'island','body_mass_g'])
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (68, 3)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>island</th><th>body_mass_g</th></tr><tr><td>str</td><td>str</td><td>f64</td></tr></thead><tbody><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3500.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3900.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3650.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3525.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3725.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3950.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3250.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3750.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>4150.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3700.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3800.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3775.0</td></tr><tr><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3250.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>4050.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3800.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3525.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3950.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3650.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3650.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>4000.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3400.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3775.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>4100.0</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>3775.0</td></tr></tbody></table></div>



## Do some math

Multiply two columns together and put the result back in the frame.

### pandas


```python

peng_pd['bill_volume'] = peng_pd['bill_length_mm']*peng_pd['bill_depth_mm']
peng_pd
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
      <th>species</th>
      <th>island</th>
      <th>bill_length_mm</th>
      <th>bill_depth_mm</th>
      <th>flipper_length_mm</th>
      <th>body_mass_g</th>
      <th>sex</th>
      <th>year</th>
      <th>bill_volume</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>39.1</td>
      <td>18.7</td>
      <td>181.0</td>
      <td>3750.0</td>
      <td>male</td>
      <td>2007</td>
      <td>731.17</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>39.5</td>
      <td>17.4</td>
      <td>186.0</td>
      <td>3800.0</td>
      <td>female</td>
      <td>2007</td>
      <td>687.30</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>40.3</td>
      <td>18.0</td>
      <td>195.0</td>
      <td>3250.0</td>
      <td>female</td>
      <td>2007</td>
      <td>725.40</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2007</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>36.7</td>
      <td>19.3</td>
      <td>193.0</td>
      <td>3450.0</td>
      <td>female</td>
      <td>2007</td>
      <td>708.31</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>339</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>55.8</td>
      <td>19.8</td>
      <td>207.0</td>
      <td>4000.0</td>
      <td>male</td>
      <td>2009</td>
      <td>1104.84</td>
    </tr>
    <tr>
      <th>340</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>43.5</td>
      <td>18.1</td>
      <td>202.0</td>
      <td>3400.0</td>
      <td>female</td>
      <td>2009</td>
      <td>787.35</td>
    </tr>
    <tr>
      <th>341</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>49.6</td>
      <td>18.2</td>
      <td>193.0</td>
      <td>3775.0</td>
      <td>male</td>
      <td>2009</td>
      <td>902.72</td>
    </tr>
    <tr>
      <th>342</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>50.8</td>
      <td>19.0</td>
      <td>210.0</td>
      <td>4100.0</td>
      <td>male</td>
      <td>2009</td>
      <td>965.20</td>
    </tr>
    <tr>
      <th>343</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>50.2</td>
      <td>18.7</td>
      <td>198.0</td>
      <td>3775.0</td>
      <td>female</td>
      <td>2009</td>
      <td>938.74</td>
    </tr>
  </tbody>
</table>
<p>344 rows × 9 columns</p>
</div>



### polars


```python
# new one

peng_pl = peng_pl.with_columns(
   biil_volume=pl.col("bill_length_mm") * pl.col("bill_depth_mm")
)

peng_pl

```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (344, 9)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>island</th><th>bill_length_mm</th><th>bill_depth_mm</th><th>flipper_length_mm</th><th>body_mass_g</th><th>sex</th><th>year</th><th>biil_volume</th></tr><tr><td>str</td><td>str</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>str</td><td>i64</td><td>f64</td></tr></thead><tbody><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.1</td><td>18.7</td><td>181.0</td><td>3750.0</td><td>&quot;male&quot;</td><td>2007</td><td>731.17</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.5</td><td>17.4</td><td>186.0</td><td>3800.0</td><td>&quot;female&quot;</td><td>2007</td><td>687.3</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>40.3</td><td>18.0</td><td>195.0</td><td>3250.0</td><td>&quot;female&quot;</td><td>2007</td><td>725.4</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td><td>2007</td><td>null</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>36.7</td><td>19.3</td><td>193.0</td><td>3450.0</td><td>&quot;female&quot;</td><td>2007</td><td>708.31</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.3</td><td>20.6</td><td>190.0</td><td>3650.0</td><td>&quot;male&quot;</td><td>2007</td><td>809.58</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>38.9</td><td>17.8</td><td>181.0</td><td>3625.0</td><td>&quot;female&quot;</td><td>2007</td><td>692.42</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.2</td><td>19.6</td><td>195.0</td><td>4675.0</td><td>&quot;male&quot;</td><td>2007</td><td>768.32</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>34.1</td><td>18.1</td><td>193.0</td><td>3475.0</td><td>null</td><td>2007</td><td>617.21</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>42.0</td><td>20.2</td><td>190.0</td><td>4250.0</td><td>null</td><td>2007</td><td>848.4</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>37.8</td><td>17.1</td><td>186.0</td><td>3300.0</td><td>null</td><td>2007</td><td>646.38</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>37.8</td><td>17.3</td><td>180.0</td><td>3700.0</td><td>null</td><td>2007</td><td>653.94</td></tr><tr><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.2</td><td>16.6</td><td>191.0</td><td>3250.0</td><td>&quot;female&quot;</td><td>2009</td><td>750.32</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>49.3</td><td>19.9</td><td>203.0</td><td>4050.0</td><td>&quot;male&quot;</td><td>2009</td><td>981.07</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.2</td><td>18.8</td><td>202.0</td><td>3800.0</td><td>&quot;male&quot;</td><td>2009</td><td>943.76</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.6</td><td>19.4</td><td>194.0</td><td>3525.0</td><td>&quot;female&quot;</td><td>2009</td><td>884.64</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>51.9</td><td>19.5</td><td>206.0</td><td>3950.0</td><td>&quot;male&quot;</td><td>2009</td><td>1012.05</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>46.8</td><td>16.5</td><td>189.0</td><td>3650.0</td><td>&quot;female&quot;</td><td>2009</td><td>772.2</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.7</td><td>17.0</td><td>195.0</td><td>3650.0</td><td>&quot;female&quot;</td><td>2009</td><td>776.9</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>55.8</td><td>19.8</td><td>207.0</td><td>4000.0</td><td>&quot;male&quot;</td><td>2009</td><td>1104.84</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>43.5</td><td>18.1</td><td>202.0</td><td>3400.0</td><td>&quot;female&quot;</td><td>2009</td><td>787.35</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>49.6</td><td>18.2</td><td>193.0</td><td>3775.0</td><td>&quot;male&quot;</td><td>2009</td><td>902.72</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.8</td><td>19.0</td><td>210.0</td><td>4100.0</td><td>&quot;male&quot;</td><td>2009</td><td>965.2</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.2</td><td>18.7</td><td>198.0</td><td>3775.0</td><td>&quot;female&quot;</td><td>2009</td><td>938.74</td></tr></tbody></table></div>




```python
# alternately

peng_pl = peng_pl.with_columns([
    (pl.col('bill_length_mm') * pl.col('bill_depth_mm')).alias('biil_volume')
])

peng_pl
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (344, 9)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>island</th><th>bill_length_mm</th><th>bill_depth_mm</th><th>flipper_length_mm</th><th>body_mass_g</th><th>sex</th><th>year</th><th>biil_volume</th></tr><tr><td>str</td><td>str</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>str</td><td>i64</td><td>f64</td></tr></thead><tbody><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.1</td><td>18.7</td><td>181.0</td><td>3750.0</td><td>&quot;male&quot;</td><td>2007</td><td>731.17</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.5</td><td>17.4</td><td>186.0</td><td>3800.0</td><td>&quot;female&quot;</td><td>2007</td><td>687.3</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>40.3</td><td>18.0</td><td>195.0</td><td>3250.0</td><td>&quot;female&quot;</td><td>2007</td><td>725.4</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td><td>2007</td><td>null</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>36.7</td><td>19.3</td><td>193.0</td><td>3450.0</td><td>&quot;female&quot;</td><td>2007</td><td>708.31</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.3</td><td>20.6</td><td>190.0</td><td>3650.0</td><td>&quot;male&quot;</td><td>2007</td><td>809.58</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>38.9</td><td>17.8</td><td>181.0</td><td>3625.0</td><td>&quot;female&quot;</td><td>2007</td><td>692.42</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.2</td><td>19.6</td><td>195.0</td><td>4675.0</td><td>&quot;male&quot;</td><td>2007</td><td>768.32</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>34.1</td><td>18.1</td><td>193.0</td><td>3475.0</td><td>null</td><td>2007</td><td>617.21</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>42.0</td><td>20.2</td><td>190.0</td><td>4250.0</td><td>null</td><td>2007</td><td>848.4</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>37.8</td><td>17.1</td><td>186.0</td><td>3300.0</td><td>null</td><td>2007</td><td>646.38</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>37.8</td><td>17.3</td><td>180.0</td><td>3700.0</td><td>null</td><td>2007</td><td>653.94</td></tr><tr><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.2</td><td>16.6</td><td>191.0</td><td>3250.0</td><td>&quot;female&quot;</td><td>2009</td><td>750.32</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>49.3</td><td>19.9</td><td>203.0</td><td>4050.0</td><td>&quot;male&quot;</td><td>2009</td><td>981.07</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.2</td><td>18.8</td><td>202.0</td><td>3800.0</td><td>&quot;male&quot;</td><td>2009</td><td>943.76</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.6</td><td>19.4</td><td>194.0</td><td>3525.0</td><td>&quot;female&quot;</td><td>2009</td><td>884.64</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>51.9</td><td>19.5</td><td>206.0</td><td>3950.0</td><td>&quot;male&quot;</td><td>2009</td><td>1012.05</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>46.8</td><td>16.5</td><td>189.0</td><td>3650.0</td><td>&quot;female&quot;</td><td>2009</td><td>772.2</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.7</td><td>17.0</td><td>195.0</td><td>3650.0</td><td>&quot;female&quot;</td><td>2009</td><td>776.9</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>55.8</td><td>19.8</td><td>207.0</td><td>4000.0</td><td>&quot;male&quot;</td><td>2009</td><td>1104.84</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>43.5</td><td>18.1</td><td>202.0</td><td>3400.0</td><td>&quot;female&quot;</td><td>2009</td><td>787.35</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>49.6</td><td>18.2</td><td>193.0</td><td>3775.0</td><td>&quot;male&quot;</td><td>2009</td><td>902.72</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.8</td><td>19.0</td><td>210.0</td><td>4100.0</td><td>&quot;male&quot;</td><td>2009</td><td>965.2</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.2</td><td>18.7</td><td>198.0</td><td>3775.0</td><td>&quot;female&quot;</td><td>2009</td><td>938.74</td></tr></tbody></table></div>



## Add a literal (constant) column

### pandas


```python
peng_pd['str_constant'] = "howdy"
peng_pd
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
      <th>species</th>
      <th>island</th>
      <th>bill_length_mm</th>
      <th>bill_depth_mm</th>
      <th>flipper_length_mm</th>
      <th>body_mass_g</th>
      <th>sex</th>
      <th>year</th>
      <th>bill_volume</th>
      <th>str_constant</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>39.1</td>
      <td>18.7</td>
      <td>181.0</td>
      <td>3750.0</td>
      <td>male</td>
      <td>2007</td>
      <td>731.17</td>
      <td>howdy</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>39.5</td>
      <td>17.4</td>
      <td>186.0</td>
      <td>3800.0</td>
      <td>female</td>
      <td>2007</td>
      <td>687.30</td>
      <td>howdy</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>40.3</td>
      <td>18.0</td>
      <td>195.0</td>
      <td>3250.0</td>
      <td>female</td>
      <td>2007</td>
      <td>725.40</td>
      <td>howdy</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2007</td>
      <td>NaN</td>
      <td>howdy</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>36.7</td>
      <td>19.3</td>
      <td>193.0</td>
      <td>3450.0</td>
      <td>female</td>
      <td>2007</td>
      <td>708.31</td>
      <td>howdy</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>339</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>55.8</td>
      <td>19.8</td>
      <td>207.0</td>
      <td>4000.0</td>
      <td>male</td>
      <td>2009</td>
      <td>1104.84</td>
      <td>howdy</td>
    </tr>
    <tr>
      <th>340</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>43.5</td>
      <td>18.1</td>
      <td>202.0</td>
      <td>3400.0</td>
      <td>female</td>
      <td>2009</td>
      <td>787.35</td>
      <td>howdy</td>
    </tr>
    <tr>
      <th>341</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>49.6</td>
      <td>18.2</td>
      <td>193.0</td>
      <td>3775.0</td>
      <td>male</td>
      <td>2009</td>
      <td>902.72</td>
      <td>howdy</td>
    </tr>
    <tr>
      <th>342</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>50.8</td>
      <td>19.0</td>
      <td>210.0</td>
      <td>4100.0</td>
      <td>male</td>
      <td>2009</td>
      <td>965.20</td>
      <td>howdy</td>
    </tr>
    <tr>
      <th>343</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>50.2</td>
      <td>18.7</td>
      <td>198.0</td>
      <td>3775.0</td>
      <td>female</td>
      <td>2009</td>
      <td>938.74</td>
      <td>howdy</td>
    </tr>
  </tbody>
</table>
<p>344 rows × 10 columns</p>
</div>



### polars


```python
peng_pl = peng_pl.with_columns([
    pl.lit("howdy").alias('str_constant')
])

peng_pl
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (344, 10)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>island</th><th>bill_length_mm</th><th>bill_depth_mm</th><th>flipper_length_mm</th><th>body_mass_g</th><th>sex</th><th>year</th><th>biil_volume</th><th>str_constant</th></tr><tr><td>str</td><td>str</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>str</td><td>i64</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.1</td><td>18.7</td><td>181.0</td><td>3750.0</td><td>&quot;male&quot;</td><td>2007</td><td>731.17</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.5</td><td>17.4</td><td>186.0</td><td>3800.0</td><td>&quot;female&quot;</td><td>2007</td><td>687.3</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>40.3</td><td>18.0</td><td>195.0</td><td>3250.0</td><td>&quot;female&quot;</td><td>2007</td><td>725.4</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td><td>2007</td><td>null</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>36.7</td><td>19.3</td><td>193.0</td><td>3450.0</td><td>&quot;female&quot;</td><td>2007</td><td>708.31</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.3</td><td>20.6</td><td>190.0</td><td>3650.0</td><td>&quot;male&quot;</td><td>2007</td><td>809.58</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>38.9</td><td>17.8</td><td>181.0</td><td>3625.0</td><td>&quot;female&quot;</td><td>2007</td><td>692.42</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.2</td><td>19.6</td><td>195.0</td><td>4675.0</td><td>&quot;male&quot;</td><td>2007</td><td>768.32</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>34.1</td><td>18.1</td><td>193.0</td><td>3475.0</td><td>null</td><td>2007</td><td>617.21</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>42.0</td><td>20.2</td><td>190.0</td><td>4250.0</td><td>null</td><td>2007</td><td>848.4</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>37.8</td><td>17.1</td><td>186.0</td><td>3300.0</td><td>null</td><td>2007</td><td>646.38</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>37.8</td><td>17.3</td><td>180.0</td><td>3700.0</td><td>null</td><td>2007</td><td>653.94</td><td>&quot;howdy&quot;</td></tr><tr><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.2</td><td>16.6</td><td>191.0</td><td>3250.0</td><td>&quot;female&quot;</td><td>2009</td><td>750.32</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>49.3</td><td>19.9</td><td>203.0</td><td>4050.0</td><td>&quot;male&quot;</td><td>2009</td><td>981.07</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.2</td><td>18.8</td><td>202.0</td><td>3800.0</td><td>&quot;male&quot;</td><td>2009</td><td>943.76</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.6</td><td>19.4</td><td>194.0</td><td>3525.0</td><td>&quot;female&quot;</td><td>2009</td><td>884.64</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>51.9</td><td>19.5</td><td>206.0</td><td>3950.0</td><td>&quot;male&quot;</td><td>2009</td><td>1012.05</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>46.8</td><td>16.5</td><td>189.0</td><td>3650.0</td><td>&quot;female&quot;</td><td>2009</td><td>772.2</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.7</td><td>17.0</td><td>195.0</td><td>3650.0</td><td>&quot;female&quot;</td><td>2009</td><td>776.9</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>55.8</td><td>19.8</td><td>207.0</td><td>4000.0</td><td>&quot;male&quot;</td><td>2009</td><td>1104.84</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>43.5</td><td>18.1</td><td>202.0</td><td>3400.0</td><td>&quot;female&quot;</td><td>2009</td><td>787.35</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>49.6</td><td>18.2</td><td>193.0</td><td>3775.0</td><td>&quot;male&quot;</td><td>2009</td><td>902.72</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.8</td><td>19.0</td><td>210.0</td><td>4100.0</td><td>&quot;male&quot;</td><td>2009</td><td>965.2</td><td>&quot;howdy&quot;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.2</td><td>18.7</td><td>198.0</td><td>3775.0</td><td>&quot;female&quot;</td><td>2009</td><td>938.74</td><td>&quot;howdy&quot;</td></tr></tbody></table></div>



## Add a new non-constant column



```python
rng = np.random.default_rng()
rvec = rng.uniform(size=peng_pl.shape[0])
```

### pandas


```python
peng_pd['rvec'] = rvec
peng_pd
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
      <th>species</th>
      <th>island</th>
      <th>bill_length_mm</th>
      <th>bill_depth_mm</th>
      <th>flipper_length_mm</th>
      <th>body_mass_g</th>
      <th>sex</th>
      <th>year</th>
      <th>bill_volume</th>
      <th>str_constant</th>
      <th>rvec</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>39.1</td>
      <td>18.7</td>
      <td>181.0</td>
      <td>3750.0</td>
      <td>male</td>
      <td>2007</td>
      <td>731.17</td>
      <td>howdy</td>
      <td>0.357830</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>39.5</td>
      <td>17.4</td>
      <td>186.0</td>
      <td>3800.0</td>
      <td>female</td>
      <td>2007</td>
      <td>687.30</td>
      <td>howdy</td>
      <td>0.328427</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>40.3</td>
      <td>18.0</td>
      <td>195.0</td>
      <td>3250.0</td>
      <td>female</td>
      <td>2007</td>
      <td>725.40</td>
      <td>howdy</td>
      <td>0.850033</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>2007</td>
      <td>NaN</td>
      <td>howdy</td>
      <td>0.917361</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Adelie</td>
      <td>Torgersen</td>
      <td>36.7</td>
      <td>19.3</td>
      <td>193.0</td>
      <td>3450.0</td>
      <td>female</td>
      <td>2007</td>
      <td>708.31</td>
      <td>howdy</td>
      <td>0.001815</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>339</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>55.8</td>
      <td>19.8</td>
      <td>207.0</td>
      <td>4000.0</td>
      <td>male</td>
      <td>2009</td>
      <td>1104.84</td>
      <td>howdy</td>
      <td>0.010642</td>
    </tr>
    <tr>
      <th>340</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>43.5</td>
      <td>18.1</td>
      <td>202.0</td>
      <td>3400.0</td>
      <td>female</td>
      <td>2009</td>
      <td>787.35</td>
      <td>howdy</td>
      <td>0.078095</td>
    </tr>
    <tr>
      <th>341</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>49.6</td>
      <td>18.2</td>
      <td>193.0</td>
      <td>3775.0</td>
      <td>male</td>
      <td>2009</td>
      <td>902.72</td>
      <td>howdy</td>
      <td>0.478277</td>
    </tr>
    <tr>
      <th>342</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>50.8</td>
      <td>19.0</td>
      <td>210.0</td>
      <td>4100.0</td>
      <td>male</td>
      <td>2009</td>
      <td>965.20</td>
      <td>howdy</td>
      <td>0.821185</td>
    </tr>
    <tr>
      <th>343</th>
      <td>Chinstrap</td>
      <td>Dream</td>
      <td>50.2</td>
      <td>18.7</td>
      <td>198.0</td>
      <td>3775.0</td>
      <td>female</td>
      <td>2009</td>
      <td>938.74</td>
      <td>howdy</td>
      <td>0.069104</td>
    </tr>
  </tbody>
</table>
<p>344 rows × 11 columns</p>
</div>



### polars


```python
# https://stackoverflow.com/questions/72245243/polars-how-to-add-a-column-with-numerical

peng_pl = peng_pl.with_columns([
    pl.Series(name='rvec', values=rvec)
])
peng_pl
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (344, 11)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>island</th><th>bill_length_mm</th><th>bill_depth_mm</th><th>flipper_length_mm</th><th>body_mass_g</th><th>sex</th><th>year</th><th>biil_volume</th><th>str_constant</th><th>rvec</th></tr><tr><td>str</td><td>str</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>str</td><td>i64</td><td>f64</td><td>str</td><td>f64</td></tr></thead><tbody><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.1</td><td>18.7</td><td>181.0</td><td>3750.0</td><td>&quot;male&quot;</td><td>2007</td><td>731.17</td><td>&quot;howdy&quot;</td><td>0.35783</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.5</td><td>17.4</td><td>186.0</td><td>3800.0</td><td>&quot;female&quot;</td><td>2007</td><td>687.3</td><td>&quot;howdy&quot;</td><td>0.328427</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>40.3</td><td>18.0</td><td>195.0</td><td>3250.0</td><td>&quot;female&quot;</td><td>2007</td><td>725.4</td><td>&quot;howdy&quot;</td><td>0.850033</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td><td>2007</td><td>null</td><td>&quot;howdy&quot;</td><td>0.917361</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>36.7</td><td>19.3</td><td>193.0</td><td>3450.0</td><td>&quot;female&quot;</td><td>2007</td><td>708.31</td><td>&quot;howdy&quot;</td><td>0.001815</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.3</td><td>20.6</td><td>190.0</td><td>3650.0</td><td>&quot;male&quot;</td><td>2007</td><td>809.58</td><td>&quot;howdy&quot;</td><td>0.620427</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>38.9</td><td>17.8</td><td>181.0</td><td>3625.0</td><td>&quot;female&quot;</td><td>2007</td><td>692.42</td><td>&quot;howdy&quot;</td><td>0.439101</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>39.2</td><td>19.6</td><td>195.0</td><td>4675.0</td><td>&quot;male&quot;</td><td>2007</td><td>768.32</td><td>&quot;howdy&quot;</td><td>0.187134</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>34.1</td><td>18.1</td><td>193.0</td><td>3475.0</td><td>null</td><td>2007</td><td>617.21</td><td>&quot;howdy&quot;</td><td>0.217048</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>42.0</td><td>20.2</td><td>190.0</td><td>4250.0</td><td>null</td><td>2007</td><td>848.4</td><td>&quot;howdy&quot;</td><td>0.892254</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>37.8</td><td>17.1</td><td>186.0</td><td>3300.0</td><td>null</td><td>2007</td><td>646.38</td><td>&quot;howdy&quot;</td><td>0.054411</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;Torgersen&quot;</td><td>37.8</td><td>17.3</td><td>180.0</td><td>3700.0</td><td>null</td><td>2007</td><td>653.94</td><td>&quot;howdy&quot;</td><td>0.282876</td></tr><tr><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td><td>&hellip;</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.2</td><td>16.6</td><td>191.0</td><td>3250.0</td><td>&quot;female&quot;</td><td>2009</td><td>750.32</td><td>&quot;howdy&quot;</td><td>0.092887</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>49.3</td><td>19.9</td><td>203.0</td><td>4050.0</td><td>&quot;male&quot;</td><td>2009</td><td>981.07</td><td>&quot;howdy&quot;</td><td>0.420681</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.2</td><td>18.8</td><td>202.0</td><td>3800.0</td><td>&quot;male&quot;</td><td>2009</td><td>943.76</td><td>&quot;howdy&quot;</td><td>0.844874</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.6</td><td>19.4</td><td>194.0</td><td>3525.0</td><td>&quot;female&quot;</td><td>2009</td><td>884.64</td><td>&quot;howdy&quot;</td><td>0.900437</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>51.9</td><td>19.5</td><td>206.0</td><td>3950.0</td><td>&quot;male&quot;</td><td>2009</td><td>1012.05</td><td>&quot;howdy&quot;</td><td>0.28132</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>46.8</td><td>16.5</td><td>189.0</td><td>3650.0</td><td>&quot;female&quot;</td><td>2009</td><td>772.2</td><td>&quot;howdy&quot;</td><td>0.020023</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>45.7</td><td>17.0</td><td>195.0</td><td>3650.0</td><td>&quot;female&quot;</td><td>2009</td><td>776.9</td><td>&quot;howdy&quot;</td><td>0.709179</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>55.8</td><td>19.8</td><td>207.0</td><td>4000.0</td><td>&quot;male&quot;</td><td>2009</td><td>1104.84</td><td>&quot;howdy&quot;</td><td>0.010642</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>43.5</td><td>18.1</td><td>202.0</td><td>3400.0</td><td>&quot;female&quot;</td><td>2009</td><td>787.35</td><td>&quot;howdy&quot;</td><td>0.078095</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>49.6</td><td>18.2</td><td>193.0</td><td>3775.0</td><td>&quot;male&quot;</td><td>2009</td><td>902.72</td><td>&quot;howdy&quot;</td><td>0.478277</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.8</td><td>19.0</td><td>210.0</td><td>4100.0</td><td>&quot;male&quot;</td><td>2009</td><td>965.2</td><td>&quot;howdy&quot;</td><td>0.821185</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;Dream&quot;</td><td>50.2</td><td>18.7</td><td>198.0</td><td>3775.0</td><td>&quot;female&quot;</td><td>2009</td><td>938.74</td><td>&quot;howdy&quot;</td><td>0.069104</td></tr></tbody></table></div>



## Aggregate by group

### pandas


```python
massf_pd = (
    peng_pd.groupby('species')[['body_mass_g']]
           .mean()
           .reset_index(drop=False, inplace=False)
)
massf_pd
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
      <th>species</th>
      <th>body_mass_g</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Adelie</td>
      <td>3700.662252</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Chinstrap</td>
      <td>3733.088235</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Gentoo</td>
      <td>5076.016260</td>
    </tr>
  </tbody>
</table>
</div>



### polars


```python
massf_pl = (
    peng_pl.groupby('species')
           .agg([
                 pl.col('body_mass_g').mean()
            ])
)

massf_pl
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (3, 2)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>body_mass_g</th></tr><tr><td>str</td><td>f64</td></tr></thead><tbody><tr><td>&quot;Gentoo&quot;</td><td>5076.01626</td></tr><tr><td>&quot;Adelie&quot;</td><td>3700.662252</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>3733.088235</td></tr></tbody></table></div>



## Aggregate by group, order by columns

Mean body mass by species and sex, order by species and sex.

### pandas


```python
massf2_pd = ( 
    peng_pd.groupby(['species', 'sex'])[['body_mass_g']]
                   .mean()
                   .sort_values(by=['species', 'sex'])
                   .reset_index(drop=False, inplace=False)
)
massf2_pd
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
      <th>species</th>
      <th>sex</th>
      <th>body_mass_g</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Adelie</td>
      <td>female</td>
      <td>3368.835616</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Adelie</td>
      <td>male</td>
      <td>4043.493151</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Chinstrap</td>
      <td>female</td>
      <td>3527.205882</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Chinstrap</td>
      <td>male</td>
      <td>3938.970588</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Gentoo</td>
      <td>female</td>
      <td>4679.741379</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Gentoo</td>
      <td>male</td>
      <td>5484.836066</td>
    </tr>
  </tbody>
</table>
</div>



### polars

Notice that polars also aggregates the rows with missing sex, which pandas quietly dropped.


```python
massf2_pl = (
    peng_pl.groupby(['species', 'sex'])
        .agg([
                 pl.col('body_mass_g').mean()
            ])
)

massf2_pl
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (8, 3)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>sex</th><th>body_mass_g</th></tr><tr><td>str</td><td>str</td><td>f64</td></tr></thead><tbody><tr><td>&quot;Gentoo&quot;</td><td>&quot;female&quot;</td><td>4679.741379</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;female&quot;</td><td>3368.835616</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;female&quot;</td><td>3527.205882</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;male&quot;</td><td>4043.493151</td></tr><tr><td>&quot;Gentoo&quot;</td><td>null</td><td>4587.5</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;male&quot;</td><td>3938.970588</td></tr><tr><td>&quot;Gentoo&quot;</td><td>&quot;male&quot;</td><td>5484.836066</td></tr><tr><td>&quot;Adelie&quot;</td><td>null</td><td>3540.0</td></tr></tbody></table></div>



Let's drop the nulls and put it in a better order.
[Reference for missing data handling](https://towardsdatascience.com/data-cleansing-in-polars-f9314ea04a8e)


```python

massf2_pl = (
    peng_pl.groupby(['species', 'sex'])
        .agg([
                 pl.col('body_mass_g').mean()
            ])
        .drop_nulls()
        .sort(by=['species', 'sex'])
)

massf2_pl
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (6, 3)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>sex</th><th>body_mass_g</th></tr><tr><td>str</td><td>str</td><td>f64</td></tr></thead><tbody><tr><td>&quot;Adelie&quot;</td><td>&quot;female&quot;</td><td>3368.835616</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;male&quot;</td><td>4043.493151</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;female&quot;</td><td>3527.205882</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;male&quot;</td><td>3938.970588</td></tr><tr><td>&quot;Gentoo&quot;</td><td>&quot;female&quot;</td><td>4679.741379</td></tr><tr><td>&quot;Gentoo&quot;</td><td>&quot;male&quot;</td><td>5484.836066</td></tr></tbody></table></div>



## Melts and Casts

### pandas

Cast: going from "long" to "wide" (which is kinda the backwards direction, but the data is already long).


```python
wide_bm = massf2_pd.pivot(index='species', columns='sex', values='body_mass_g').reset_index(drop=False, inplace=False)
wide_bm.columns = wide_bm.columns.values # to get rid of the nesting on column index
wide_bm
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
      <th>species</th>
      <th>female</th>
      <th>male</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Adelie</td>
      <td>3368.835616</td>
      <td>4043.493151</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Chinstrap</td>
      <td>3527.205882</td>
      <td>3938.970588</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Gentoo</td>
      <td>4679.741379</td>
      <td>5484.836066</td>
    </tr>
  </tbody>
</table>
</div>



Melt: Wide to long.


```python
longf = wide_bm.melt(id_vars=['species'], 
                     value_vars=['female', 'male'],
                     var_name='sex', 
                     value_name='body_mass')
longf
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
      <th>species</th>
      <th>sex</th>
      <th>body_mass</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Adelie</td>
      <td>female</td>
      <td>3368.835616</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Chinstrap</td>
      <td>female</td>
      <td>3527.205882</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Gentoo</td>
      <td>female</td>
      <td>4679.741379</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Adelie</td>
      <td>male</td>
      <td>4043.493151</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Chinstrap</td>
      <td>male</td>
      <td>3938.970588</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Gentoo</td>
      <td>male</td>
      <td>5484.836066</td>
    </tr>
  </tbody>
</table>
</div>



### polars

Cast


```python
wide_bm = massf2_pl.pivot(index='species', columns='sex', values='body_mass_g')
wide_bm
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (3, 3)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>female</th><th>male</th></tr><tr><td>str</td><td>f64</td><td>f64</td></tr></thead><tbody><tr><td>&quot;Adelie&quot;</td><td>3368.835616</td><td>4043.493151</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>3527.205882</td><td>3938.970588</td></tr><tr><td>&quot;Gentoo&quot;</td><td>4679.741379</td><td>5484.836066</td></tr></tbody></table></div>



Melt


```python
longf = wide_bm.melt(id_vars=['species'], 
                     value_vars=['female', 'male'],
                     variable_name='sex', 
                     value_name='body_mass')
longf
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (6, 3)</small><table border="1" class="dataframe"><thead><tr><th>species</th><th>sex</th><th>body_mass</th></tr><tr><td>str</td><td>str</td><td>f64</td></tr></thead><tbody><tr><td>&quot;Adelie&quot;</td><td>&quot;female&quot;</td><td>3368.835616</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;female&quot;</td><td>3527.205882</td></tr><tr><td>&quot;Gentoo&quot;</td><td>&quot;female&quot;</td><td>4679.741379</td></tr><tr><td>&quot;Adelie&quot;</td><td>&quot;male&quot;</td><td>4043.493151</td></tr><tr><td>&quot;Chinstrap&quot;</td><td>&quot;male&quot;</td><td>3938.970588</td></tr><tr><td>&quot;Gentoo&quot;</td><td>&quot;male&quot;</td><td>5484.836066</td></tr></tbody></table></div>



## Frame concatenation: `rbind`

E.g. concatenate frames vertically.


```python
apd = pd.DataFrame({
    'name': ['Aya', 'Bob', 'Carlos'],
    'age': [39, 22, 56]
})

apl = pl.from_pandas(apd)

# handy that the notation is the same
bpl = pl.DataFrame({
    'name': ['Dev', 'Elsa', 'Fumi'],
    'age' : [15, 28, 43]
})

bpd = bpl.to_pandas()


cpd = pd.DataFrame({
    'state': ['CA', 'NV', 'NY'],
    'city': ['San Francisco', 'Las Vegas', 'New York City']
})

cpl = pl.from_pandas(cpd)
```

### pandas


```python
pd.concat([apd, bpd], ignore_index=True)
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
      <th>name</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Aya</td>
      <td>39</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Bob</td>
      <td>22</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Carlos</td>
      <td>56</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Dev</td>
      <td>15</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Elsa</td>
      <td>28</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Fumi</td>
      <td>43</td>
    </tr>
  </tbody>
</table>
</div>



### polars


```python
pl.concat([apl, bpl])
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (6, 2)</small><table border="1" class="dataframe"><thead><tr><th>name</th><th>age</th></tr><tr><td>str</td><td>i64</td></tr></thead><tbody><tr><td>&quot;Aya&quot;</td><td>39</td></tr><tr><td>&quot;Bob&quot;</td><td>22</td></tr><tr><td>&quot;Carlos&quot;</td><td>56</td></tr><tr><td>&quot;Dev&quot;</td><td>15</td></tr><tr><td>&quot;Elsa&quot;</td><td>28</td></tr><tr><td>&quot;Fumi&quot;</td><td>43</td></tr></tbody></table></div>



## Frame concatenation: `cbind`

E.g. concatenate frames horizontally

### pandas


```python
pd.concat([apd, cpd], axis=1)
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
      <th>name</th>
      <th>age</th>
      <th>state</th>
      <th>city</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Aya</td>
      <td>39</td>
      <td>CA</td>
      <td>San Francisco</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Bob</td>
      <td>22</td>
      <td>NV</td>
      <td>Las Vegas</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Carlos</td>
      <td>56</td>
      <td>NY</td>
      <td>New York City</td>
    </tr>
  </tbody>
</table>
</div>



### polars


```python
pl.concat([apl, cpl], how='horizontal')
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (3, 4)</small><table border="1" class="dataframe"><thead><tr><th>name</th><th>age</th><th>state</th><th>city</th></tr><tr><td>str</td><td>i64</td><td>str</td><td>str</td></tr></thead><tbody><tr><td>&quot;Aya&quot;</td><td>39</td><td>&quot;CA&quot;</td><td>&quot;San Francisco&quot;</td></tr><tr><td>&quot;Bob&quot;</td><td>22</td><td>&quot;NV&quot;</td><td>&quot;Las Vegas&quot;</td></tr><tr><td>&quot;Carlos&quot;</td><td>56</td><td>&quot;NY&quot;</td><td>&quot;New York City&quot;</td></tr></tbody></table></div>




```python
# left join: merge in pandas
# rename
# ifelse

```

## Join


```python
cpd['name'] = ['Bob', 'Carlos', 'Aya']
cpl = pl.from_pandas(cpd)
cpl
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (3, 3)</small><table border="1" class="dataframe"><thead><tr><th>state</th><th>city</th><th>name</th></tr><tr><td>str</td><td>str</td><td>str</td></tr></thead><tbody><tr><td>&quot;CA&quot;</td><td>&quot;San Francisco&quot;</td><td>&quot;Bob&quot;</td></tr><tr><td>&quot;NV&quot;</td><td>&quot;Las Vegas&quot;</td><td>&quot;Carlos&quot;</td></tr><tr><td>&quot;NY&quot;</td><td>&quot;New York City&quot;</td><td>&quot;Aya&quot;</td></tr></tbody></table></div>



### pandas


```python
apd.merge(
    cpd, 
    on = ['name'],
    how = 'left'
)
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
      <th>name</th>
      <th>age</th>
      <th>state</th>
      <th>city</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Aya</td>
      <td>39</td>
      <td>NY</td>
      <td>New York City</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Bob</td>
      <td>22</td>
      <td>CA</td>
      <td>San Francisco</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Carlos</td>
      <td>56</td>
      <td>NV</td>
      <td>Las Vegas</td>
    </tr>
  </tbody>
</table>
</div>



### polars


```python
apl.join(
    cpl,
    on = ['name'],
    how = 'left'
)
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (3, 4)</small><table border="1" class="dataframe"><thead><tr><th>name</th><th>age</th><th>state</th><th>city</th></tr><tr><td>str</td><td>i64</td><td>str</td><td>str</td></tr></thead><tbody><tr><td>&quot;Aya&quot;</td><td>39</td><td>&quot;NY&quot;</td><td>&quot;New York City&quot;</td></tr><tr><td>&quot;Bob&quot;</td><td>22</td><td>&quot;CA&quot;</td><td>&quot;San Francisco&quot;</td></tr><tr><td>&quot;Carlos&quot;</td><td>56</td><td>&quot;NV&quot;</td><td>&quot;Las Vegas&quot;</td></tr></tbody></table></div>



## Rename

### pandas


```python
bpd
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
      <th>name</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Dev</td>
      <td>15</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Elsa</td>
      <td>28</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Fumi</td>
      <td>43</td>
    </tr>
  </tbody>
</table>
</div>




```python
bpd.rename(columns={'name': 'nombre'})
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
      <th>nombre</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Dev</td>
      <td>15</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Elsa</td>
      <td>28</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Fumi</td>
      <td>43</td>
    </tr>
  </tbody>
</table>
</div>



### polars


```python
bpl
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (3, 2)</small><table border="1" class="dataframe"><thead><tr><th>name</th><th>age</th></tr><tr><td>str</td><td>i64</td></tr></thead><tbody><tr><td>&quot;Dev&quot;</td><td>15</td></tr><tr><td>&quot;Elsa&quot;</td><td>28</td></tr><tr><td>&quot;Fumi&quot;</td><td>43</td></tr></tbody></table></div>




```python
bpl.rename({'name': 'nombre'})
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (3, 2)</small><table border="1" class="dataframe"><thead><tr><th>nombre</th><th>age</th></tr><tr><td>str</td><td>i64</td></tr></thead><tbody><tr><td>&quot;Dev&quot;</td><td>15</td></tr><tr><td>&quot;Elsa&quot;</td><td>28</td></tr><tr><td>&quot;Fumi&quot;</td><td>43</td></tr></tbody></table></div>



## if-else

### pandas


```python
apd
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
      <th>name</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Aya</td>
      <td>39</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Bob</td>
      <td>22</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Carlos</td>
      <td>56</td>
    </tr>
  </tbody>
</table>
</div>




```python
apd['over_30'] = np.where(apd['age'] > 30, 'yes', 'no')
apd
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
      <th>name</th>
      <th>age</th>
      <th>over_30</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Aya</td>
      <td>39</td>
      <td>yes</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Bob</td>
      <td>22</td>
      <td>no</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Carlos</td>
      <td>56</td>
      <td>yes</td>
    </tr>
  </tbody>
</table>
</div>



### polars


```python
apl
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (3, 2)</small><table border="1" class="dataframe"><thead><tr><th>name</th><th>age</th></tr><tr><td>str</td><td>i64</td></tr></thead><tbody><tr><td>&quot;Aya&quot;</td><td>39</td></tr><tr><td>&quot;Bob&quot;</td><td>22</td></tr><tr><td>&quot;Carlos&quot;</td><td>56</td></tr></tbody></table></div>




```python
apl.with_columns([
    pl.when(pl.col('age') > 30).then('yes').otherwise('no').alias('over_30')
])
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (3, 3)</small><table border="1" class="dataframe"><thead><tr><th>name</th><th>age</th><th>over_30</th></tr><tr><td>str</td><td>i64</td><td>str</td></tr></thead><tbody><tr><td>&quot;Aya&quot;</td><td>39</td><td>&quot;yes&quot;</td></tr><tr><td>&quot;Bob&quot;</td><td>22</td><td>&quot;no&quot;</td></tr><tr><td>&quot;Carlos&quot;</td><td>56</td><td>&quot;yes&quot;</td></tr></tbody></table></div>



Both will accept column arguments. 


```python
apd['over_30'] = np.where(apd['age'] > 30, 'yes', apd['name'])
apd
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
      <th>name</th>
      <th>age</th>
      <th>over_30</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Aya</td>
      <td>39</td>
      <td>yes</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Bob</td>
      <td>22</td>
      <td>Bob</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Carlos</td>
      <td>56</td>
      <td>yes</td>
    </tr>
  </tbody>
</table>
</div>




```python
apl.with_columns([
    pl.when(pl.col('age') > 30).then('yes').otherwise(pl.col('name')).alias('over_30')
])
```




<div><style>
.dataframe > thead > tr > th,
.dataframe > tbody > tr > td {
  text-align: right;
}
</style>
<small>shape: (3, 3)</small><table border="1" class="dataframe"><thead><tr><th>name</th><th>age</th><th>over_30</th></tr><tr><td>str</td><td>i64</td><td>str</td></tr></thead><tbody><tr><td>&quot;Aya&quot;</td><td>39</td><td>&quot;yes&quot;</td></tr><tr><td>&quot;Bob&quot;</td><td>22</td><td>&quot;Bob&quot;</td></tr><tr><td>&quot;Carlos&quot;</td><td>56</td><td>&quot;yes&quot;</td></tr></tbody></table></div>




```python

```
