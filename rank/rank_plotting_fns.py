
import os
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import sklearn.metrics
from scipy.stats import spearmanr
from IPython.display import display
import xgboost as xgb
from cmdstanpy import CmdStanModel
from plotnine import *
from wvu.util import plot_roc, threshold_plot


def logit(v):
    v = np.array(v)
    return np.log(v/(1-v))


def predict_score(
    d,
    *,
    model,
    model_type: 'str',  # type of model ('classifier', 'regression', 'coef')
):
    if model_type == 'classifier':
        preds = model.predict_proba(d)
        eval_scores = logit(np.array(preds)[:, 1])
    elif model_type == 'regression':
        eval_scores = model.predict(d)
    elif model_type == 'coef':
        eval_scores = d @ np.array(model)
    else:
        raise(f"unexpected model type {model_type}")
    return np.array(eval_scores)


def mk_example(
    features_frame: pd.DataFrame,
    *,
    features_scores: pd.DataFrame,
    position_penalties,
    m_examples: int,
    score_name: str,
    noise_scale: float,
    rng,
) -> pd.DataFrame:
    # assemble panels of observations with top scoring entry picked
    n_alternatives = len(position_penalties)
    observations = dict()
    for sel_i in range(n_alternatives):
        observations[f"display_position_{sel_i}"] = [sel_i] * m_examples
        selected_examples = rng.choice(
            features_frame.shape[0], size=m_examples, replace=True
        )
        observations[f"item_id_{sel_i}"] = selected_examples
        observations[f"score_value_{sel_i}"] = (
            [  # noisy observation of score plus position penalty
                features_scores.loc[int(selected_examples[i]), score_name]  # item score
                + position_penalties[sel_i]  # positional penalty
                + noise_scale * rng.normal(size=1)[0]  # observation noise
                for i in range(m_examples)
            ]
        )
        observations[f"pick_value_{sel_i}"] = [0] * m_examples
    observations = pd.DataFrame(observations)
    # mark selections
    for i in range(m_examples):
        best_j = 0
        for j in range(1, n_alternatives):
            if (
                observations[f"score_value_{j}"][i]
                > observations[f"score_value_{best_j}"][i]
            ):
                best_j = j
        observations.loc[i, f"pick_value_{best_j}"] = 1
    return observations


def estimate_model_from_scores(
    observations: pd.DataFrame,
    *,
    features_frame: pd.DataFrame,
):
    # get a perfect model for comparison
    n_alternatives = len([c for c in observations if c.startswith("item_id_")])
    x = []
    y = []
    for row_i in range(observations.shape[0]):
        for sel_i in range(n_alternatives):
            item_id = observations.loc[row_i, f'item_id_{sel_i}']
            score_v = observations.loc[row_i, f'score_value_{sel_i}']
            posn_details = [0] * n_alternatives
            posn_details[sel_i] = 1
            x_i = list(features_frame.loc[item_id, :]) + posn_details
            x.append(np.array(x_i))
            y.append(score_v)
    x = pd.DataFrame(x)
    new_names = list(features_frame.columns) + [f'posn_{i}' for i in range(n_alternatives)]
    x.columns = new_names
    y = np.array(y)
    direct_model = LinearRegression()
    direct_model.fit(
        x,
        y,
    )
    return np.array(direct_model.coef_)


def sort_observations_frame(
    observations: pd.DataFrame,
):
    # swap all observed alternatives selections into picked position
    m_examples = observations.shape[0]
    n_alternatives = len([c for c in observations if c.startswith("item_id_")])
    observations_sorted = observations.copy()
    for passed_i in range(1, n_alternatives):
        for row_i in range(m_examples):
            if observations_sorted.loc[row_i, f"pick_value_{passed_i}"] > 0:
                # swap where data is stored in row
                for dest_col, source_col in (
                    ("display_position_0", f"display_position_{passed_i}"),
                    ("item_id_0", f"item_id_{passed_i}"),
                    ("pick_value_0", f"pick_value_{passed_i}"),
                ):
                    v_source = observations_sorted.loc[row_i, source_col]
                    v_dest = observations_sorted.loc[row_i, dest_col]
                    observations_sorted.loc[row_i, source_col] = v_dest
                    observations_sorted.loc[row_i, dest_col] = v_source
    observations_sorted.rename(
        columns={
            f"display_position_{i}": f"encoding_{i}" for i in range(n_alternatives)
        },
        inplace=True,
    )
    return observations_sorted


