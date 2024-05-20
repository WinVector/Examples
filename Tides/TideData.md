```python

```



Data from https://tidesandcurrents.noaa.gov/waterlevels.html?id=9414290&units=standard&bdate=20190701&edate=20190801&timezone=GMT&datum=MLLW&interval=6&action=data


```python
import math
import datetime
import pytz
import glob
import functools
import operator
import numpy
import pandas
import matplotlib.pyplot
import matplotlib.pylab
import seaborn
import sklearn.linear_model
import sklearn.metrics
import vtreat.cross_plan

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
```


```python
date_fmt = '%Y/%m/%d %H:%M'
tz = pytz.utc

def parse_date(dtstr):
    d0 = datetime.datetime.strptime(dtstr, date_fmt)
    return d0.replace(tzinfo=tz)
    
base_date_time = datetime.datetime(2001, 1, 1, tzinfo=tz)
```


```python
print("TZ NAME: {tz}".format(tz=base_date_time.tzname()))
```

    TZ NAME: UTC



```python
print(base_date_time)
```

    2001-01-01 00:00:00+00:00



```python
na_values = [ '', '-' ]
files = [f for f in glob.glob("tide_data/*.csv", recursive=False)]
files.sort()
tides = [pandas.read_csv(f, na_values=na_values) for f in files]
tides = pandas.concat(tides, axis=0)
tides.reset_index(inplace=True, drop=True)
tides.head()
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
      <th>Date</th>
      <th>Time (GMT)</th>
      <th>Predicted (ft)</th>
      <th>Preliminary (ft)</th>
      <th>Verified (ft)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2017/01/01</td>
      <td>00:00</td>
      <td>1.849</td>
      <td>NaN</td>
      <td>2.12</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2017/01/01</td>
      <td>00:06</td>
      <td>1.695</td>
      <td>NaN</td>
      <td>1.97</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2017/01/01</td>
      <td>00:12</td>
      <td>1.543</td>
      <td>NaN</td>
      <td>1.88</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2017/01/01</td>
      <td>00:18</td>
      <td>1.393</td>
      <td>NaN</td>
      <td>1.78</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2017/01/01</td>
      <td>00:24</td>
      <td>1.247</td>
      <td>NaN</td>
      <td>1.66</td>
    </tr>
  </tbody>
</table>
</div>




```python
d0 = parse_date('2001/01/01 00:00')
(d0 - base_date_time).total_seconds()
```




    0.0




```python
print("TZ NAME: {tz}".format(tz=d0.tzname()))
```

    TZ NAME: UTC



```python
tides['dt'] = [parse_date(tides['Date'][i] + ' ' + tides['Time (GMT)'][i]) for i in range(tides.shape[0])]
tides['dts'] = [(t - base_date_time).total_seconds() for t in tides['dt']]
```


```python
tides['tide feet'] = tides['Verified (ft)'].copy()
null_posns = pandas.isnull(tides['tide feet'])
tides.loc[null_posns, 'tide feet'] = tides.loc[null_posns, 'Preliminary (ft)']
```


```python
tides.head()
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
      <th>Date</th>
      <th>Time (GMT)</th>
      <th>Predicted (ft)</th>
      <th>Preliminary (ft)</th>
      <th>Verified (ft)</th>
      <th>dt</th>
      <th>dts</th>
      <th>tide feet</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2017/01/01</td>
      <td>00:00</td>
      <td>1.849</td>
      <td>NaN</td>
      <td>2.12</td>
      <td>2017-01-01 00:00:00+00:00</td>
      <td>504921600.0</td>
      <td>2.12</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2017/01/01</td>
      <td>00:06</td>
      <td>1.695</td>
      <td>NaN</td>
      <td>1.97</td>
      <td>2017-01-01 00:06:00+00:00</td>
      <td>504921960.0</td>
      <td>1.97</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2017/01/01</td>
      <td>00:12</td>
      <td>1.543</td>
      <td>NaN</td>
      <td>1.88</td>
      <td>2017-01-01 00:12:00+00:00</td>
      <td>504922320.0</td>
      <td>1.88</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2017/01/01</td>
      <td>00:18</td>
      <td>1.393</td>
      <td>NaN</td>
      <td>1.78</td>
      <td>2017-01-01 00:18:00+00:00</td>
      <td>504922680.0</td>
      <td>1.78</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2017/01/01</td>
      <td>00:24</td>
      <td>1.247</td>
      <td>NaN</td>
      <td>1.66</td>
      <td>2017-01-01 00:24:00+00:00</td>
      <td>504923040.0</td>
      <td>1.66</td>
    </tr>
  </tbody>
</table>
</div>




```python
numpy.mean(tides['tide feet'])
```




    3.354944709837226




```python
deltas = [tides['dts'][i+1] - tides['dts'][i] for i in range(tides.shape[0]-1)]
```


```python
max(deltas)
```




    360.0




```python
min(deltas)
```




    360.0




```python
tides.to_pickle('tides.pickle.gz')
```


```python

```
