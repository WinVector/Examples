
from typing import Optional
from collections import namedtuple
from scipy.stats import f
from scipy.optimize import minimize_scalar
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plotnine import *
from sklearn.linear_model import LinearRegression


F_inference = namedtuple(
    "F_result", 
    [
        "instances_per_sample",
        "empirical_mean",
        "empirical_var",
        "implied_n_variables",
        "implied_d1",
        "implied_d2",
        "implied_mean",
        "implied_var",
    ])


def _int_minimize(f, *, min_x: int, max_x: int, x0: int) -> int:
    min_x = int(min_x)
    max_x = int(max_x)
    x0 = int(x0)
    assert max_x >= min_x
    # start opt
    xs = (min_x, x0, max_x)
    ys = tuple([f(xi) for xi in xs])
    # small system or, don't have a good x0 invariant. 
    # brute force search in this case.
    if (max_x - min_x <= 5) or (x0 <= min_x) or (x0 >= max_x) or (ys[0] <= ys[1]) or (ys[2] <= ys[1]):
        best_x = min_x
        best_y = f(best_x)
        for x in range(min_x + 1, max_x + 1):
            y = f(x)
            if y < best_y:
                best_x = x
                best_y = y
        return best_x
    # iterate to improve
    while True:
        # confirm invariant
        assert (ys[1] < ys[0]) and (ys[1] < ys[2])
        assert (xs[0] < xs[1]) and (xs[1] < xs[2])
        left_unknown = (xs[1] - xs[0]) - 1
        right_unknown = (xs[2] - xs[1]) - 1
        if (left_unknown <= 0) and (right_unknown <= 0):
            return xs[1]
        if left_unknown >= right_unknown:
            probe = int(np.round((xs[0] + xs[1]) / 2))
            assert (xs[0] < probe) and (probe < xs[1])
            y = f(probe)
            if y < ys[1]:
                xs = [xs[0], probe, xs[1]]
                ys = [ys[0], y, ys[1]]
            else:
                xs = [probe, xs[1], xs[2]]
                ys = [y, ys[1], ys[2]]
        else:
            probe = int(np.round((xs[1] + xs[2]) / 2))
            assert (xs[1] < probe) and (probe < xs[2])
            y = f(probe)
            if y < ys[1]:
                xs = [xs[1], probe, xs[2]]
                ys = [ys[1], y, ys[2]]
            else:
                xs = [xs[0], xs[1], probe]
                ys = [ys[0], ys[1], y]


def infer_d1_d2(
        *,
        instances_per_sample: int,
        empirical_mean: float,
        empirical_var: float,
) -> F_inference:
    assert instances_per_sample > 1
    assert empirical_var > 0
    def loss(n_variables):
        # plug in what we would expect if we knew n_variables
        d1 = np.max([0.5, n_variables - 1])
        d2 = np.max([4.5, instances_per_sample - n_variables + 1])
        # get implied quantities
        implied_mean = d2 / (d2 - 2)
        implied_var = 2 * d2**2 * (d1 + d2 - 2) / (d1 * (d2 - 2)**2 * (d2 - 4))
        # convert to loss (mean should always be above 1 for F-dist)
        loss = (implied_mean / np.max([1, empirical_mean]) - 1)**2 + (implied_var / empirical_var - 1)**2
        return loss
    # good mean near 1, d1 near infinity start
    n_variables0 = int(np.round(1 + 2 / empirical_var))
    n_variables = _int_minimize(loss, min_x=1, max_x=instances_per_sample, x0=n_variables0)
    assert n_variables >= 1
    assert n_variables <= instances_per_sample
    assert loss(n_variables) <= loss(n_variables0)
    d1 = n_variables - 1
    d2 = instances_per_sample - n_variables + 1
    implied_mean = d2 / (d2 - 2)
    implied_var = 2 * d2**2 * (d1 + d2 - 2) / (d1 * (d2 - 2)**2 * (d2 - 4))
    return F_inference(
        instances_per_sample=instances_per_sample,
        empirical_mean=empirical_mean,
        empirical_var=empirical_var,
        implied_n_variables=n_variables,
        implied_d1=d1,
        implied_d2=d2,
        implied_mean=implied_mean,
        implied_var=implied_var,
    )


F_result = namedtuple(
    "F_result", 
    [
        "instances_per_sample",
        "n_samples",
        "empirical_mean",
        "empirical_var",
        "inferred_params",
    ])


