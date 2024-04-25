from util import *


import pandas as pd
import json
from collections import defaultdict
from numpyencoder import NumpyEncoder


path_mtrs = PATH_SCRIPT / "out" / "metrics"

path_out = PATH_SCRIPT / "out" / 'correlation2'
path_out.mkdir(parents=True, exist_ok=True)
        
sort_dict = lambda d: dict(sorted(d.items(), key=lambda item: len(item[1]), reverse=True)) 

def compute():
    """
    compute the Spearman’s rank correlation for each sub-dataset of a refactoring
    """
    ans = defaultdict(dict)
    
    path_input = path_mtrs / 'normalized'
    
    projects = path_input.glob('*.csv')
    for pro in projects:
        ref_mtr = pd.read_csv(pro)
        refactorings = ref_mtr['refactoring'].unique()
        
        for ref in refactorings:
            df = ref_mtr[ref_mtr['refactoring'] == ref][METRIC_COLUMNS]
            correlation_matrix = df.corr(method='spearman')
            
            # Filter pairs with correlation > 0.8
            high_correlation_pairs = []
            high_correlation_dict = defaultdict(list)
            for col1 in correlation_matrix.columns:
                for col2 in correlation_matrix.columns:
                    if col1 < col2 and correlation_matrix.loc[col1, col2] >= 0.8:
                        high_correlation_pairs.append((col1, col2, correlation_matrix.loc[col1, col2]))
                        high_correlation_dict[col1].append(col2)
                        high_correlation_dict[col2].append(col1)
                    
            if high_correlation_pairs:                       
                ans[pro.stem][ref] = {'high_correlation_pairs': high_correlation_pairs, 'high_correlation_dict': sort_dict(high_correlation_dict)}
            
    with open(path_out / 'correlation.json', 'w') as f:
        json.dump(ans, f, indent=4, cls=NumpyEncoder)


def auto_remove():
    # decide the columns should be removed for each sub-dataset of a refactoring
    # remove the column correlating to the most columns first
    
    with open(path_out / 'correlation.json', 'r') as f:
        correlation = json.load(f)
        
    ans = defaultdict(dict)
    for proj, data in correlation.items():
        for ref, cor_data in data.items():
            cor_dict = cor_data.get('high_correlation_dict', None)
            
            metrics_to_remove = list()
            
            while cor_dict:
                keys = list(cor_dict.keys())
                
                # remove keys[0] and update the values of other keys
                if keys[0] == 'loc' and len(cor_dict[keys[0]]) == len(cor_dict[keys[1]]):
                    # prefer to keep loc
                    metrics_to_remove.append(keys[1])
                    del cor_dict[keys[1]]
                else:
                    metrics_to_remove.append(keys[0])
                    del cor_dict[keys[0]]
                
                keys = list(cor_dict.keys())
                for k in keys:
                    correlated_metrics = cor_dict[k]
                    if metrics_to_remove[-1] in correlated_metrics:
                        correlated_metrics.remove(metrics_to_remove[-1])
                    
                    if not correlated_metrics:
                        del cor_dict[k]
                        
            ans[proj][ref] = metrics_to_remove
            
    with open(path_out / 'remove.json', 'w') as f:
        json.dump(ans, f, indent=4, cls=NumpyEncoder)        
                          

# compute()
auto_remove()