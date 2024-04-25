"""
Build model from dataset
"""

#%%
from util import *

import json
import statsmodels.api as sm
import numpy as np
import pandas as pd
import logging

from statsmodels.discrete.discrete_model import BinaryResultsWrapper
from statsmodels.stats.outliers_influence import variance_inflation_factor
from numpyencoder import NumpyEncoder


path_dataset = PATH_SCRIPT / "out" / "metrics" / "normalized"

path_out = PATH_SCRIPT / "out" / 'models'
path_out.mkdir(parents=True, exist_ok=True)

#%%
# Configure logging
logging.basicConfig(filename=path_out / 'model.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


columns_to_remove = {}


is_significant = lambda num_str: float(num_str.strip()) <= 0.05


def parse_result(result:BinaryResultsWrapper):
    """
    table 1:
                                    Logit Regression Results                           
        ==============================================================================
        Dep. Variable:                      y   No. Observations:                   11
        Model:                          Logit   Df Residuals:                        3
        Method:                           MLE   Df Model:                            7
        Date:                Thu, 21 Mar 2024   Pseudo R-squ.:                     inf
        Time:                        17:34:10   Log-Likelihood:            -2.9859e-11
        converged:                      False   LL-Null:                        0.0000
        Covariance Type:            nonrobust   LLR p-value:                     1.000

    table 2:
                        coef    std err          z      P>|z|      [0.025      0.975]
        ------------------------------------------------------------------------------
        const         14.1883   9.19e+07   1.54e-07      1.000    -1.8e+08     1.8e+08
        x1             2.0124   5.78e+06   3.48e-07      1.000   -1.13e+07    1.13e+07
        x2             1.8430   7.51e+06   2.45e-07      1.000   -1.47e+07    1.47e+07
        x3             8.7950   9.19e+07   9.57e-08      1.000    -1.8e+08     1.8e+08
        x4             0.2822   2.39e+06   1.18e-07      1.000   -4.68e+06    4.68e+06
        x5            -1.4012   6.85e+06  -2.05e-07      1.000   -1.34e+07    1.34e+07
        x6             1.1969   1.78e+06   6.71e-07      1.000    -3.5e+06     3.5e+06
        x7            -0.0245   1.08e+07  -2.27e-09      1.000   -2.11e+07    2.11e+07

    extra_txt:
        Complete Separation: The results show that there iscomplete separation or perfect prediction.
        In this case the Maximum Likelihood Estimator does not exist and the parameters
        are not identified.
    """
    summary = result.summary()

    tab1 = summary.tables[0]
    tab2 = summary.tables[1]
    extra_txt = summary.extra_txt

    extract_key = lambda x: x.strip()[:-1]

    # tab1
    dic1 = dict()
    for row in tab1.data:
        dic1[extract_key(row[0])] = row[1].strip()
        dic1[extract_key(row[2])] = row[3].strip()

    # tab2
    df = pd.DataFrame(tab2.data[1:], columns=tab2.data[0])
    df.set_index('', inplace=True)
    dic2 = json.loads(df.to_json(orient='index'))   # can recover by pd.read_json(StringIO(json_str), orient='index')
    
    # significance
    significance = {var: is_significant(info["P>|z|"]) for var, info in dic2.items() if var != 'const'}

    # compute odd ratio
    odd_ratio = np.exp(result.params)
    odd_ratio = odd_ratio.drop('const', errors='ignore')

    return {'model info': dic1, 'coef info': dic2, 'extra_txt': extra_txt, 'odd_ratio': odd_ratio.to_dict(), 'significance': significance}


#%%
def build_model(project_path:Path):
    ref_mtr = pd.read_csv(project_path) 
    refactorings = ref_mtr['refactoring'].unique()

    # remove columns according to Spearman’s rank correlation
    mtrs_to_remove = columns_to_remove.get(project_path.stem, None)
    if mtrs_to_remove:
        iv_names = [m for m in METRIC_COLUMNS if m not in mtrs_to_remove]
        ref_mtr = ref_mtr.drop(columns=mtrs_to_remove)

    iv_names = list(ref_mtr.columns)[1:]  # remove the first column 'refactoring'

    ref_models = dict()
    for ref in refactorings:
        data = ref_mtr[ref_mtr['refactoring'] == ref][iv_names]
        Y = np.ones(len(data))

        # # Calculate VIF for each feature: the data size for some refactorings is too small
        # vif_data = pd.DataFrame()
        # vif_data["feature"] = data.columns
        # vif_data["VIF"] = [variance_inflation_factor(data.values, i) for i in range(len(data.columns))]
        # feature_to_remove = vif_data[vif_data['VIF'] > 10]['feature']

        # Add constant to the independent variables
        X = sm.add_constant(data)
        # Fit logistic regression model
        model = sm.Logit(Y, X)

        result = None
        
        for max_iter in [1500, 1000, 500, 100, 35]:
            try:
                result = model.fit(maxiter=max_iter)
            except Exception as e:
                logging.info(f"{project_path.stem} : {ref} : data size {len(X)} : maxiter {max_iter}\n{e}")
                continue

            break
             
        if result:
            # Check for ConvergenceWarning
            if not result.mle_retvals['converged']:
                logging.info(f"Non-Converged model for {project_path.stem} : {ref} : data size {len(X)} : max_iter = {max_iter}")
            else:
                logging.info(f"Converged model for {project_path.stem} : {ref} : data size {len(X)} : maxiter {max_iter}")

            ref_models[ref] = parse_result(result)
        else:
            logging.error(f"Fail to build model for {project_path.stem} : {ref} : data size {len(X)}")
    return {'independent variables': iv_names, 'refactoring models': ref_models}


def main():
    projects = path_dataset.glob('*.csv')
    for project in projects:
        project_models = build_model(project)
    
        with open(path_out / f'{project.stem}.json', 'w') as f:
            json.dump(project_models, f, indent=4, cls=NumpyEncoder)

main()