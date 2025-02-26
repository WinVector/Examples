from typing import Iterable, Optional, Tuple
import re
import os

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from cmdstanpy import CmdStanModel
from sklearn.metrics import root_mean_squared_error, r2_score

from plotnine import *


# build example
def build_example(
    *,
    rng,
    generating_lags: Iterable[int],
    b_auto: Iterable[float],
    b_auto_0: float,
    b_z: Iterable[float],
    b_imp_0: float,
    b_x: Iterable[float],
    n_step: int = 1000,
    error_scale: float,
) -> pd.DataFrame:
    generating_lags = list(generating_lags)
    b_auto = list(b_auto)
    b_x = list(b_x)
    assert len(generating_lags) == len(b_auto)
    assert len(generating_lags) > 0
    assert len(generating_lags) == len(set(generating_lags))
    max_lag = np.max(generating_lags)
    d_example = {"time_tick": range(n_step)}
    for i, b_z_i in enumerate(b_z):
        zi = rng.choice((-1, 0, 1), p=(0.01, 0.98, 0.01), size=n_step)
        d_example[f"z_{i}"] = zi
    # start at typical points (most will be overwritten by forward time process)
    y_auto = np.maximum(
        np.zeros(n_step) + b_auto_0 / (1 - np.sum(b_auto)) + rng.normal(size=n_step), 0
    )
    for idx in range(max_lag, n_step):
        y_auto_i = b_auto_0 + 0.2 * rng.normal(size=1)[0]  # durable AR-style noise
        for i, b_z_i in enumerate(b_z):
            y_auto_i = y_auto_i + b_z_i * d_example[f"z_{i}"][idx]
        for i, lag in enumerate(generating_lags):
            y_auto_i = y_auto_i + b_auto[i] * y_auto[idx - lag]
        y_auto[idx] = max(0, y_auto_i)
    y = y_auto + rng.normal(size=n_step)  # transient MA-style noise
    for i, b_x_i in enumerate(b_x):
        xi = rng.binomial(n=1, p=0.35, size=n_step)
        d_example[f"x_{i}"] = xi
        y = y + b_x_i * xi
    d_example["y"] = np.maximum(0, y + b_imp_0 + rng.normal(size=n_step) * error_scale)
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


