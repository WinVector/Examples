
# import our modules
import tempfile
import numpy as np
import pandas as pd
from scipy.stats import norm
from data_algebra.cdata import RecordSpecification
from IPython.display import Image
from plotnine import *
import PIL


def binomial_diff_sig_pow_visual(
    stdev: float,
    effect_size: float,
    threshold: float,
    title: str = 'Area under the tails give you significance and (1-power)',
    subtitle: str = 'Significance: assumed_no_effect right tail; (1-Power): assumed_large_effect left tail',
    assumed_no_effect_color:str = '#f1a340',
    assumed_large_effect_color:str = '#998ec3',
    suppress_assumed_large_effect:bool = False,
    suppress_assumed_no_effect:bool = False,
):
    """
    Show (approximate) significance and power of a difference between binomials experiment with a specified assumed effect size and decision threshold.
    Based on: https://github.com/WinVector/Examples/blob/main/calling_R_from_Python/significance_power_visuals.R .
    This plot shows two normals, each one approximating a specified difference in binomial rates.
    H0 is the null hypothesis with mean 0, the case where the rates are identical.
    H1 is the alternate hypothesis, that the rate difference is effect_size.
    The areas of significance (false positive rate) and 1-power (false negative rate) are shaded.


    :param stdev: assumed standard deviation of process (same used for both null and H1), usually an upper bound.
    :param effect_size: assumed effect size (difference in binomial rates)
    :param threshold: effect decision threshold
    :param title: plot title
    :param subtitle: plot subtitle
    :param assumed_no_effect_color: color of Null or H0 mass
    :param assumed_large_effect_color: color of H1 mass (assuming an effect)
    :param suppress_assumed_large_effect: leave off assumed_large_effect curve
    :param supress_assumed_no_effect: leave off assumed_no_effect curve
    :return: plotnine plot
    """
    eps:float = 1e-6
    # define the wide plotting data
    x = set(np.arange(-5 * stdev, 5 * stdev + effect_size, step=stdev / 100))
    x.update([threshold, threshold-eps, threshold+eps])
    x = sorted(x)
    pframe = pd.DataFrame({
        'x': x,
        'assumed_no_effect': norm.pdf(x, loc=0, scale=stdev),
        'assumed_large_effect': norm.pdf(x, loc=effect_size, scale=stdev),
    })
    # assumed_no_effect's right tail
    pframe['assumed_no_effect_tail'] = np.where(pframe['x'] > threshold, pframe['assumed_no_effect'], 0)
    # assumed_large_effect's left tail
    pframe['assumed_large_effect_tail'] = np.where(pframe['x'] <= threshold, pframe['assumed_large_effect'], 0)
    # convert from to long for for plotting using the data algebra
    # specify the cdata record transform
    record_transform = RecordSpecification(
        pd.DataFrame({
            'group': ['assumed_large_effect', 'assumed_no_effect'],
            'y': ['assumed_large_effect', 'assumed_no_effect'],
            'tail': ['assumed_large_effect_tail', 'assumed_no_effect_tail'],
        }),
        record_keys=['x'],
        control_table_keys=['group'],
    ).map_from_rows()
    # apply the record transform
    pframelong = record_transform(pframe)
    pframelong = pframelong.loc[pframelong["y"] > 1e-6, :].reset_index(drop=True, inplace=False)
    if suppress_assumed_large_effect:
        pframelong = pframelong.loc[pframelong["group"] != "assumed_large_effect", :].reset_index(drop=True, inplace=False)
    if suppress_assumed_no_effect:
        pframelong = pframelong.loc[pframelong["group"] != "assumed_no_effect", :].reset_index(drop=True, inplace=False)
    # make the plot using the plotnine implementation 
    # of Leland Wilkinson's Grammar of Graphics
    # (nearly call equiv to Hadley Wickham ggplot2 realization)
    palette = {
        'assumed_no_effect': assumed_no_effect_color, 
        'assumed_large_effect': assumed_large_effect_color,
        }
    p = (
        ggplot(pframelong, aes(x='x', y='y'))
            + geom_line(
                aes(color='group', linetype='group')
                )
            + geom_vline(
                xintercept=threshold, 
                color='blue', 
                size=2.0,
                )
            + geom_ribbon(
                aes(ymin=0, ymax='tail', fill='group'), 
                alpha = 0.8)
            + scale_color_manual(values=palette)
            + scale_fill_manual(values=palette)
            + ylab('density')
            + xlab('observed difference')
            + ggtitle(
                title 
                + "\n" + subtitle,
                )
            + theme_minimal()
        )
    return p