def characterize_as_F_distribution(sampled_Fs, *, instances_per_sample: int) -> F_result:
    instances_per_sample = int(instances_per_sample)
    assert instances_per_sample > 0
    n_samples = len(sampled_Fs)
    empirical_mean = np.mean(sampled_Fs)
    empirical_var = np.mean((np.asarray(sampled_Fs) - empirical_mean)**2)  # not Bessel correcting
    return F_result(
        instances_per_sample = instances_per_sample,
        n_samples = n_samples,
        empirical_mean=empirical_mean,
        empirical_var=empirical_var,
        inferred_params=infer_d1_d2(
            instances_per_sample=instances_per_sample,
            empirical_mean=empirical_mean,
            empirical_var=empirical_var,
        )
    )


F_plot = namedtuple(
    "F_result", 
    [
        "plot",
        "d1",
        "d2",
        "f_summary",
        "statistic", 
        "empirical_significance",
        "theoretical_significance",
    ])


def plot_F_curve(
        sampled_Fs, 
        *,
        ref_value: Optional[float] = None,
        title: str,
        n_blocks: int, 
        block_size: int) -> F_plot:
    """Plot a density and theoretical F statistic curve"""
    # get theoretical density
    theory_fs = np.linspace(np.min(sampled_Fs), np.max(sampled_Fs), num=200)
    if ref_value is not None:
        theory_fs = set(theory_fs)
        theory_fs.add(ref_value)
        theory_fs = sorted(theory_fs)
    d_theory = pd.DataFrame({
        'F statistic': theory_fs
    })
    d1 = n_blocks - 1
    d2 = n_blocks * block_size - n_blocks
    theoretical_mean_value = d2 / (d2 - 2)
    d_theory["density"] = [f.pdf(x, d1, d2) for x in d_theory["F statistic"]]
    # make plot
    plot = (
        ggplot()
            + geom_density(
                data=pd.DataFrame({
                    'F statistic': sampled_Fs,
                }), 
                mapping=aes(x='F statistic'), 
                fill="grey",
                color="grey",
                )
            + geom_line(
                data=d_theory,
                mapping=aes(x='F statistic', y='density'),
                color='orange',
                linetype='dashed',
                )
        )
    theoretical_significance = None
    empirical_significance = None
    if ref_value is not None:
        theoretical_significance = f.sf(ref_value, d1, d2)
        empirical_significance = np.sum([v >= ref_value for v in sampled_Fs]) / len(sampled_Fs)
        plot = (
            plot 
            + geom_vline(
                xintercept=ref_value,
                color='blue',
                )
            + geom_ribbon(
                data=d_theory.loc[d_theory['F statistic'] >= ref_value, :],
                mapping=aes(x='F statistic', ymin=0, ymax='density'),
                color='blue',
                fill='blue',
                )
            + ggtitle(title + f"\ntheoretical significance: {theoretical_significance:{4.2}}, empirical significance: {empirical_significance:{4.2}}")
        )
    else:
        plot = plot + ggtitle(title)
    mean_value = np.mean(sampled_Fs)  #  d2 / (d2 - 2)  # expected value
    median_value = np.median(sampled_Fs)
    plot = (
        plot
        + geom_vline(
            xintercept=theoretical_mean_value,
            color='orange',
            alpha=0.8,
            linetype='dashed',
            )
        + geom_vline(
            xintercept=mean_value,
            color='black',
            alpha=0.8,
            linetype='dashed',
            )
        + geom_vline(
            xintercept=median_value,
            color='black',
            alpha=0.8,
            linetype='dotted',
            )
    )
    return F_plot(
        plot=plot,
        d1=d1,
        d2=d2,
        f_summary=characterize_as_F_distribution(
            sampled_Fs,
            instances_per_sample=n_blocks * block_size,
        ),
        statistic = ref_value,
        empirical_significance=empirical_significance,
        theoretical_significance=theoretical_significance,
    )



# show knowing the group label tells a lot about the group mean
def plt_block_reln(
        *,
        group_adjustments,
        split_data_effect
):
    d_effect = pd.DataFrame({
        "injected block effect": group_adjustments,
        "observed block effect": [np.mean(gi) for gi in split_data_effect],
    })
    obs_group = LinearRegression()
    obs_group.fit(d_effect.loc[:, ["observed block effect"]], d_effect["injected block effect"])
    return (
        ggplot(
            data=d_effect,
            mapping=aes(
                x="observed block effect",
                y="injected block effect",
                )
            )
        + geom_point()
        + geom_abline(
            intercept=obs_group.intercept_, 
            slope=obs_group.coef_[0],
            color="blue",
            alpha=0.7,
            size=2)
        + ggtitle("relation between observed and intended per-block effect")
    )
