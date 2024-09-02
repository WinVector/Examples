
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
        model = np.array(model)
        assert d.shape[1] == len(model)
        eval_scores = d @ model
    else:
        raise(f"unexpected model type {model_type}")
    return np.array(eval_scores)


def mk_example(
    features_frame: pd.DataFrame,
    *,
    features_scores: pd.DataFrame,
    continue_inspection_probability: float,
    n_alternatives: int,
    m_examples: int,
    score_name: str,
    noise_scale: float,
    price_limit_shape: float,
    price_limit_scale: float,
    rng,
) -> pd.DataFrame:
    # assemble lists of observations with top scoring entry picked
    observations = dict()
    for sel_j in range(n_alternatives):
        observations[f"display_position_{sel_j}"] = [sel_j] * m_examples
        selected_examples = rng.choice(
            features_frame.shape[0], size=m_examples, replace=True
        )
        observations[f"item_id_{sel_j}"] = selected_examples
        observations[f"pick_value_{sel_j}"] = [0] * m_examples
        observations[f"score_value_{sel_j}"] = (
            [  # noisy observation of score/utility
                features_scores.loc[int(selected_examples[row_i]), score_name]  # item score
                    + noise_scale * rng.normal(size=1)[0]  # score noise
                for row_i in range(m_examples)
            ]
        )
        observations[f'price_{sel_j}'] = [features_frame.loc[int(selected_examples[row_i]), 'price'] for row_i in range(m_examples)]
        observations['price_limit'] = rng.gamma(shape=price_limit_shape, scale=price_limit_scale, size=m_examples)
    observations = pd.DataFrame(observations)
    # mark selections
    for row_i in range(m_examples):
        best_j = None
        for sel_j in range(n_alternatives):
            if observations[f"price_{sel_j}"][row_i] <= observations['price_limit'][row_i]:
                if (best_j is None) or (observations[f"score_value_{sel_j}"][row_i] > observations[f"score_value_{best_j}"][row_i]):
                    best_j = sel_j
            if rng.binomial(n=1, p=continue_inspection_probability) <= 0:
                break  # end inspection prefix
        if best_j is not None:
            observations.loc[row_i, f"pick_value_{best_j}"] = 1
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
        for sel_j in range(n_alternatives):
            item_id = observations.loc[row_i, f'item_id_{sel_j}']
            score_v = observations.loc[row_i, f'score_value_{sel_j}']
            posn_details = [0] * n_alternatives
            posn_details[sel_j] = 1
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


