
# import our modules
import numpy as np
import pandas as pd
from scipy.stats import norm
from data_algebra.cdata import RecordSpecification
from plotnine import (
    aes, 
    ggplot, 
    geom_line, geom_point, geom_ribbon, geom_vline,
    scale_color_manual, scale_fill_manual,
    xlab, ylab,
    ggtitle,
    theme, theme_minimal
)


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
                color='black', 
                size=1.0,
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
