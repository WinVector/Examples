from typing import Iterable, Optional, Tuple
import re

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import root_mean_squared_error, r2_score

from plotnine import *


# build example
def build_example(
    *,
    rng,
    generating_lags: Iterable[int],
    b_auto: Iterable[float],
    b_auto_0: float,
    beta_durable: Iterable[float],
    beta_transient_0: float,
    beta_transient: Iterable[float],
    n_step: int = 1000,
    error_scale: float,
) -> pd.DataFrame:
    generating_lags = list(generating_lags)
    b_auto = list(b_auto)
    beta_transient = list(beta_transient)
    assert len(generating_lags) == len(b_auto)
    assert len(generating_lags) > 0
    assert len(generating_lags) == len(set(generating_lags))
    max_lag = np.max(generating_lags)
    d_example = {"time_tick": range(n_step)}
    for i, b_z_i in enumerate(beta_durable):
        zi = rng.choice((-1, 0, 1), p=(0.02, 0.96, 0.02), size=n_step)
        d_example[f"x_durable_{i}"] = zi
    # start at typical points (most will be overwritten by forward time process)
    y_auto = np.maximum(
        np.zeros(n_step) + b_auto_0 / (1 - np.sum(b_auto)) + rng.normal(size=n_step), 0
    )
    for idx in range(max_lag, n_step):
        y_auto_i = b_auto_0 + 0.2 * rng.normal(size=1)[0]  # durable AR-style noise
        for i, b_z_i in enumerate(beta_durable):
            y_auto_i = y_auto_i + b_z_i * d_example[f"x_durable_{i}"][idx]
        for i, lag in enumerate(generating_lags):
            y_auto_i = y_auto_i + b_auto[i] * y_auto[idx - lag]
        y_auto[idx] = max(0, y_auto_i)
    y = y_auto + rng.normal(size=n_step)  # transient MA-style noise
    for i, b_x_i in enumerate(beta_transient):
        xi = rng.choice((-1, 0, 1), p=(0.1, 0.8, 0.1), size=n_step)
        d_example[f"x_transient_{i}"] = xi
        y = y + b_x_i * xi
    d_example["y"] = np.maximum(0, np.round(y + beta_transient_0 + rng.normal(size=n_step) * error_scale))
    return pd.DataFrame(d_example)


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
    enforce_nonnegative: bool = False,
    external_regressors: Optional[Iterable[str]] = None,
):
    d_test = d_test.reset_index(drop=True, inplace=False)  # copy for no side effects
    d_test["external_regressors"] = ""
    if external_regressors is not None:
        external_regressors = list(external_regressors)
        d_test["external_regressors"] = [
            str({k: d_test.loc[i, k] for k in external_regressors})
            for i in range(d_test.shape[0])
        ]
    # arrange forecast solution for plotting
    sf_frame = forecast_soln.loc[
        :, [c for c in forecast_soln.columns if c.startswith("y_future[")]
    ].reset_index(drop=True, inplace=False)
    if enforce_nonnegative:
        sf_frame[sf_frame < 0] = 0.0
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
                shape="external_regressors",
                color="external_regressors",
            ),
            size=2,
        )
        + guides(shape=guide_legend(reverse=True))
        + ggtitle(
            f"{model_name} out of sample forecast\ndots are actuals, lines are predictions"
        )
    )
    return plt, sf_frame



def plot_model_quality(
    d_test: pd.DataFrame,
    *,
    result_name: str,
    external_regressors: Optional[Iterable[str]] = None,
):
    d_test = d_test.reset_index(drop=True, inplace=False)
    d_test["external_regressors"] = ""
    if external_regressors is not None:
        external_regressors = list(external_regressors)
        d_test["external_regressors"] = [
            str({k: d_test.loc[i, k] for k in external_regressors})
            for i in range(d_test.shape[0])
        ]
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
            data=d_test, mapping=aes(x=result_name, y="y", shape="external_regressors")
        )
        + geom_abline(intercept=0, slope=1, color="blue", alpha=0.5)
        + geom_point(mapping=aes(color="time_tick"), size=2)
        + scale_colour_gradient(low="#253494", high="#a1dab4")
        + ylim(plt_bounds)
        + xlim(plt_bounds)
        + coord_fixed()
        + guides(shape=guide_legend(reverse=True))
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
            - (forecast_soln["beta_transient[0]"] * d_train.loc[i, "x_0"])
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