def define_Stan_panel_src(
    n_alternatives: int,
):
    stan_model_panel_src = (
        """
data {
  int<lower=1> n_vars;                     // number of variables per alternative
  int<lower=1> m_examples;                 // number of examples
  matrix[m_examples, n_vars] x_picked;     // character of picked examples
"""
        + "".join(
            [
                f"""  matrix[m_examples, n_vars] x_passed_{i};   // character of passed examples
"""
                for i in range(1, n_alternatives)
            ]
        )
        + """}
parameters {
  vector[n_vars] beta;                      // model parameters
  vector[m_examples] error_picked;          // reified noise term on picks (the secret sauce!)
}
transformed parameters {
  vector[m_examples] expect_picked;
  vector[m_examples] v_picked;
"""
        + "".join(
            [
                f"""  vector[m_examples] expect_passed_{i};
"""
                for i in range(1, n_alternatives)
            ]
        )
        + """  expect_picked = x_picked * beta;          // modeled expected score of picked item
  v_picked = expect_picked + error_picked;  // reified actual score of picked item
"""
        + "".join(
            [
                f"""  expect_passed_{i} = x_passed_{i} * beta;      // modeled expected score of passed item
"""
                for i in range(1, n_alternatives)
            ]
        )
        + """}
model {
    // basic priors
  beta ~ normal(0, 10);
  error_picked ~ normal(0, 10);
    // log probability of observed ordering as a function of parameters
    // terms are independent conditioned on knowing value of v_picked!
"""
        + "".join(
            [
                f"""  target += normal_lcdf( v_picked | expect_passed_{i}, 10);
"""
                for i in range(1, n_alternatives)
            ]
        )
        + """}
"""
    )
    return stan_model_panel_src


def define_Stan_choice_src(
    n_alternatives: int,
):
    stan_model_comparison_src = (
        """
data {
  int<lower=1> n_vars;                     // number of variables per alternative
  int<lower=1> m_examples;                 // number of examples
  matrix[m_examples, n_vars] x_picked;     // character of picked examples
"""
        + "".join(
            [
                f"""  matrix[m_examples, n_vars] x_passed_{i};   // character of passed examples
"""
                for i in range(1, n_alternatives)
            ]
        )
        + """}
parameters {
  vector[n_vars] beta;                      // model parameters
}
transformed parameters {
  vector[m_examples] expect_picked;
"""
        + "".join(
            [
                f"""  vector[m_examples] expect_passed_{i};
"""
                for i in range(1, n_alternatives)
            ]
        )
        + """  expect_picked = x_picked * beta;          // modeled expected score of picked item
"""
        + "".join(
            [
                f"""  expect_passed_{i} = x_passed_{i} * beta;      // modeled expected score of passed item
"""
                for i in range(1, n_alternatives)
            ]
        )
        + """}
model {
    // basic priors
  beta ~ normal(0, 10);
    // log probability of observed ordering as a function of parameters
"""
        + "".join(
            [
                f"""  target += normal_lcdf( 0 | expect_passed_{i} - expect_picked, sqrt(2) * 10);
"""
                for i in range(1, n_alternatives)
            ]
        )
        + """}
"""
    )
    return stan_model_comparison_src


