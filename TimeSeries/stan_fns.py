from typing import Iterable, Optional
import re
import os

import numpy as np
import pandas as pd
from cmdstanpy import CmdStanModel

from plotnine import *


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
    b_x_transient_decl = ""
    b_x_transient_dist = ""
    b_x_durable_decl = ""
    b_x_durable_dist = ""
    b_x_joint_dist = ""
    ext_terms_imp = ""
    ext_terms_dur = ""
    x_data_decls = ""
    if n_transient_external_regressors > 0:
        b_x_transient_decl = f"\n  vector[{n_transient_external_regressors}] beta_transient;                                 // transient external regressor coefficients"
        b_x_transient_dist = "\n  beta_transient ~ normal(0, 10);"
        ext_terms_imp = [
            f"beta_transient[{i+1}] * x_transient_{i+1}"
            for i in range(n_transient_external_regressors)
        ]
        ext_terms_imp = " + " + "\n     + ".join(ext_terms_imp)
        x_data_decls = x_data_decls + "  ".join(
            [
                f"""
  vector[N_y_observed + N_y_future] x_transient_{i+1};  // observed transient external regressor"""
                for i in range(n_transient_external_regressors)
            ]
        )
    if n_durable_external_regressors > 0:
        b_x_durable_decl = f"\n  vector[{n_durable_external_regressors}] beta_durable;                          // durable external regressor coefficients"
        b_x_durable_dist = "\n  beta_durable ~ normal(0, 10);"
        ext_terms_dur = [
            f"beta_durable[{i+1}] * x_durable_{i+1}[{max_lag+1}:(N_y_observed + N_y_future)]"
            for i in range(n_durable_external_regressors)
        ]
        ext_terms_dur = " \n     + " + "\n     + ".join(ext_terms_dur)
        x_data_decls = x_data_decls + "  ".join(
            [
                f"""
  vector[N_y_observed + N_y_future] x_durable_{i+1};  // observed durable external regressor"""
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
  real b_auto_0;                     // auto-regress intercept
  real beta_transient_0;                      // total/impulse/transient intercept
  vector[{n_lags}] b_auto;                    // auto-regress coefficients{b_x_transient_decl}{b_x_durable_decl}
  vector<lower=0>[N_y_future] y_future;                // to be inferred future state
  vector<lower=0>[N_y_observed + N_y_future] y_auto;   // unobserved auto-regressive state
  real<lower=0> b_var_y_auto;                 // presumed y_auto (durable) noise variance
  real<lower=0> b_var_y;                      // presumed y (transient) noise variance
}}
transformed parameters {{
        // y_observed and y_future in one notation (for subscripting)
  vector[N_y_observed + N_y_future] y;
  vector[N_y_observed + N_y_future] y_transient_effect;
  y[1:N_y_observed] = y_observed;
  y[(N_y_observed + 1):(N_y_observed + N_y_future)] = y_future;
  y_transient_effect = beta_transient_0{ext_terms_imp};
}}
model {{
  b_var_y_auto ~ chi_square(1);               // prior for y_auto (durable) noise variance
  b_var_y ~ chi_square(1);                    // prior for y (transient) noise variance
        // priors for parameter estimates
  b_auto_0 ~ normal(0, 10);
  beta_transient_0 ~ normal(0, 10);
  b_auto ~ normal(0, 10);{b_x_transient_dist}{b_x_durable_dist}{b_x_joint_dist}
        // autoregressive system evolution
  y_auto[{max_lag+1}:(N_y_observed + N_y_future)] ~ normal(
    b_auto_0 
     + {auto_terms}{ext_terms_dur},
    b_var_y_auto);
        // criticize observations
  for (i in 1:N_y_observed) {{
      if (y_observed[i] > 0) {{
        target += normal_lpdf(
            y_observed[i] |
            y_transient_effect[i] + y_auto[i], 
            b_var_y); 
      }} else {{
        target += normal_lcdf(  // Tobit style scoring, matching above loss
            0 |
            y_transient_effect[i] + y_auto[i], 
            b_var_y); 
      }}
  }}
        // future
  y_future ~ normal(
    y_transient_effect[(N_y_observed + 1):(N_y_observed + N_y_future)] + y_auto[(N_y_observed + 1):(N_y_observed + N_y_future)], 
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



def extract_sframe_result(s_frame: pd.DataFrame):
    stan_preds = s_frame.loc[s_frame["quantile"] == "0.5", ["time_tick", "y"]]
    stan_preds.sort_values(["time_tick"], ignore_index=True)
    stan_preds = np.array(stan_preds["y"])
    return stan_preds


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
"x_transient_{i+1}" : {list(d_train[v]) + list(d_apply[v])}
"""
                for i, v in enumerate(transient_external_regressors)
            ]
        )
    if len(durable_external_regressors) > 0:
        nested_model_data_str = nested_model_data_str + "".join(
            [
                f""",
"x_durable_{i+1}" : {list(d_train[v]) + list(d_apply[v])}
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
    for c in res.columns:
        if c.startswith('y['):
            res[c] = np.maximum(0, res[c])
    if cache_file_name is not None:
        res.to_csv(cache_file_name, index=False)
    return res


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



def plot_past_and_future(
    *,
    forecast_soln_i: pd.DataFrame,
    d_train: pd.DataFrame,
    d_test: pd.DataFrame,
):
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




def plot_decomposition(
        forecast_soln_i: pd.DataFrame,
        *,
        d_train: pd.DataFrame,
        d_test: pd.DataFrame,
):
    # get distribution of breakdown of predictions
    history_frame = (
        forecast_soln_i
            .loc[:, [c for c in forecast_soln_i.columns if c.startswith('y[') or c.startswith('y_auto[') or c.startswith('y_transient_effect[')]]
            .reset_index(drop=True, inplace=False)
    )
    history_frame['trajectory_id'] = range(history_frame.shape[0])
    history_frame = history_frame.melt(id_vars=['trajectory_id'])
    history_frame['time_tick'] = [int(re.sub(r'^.*\[', '', v).replace(']', '')) for v in history_frame['variable']]
    history_frame['variable'] = [re.sub(r'\[.*\]', '', v) for v in history_frame['variable']]
    # get quantiles
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
            "beta_durable[0]": [generating_params["beta_durable"][0]],
            "beta_transient[0]": [generating_params["beta_transient"][0]],
        }
    )
    x_max = np.ceil(np.max(np.max(answer_frame)) + 0.1)
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
        + facet_wrap("variable", scales="free_y", ncol=1)
        + scale_color_brewer(type="qualitative", palette="Dark2")
        + scale_fill_brewer(type="qualitative", palette="Dark2")
        + xlim((0, x_max))
        + ggtitle("Stan inferred parameter distributions\n(generating values dashed lines)")
    )
