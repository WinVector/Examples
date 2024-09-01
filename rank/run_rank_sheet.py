
# python run_rank_sheet.py
import os
import numpy as np
import pandas as pd
from wvpy.jtools import JTask

def try_run_k_times(task: JTask, *, k: int = 3):
    """Work around non-determinism in Apple file system"""
    for retry in range(3):
        try:
            task.render_as_html()
            return
        except Exception:
            pass


if __name__ == '__main__':
    # shut up the "Debugger warning: It seems that frozen modules are being used, which may"
    # warning coming in through debugging checks in nbconvert
    os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

    rng = np.random.default_rng(2024)

    # display examples
    m_examples_small = 100
    m_examples_large = 1000
    results = []
    for i in range(20):
        seed_i = rng.choice(2**31)
        result_fname = f'rankresult_tmp_{i}_{seed_i}.csv'
        task = JTask(
                sheet_name='learning_to_rank.ipynb',
                sheet_vars={
                    'rand_seed': seed_i,
                    'm_examples': m_examples_small,
                    'result_fname': result_fname,
                    'do_display': False,
                    'clean_up': True,
                    },
                output_suffix=f'_rankresult_tmp_{i}_{seed_i}',
            )
        try_run_k_times(task)
        result_i = pd.read_csv(result_fname)
        result_i['run_i'] = i
        result_i['rand_seed'] = seed_i
        results.append(result_i)
        html_result_name = f'learning_to_rank_rankresult_tmp_{i}_{seed_i}.html'
        os.remove(result_fname)
        os.remove(html_result_name)
    results = pd.concat(results, ignore_index=True)
    results.to_csv('rank_runs_summary.csv', index=False)
    for m_examples in [m_examples_small, m_examples_large]:
        for score_name in ["quality", "linear_score"]:
            seed_i = rng.choice(2**31)
            task = JTask(
                sheet_name='learning_to_rank.ipynb',
                sheet_vars={
                    'rand_seed': seed_i,
                    'm_examples': m_examples,
                    'score_name': score_name,
                    'clean_up': True,
                    },
                output_suffix=f'_display_{score_name}_{m_examples}',
            )
            try_run_k_times(task)