def format_Stan_data(
    observations_sorted: pd.DataFrame,
    *,
    features_frame: pd.DataFrame,
):
    m_examples = observations_sorted.shape[0]
    n_alternatives = len([c for c in observations_sorted if c.startswith("item_id_")])
    n_vars = features_frame.shape[1] + n_alternatives
    def fmt_array(a) -> str:
        return json.dumps([v for v in a])

    def mk_posn_indicator(posn: int) -> str:
        posn_indicators = [0] * n_alternatives
        posn_indicators[posn] = 1
        return posn_indicators

    def f_i(sel_i: int) -> str:
        id_seq = observations_sorted[f"item_id_{sel_i}"]
        posn_seq = observations_sorted[f"encoding_{sel_i}"]
        return fmt_array(
            [
                list(features_frame.loc[int(id), :]) + mk_posn_indicator(int(posn))
                for id, posn in zip(id_seq, posn_seq)
            ]
        )

    data_str = (f"""
{{
 "n_vars" : {n_vars},
 "m_examples" : {m_examples},
 "x_picked" : {f_i(0)},
"""
    + """,
""".join(
        [f""" "x_passed_{i}" : {f_i(i)}""" for i in range(1, n_alternatives)]
    )
    + """
}
""")
    return data_str


def run_stan_model(
    stan_model_src: str,
    *,
    data_str: str,
):
    # build model
    # export source and data
    stan_file = "rank_src_tmp.stan"
    data_file = "rank_data_tmp.json"
    with open(stan_file, "w", encoding="utf8") as file:
        file.write(stan_model_src)
    with open(data_file, "w", encoding="utf8") as file:
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
    fit_line_model.fit(df[[xcol]], df[ycol])
    fit_frame = pd.DataFrame(
        {
            xcol: [np.min(df[xcol]), np.max(df[xcol])],
        }
    )
    fit_frame[ycol] = fit_line_model.predict(fit_frame[[xcol]])
    return fit_frame


def calc_auc(*, y_true, y_score) -> float:
    fpr, tpr, _ = sklearn.metrics.roc_curve(
        y_true=y_true,
        y_score=y_score,
    )
    return sklearn.metrics.auc(fpr, tpr)


def est_position_effect(
    i: int,
    *,
    model,  # score predicting model
    model_type: 'str',  # type of model ('classifier', 'regression', 'coef')
    n_alternatives: int,  # size of panels
    features_frame,  # features by row id
) -> float:
    eval_frame = pd.concat([
        features_frame,
        pd.DataFrame({
            f'position_{pi}': [0] * features_frame.shape[0] 
            for pi in range(n_alternatives)
        })
    ], axis=1)
    eval_frame[f'position_{i}'] = 1
    estimated_item_scores = predict_score(
        eval_frame,
        model=model,
        model_type=model_type,
    )
    return np.mean(estimated_item_scores)


