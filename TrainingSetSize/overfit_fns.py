
import os
import numpy as np
import pandas as pd
import sklearn.linear_model
from plotnine import *


def measure_train_test_quality(
        *, 
        m_row: int,
        n_variables: int,  # number of variables in frame
        n_parameters: int,   # number of parameters in model
        alpha: float, 
        example_factory,
        rng,
        d_large_ideal_test: pd.DataFrame):
    d_train = example_factory(m_row, n_variables)
    variables = list(set(d_train.columns) - set(['y']))
    variables.sort()
    variables_used = [variables[i] for i in range(n_parameters)]
    # build predictions
    model = sklearn.linear_model.Ridge(alpha=alpha, fit_intercept=False)
    model.fit(d_train.loc[:, variables_used], d_train["y"])
    predict_train = model.predict(d_train.loc[:, variables_used])
    predict_ideal_test = model.predict(d_large_ideal_test.loc[:, variables_used])
    predict_train_cross = np.zeros((m_row, ))
    if m_row > 1:
        # run a cross validation scoring
        hold_out_size = np.max([1, int(np.floor(m_row / 10))])
        test_sets = np.array_split(
            rng.permutation(range(m_row)), 
            int(np.floor(m_row / hold_out_size)))
        for test_indices in test_sets:
            train_indices = sorted(set(range(m_row)) - set(test_indices))
            model.fit(d_train.loc[train_indices, variables_used], d_train.loc[train_indices, "y"])
            preds_i = model.predict(d_train.loc[test_indices, variables_used])
            predict_train_cross[test_indices] = preds_i
    # estimate losses
    rmse_train = np.sqrt(np.mean( (d_train['y'] - predict_train)**2 ))
    if n_parameters >= m_row:
        rmse_train_adj = np.inf
    else:
        rmse_train_adj = np.sqrt(np.sum( (d_train['y'] - predict_train)**2 ) / (m_row - n_parameters))
    rmse_train_cross = np.sqrt(np.mean( (d_train['y'] - predict_train_cross)**2 ))
    rmse_ideal_test = np.sqrt(np.mean( (d_large_ideal_test['y'] - predict_ideal_test)**2 ))
    return pd.DataFrame({
        'training rows': m_row,
        'n variables': n_variables,
        'n parameters': n_parameters,
        'alpha': alpha,
        'measurement': ['RMSE train', 'RMSE train adjusted', 'RMSE train cross', 'RMSE ideal test'],
        'value': [rmse_train, rmse_train_adj, rmse_train_cross, rmse_ideal_test],
    })


def run_training_size_modeling_experiments(
    *,
    cache_file_name: str = 'plot_frame_sizes.parquet',
    d_large_ideal_test: pd.DataFrame,
    example_factory,
    rng,
    rmse_null: float,
    rmse_perfect: float,
    alphas,
    n_repetitions: int = 10,
    param_excess: float = 20,
):
    # build or get model evaluation data
    if os.path.isfile(cache_file_name):
        plot_frame = pd.read_parquet(cache_file_name)
    else:
        # define experiment
        variables = list(set(d_large_ideal_test.columns) - set(['y']))
        variables.sort()
        n_parameters = len(variables)
        eval_ms = sorted(set(np.linspace(
            start=1,
            stop= param_excess * n_parameters,
            endpoint=True,
            num=500).astype(int)))
        # generate data for different training set sizes (m_row)
        # and degrees of model regularization (alpha)
        plot_frame = [[[
                measure_train_test_quality(
                    m_row=m_row,
                    n_variables=n_parameters,
                    n_parameters=n_parameters,
                    alpha=alpha, 
                    example_factory=example_factory,
                    rng=rng,
                    d_large_ideal_test=d_large_ideal_test) 
                    for m_row in eval_ms] 
                for alpha in alphas]
            for rep in range(n_repetitions)]
        # flatten lists into a single data frame
        plot_frame = sum(plot_frame, [])
        plot_frame = sum(plot_frame, [])
        plot_frame = pd.concat(plot_frame)
        # some derived columns
        plot_frame['L2 regularization'] = np.asarray(plot_frame['alpha']).astype(str)
        plot_frame['rmse_null'] = rmse_null
        plot_frame['rmse_perfect'] = rmse_perfect
        # save for re-use
        plot_frame.to_parquet(cache_file_name)
    return plot_frame


