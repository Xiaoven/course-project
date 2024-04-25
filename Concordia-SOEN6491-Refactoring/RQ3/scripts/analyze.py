from util import *

import json
import pandas as pd
import numpy as np
from collections import defaultdict
import math

path_models = PATH_SCRIPT / "out" / 'models'

path_out = PATH_SCRIPT / "out" / 'analyze'
path_out.mkdir(parents=True, exist_ok=True)


def _is_significant(pval:str):
    pval = pval.lower().strip()
    
    try:
        pnum = float(pval)
        return pnum < 0.05
    except ValueError:
        return False
    
    
def find_significant():
    # load coef info
    dataset = dict()
    projects = path_models.glob('*.json')
    for project in projects:
        with open(project, 'r') as f:
            models = json.load(f)

        dataset[project.stem] = {
            ref: info['coef info'] for ref, info in models['refactoring models'].items()
        }
    ans = defaultdict(dict)
    for project, data in dataset.items():
        for ref, coefs in data.items():
            sig = [f"{c}:{info['P>|z|'].strip()}" for c, info in coefs.items() if c != 'const' and _is_significant(info['P>|z|'])]
            if sig:
                ans[project][ref] = sig
    
    with open(path_out / 'significance.json', 'w') as f:
        json.dump(ans, f, indent=4)
    
    

def main():
    # load odd ratio
    dataset = dict()
    projects = path_models.glob('*.json')
    for project in projects:
        with open(project, 'r') as f:
            models = json.load(f)

        dataset[project.stem] = {
            ref: info['odd_ratio'] for ref, info in models['refactoring models'].items()
        }


    ref_k = set(dataset['kafka'].keys())
    ref_gson  = set(dataset['gson'].keys())
    ref_spring = set(dataset['spring-security'].keys())

    # dataframe 1: gson union spring-security
    df1 = pd.DataFrame(columns=['Refactoring', 'System', *METRIC_COLUMNS])
    refs = ref_gson | ref_spring
    for ref in refs:
        for project, data in dataset.items():
            if ref not in data:
                row = {metric: np.nan for metric in METRIC_COLUMNS}
            else:
                row = {metric: data[ref].get(metric, np.nan) for metric in METRIC_COLUMNS}
                
            row = {key: round(value, 2) if not (value == float('inf') or value == float('nan')) else value 
                for key, value in row.items()}
            # process large number
            row = {key: "{:.2e}".format(value) if value > 10000 else value for key, value in row.items()}
            
            row['Refactoring'] = ref
            row['System'] = project
            df1.loc[len(df1)] = row
            
     # remove rows that all metrics are nan
    df1 = df1[df1[METRIC_COLUMNS].notna().all(axis=1)]

    df1 = df1.fillna('-')
    
    df1 = df1.sort_values(by=['Refactoring', 'System'])
    
    df1.to_csv(path_out / 'gson-spring.csv', index=False)
    

    # dataframe 2: the rest of refactorings in kafka
    df2 = pd.DataFrame(columns=['Refactoring', *METRIC_COLUMNS])
    refs = ref_k - refs
    data = dataset['kafka']
    for ref in refs:
        row = {metric: data[ref].get(metric, np.nan) for metric in METRIC_COLUMNS}
        row = {key: round(value, 2) if not (value == float('inf') or value == float('nan')) else value 
                for key, value in row.items()}
        row = {key: "{:.2e}".format(value) if value > 10000 else value for key, value in row.items()}
        row['Refactoring'] = ref
        df2.loc[len(df2)] = row

    # remove rows that all metrics are nan
    df2 = df2[df2[METRIC_COLUMNS].notna().all(axis=1)]

    df2 = df2.fillna('-')
    
    df2 = df2.sort_values(by='Refactoring')
    df2.to_csv(path_out / 'kafka.csv', index=False)

main()
find_significant()
    
