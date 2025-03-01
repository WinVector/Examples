from typing import Iterable, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import root_mean_squared_error, r2_score

from plotnine import *


# build example
def build_example(
    *,
    rng,
    generating_lags: Iterable[int],
    beta_auto: Iterable[float],
    beta_auto_intercept: float,
    beta_durable: Iterable[float],
    effect_shift: float,
    beta_transient: Iterable[float],
    n_step: int,
    error_scale: float,
) -> pd.DataFrame:
    n_step = int(n_step)
    generating_lags = list(generating_lags)
    beta_auto = list(beta_auto)
    beta_transient = list(beta_transient)
    assert len(generating_lags) == len(beta_auto)
    assert len(generating_lags) > 0
    assert len(generating_lags) == len(set(generating_lags))
    assert np.min(generating_lags) > 0
    max_lag = np.max(generating_lags)
    assert n_step > max_lag
    n_warmup = 200
    n_step = n_step + n_warmup
    d_example = {"time_tick": range(-n_warmup, n_step - n_warmup)}
    for i, b_z_i in enumerate(beta_durable):
        zi = rng.choice((-1, 0, 1), p=(0.025, 0.95, 0.025), size=n_step)
        d_example[f"x_durable_{i}"] = zi
    # start at typical points (most will be overwritten by forward time process)
    y_auto = np.zeros(n_step, dtype=float)
    y_auto[0] = rng.uniform(size=1)[0] * 100
    for idx in range(1, max_lag):
        y_auto[idx] = y_auto[idx - 1] + rng.normal(size=1)[0] * 10
    for idx in range(max_lag, n_step):
        y_auto_i = beta_auto_intercept + 0.2 * rng.normal(size=1)[0]  # durable AR-style noise
        for i, b_z_i in enumerate(beta_durable):
            if d_example[f"x_durable_{i}"][idx] != 0:
                y_auto_i = y_auto_i + rng.poisson(b_z_i) * d_example[f"x_durable_{i}"][idx]
        for i, lag in enumerate(generating_lags):
            y_auto_i = y_auto_i + beta_auto[i] * y_auto[idx - lag]
        y_auto[idx] = max(0, y_auto_i)
    y = y_auto + rng.normal(size=n_step)  # transient MA-style noise
    for i, b_x_i in enumerate(beta_transient):
        xi = rng.choice((-2, -1, 0, 1, 2), p=(0.025, 0.05, 0.85, 0.05, 0.025), size=n_step)
        d_example[f"x_transient_{i}"] = xi
        for idx in range(n_step):
            if xi[idx] != 0:
                y[idx] = y[idx] + rng.poisson(b_x_i) * xi[idx]
    d_example["y"] = np.maximum(0, np.round(y + effect_shift + rng.normal(size=n_step) * error_scale))
    d_example = pd.DataFrame(d_example)
    d_example = d_example.loc[range(n_warmup, n_step), :].reset_index(drop=True, inplace=False)
    return d_example