def graph_factory(
    *,
    n:float = 557,  # the experiment size
    r:float = 0.1,  # the assumed large effect size (difference in conversion rates)
):
    """
    Build function that returns 3 related A/B difference in rates graphs

    :param n: the experiment size
    :param r: the assumed large effect size (difference in conversion rates)
    :return: tuple of 3 plotnine graphs
    """
    # get the overall expected behavior of the experiment size
    n_b_steps = 100
    behaviors = pd.DataFrame({
        'threshold': np.arange(0, r + r/n_b_steps, r/n_b_steps)
    })
    stdev = np.sqrt(0.5 / n)
    behaviors['false positive rate'] = [
        norm.sf(x=threshold, loc=0, scale=stdev) for threshold in behaviors["threshold"]]
    behaviors['true positive rate'] = [
        norm.cdf(x=r, loc=threshold, scale=stdev) for threshold in behaviors["threshold"]]
    # get the keyed column version
    map = RecordSpecification(
        pd.DataFrame({
            'measure': ["false positive rate", "true positive rate"],
            'value': ["false positive rate", "true positive rate"],
        }),
        record_keys=['threshold'],
        control_table_keys=['measure'],
    ).map_from_rows()
    behaviors_kv = map.transform(behaviors)
    def make_graphs(threshold):
        # convert to what were the function arguments
        threshold = float(threshold)
        stdev = np.sqrt(0.5 / n)
        effect_size = r
        sig_area = norm.sf(x=threshold, loc=0, scale=stdev)  # .sf() = 1 - .cdf()
        mpow_area = norm.sf(x=effect_size, loc=threshold, scale=stdev)
        title='Shaded area under the tails give you significance and 1-power '
        subtitle = f' H0: significance (false positive rate) = {sig_area:.3f} = right area\n H1: 1-power (false negative rate) = {mpow_area:.3f} = left area'
        # find nearest threshold
        row_dist = np.abs(behaviors["threshold"] - threshold)
        selected_rows = behaviors.loc[[np.argmin(row_dist)], :].reset_index(drop=True, inplace=False)
        g_areas = ( 
            binomial_diff_sig_pow_visual(
                stdev=stdev,
                effect_size=effect_size,
                threshold=threshold,
                title=title,
                subtitle=subtitle
            )
        )
        g_thresholds = (
            ggplot(
                    data=behaviors_kv,
                    mapping=aes(x='threshold', y='value'),
                )
                + geom_line()
                + ylim(0, 1)
                + geom_vline(xintercept=threshold, size=2, color="blue")
                + facet_wrap("measure", ncol=1)
        )
        g_roc = (
            ggplot(
                    data=behaviors,
                    mapping=aes(x='false positive rate', y='true positive rate'),
                )
                + geom_point(
                    data=selected_rows,
                    size=3,
                    color="blue",
                )
                + geom_line()
                + coord_fixed()
                + ylim(0.5, 1)
                + xlim(0, 0.5)
        )
        return (g_areas, g_thresholds, g_roc)
    return make_graphs


def convert_plotnine_to_PIL_image(plt) -> PIL.Image:
    """
    Convert plotnine plot to Image.
    """
    # https://stackoverflow.com/a/70817254
    fig = plt.draw(show=False)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tf:
        fig.savefig(tf.name, dpi=300)
        result = PIL.Image.open(tf.name)
    return result


def composite_graphs_using_PIL(graphs) -> PIL.Image:
    """
    Composite 3 graphs to images of the same size using PIL and then composite
    """
    # composite the images using PIL
    imgs = [convert_plotnine_to_PIL_image(g) for g in graphs]
    img_c = PIL.Image.new("RGB", (2 * imgs[0].size[0], 2 * imgs[0].size[1]), "white")
    img_c.paste(imgs[0], (0, int(imgs[0].size[1]/2)))
    img_c.paste(imgs[1], (imgs[0].size[0], 0))
    img_c.paste(imgs[2], (imgs[0].size[0], imgs[0].size[1]))
    return img_c
