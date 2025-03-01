
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import root_mean_squared_error


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
    # try to pull off transient regressors
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

