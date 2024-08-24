
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import sklearn.metrics
from scipy.stats import spearmanr
from IPython.display import display
from cmdstanpy import CmdStanModel
from plotnine import *
from wvu.util import plot_roc, threshold_plot


def run_stan_model(
        stan_model_src: str,
        *,
        data_str: str,
):
    # build model
    # export source and data
    stan_file = 'rank_src_tmp.stan'
    data_file = 'rank_data_tmp.json'
    with open(stan_file, 'w', encoding='utf8') as file:
        file.write(stan_model_src)
    with open(data_file, 'w', encoding='utf8') as file:
        file.write(data_str)
    # instantiate the model object
    model_comp = CmdStanModel(stan_file=stan_file)
    # fit to data
    fit = model_comp.sample(
        data=data_file,
        show_progress=False,
        show_console=False,
    )
    os.remove(stan_file)
    os.remove(data_file)
    return fit


def build_line_frame(df: pd.DataFrame, *, xcol: str, ycol: str) -> pd.DataFrame:
    fit_line_model = LinearRegression()
    fit_line_model.fit(
        df[[xcol]],
        df[ycol]
    )
    fit_frame = pd.DataFrame({
        xcol: [np.min(df[xcol]), np.max(df[xcol])],
    })
    fit_frame[ycol] = fit_line_model.predict(fit_frame[[xcol]])
    return fit_frame


def calc_auc(*, y_true, y_score) -> float:
    fpr, tpr, _ = sklearn.metrics.roc_curve(
        y_true=y_true, 
        y_score=y_score,
    )
    return sklearn.metrics.auc(fpr, tpr)