def run_n_variables_modeling_experiments(
    *,
    cache_file_name = 'plot_frame_parameters.parquet',
    d_large_ideal_test: pd.DataFrame,
    m_row: int,
    example_factory,
    rng,
    rmse_null: float,
    rmse_perfect: float,
    alphas,
):
    # build or get model evaluation data
    if os.path.isfile(cache_file_name):
        plot_frame = pd.read_parquet(cache_file_name)
    else:
        # define experiment
        variables = list(set(d_large_ideal_test.columns) - set(['y']))
        variables.sort()
        n_variables = len(variables)
        eval_ns = sorted(set(
            list(np.linspace(
                start=1,
                stop=n_variables,
                endpoint=True,
                num=200).astype(int))
            + list(
                range(1, min(2 * m_row, n_variables))
            )
        ))
        # generate data for different numbers of variables
        # and degrees of model regularization (alpha)
        plot_frame = [[[
                measure_train_test_quality(
                    m_row=m_row,
                    n_variables=n_variables,
                    n_parameters=n_parameters,
                    alpha=alpha, 
                    example_factory=example_factory,
                    rng=rng,
                    d_large_ideal_test=d_large_ideal_test) 
                    for n_parameters in eval_ns] 
                for alpha in alphas]
            for rep in range(5)]
        # flatten lists into a single data frame
        plot_frame = sum(plot_frame, [])
        plot_frame = sum(plot_frame, [])
        plot_frame = pd.concat(plot_frame)
        # some derived columns
        plot_frame['L2 regularization'] = np.asarray(plot_frame['alpha']).astype(str)
        plot_frame['rmse_null'] = rmse_null
        plot_frame['rmse_perfect'] = rmse_perfect
        # save for re-use
        plot_frame.to_parquet(cache_file_name)
    return plot_frame
    

def plot_error_curves(
        plot_frame: pd.DataFrame,
        *, 
        title: str,
        log_scale_y: bool = False,
        draw_points: bool = True,
        draw_lines: bool = True,
        draw_smooth: bool = False,
        x_variable_name: str = 'training rows',
        vline = None,
        line_function: str = "median",
        alpha_adjust: bool = True
        ):
    colors = {  # https://colorbrewer2.org/?type=qualitative&scheme=Dark2&n=4
        'RMSE train': '#e7298a',
        'RMSE train cross': '#7570b3',
        'RMSE ideal test': '#1b9e77',
        'RMSE train adjusted': '#d95f02',
    }
    keys = sorted(set(plot_frame['measurement']))
    for k in keys:
        assert colors[k] is not None  # actually to force key lookup error on mismatch
    style_mapping = {
        'x': x_variable_name,
        'y': 'value',
    }
    rmse_perfect = None
    rmse_null = None
    if ('rmse_perfect' in plot_frame.columns) and ('rmse_null' in plot_frame.columns):
        rmse_perfect = np.mean(plot_frame['rmse_perfect'])
        rmse_null = np.mean(plot_frame['rmse_null'])
    multiple_L2s = len(set(plot_frame['L2 regularization'])) > 1
    style_on_measurement = True  # len(set(plot_frame['measurement'])) > 1
    if style_on_measurement:
        style_mapping['linetype'] = 'measurement'
        style_mapping['shape'] = 'measurement'
        style_mapping['color'] = 'measurement'
    line_frame = (
        plot_frame
            .loc[:, [x_variable_name, "alpha", "measurement", "L2 regularization", "value"]]
            .groupby([x_variable_name, "alpha", "measurement", "L2 regularization"])
            .apply(line_function)
            .reset_index(drop=False, inplace=False)
    )
    gplot = (
        ggplot(
            data=plot_frame,
        )
    )
    if vline is not None:
        gplot = (
            gplot
            + geom_vline(xintercept=vline, alpha=0.3)
        )
    if (rmse_perfect is not None) and (rmse_null is not None):
        gplot = (
            gplot
            + geom_ribbon(
                mapping=aes(x=x_variable_name, ymin=rmse_perfect, ymax=rmse_null),
                alpha=0.2)
        )
    if draw_points:
        alpha = 1
        if alpha_adjust and (draw_lines or draw_smooth):
            alpha=0.05
        gplot = (
            gplot 
            + geom_point(
                mapping=aes(**style_mapping),
                alpha=alpha)
        )
    if draw_lines:
        alpha = 1
        if alpha_adjust and draw_smooth:
            alpha=0.15
        gplot = (
            gplot
            + geom_line(
                data = line_frame,
                mapping=aes(**style_mapping),
                alpha=alpha)
        )
    if draw_smooth:
        gplot = (
            gplot
            + geom_smooth(
                mapping=aes(**style_mapping),
                method='loess',
                span=0.2,
                se=False,
            )
        )
    if style_on_measurement:
        gplot = (
            gplot 
            + scale_colour_manual(values=colors)
        )
    if multiple_L2s:
        gplot = (
            gplot 
            + facet_wrap(
                "L2 regularization", 
                ncol=1, 
                labeller="label_both",
                scales="free_y",
                )
        )
    if log_scale_y:
        gplot = (
            gplot 
            + scale_y_log10(name='root mean square error (lower better)')
        )
    else:
        gplot = (
            gplot
            + ylab('root mean square error (lower better)')
            )
    gplot = (
        gplot
        + ggtitle(title)
        + theme(figure_size=(16, 8))
    )
    return gplot