def generate_Stan_model_def(
    *,
    application_lags: Iterable[int],
    n_transient_external_regressors: int = 0,
    n_durable_external_regressors: int = 0,
):
    # for any variables known to be both transient and durable- probably want to introduce a complementarity bias by saying their product is distributed like a small number
    application_lags = list(application_lags)
    n_lags = len(application_lags)
    assert n_lags == len(set(application_lags))
    assert n_lags > 0
    assert n_transient_external_regressors >= 0
    assert n_durable_external_regressors >= 0
    max_lag = np.max(application_lags)
    # specify Stan program file
    auto_terms = [
        f"b_auto[{i+1}] * y_auto[{1 + max_lag - lag}:(N_y_observed + N_y_future - {lag})]"
        for i, lag in enumerate(application_lags)
    ]
    auto_terms = "\n     + ".join(auto_terms)
    b_x_imp_decl = ""
    b_x_imp_dist = ""
    b_x_dur_decl = ""
    b_x_dur_dist = ""
    b_x_joint_dist = ""
    ext_terms_imp = ""
    ext_terms_dur = ""
    x_data_decls = ""
    if n_transient_external_regressors > 0:
        b_x_imp_decl = f"\n  vector[{n_transient_external_regressors}] b_x_imp;                                 // transient external regressor coefficients"
        b_x_imp_dist = "\n  b_x_imp ~ normal(0, 10);"
        ext_terms_imp = [
            f"b_x_imp[{i+1}] * x_imp_{i+1}"
            for i in range(n_transient_external_regressors)
        ]
        ext_terms_imp = " \n     + " + "\n     + ".join(ext_terms_imp)
        x_data_decls = x_data_decls + "  ".join(
            [
                f"""
  vector[N_y_observed + N_y_future] x_imp_{i+1};  // observed transient external regressor"""
                for i in range(n_transient_external_regressors)
            ]
        )
    if n_durable_external_regressors > 0:
        b_x_dur_decl = f"\n  vector[{n_durable_external_regressors}] b_x_dur;                          // durable external regressor coefficients"
        b_x_dur_dist = "\n  b_x_dur ~ normal(0, 10);"
        ext_terms_dur = [
            f"b_x_dur[{i+1}] * x_dur_{i+1}[{max_lag+1}:(N_y_observed + N_y_future)]"
            for i in range(n_durable_external_regressors)
        ]
        ext_terms_dur = " \n     + " + "\n     + ".join(ext_terms_dur)
        x_data_decls = x_data_decls + "  ".join(
            [
                f"""
  vector[N_y_observed + N_y_future] x_dur_{i+1};  // observed durable external regressor"""
                for i in range(n_durable_external_regressors)
            ]
        )
    nested_model_stan_str = (
        """
data {
  int<lower=1> N_y_observed;                  // number of observed y outcomes
  int<lower=1> N_y_future;                    // number of future outcomes to infer
  vector<lower=0>[N_y_observed] y_observed;   // observed outcomes"""
        + x_data_decls
        + "\n}"
        + f"""
parameters {{
  real b_auto_0;                              // auto-regress intercept
  real<lower=0> b_imp_0;                      // total/impulse/transient intercept
  vector[{n_lags}] b_auto;                    // auto-regress coefficients{b_x_imp_decl}{b_x_dur_decl}
  vector<lower=0>[N_y_future] y_future;                // to be inferred future state
  vector<lower=0>[N_y_observed + N_y_future] y_auto;   // unobserved auto-regressive state
  real<lower=0> b_var_y_auto;                 // presumed y_auto (durable) noise variance
  real<lower=0> b_var_y;                      // presumed y (transient) noise variance
}}
transformed parameters {{
        // y_observed and y_future in one notation (for subscripting)
  vector[N_y_observed + N_y_future] y;
  vector[N_y_observed + N_y_future] y_imp;   
  y[1:N_y_observed] = y_observed;
  y[(N_y_observed + 1):(N_y_observed + N_y_future)] = y_future;
  y_imp = b_imp_0{ext_terms_imp};
}}
model {{
  b_var_y_auto ~ chi_square(1);               // prior for y_auto (durable) noise variance
  b_var_y ~ chi_square(1);                    // prior for y (transient) noise variance
        // priors for parameter estimates
  b_auto_0 ~ normal(0, 10);
  b_imp_0 ~ chi_square(1);
  b_auto ~ normal(0, 10);{b_x_imp_dist}{b_x_dur_dist}{b_x_joint_dist}
        // autoregressive system evolution
  y_auto[{max_lag+1}:(N_y_observed + N_y_future)] ~ normal(
    b_auto_0 
     + {auto_terms}{ext_terms_dur},
    b_var_y_auto);
        // how observations are formed
  target += normal_lpdf(
    y_observed |
    y_imp[1:N_y_observed] + y_auto[1:N_y_observed], 
    b_var_y);
        // future
  y_future ~ normal(
    y_imp[(N_y_observed + 1):(N_y_observed + N_y_future)] + y_auto[(N_y_observed + 1):(N_y_observed + N_y_future)], 
    b_var_y);
}}
"""
    )
    return nested_model_stan_str


# chat gpt soln to "In Python how do your write code to replace "[k]" with "[k-1]" in a string?"
def _replace_k_with_k_minus_1(string):
    def decrement(match):
        # Extract the number inside the brackets
        num = int(match.group(1))
        # Return the decremented number in the original format
        return f"[{num-1}]"

    # Use re.sub with a regex pattern to match [number]
    result = re.sub(r"\[(\d+)\]", decrement, string)
    return result


def write_Stan_data(
    *,
    d_train: pd.DataFrame,
    d_apply: pd.DataFrame,
    transient_external_regressors: Optional[Iterable[str]] = None,
    durable_external_regressors: Optional[Iterable[str]] = None,
    data_file_name: str,
):
    # prep arguments
    if transient_external_regressors is not None:
        transient_external_regressors = list(transient_external_regressors)
    else:
        transient_external_regressors = []
    if durable_external_regressors is not None:
        durable_external_regressors = list(durable_external_regressors)
    else:
        durable_external_regressors = []
    # write data
    nested_model_data_str = (
        "{"
        + f"""
"N_y_observed" : {d_train.shape[0]},
"N_y_future" : {d_apply.shape[0]},
"y_observed" : {list(d_train['y'])}"""
    )
    if len(transient_external_regressors) > 0:
        nested_model_data_str = nested_model_data_str + "".join(
            [
                f""",
"x_imp_{i+1}" : {list(d_train[v]) + list(d_apply[v])}
"""
                for i, v in enumerate(transient_external_regressors)
            ]
        )
    if len(durable_external_regressors) > 0:
        nested_model_data_str = nested_model_data_str + "".join(
            [
                f""",
"x_dur_{i+1}" : {list(d_train[v]) + list(d_apply[v])}
"""
                for i, v in enumerate(durable_external_regressors)
            ]
        )
    nested_model_data_str = nested_model_data_str + "}"
    with open(data_file_name, "w", encoding="utf8") as file:
        file.write(nested_model_data_str)