def plot_rank_performance(
    model,  # score predicting model
    *,
    model_type: 'str',  # type of model ('classifier', 'regression', 'coef')
    example_name: str,  # name of data set
    n_alternatives: int,  # size of panels
    features_frame,  # features by row id
    observations_train: pd.DataFrame,  # training observations layout frame
    observations_test: pd.DataFrame,  # evaluation observations layout frame
    estimate_name: str,  # display name of estimate
    position_penalties=None,  # ideal position penalties
    score_compare_frame,  # score comparison frame (altered by call)
    rng,  # pseudo random source
    show_plots: bool = True,  # show plots
) -> pd.DataFrame:
    simulation_sigma = 10

    position_effects_frame = pd.DataFrame({
            "position": [f"posn_{i}" for i in range(n_alternatives)],
            "estimated effect": [
                est_position_effect(
                    i=i,
                    model=model,
                    model_type=model_type,
                    n_alternatives=n_alternatives,
                    features_frame=features_frame,
                )
                for i in range(n_alternatives)
            ]
        })
    position_effects_frame["estimated effect"] = (
        position_effects_frame["estimated effect"]
        - np.max(position_effects_frame["estimated effect"])
    )
    if show_plots and (position_penalties is not None):
        position_effects_frame["actual effect"] = position_penalties
        plt_posns = (
            ggplot(
                data=position_effects_frame,
                mapping=aes(
                    x="estimated effect",
                    y="actual effect",
                    label="position",
                ),
            )
            + geom_label(ha="left", va="top")
            + geom_point()
            + ggtitle(
                f"{example_name} {estimate_name}\nactual position effect as a function estimated effect"
            )
        )
        print("estimated position influences")
        display(position_effects_frame)
        plt_posns.show()
    eval_frame = pd.concat([
        features_frame,
        pd.DataFrame({
            f'position_{i}': [1/n_alternatives] * features_frame.shape[0] 
            for i in range(n_alternatives)
        })
    ], axis=1)
    estimated_item_scores = predict_score(
        eval_frame,
        model=model,
        model_type=model_type,
    )

    def p_select(row_i: int):
        n_draws: int = 10000
        est_row = [
            estimated_item_scores[
                int(observations_test.loc[row_i, f"item_id_{sel_i}"])
            ]  # estimated per item score
            + position_effects_frame.loc[
                sel_i, "estimated effect"
            ]  # estimated position effect
            for sel_i in range(n_alternatives)
        ]
        est_picks = [0] * n_alternatives
        est_picks[np.argmax(est_row)] = 1
        draws = pd.DataFrame(
            {
                f"est_{i}": rng.normal(
                    loc=est_row[i], scale=simulation_sigma, size=n_draws
                )
                for i in range(n_alternatives)
            }
        )
        draws_maxes = draws.max(axis=1)
        draws = pd.DataFrame({k: draws[k] >= draws_maxes for k in draws.columns})
        draws = draws.sum(axis=0)
        draws = draws / np.sum(draws)
        train_pick = [
            observations_test.loc[row_i, f"pick_value_{sel_i}"] == 1
            for sel_i in range(n_alternatives)
        ]
        return pd.DataFrame(
            {
                "row": row_i,
                "position": range(n_alternatives),
                "pick probability estimate": draws,
                "was pick": train_pick,
            }
        )

    pick_frame = [p_select(row_i) for row_i in range(observations_test.shape[0])]
    pick_frame = pd.concat(pick_frame, ignore_index=True)
    pick_auc = calc_auc(
        y_true=pick_frame["was pick"],
        y_score=pick_frame["pick probability estimate"],
    )
    kl_divergence = -np.sum(np.log(pick_frame.loc[pick_frame["was pick"] == True, "pick probability estimate"])) / np.log(2.0)
    mean_pick_kl_divergence = kl_divergence / pick_frame.shape[0]  # average per panel
    if show_plots:
        print("picks")
        display(pick_frame.head(10))
        (
            ggplot(
                data=pick_frame,
                mapping=aes(
                    x="pick probability estimate",
                    color="was pick",
                    fill="was pick",
                ),
            )
            + geom_density(alpha=0.7)
            + ggtitle(
                f"{example_name} {estimate_name}\npick probability estimate grouped by truth value"
            )
        ).show()
        plot_roc(
            prediction=pick_frame["pick probability estimate"],
            istrue=pick_frame["was pick"],
            ideal_line_color="lightgrey",
            title=f"{example_name} {estimate_name}\nROC of pick selection (mean KL div.: {mean_pick_kl_divergence:.2f})",
        )
        threshold_plot(
            pick_frame,
            pred_var="pick probability estimate",
            truth_var="was pick",
            plotvars=("precision", "recall"),
            title=f"{example_name} {estimate_name}\nprecision recall tradeoffs",
        )
    score_compare_frame[estimate_name] = estimated_item_scores
    spearman_all = spearmanr(
        score_compare_frame[estimate_name],
        score_compare_frame["hidden concept"],
    )
    if show_plots:
        fit_frame = build_line_frame(
            score_compare_frame, xcol=estimate_name, ycol="hidden concept"
        )
        (
            ggplot(
                data=score_compare_frame,
                mapping=aes(x=estimate_name, y="hidden concept"),
            )
            + geom_point(alpha=0.2)
            + geom_line(data=fit_frame, color="blue")
            + ggtitle(
                f"{example_name} {estimate_name} Spearman R: {spearman_all.statistic:.2f}\noriginal score as a function of recovered evaluation function"
            )
        ).show()
    observed_ids = set(
        observations_train.loc[
            :, [c for c in observations_train.columns if c.startswith("item_id_")]
        ].values.flatten()
    )
    unobserved_ids = [
        i for i in range(features_frame.shape[0]) if i not in observed_ids
    ]
    spearman_test = np.nan
    if len(unobserved_ids) > 10:
        score_compare_frame_test = score_compare_frame.loc[
            unobserved_ids, :
        ].reset_index(drop=True, inplace=False)
        spearman_test = spearmanr(
            score_compare_frame_test[estimate_name],
            score_compare_frame_test["hidden concept"],
        )
        if show_plots:
            fit_frame_test = build_line_frame(
                score_compare_frame_test, xcol=estimate_name, ycol="hidden concept"
            )
            (
                ggplot(
                    data=score_compare_frame_test,
                    mapping=aes(x=estimate_name, y="hidden concept"),
                )
                + geom_point(alpha=0.2)
                + geom_line(data=fit_frame_test, color="blue")
                + ggtitle(
                    f"{example_name} {estimate_name} Spearman R: {spearman_test.statistic:.2f} (out of sample data)\noriginal score as a function of recovered evaluation function"
                )
            ).show()
    return pd.DataFrame(
        {
            "example_name": [example_name],
            "estimate_name": [estimate_name],
            "SpearmanR_all": [spearman_all.statistic],
            "SpearmanR_test": [spearman_test.statistic],
            "pick_auc": [pick_auc],
            "mean pick KL divergence": [mean_pick_kl_divergence],
            "training panels": [observations_train.shape[0]],
            "test panels": [observations_test.shape[0]],
            "data_size": [features_frame.shape[0]],
            "test_size": [len(unobserved_ids)],
        }
    )