def define_Stan_list_src(
    n_alternatives: int,
):
    stan_model_list_src = (
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
    return stan_model_list_src


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
                f"""  target += normal_lcdf( expect_picked | expect_passed_{i}, sqrt(2) * 10);
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

    def f_i(sel_j: int) -> str:
        id_seq = observations_sorted[f"item_id_{sel_j}"]
        posn_seq = observations_sorted[f"encoding_{sel_j}"]
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
    clean_up: bool = True,
    model_note: str = '',
    show_progress: bool = False,
    show_console: bool = False,
):
    # build model
    # export source and data
    stan_file = f"rank_src_{model_note}_tmp.stan"
    data_file = f"rank_data_{model_note}_tmp.json"
    with open(stan_file, "w", encoding="utf8") as file:
        file.write(stan_model_src)
    with open(data_file, "w", encoding="utf8") as file:
        file.write(data_str)
    # instantiate the model object
    model_comp = CmdStanModel(stan_file=stan_file)
    # fit to data
    fit = model_comp.sample(
        data=data_file,
        show_progress=show_progress,
        show_console=show_console,
    )
    if clean_up:
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


def estimate_selection_probs(
    *,
    est_row, 
    simulation_sigma: float,
    continue_inspection_probability: float,
    rng,
):
    n_draws = 100
    n_alternatives = len(est_row)
    draws = pd.DataFrame({
            f"est_{j}": rng.normal(
                loc=est_row[j], scale=simulation_sigma, size=n_draws
            )
            for j in range(n_alternatives)
        })
    picks = pd.DataFrame({
            f"pick_{j}": [0.0] * n_draws
            for j in range(n_alternatives)
        })
    # simulate sequential inspection
    for draw_i in range(n_draws):
        best_j = 0
        for j in range(1, n_alternatives):
            if rng.binomial(size=1, n=1, p=continue_inspection_probability)[0] <= 0:
                break  # abort sequential inspection
            if draws.loc[draw_i, f'est_{j}'] > draws.loc[draw_i, f'est_{best_j}']:
                best_j = j
        picks.loc[draw_i, f'pick_{best_j}'] = 1.0
    picks = np.array(picks.sum(axis=0)) + 1e-5
    picks = picks / np.sum(picks)
    return picks


def plot_rank_performance(
    model,  # score predicting model
    *,
    model_type: 'str',  # type of model ('classifier', 'regression', 'coef')
    example_name: str,  # name of data set
    n_alternatives: int,  # size of lists
    simulation_sigma: float,  # noise level in utility/score
    continue_inspection_probability: float,  # probability of inspecting next element
    features_frame,  # features by row id
    observations_train: pd.DataFrame,  # training observations layout frame
    observations_test: pd.DataFrame,  # evaluation observations layout frame
    estimate_name: str,  # display name of estimate
    score_compare_frame,  # score comparison frame (altered by call)
    rng,  # pseudo random source
    show_plots: bool = True,  # show plots
) -> pd.DataFrame:
    estimated_item_scores = predict_score(
        features_frame,
        model=model,
        model_type=model_type,
    )

    def p_select(row_i: int):
        est_row = [
            estimated_item_scores[
                int(observations_test.loc[row_i, f"item_id_{sel_j}"])
            ]  # estimated per item score
            for sel_j in range(n_alternatives)
        ]
        probs = estimate_selection_probs(
            est_row=est_row, 
            simulation_sigma=simulation_sigma,
            continue_inspection_probability=continue_inspection_probability,
            rng=rng,
        )
        train_pick = [
            observations_test.loc[row_i, f"pick_value_{sel_j}"] == 1
            for sel_j in range(n_alternatives)
        ]
        return pd.DataFrame(
            {
                "row": row_i,
                "position": range(n_alternatives),
                "pick probability estimate": probs,
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
    mean_pick_kl_divergence = kl_divergence / pick_frame.shape[0]  # average per list
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
                    f"{example_name} {estimate_name} Spearman R: {spearman_test.statistic:.2f}\n(out of sample data)\noriginal score as a function of recovered evaluation function"
                )
            ).show()
    return pd.DataFrame(
        {
            "example_name": [example_name],
            "estimate_name": [estimate_name],
            "SpearmanR_all": [spearman_all.statistic],
            "SpearmanR_test": [spearman_test.statistic],
            "pick_auc_test": [pick_auc],
            "pick_KL_div_test": [mean_pick_kl_divergence],
            "training_lists": [observations_train.shape[0]],
            "test_lists": [observations_test.shape[0]],
            "data_size": [features_frame.shape[0]],
            "test_size": [len(unobserved_ids)],
            "extra_info": [""],
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


def define_Stan_inspection_src(
    n_alternatives: int,
):
    stan_model_list_src = (
        """
data {
  int<lower=1> n_vars;  // number of variables per alternative"""
  + f"""
  int<lower={n_alternatives}, upper={n_alternatives}> n_alternatives;  // number of alternatives"""
  + """
  int<lower=1> m_examples;  // number of examples
  array[m_examples, n_alternatives] real<lower=0> price; // price of each item
  array[m_examples, n_alternatives] int<lower=0, upper=1> picked_indicator;  // picked position indicator
  array[m_examples] int<lower=0, upper=1> n_picks_seen;  // number marked picks per alternative
"""
        + "".join(
            [
                f"""  matrix[m_examples, n_vars] x_{j};  // features examples
"""
                for j in range(1, n_alternatives + 1)
            ]
        )
        + """}
parameters {
  real<lower=0, upper=1> p_continue;  // modeled probability of inspecting on
  vector[n_vars] beta;  // model parameter
  vector[m_examples] price_limit;  // upper bound on price willing to spend
  array[n_alternatives] vector[m_examples] error_picked;  // reified noise term on picks
}
transformed parameters {
  array[n_alternatives] vector[m_examples] drawn_value;  // modeled realized score of item
"""
  + """  real running_mass;   // mass we are analyzing
  real best_j_seen;  // best j seen up until now
  real best_draw_value_seen;  // best draw value until now
  real choice_was_a_pick;  // if best choice is in the pick data
  real supporting_mass;  // mass of all supporting observation states
  real countering_mass;  // mass of all countering observation states
  real stop_here_prob;  // probability of stopping at current inspection index
  vector[m_examples] p_supporting;  // sum of supporting event probabilities
      // modeled expected utility values
"""        + "".join([
                f"""  drawn_value[{j}] = x_{j} * beta + error_picked[{j}];
"""
                for j in range(1, n_alternatives + 1)
            ])
        + """  for (ex_i in 1:m_examples) {
    running_mass = 1.0;
    supporting_mass = 0.0;
    countering_mass = 0.0;
    best_j_seen = 0;
    best_draw_value_seen = 0;
    choice_was_a_pick = 0;
    if (n_picks_seen[ex_i] < 1) { // nothing picked case
      for (alt_j in 1:n_alternatives) {
        if (alt_j < n_alternatives) {
          stop_here_prob = running_mass * (1 - p_continue);
        } else {
          stop_here_prob = running_mass;
        }
        if (price[ex_i, alt_j] <= price_limit[ex_i]) {
          if ((best_j_seen <= 0) || 
            (drawn_value[alt_j][ex_i] >= best_draw_value_seen)) {
            best_j_seen = alt_j;
            best_draw_value_seen = drawn_value[alt_j][ex_i];
          }
        }
        if (best_j_seen >= 0) {
          countering_mass = countering_mass + stop_here_prob;
        }
        if (alt_j < n_alternatives) {
          running_mass = running_mass * p_continue;
        }
      }
      supporting_mass = supporting_mass + running_mass;
    } else {  // something picked case
      for (alt_j in 1:n_alternatives) {
        if (alt_j < n_alternatives) {
          stop_here_prob = running_mass * (1 - p_continue);
        } else {
          stop_here_prob = running_mass;
        }
        if (price[ex_i, alt_j] <= price_limit[ex_i]) {
          if ((best_j_seen <= 0) || 
            (drawn_value[alt_j][ex_i] >= best_draw_value_seen)) {
            best_j_seen = alt_j;
            best_draw_value_seen = drawn_value[alt_j][ex_i];
            choice_was_a_pick = 0;
            if (picked_indicator[ex_i, alt_j] > 0) {
              choice_was_a_pick = 1;
            }
          }
        }
        if (best_j_seen >= 0) {
          if (choice_was_a_pick > 0) {
            supporting_mass = supporting_mass + stop_here_prob;
          } else {
            countering_mass = countering_mass + stop_here_prob;
          }
        }
        if (alt_j < n_alternatives) {
          running_mass = running_mass * p_continue;
        }
      }
      countering_mass = countering_mass + running_mass;
    }
    p_supporting[ex_i] = (supporting_mass + 1.0e-7) / (supporting_mass + 1.0e-7 + countering_mass + 1.0e-7);  // Cromwell's rule smoothing
    if ((p_supporting[ex_i] <= 0) || (p_supporting[ex_i] >= 1)) {
        reject("p_supporting[ex_i] out of range", p_supporting[ex_i]);
    }
  }
}
model {
    // basic priors
  price_limit ~ normal(30, 30);
  p_continue ~ beta(1.0, 1.0);
  beta ~ normal(0, 10);
"""
  + "".join([
                f"""  error_picked[{i}] ~ normal(0, 10);
"""
                for i in range(1, n_alternatives + 1)
            ])
  + """    // log probability of observed selection as a function of parameters
  target += log(p_supporting);
}
""")
    return stan_model_list_src


def format_Stan_inspection_data(
    observations: pd.DataFrame,
    *,
    features_frame: pd.DataFrame,
):
    m_examples = observations.shape[0]
    n_alternatives = len([c for c in observations if c.startswith("item_id_")])
    n_vars = features_frame.shape[1]
    picks = observations.loc[:, [f'pick_value_{sel_j}' for sel_j in range(n_alternatives)]].reset_index(drop=True, inplace=False)
    n_picks_seen = np.array(picks.sum(axis=1), dtype=int).tolist()
    picks = np.array(picks, dtype=int).tolist()
    price = np.array(observations.loc[:, [f'price_{sel_j}' for sel_j in range(n_alternatives)]].reset_index(drop=True, inplace=False), dtype=float).tolist()

    def fmt_array(a) -> str:
        return json.dumps([v for v in list(a)])
    
    def fmt_matrix(a) -> str:
        return json.dumps([list(v) for v in list(a)])
    
    def mk_x_vec(sel_j: int):
        v = np.zeros((m_examples, n_vars), dtype=float)
        for row_i in range(m_examples):
            v[row_i, :] = features_frame.loc[int(observations.loc[row_i, f'item_id_{sel_j}']), :]
        return v

    data_str = (f"""
{{
 "n_vars" : {n_vars},
 "n_alternatives" : {n_alternatives},
 "m_examples" : {m_examples},
 "picked_indicator" : {fmt_matrix(picks)},
 "n_picks_seen" : {fmt_array(n_picks_seen)},
 "price": {fmt_matrix(price)},
"""
    + """,
""".join(
        [f""" "x_{sel_j+1}" : {fmt_matrix(mk_x_vec(sel_j))}""" for sel_j in range(n_alternatives)]
    )
    + """
}
""")
    return data_str