def solve_forecast_by_Stan(
    model_src: str,
    *,
    d_train: pd.DataFrame,
    d_apply: pd.DataFrame,
    transient_external_regressors: Optional[Iterable[str]] = None,
    durable_external_regressors: Optional[Iterable[str]] = None,
    cache_file_name: Optional[str] = None,
) -> pd.DataFrame:
    """
    Fit a forecast through d_train, and then apply the forecast in the d_apply region (d_apply doesn't need y value).
    Caching is oblivious of the inputs (user must invalidate the cache on their own).
    """
    if (cache_file_name is not None) and (os.path.isfile(cache_file_name)):
        return pd.read_csv(cache_file_name)
    # specify data file
    data_file_name: str = "nested_model_tmp.data.json"
    # write data
    write_Stan_data(
        d_train=d_train,
        d_apply=d_apply,
        transient_external_regressors=transient_external_regressors,
        durable_external_regressors=durable_external_regressors,
        data_file_name=data_file_name,
    )
    # fit the model and draw observations
    # https://mc-stan.org/cmdstanpy/api.html#cmdstanpy.CmdStanModel.sample
    stan_file_name = "nested_model_tmp.stan"
    with open(stan_file_name, "w", encoding="utf8") as file:
        file.write(model_src)
    # instantiate the model object
    model = CmdStanModel(stan_file=stan_file_name)
    fit = model.sample(
        data=data_file_name,
        # iter_warmup=8000,
        # iter_sampling=8000,
        show_progress=False,
        show_console=False,
    )
    # get the samples
    res = fit.draws_pd().reset_index(drop=True, inplace=False)  # force copy just in case
    # re-number from zero for Python convenience
    res = res.rename(
        columns={
            k: _replace_k_with_k_minus_1(k)
            for k in res.columns
            if ("[" in k) and (not k.endswith("__")) and (not k.startswith("__"))
        },
        inplace=False,
    )
    if cache_file_name is not None:
        res.to_csv(cache_file_name, index=False)
    return res


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
    # set some plotting controls
    plotting_quantiles = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
    plotting_colors = {
        "0.05": "#66c2a4",
        "0.1": "#2ca25f",
        "0.25": "#006d2c",
        "0.5": "#005824",
        "0.75": "#006d2c",
        "0.9": "#2ca25f",
        "0.95": "#66c2a4",
    }
    ribbon_pairs = [("0.05", "0.95"), ("0.1", "0.9"), ("0.25", "0.75")]
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