def plot_rank_performance(
    estimated_beta,               # estimated coefficients
    *,
    example_name: str,            # name of data set
    n_vars: int,                  # number of variables (including position variables)
    n_alternatives: int,          # size of panels
    features_frame,               # features by row id
    observations,                 # observation layout frame
    estimate_name: str,           # display name of estimate
    position_quantiles = None,    # quantiles of estimated positions
    position_penalties = None,    # ideal position penalties
    score_compare_frame,          # score comparison frame (altered by call)
    rng,                          # pseudo random source
    show_plots: bool = True,      # show plots
) -> pd.DataFrame:
    simulation_sigma = 10
    estimated_beta = np.array(estimated_beta)
    position_effects_frame = pd.DataFrame({
        'position': [f'posn_{i}' for i in range(len(position_penalties))],
        'estimated effect': estimated_beta[features_frame.shape[1]:n_vars],
    })
    if show_plots and (position_penalties is not None):
        position_effects_frame['actual effect'] = position_penalties
        if position_quantiles is not None:
            position_effects_frame = pd.concat([position_effects_frame, position_quantiles], axis=1)
        plt_posns = (
            ggplot(
                data=position_effects_frame,
                mapping=aes(
                    x='estimated effect', 
                    y='actual effect',
                    label='position',
                    ),
            )
            + geom_label(ha='left', va='top')
            + geom_point()
            + ggtitle(f'{example_name} {estimate_name}\nactual position effect as a function estimated effect')
            
        )
        print("estimated position influences")
        display(position_effects_frame)
        if position_quantiles is not None:
            plt_posns = (
                plt_posns
                    + geom_segment(
                        mapping=aes(yend='actual effect', x='0.25', xend='0.75'),
                        color='blue',
                        size=4,
                        alpha=0.5,
                    )
            )
        plt_posns.show()
    estimated_item_scores = features_frame @ estimated_beta[range(features_frame.shape[1])]

    def p_select(row_i: int):
        n_draws: int  = 10000
        est_row = [
            estimated_item_scores[
                int(observations.loc[row_i, f'item_id_{sel_i}'])]    # estimated per item score
            + position_effects_frame.loc[sel_i, 'estimated effect']  # estimated position effect
            for sel_i in range(n_alternatives)]
        est_picks = [0] * n_alternatives
        est_picks[np.argmax(est_row)] = 1
        draws = pd.DataFrame({
            f'est_{i}': rng.normal(loc=est_row[i], scale=simulation_sigma, size=n_draws) for i in range(n_alternatives)
        })
        draws_maxes = draws.max(axis=1)
        draws = pd.DataFrame({
            k: draws[k] >= draws_maxes for k in draws.columns
        })
        draws = draws.sum(axis=0)
        draws = draws / np.sum(draws)
        train_pick = [observations.loc[row_i, f'pick_value_{sel_i}'] == 1 for sel_i in range(n_alternatives)]
        return pd.DataFrame({
            'row': row_i,
            'position': range(n_alternatives),
            'pick probability estimate': draws,
            'was pick': train_pick
        })

    pick_frame = [p_select(row_i) for row_i in range(observations.shape[0])]
    pick_frame = pd.concat(pick_frame, ignore_index=True)
    if show_plots:
        print("picks")
        display(pick_frame.head(10))
        (
            ggplot(
                data=pick_frame,
                mapping=aes(
                    x='pick probability estimate',
                    color='was pick',
                    fill='was pick',
                )
            )
            + geom_density(alpha=0.7)
            + ggtitle(f'{example_name} {estimate_name}\npick probability estimate grouped by truth value')
        ).show()
        plot_roc(
            prediction=pick_frame['pick probability estimate'],
            istrue=pick_frame['was pick'],
            ideal_line_color='lightgrey',
            title=f'{example_name} {estimate_name}\nROC of pick selection',
        )
        threshold_plot(
            pick_frame,
            pred_var='pick probability estimate',
            truth_var='was pick',
            plotvars=("precision", "recall"),
            title=f'{example_name} {estimate_name}\nprecision recall tradeoffs',
        )
    pick_auc = calc_auc(
        y_true=pick_frame['was pick'], 
        y_score=pick_frame['pick probability estimate'],
    )
    pick_spearmanr = spearmanr(
        pick_frame['was pick'],
        pick_frame['pick probability estimate'],
    )
    score_compare_frame[estimate_name] = estimated_item_scores
    spearman_all = spearmanr(
        score_compare_frame[estimate_name],
        score_compare_frame['hidden concept'],
    )
    if show_plots:
        fit_frame = build_line_frame(score_compare_frame, xcol=estimate_name, ycol='hidden concept')
        (
            ggplot(
                data=score_compare_frame,
                mapping=aes(x=estimate_name, y='hidden concept'),
            )
            + geom_point(alpha=0.2)
            + geom_line(data=fit_frame, color='blue')
            + ggtitle(f'{example_name} {estimate_name} Spearman R: {spearman_all.statistic:.2f}\noriginal score as a function of recovered evaluation function')
        ).show()
    observed_ids = set(observations.loc[
        :, 
        [c for c in observations.columns if c.startswith('item_id_')]].values.flatten())
    unobserved_ids = [i for i in range(features_frame.shape[0]) if i not in observed_ids]
    spearman_test = np.nan
    if len(unobserved_ids) > 10:
        score_compare_frame_test = score_compare_frame.loc[unobserved_ids, :].reset_index(drop=True, inplace=False)
        spearman_test = spearmanr(
            score_compare_frame_test[estimate_name],
            score_compare_frame_test['hidden concept'],
        )
        if show_plots:
            fit_frame_test = build_line_frame(score_compare_frame_test, xcol=estimate_name, ycol='hidden concept')
            (
                ggplot(
                    data=score_compare_frame_test,
                    mapping=aes(x=estimate_name, y='hidden concept'),
                )
                + geom_point(alpha=0.2)
                + geom_line(data=fit_frame_test, color='blue')
                + ggtitle(f'{example_name} {estimate_name} Spearman R: {spearman_test.statistic:.2f} (out of sample data)\noriginal score as a function of recovered evaluation function')
            ).show()
    return pd.DataFrame({
        'example_name': [example_name],
        'estimate_name': [estimate_name],
        'SpearmanR_all': [spearman_all.statistic],
        'SpearmanR_test': [spearman_test.statistic],
        'pick_SpearmanR': [pick_spearmanr.statistic],
        'pick_auc': [pick_auc],
        'data_size': [features_frame.shape[0]],
        'test_size': [len(unobserved_ids)],
        })
