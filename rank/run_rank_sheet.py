
# python run_rank_sheet.py
import os
import numpy as np
import pandas as pd
from wvpy.jtools import JTask

if __name__ == '__main__':
    # shut up the "Debugger warning: It seems that frozen modules are being used, which may"
    # warning coming in through debugging checks in nbconvert
    os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

    rng = np.random.default_rng(2024)

    # display examples
    for m_examples in [100, 1000]:
        for score_name in ["quality", "linear_score"]:
            seed_i = rng.choice(2**31)
            task = JTask(
                sheet_name='learning_to_rank.ipynb',
                sheet_vars={
                    'rand_seed': seed_i,
                    'm_examples': m_examples,
                    'score_name': score_name,
                    'clean_up': True,
                    'show_console': True,
                    },
                output_suffix=f'_display_{score_name}_{m_examples}',
            )
            task.render_as_html()
    results = []
    for i in range(20):
        seed_i = rng.choice(2**31)
        result_fname = f'rankresult_tmp_{i}_{seed_i}.csv'
        task = JTask(
                sheet_name='learning_to_rank.ipynb',
                sheet_vars={
                    'rand_seed': seed_i, 
                    'result_fname': result_fname,
                    'do_display': False,
                    'clean_up': True,
                    'show_console': True,
                    },
                output_suffix=f'_rankresult_tmp_{i}_{seed_i}',
            )
        task.render_as_html()
        result_i = pd.read_csv(result_fname)
        result_i['run_i'] = i
        result_i['rand_seed'] = seed_i
        results.append(result_i)
        html_result_name = f'learning_to_rank_rankresult_tmp_{i}_{seed_i}.html'
        os.remove(result_fname)
        os.remove(html_result_name)
    results = pd.concat(results, ignore_index=True)
    results.to_csv('rank_runs_summary.csv', index=False)