def plot_past_and_future(
    *,
    forecast_soln_i: pd.DataFrame,
    d_train: pd.DataFrame,
    d_test: pd.DataFrame,
):
    plotting_quantiles = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
    plotting_colors = {
        "0.05": "#66c2a4",
        "0.1": "#2ca25f",
        "0.25": "#006d2c",
        "0.5": "#005824",
        "0.75": "#006d2c",
        "0.9": "#2ca25f",
        "0.95": "#66c2a4",
    }
    ribbon_pairs = [("0.05", "0.95"), ("0.1", "0.9"), ("0.25", "0.75")]
    sf_frame = forecast_soln_i.loc[
        :, [c.startswith("y[") for c in forecast_soln_i.columns]
    ].reset_index(drop=True, inplace=False)
    sf_frame["trajectory_id"] = range(sf_frame.shape[0])
    sf_frame = sf_frame.melt(
        id_vars=["trajectory_id"], var_name="time_tick", value_name="y"
    )
    sf_frame["time_tick"] = [
        int(c.replace("y[", "").replace("]", "")) for c in sf_frame["time_tick"]
    ]
    sf_frame = (
        sf_frame.loc[:, ["time_tick", "y"]]
        .groupby(["time_tick"])
        .quantile(plotting_quantiles)
        .reset_index(drop=False)
    )
    sf_frame.rename(columns={"level_1": "quantile"}, inplace=True)
    sf_frame["quantile"] = [str(v) for v in sf_frame["quantile"]]
    sf_p = sf_frame.pivot(index="time_tick", columns="quantile")
    sf_p.columns = [c[1] for c in sf_p.columns]
    sf_p = sf_p.reset_index(drop=False, inplace=False)
    # jitter to get ribbon
    sf_p_l = sf_p.copy()
    sf_p_l['time_tick'] = sf_p_l['time_tick'] - 0.49
    sf_p_h = sf_p.copy()
    sf_p_h['time_tick'] = sf_p_h['time_tick'] + 0.49
    sf_p_j = pd.concat([sf_p_l, sf_p, sf_p_h], ignore_index=True)
    plt = ggplot()
    plt = (
        plt
        + geom_point(
            data=d_train,
            mapping=aes(x="time_tick", y="y"),
            size=2,
        )
        + geom_step(
            data=sf_frame.loc[sf_frame["quantile"] == "0.5", :],
            mapping=aes(x="time_tick", y="y"),
            direction="mid",
            color="#005824",
        )
    )
    for r_min, r_max in ribbon_pairs:
        plt = plt + geom_ribbon(
            data=sf_p_j,
            mapping=aes(x="time_tick", ymin=r_min, ymax=r_max),
            fill=plotting_colors[r_min],
            alpha=0.4,
            linetype="",
        )
    plt_train_only = plt + xlim(900, 1000) + ggtitle("data leading to a projection into the future")
    plt = ggplot()
    plt = (
        plt
        + geom_point(
            data=d_test,
            mapping=aes(x="time_tick", y="y"),
            size=2,
        )
        + geom_point(
            data=d_train,
            mapping=aes(x="time_tick", y="y"),
            size=2,
        )
        + geom_step(
            data=sf_frame.loc[sf_frame["quantile"] == "0.5", :],
            mapping=aes(x="time_tick", y="y"),
            direction="mid",
            color="#005824",
        )
    )
    for r_min, r_max in ribbon_pairs:
        plt = plt + geom_ribbon(
            data=sf_p_j,
            mapping=aes(x="time_tick", ymin=r_min, ymax=r_max),
            fill=plotting_colors[r_min],
            alpha=0.4,
            linetype="",
        )
    plt_train_test = (
        plt
        + xlim(900, 1000)
        + ggtitle(
            "data leading to a projection into the future, matched to held out future"
        )
    )
    return (plt_train_only, plt_train_test)



def extract_sframe_result(s_frame: pd.DataFrame):
    stan_preds = s_frame.loc[s_frame["quantile"] == "0.5", ["time_tick", "y"]]
    stan_preds.sort_values(["time_tick"], ignore_index=True)
    stan_preds = np.array(stan_preds["y"])
    return stan_preds


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
    """not generic (specialzed to to lags and one external regressor)"""
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
            - (forecast_soln["b_x_imp[0]"] * d_train.loc[i, "x_0"])
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