def train_test_split(
    d_example: pd.DataFrame, *, test_length: int = 50
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    cut_idx = d_example.shape[0] - test_length
    d_train = d_example.loc[range(cut_idx), :].reset_index(drop=True, inplace=False)
    d_test = d_example.loc[range(cut_idx, d_example.shape[0]), :].reset_index(
        drop=True, inplace=False
    )
    return d_train, d_test


# set some plotting controls
plotting_quantiles = [0.1, 0.25, 0.5, 0.75, 0.9]
plotting_colors = {
    "0.1": "#2ca25f",
    "0.25": "#006d2c",
    "0.5": "#005824",
    "0.75": "#006d2c",
    "0.9": "#2ca25f",
}
ribbon_pairs = [("0.1", "0.9"), ("0.25", "0.75")]


def plot_forecast(
    forecast_soln: pd.DataFrame,
    d_test: pd.DataFrame,
    *,
    model_name: str,
):
    d_test = d_test.reset_index(drop=True, inplace=False)  # copy for no side effects
    # arrange forecast solution for plotting
    sf_frame = forecast_soln.loc[
        :, [c for c in forecast_soln.columns if c.startswith("y_future[")]
    ].reset_index(drop=True, inplace=False)
    sf_frame["trajectory_id"] = range(sf_frame.shape[0])
    sf_frame = sf_frame.melt(
        id_vars=["trajectory_id"], var_name="time_tick", value_name="y"
    )
    sf_frame["time_tick"] = [
        int(c.replace("y_future[", "").replace("]", "")) for c in sf_frame["time_tick"]
    ]
    sf_frame = (
        sf_frame.loc[:, ["time_tick", "y"]]
        .groupby(["time_tick"])
        .quantile(plotting_quantiles)
        .reset_index(drop=False)
    )
    sf_frame.rename(columns={"level_1": "quantile"}, inplace=True)
    sf_frame["quantile"] = [str(v) for v in sf_frame["quantile"]]
    sf_frame["time_tick"] = sf_frame["time_tick"] + d_test.loc[0, "time_tick"]
    sf_p = sf_frame.pivot(index="time_tick", columns="quantile")
    sf_p.columns = [c[1] for c in sf_p.columns]
    sf_p = sf_p.reset_index(drop=False, inplace=False)
    # jitter to get ribbon
    sf_p_l = sf_p.copy()
    sf_p_l['time_tick'] = sf_p_l['time_tick'] - 0.49
    sf_p_h = sf_p.copy()
    sf_p_h['time_tick'] = sf_p_h['time_tick'] + 0.49
    sf_p_j = pd.concat([sf_p_l, sf_p, sf_p_h], ignore_index=True)
    # plot quality of out of forecasts
    plt = ggplot()
    for r_min, r_max in ribbon_pairs:
        plt = plt + geom_ribbon(
            data=sf_p_j,
            mapping=aes(x="time_tick", ymin=r_min, ymax=r_max),
            fill=plotting_colors[r_min],
            alpha=0.4,
            linetype="",
        )
    plt = (
        plt
        + geom_step(
            data=sf_frame.loc[(sf_frame["quantile"] == "0.5"), :],
            mapping=aes(x="time_tick", y="y"),
            direction="mid",
            color="#005824",
        )
        + geom_point(
            data=d_test,
            mapping=aes(
                x="time_tick",
                y="y",
            ),
            size=2,
        )
        + ggtitle(
            f"{model_name} out of sample forecast\ndots are actuals, lines are predictions"
        )
    )
    return plt, sf_frame



def plot_model_quality(
    d_test: pd.DataFrame,
    *,
    result_name: str,
):
    d_test = d_test.reset_index(drop=True, inplace=False)
    rmse = root_mean_squared_error(
        y_true=d_test["y"],
        y_pred=d_test[result_name],
    )
    r2 = r2_score(
        y_true=d_test["y"],
        y_pred=d_test[result_name],
    )
    plt_bounds = (
        np.min([np.min(d_test[result_name]), np.min(d_test["y"])]),
        np.max([np.max(d_test[result_name]), np.max(d_test["y"])]),
    )
    return (
        ggplot(
            data=d_test, mapping=aes(x=result_name, y="y")
        )
        + geom_abline(intercept=0, slope=1, color="blue", alpha=0.5)
        + geom_point(mapping=aes(color="time_tick"), size=2)
        + scale_colour_gradient(low="#253494", high="#a1dab4")
        + ylim(plt_bounds)
        + xlim(plt_bounds)
        + coord_fixed()
        + ggtitle(f"y ~ {result_name}\nRMSE = {rmse:.2g}, Rsquared = {r2:.2g}")
    )


def plot_model_quality_by_prefix(
    *,
    s_frame: pd.DataFrame,
    d_test: pd.DataFrame,
    result_name: str,
):
    d_test = d_test.reset_index(drop=True, inplace=False)
    stan_preds = s_frame.loc[s_frame["quantile"] == "0.5", ["time_tick", "y"]]
    stan_preds.sort_values(["time_tick"], ignore_index=True)
    stan_preds = np.array(stan_preds["y"])
    d_test[result_name] = stan_preds
    pf = pd.DataFrame(
        {
            "max(time_tick)": [
                d_test.loc[prefix_len, "time_tick"]
                for prefix_len in range(stan_preds.shape[0])
            ],
            "rmse": [
                root_mean_squared_error(
                    y_true=d_test.loc[range(prefix_len + 1), "y"],
                    y_pred=stan_preds[range(prefix_len + 1)],
                )
                for prefix_len in range(stan_preds.shape[0])
            ],
        }
    )
    return (
        ggplot(data=pf, mapping=aes(x="max(time_tick)", y="rmse"))
        + geom_line()
        + geom_point(size=2)
        + guides(shape=guide_legend(reverse=True))
        + ggtitle(f"{result_name}\nquality by forecast horizon")
    )


def plot_recent_state_distribution(
    *,
    d_train: pd.DataFrame,
    forecast_soln: pd.DataFrame,
    generating_lags,
    result_name: str,
):
    """not generic (specialized to to lags and one external regressor)"""
    assert len(generating_lags) == 2
    t_l0 = d_train.shape[0] - generating_lags[0]
    t_l1 = d_train.shape[0] - generating_lags[1]
    recent_hidden_state = forecast_soln.loc[
        :,
        [
            f"y_auto[{i}]"
            for i in range(d_train.shape[0] - np.max(generating_lags), d_train.shape[0])
        ],
    ]
    est_h_state = pd.DataFrame(
        {
            f"y[{i}] - f(x)": d_train.loc[i, "y"]
            - (forecast_soln["beta_transient[0]"] * d_train.loc[i, "x_intercept"])
            for i in range(d_train.shape[0] - np.max(generating_lags), d_train.shape[0])
        }
    )
    recent_hidden_state = recent_hidden_state.melt(id_vars=[])
    compare_colors = {f"y_auto[{t_l1}]": "#ff7f00", f"y_auto[{t_l0}]": "#7570b3"}
    compare_linetypes = {f"y_auto[{t_l1}]": "solid", f"y_auto[{t_l0}]": "dashed"}
    return (
        ggplot(
            data=recent_hidden_state,
            mapping=aes(
                x="value",
                color="variable",
                fill="variable",
                linetype="variable",
            ),
        )
        + geom_density(alpha=0.5, size=1)
        + scale_linetype_manual(values=compare_linetypes)
        + scale_color_manual(values=compare_colors)
        + scale_fill_manual(values=compare_colors)
        + geom_vline(
            xintercept=est_h_state[f"y[{t_l1}] - f(x)"].mean(),
            color=compare_colors[f"y_auto[{t_l1}]"],
            linetype=compare_linetypes[f"y_auto[{t_l1}]"],
            size=1,
        )
        + geom_vline(
            xintercept=est_h_state[f"y[{t_l0}] - f(x)"].mean(),
            color=compare_colors[f"y_auto[{t_l0}]"],
            linetype=compare_linetypes[f"y_auto[{t_l0}]"],
            size=1,
        )
        + ggtitle(
            f"{result_name}\ndistribution of hidden state estimates\nvertical lines are naive observed minus effect point estimates"
        )
    )
