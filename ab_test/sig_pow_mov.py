
""" begin text
Interactive version of the graph from [A/B Tests for Engineers](https://win-vector.com/2023/10/15/a-b-tests-for-engineers/).

To see the interaction: download [directory](https://github.com/WinVector/Examples/tree/main/ab_test) and run this Jupyter notebook in JupyterLab or VSCode.

[Jupyter Widgets documentation](https://ipywidgets.readthedocs.io/en/latest/index.html)
"""  # end text

# import our modules
import numpy as np
import pandas as pd
import os
import shutil
from sig_pow_visual import composite_graphs_using_PIL, graph_factory
import PIL
from multiprocessing import Pool


# derived from the above
n = 557  # the experiment size
r = 0.1  # the assumed large effect size (difference in conversion rates)



mk_graphs = graph_factory(
    n=n,  # the experiment size
    r=r,  # the assumed large effect size (difference in conversion rates)
)


dir = "imgs"


def f(v):
    i, threshold = v
    graphs = mk_graphs(threshold)
    # composite the images using PIL
    img_c = composite_graphs_using_PIL(graphs)
    img_c.save(os.path.join(dir, f"img_{i:08d}.png"))


if __name__ == '__main__':
    n_step = 500
    thresholds = list(enumerate(np.arange(0, r + r/n_step, r/n_step)))
    os.makedirs(dir)
    with Pool(5) as p:
        p.map(f, thresholds)
    i_max = thresholds[len(thresholds) - 1][0]
    i_current = i_max + 1
    # run backwards
    for i in range(len(thresholds)):
        shutil.copyfile(  # symlink wasn't readable
            src=os.path.join(dir, f"img_{(i_max - i):08d}.png"),
            dst=os.path.join(dir, f"img_{i_current:08d}.png"),
        )
        i_current = i_current + 1
    # run forwards
    for i in range(len(thresholds)):
        shutil.copyfile(
            src=os.path.join(dir, f"img_{i:08d}.png"),
            dst=os.path.join(dir, f"img_{i_current:08d}.png"),
        )
        i_current = i_current + 1


# ffmpeg -framerate 25 -pattern_type glob -i 'imgs/img_*.png' -c:v libx264 -pix_fmt yuv420p out.mp4