def plot_decomposition(
        forecast_soln_i: pd.DataFrame,
        *,
        d_train: pd.DataFrame,
        d_test: pd.DataFrame,
):
    # get distribution of breakdown of predictions
    history_frame = (
        forecast_soln_i
            .loc[:, [c for c in forecast_soln_i.columns if c.startswith('y[') or c.startswith('y_auto[')]]
            .reset_index(drop=True, inplace=False)
    )
    idx_max = np.max([int(c.replace('y[', '').replace(']', '')) for c in history_frame.columns if c.startswith('y[')])
    new_cols = {}
    for i in range(idx_max + 1):
        new_cols[f'y_transient[{i}]'] = history_frame[f'y[{i}]'] - history_frame[f'y_auto[{i}]']
    history_frame = pd.concat([history_frame, pd.DataFrame(new_cols)], axis=1)
    history_frame['trajectory_id'] = range(history_frame.shape[0])
    history_frame = history_frame.melt(id_vars=['trajectory_id'])
    history_frame['time_tick'] = [int(re.sub(r'^.*\[', '', v).replace(']', '')) for v in history_frame['variable']]
    history_frame['variable'] = [re.sub(r'\[.*\]', '', v) for v in history_frame['variable']]
    # get quantiles
    plotting_quantiles = [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]
    plotting_colors = {
        "0.05": "#66c2a4",
        "0.1": "#2ca25f",
        "0.25": "#006d2c",
        "0.5": "#005824",
        "0.75": "#006d2c",
        "0.9": "#2ca25f",
        "0.95": "#66c2a4",
    }
    history_plot = (
        history_frame
            .loc[:, ['variable', 'value', 'time_tick']]
            .groupby(['variable', 'time_tick'])
            .quantile(plotting_quantiles)
            .reset_index(drop=False, inplace=False)
    )
    history_plot.rename(columns={"level_2": "quantile"}, inplace=True)
    history_plot["quantile"] = [str(v) for v in history_plot["quantile"]]
    idx0 = d_train.shape[0] - 2 * d_test.shape[0]
    d_actuals_train = d_train.loc[:, ['time_tick', 'y', 'ext_regressors']].reset_index(drop=True, inplace=False)
    d_actuals_train['variable'] = 'y'
    d_actuals_test = d_test.loc[:, ['time_tick', 'y', 'ext_regressors']].reset_index(drop=True, inplace=False)
    d_actuals_test['variable'] = 'y'
    plt = (
        ggplot(
            data=history_plot.loc[(history_plot['time_tick'] >= idx0) & (history_plot['quantile'] =='0.5'), :],
            mapping=aes(x='time_tick', y='value')
        )
        + annotate(
            "rect",
            xmin=-np.inf, 
            xmax=d_train.shape[0], 
            ymin=-np.inf, 
            ymax=np.inf,
            alpha=0.5,
            fill='#e0d7c6',
        )
        + facet_wrap('variable', ncol=1, scales='free_y')
        + geom_step(direction="mid")
        + geom_vline(xintercept=d_train.shape[0], alpha=0.5, linetype='dashed')
        + geom_point(
            data=d_actuals_train.loc[d_actuals_train['time_tick'] >= idx0, :],
            mapping=aes(x='time_tick', y='y', color='ext_regressors', shape='ext_regressors'),
            size=2,
        )
        + geom_point(
            data=d_actuals_test.loc[d_actuals_test['time_tick'] >= idx0, :],
            mapping=aes(x='time_tick', y='y', color='ext_regressors', shape='ext_regressors'),
            size=1,
        )
        + ggtitle('past and future visits decomposed into sub-populations\n(left side training, right side forecast)')
    )
    # add in annotation regions
    ribbon_pairs = [("0.05", "0.95"), ("0.1", "0.9"), ("0.25", "0.75")]
    for rp in ribbon_pairs:
        rp_low = (
            history_plot
                .loc[history_plot['quantile'] == rp[0], ['variable', 'time_tick', 'value']]
                .reset_index(drop=True, inplace=False)
        )
        rp_low.rename(columns={'value': 'v_low'}, inplace=True)
        rp_high = (
            history_plot
                .loc[history_plot['quantile'] == rp[1], ['variable', 'time_tick', 'value']]
                .reset_index(drop=True, inplace=False)
        )
        rp_high.rename(columns={'value': 'v_high'}, inplace=True)
        range_frame = pd.merge(
            rp_low,
            rp_high,
            how='inner',
            on=['variable', 'time_tick']
        )
        r_left = range_frame.copy()
        r_right = range_frame.copy()
        r_left['time_tick'] = r_left['time_tick'] - 0.49
        r_right['time_tick'] = r_right['time_tick'] + 0.49
        block_frame = pd.concat([r_left, range_frame, r_right], ignore_index=True)
        plt = (
            plt + 
                geom_ribbon(
                        data=block_frame.loc[block_frame['time_tick'] >= idx0, :],
                        mapping=aes(x="time_tick", ymin='v_low', ymax='v_high'),
                        inherit_aes=False,
                        fill=plotting_colors[rp[0]],
                        alpha=0.3,
                        linetype="",
                    )
        )
    return plt


def plot_params(
    *,
    forecast_soln_i: pd.DataFrame,
    generating_params,
):
    answer_frame = pd.DataFrame(
        {
            "b_x_dur[0]": [generating_params["b_z"][0]],
            "b_x_imp[0]": [generating_params["b_x"][0]],
        }
    )
    parameter_plt_frame = forecast_soln_i.loc[:, [c for c in answer_frame.columns]].melt()
    return (
        ggplot()
        + geom_density(
            data=parameter_plt_frame,
            mapping=aes(x="value", fill="variable", color="variable"),
            linetype="",
            alpha=0.5,
        )
        + geom_vline(
            data=answer_frame.melt(),
            mapping=aes(xintercept="value", color="variable", fill="variable"),
            linetype="dashed",
            size=1,
        )
        + facet_wrap("variable", scales="free")
        + scale_color_brewer(type="qualitative", palette="Dark2")
        + scale_fill_brewer(type="qualitative", palette="Dark2")
        + ggtitle("Stan inferred parameter distributions\n(generating values dashed lines)")
    )
