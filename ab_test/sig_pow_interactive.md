Interactive version of the graph from [A/B Tests for Engineers](https://win-vector.com/2023/10/15/a-b-tests-for-engineers/).

To see the interaction: download [directory](https://github.com/WinVector/Examples/tree/main/ab_test) and run this Jupyter notebook in JupyterLab or VSCode.

[Jupyter Widgets documentation](https://ipywidgets.readthedocs.io/en/latest/index.html)


```python
# import our modules
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
from scipy.stats import norm
import matplotlib.pyplot as plt
from sig_pow_visual import composite_graphs_using_PIL, graph_factory
import PIL
import ipywidgets as widgets
```


```python
# our specification of interest
# derived from the above
n = 557  # the experiment size
r = 0.1  # the assumed large effect size (difference in conversion rates)
t = 0.061576 # the correct threshold for specified power and significance

```


```python
mk_graphs = graph_factory(
    n=n,  # the experiment size
    r=r,  # the assumed large effect size (difference in conversion rates)
)
```


```python

w = widgets.FloatSlider(
    value=t,
    min=0.0,
    max=r,
    step=0.001,
    description='Threshold Value:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='.4f'
)

display(w)

button = widgets.Button(description = "Plot it")
output = widgets.Output()

display(button, output)

# this works, need a clear command
def on_button_clicked(b):
    with output:
        clear_output(wait=False)
        print(f'Decision threshold = {w.value:.04f}')
        graphs = mk_graphs(w.value)
        # composite the images using PIL
        img_c = composite_graphs_using_PIL(graphs)
        img_c = img_c.resize((int(0.25 * img_c.size[0]), int(0.25 * img_c.size[1])))
        display(img_c)
on_button_clicked(t)
button.on_click(on_button_clicked)
```