def fit_external_regressors(
    *,
    modeling_lags: Iterable[int],
    external_regressors: Iterable[str],
    d_train: pd.DataFrame,
    verbose: bool = False,
):
    # copy data
    modeling_lags = list(modeling_lags)
    external_regressors = list(external_regressors)
    train_frame = d_train.loc[:, ["y"] + external_regressors].reset_index(
        drop=True, inplace=False
    )  # copy, no side effects
    orig_train_y = np.array(train_frame["y"])
    external_regressor_effect_estimate = np.zeros(train_frame.shape[0], dtype=float)
    lagged_variable_effect_estimate = np.zeros(train_frame.shape[0], dtype=float)
    best_ext_model = None
    best_rmse = np.inf
    for rep in range(5):
        # estimate external regressors
        # prepare adjusted y, pull off lagged regressors
        train_frame["y"] = orig_train_y - lagged_variable_effect_estimate
        ext_model = Ridge(alpha=1e-3)
        ext_model.fit(train_frame.loc[:, external_regressors], train_frame["y"])
        external_regressor_effect_estimate = ext_model.predict(
            train_frame.loc[:, external_regressors]
        )
        # estimated auto/lagged regressors
        # prepare adjusted y, pull of external regressors
        train_frame["y"] = orig_train_y - external_regressor_effect_estimate
        # get observable lags of outcome
        lagged_variables = []
        for lag_i, lag in enumerate(modeling_lags):
            v_name = f"y_lag_{lag_i}_{lag}"
            lagged_variables.append(v_name)
            train_frame[v_name] = train_frame["y"].shift(
                lag
            )  # move past forward for observable variables
        auto_model = Ridge(alpha=1e-3)
        complete_cases_auto = (
            train_frame.loc[:, lagged_variables].notna().all(axis="columns")
        )
        auto_model.fit(
            train_frame.loc[complete_cases_auto, lagged_variables],
            train_frame.loc[complete_cases_auto, "y"],
        )
        lagged_variable_effect_estimate = np.zeros(train_frame.shape[0], dtype=float)
        lagged_variable_effect_estimate[complete_cases_auto] = auto_model.predict(
            train_frame.loc[complete_cases_auto, lagged_variables]
        )
        # continue to next pass
        rmse = root_mean_squared_error(
            y_true=orig_train_y,
            y_pred=external_regressor_effect_estimate + lagged_variable_effect_estimate,
        )
        mean_ext_effect = root_mean_squared_error(
            y_true=np.zeros(train_frame.shape[0], dtype=float),
            y_pred=external_regressor_effect_estimate,
        )
        mean_auto_effect = root_mean_squared_error(
            y_true=np.zeros(train_frame.shape[0], dtype=float),
            y_pred=lagged_variable_effect_estimate,
        )
        if (rep <= 0) or (rmse < best_rmse):
            best_ext_model = ext_model
            best_rmse = rmse
        if verbose:
            coef_dict = {k: v for k, v in zip(external_regressors, ext_model.coef_)}
            print(f"pass({rep})")
            print(
                f"   rmse: {rmse}, mean_ext_effect: {mean_ext_effect}, mean_auto_effect: {mean_auto_effect}"
            )
            print(f"   {coef_dict}")
    return best_ext_model


def apply_linear_model_bundle_method(
    *,
    modeling_lags: Iterable[int],
    durable_external_regressors: Optional[Iterable[str]] = None,
    transient_external_regressors: Optional[Iterable[str]] = None,
    d_train: pd.DataFrame,
    d_apply: pd.DataFrame,
):
    # copy data
    modeling_lags = list(modeling_lags)
    if durable_external_regressors is None:
        durable_external_regressors = []
    else:
        durable_external_regressors = list(durable_external_regressors)
    if transient_external_regressors is None:
        transient_external_regressors = []
    else:
        transient_external_regressors = list(transient_external_regressors)
    train_frame = d_train.loc[
        :,
        ["y"]
        + sorted(set(durable_external_regressors + transient_external_regressors)),
    ].reset_index(
        drop=True, inplace=False
    )  # copy, no side effects
    apply_frame = d_apply.loc[
        :,
        ["y"]
        + sorted(set(durable_external_regressors + transient_external_regressors)),
    ].reset_index(
        drop=True, inplace=False
    )  # copy, no side effects
    # pull off transient regressors
    if len(transient_external_regressors) > 0:
        ext_model = fit_external_regressors(
            modeling_lags=modeling_lags,
            external_regressors=transient_external_regressors,
            d_train=d_train,
        )
        external_train_effects = ext_model.predict(
            train_frame.loc[:, transient_external_regressors]
        )
        train_frame["y"] = train_frame["y"] - external_train_effects
        external_apply_effects = ext_model.predict(
            apply_frame.loc[:, transient_external_regressors]
        )
        apply_frame["y"] = apply_frame["y"] - external_apply_effects
    # model the auto correlated or lags section of the problem
    model_vars = list(durable_external_regressors)
    # get observable lags of outcome
    for lag_i, lag in enumerate(modeling_lags):
        v_name = f"y_lag_{lag_i}_{lag}"
        model_vars.append(v_name)
        train_frame[v_name] = train_frame["y"].shift(
            lag
        )  # move past forward for observable variables
        apply_frame[v_name] = apply_frame["y"].shift(
            lag
        )  # move past forward for observable variables
    # build and apply models
    x_train_frame = train_frame.loc[:, model_vars]
    x_apply_frame = apply_frame.loc[:, model_vars]
    complete_apply_cases = x_apply_frame.notna().all(axis="columns")
    first_complete_apply_index = np.where(complete_apply_cases)[0][0]
    preds = np.zeros(apply_frame.shape[0]) + np.nan
    for apply_i in range(first_complete_apply_index, apply_frame.shape[0]):
        if complete_apply_cases[apply_i]:
            y_vec = np.array(
                train_frame["y"].shift(-(apply_i - first_complete_apply_index))
            )
            complete_train_cases = x_train_frame.notna().all(axis="columns") & (
                pd.isnull(y_vec) == False
            )
            model = Ridge(alpha=1e-3)
            model.fit(
                x_train_frame.loc[complete_train_cases, model_vars],
                y_vec[complete_train_cases],
            )
            apply_row = x_apply_frame.loc[
                [first_complete_apply_index], model_vars
            ].reset_index(
                drop=True, inplace=False
            )  # copy
            if len(durable_external_regressors) > 0:
                # get in-time external regressor values
                for v in durable_external_regressors:
                    apply_row[v] = x_apply_frame.loc[apply_i, v]
            preds[apply_i] = model.predict(apply_row)[0]
    if len(transient_external_regressors) > 0:
        preds = preds + external_apply_effects
    return np.maximum(preds, 0)  # Could use a Tobit regression pattern here

