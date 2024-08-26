
# python run_rank_sheet.py
import os
import numpy as np
import pandas as pd
from wvpy.jtools import JTask

if __name__ == '__main__':
    rng = np.random.default_rng(2024)

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