# https://xgboost.readthedocs.io/en/latest/tutorials/learning_to_rank.html
class XgboostClassifier():
    bst_ = None
    rng_ = None

    def __init__(self, *, rng):
        self.rng_ = rng

    def fit(
        self,
        X,
        y,
    ):
        y = np.array(y)
        # conda install -c conda-forge xgboost 
        # pip install xgboost
        # https://xgboost.readthedocs.io/en/stable/python/python_intro.html
        param = {
            'max_depth': 5, 
            'eta': 1, 
            'objective': 'binary:logistic',
            'nthread': 4,
            'eval_metric': ['logloss', 'auc']
            }
        num_round = 100
        train_group = self.rng_.choice(3, size=X.shape[0], replace=True)
        X_train_data = X.loc[train_group != 2, :].reset_index(drop=True, inplace=False)
        X_train_label = y[train_group != 2]
        dtrain = xgb.DMatrix(
            X_train_data,
            label=X_train_label,
        )
        X_test_data = X.loc[train_group == 2, :].reset_index(drop=True, inplace=False)
        X_test_label = y[train_group == 2]
        dtest = xgb.DMatrix(
            X_test_data,
            label=X_test_label,
        )
        evallist = [(dtrain, 'train'), (dtest, 'eval')]
        self.bst_ = xgb.train(
            params=param, 
            dtrain=dtrain, 
            num_boost_round=num_round, 
            early_stopping_rounds=10, 
            evals=evallist,
        )
        return self

    def predict_proba(
        self,
        X,
    ):
        preds = self.bst_.predict(
            xgb.DMatrix(X), 
            iteration_range=(0, self.bst_.best_iteration + 1),
        )
        return np.array([[1-pi, pi] for pi in preds])
