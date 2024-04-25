"""
Read metrics of the classes for each refactoring type identified in process_refactorings.
Prepare input data for the logistic regression model
"""

#%%
from util import *

import json
from collections import defaultdict
import pandas as pd
import logging


path_out = PATH_SCRIPT / 'out' / 'metrics'
path_out.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(filename=path_out / 'process_metrics.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


path_input_refactorings = PATH_SCRIPT / 'out' / 'refactorings'

#%%
def _concat_csvs(project_name:str):
    """
    Load selected metrics for a given project: LOC, WMC, DIT, NOC, RFC, CBO, LCOM
    Return a list of dataframe
    """
    root = PATH_METRICS / project_name
    versions = [item for item in root.iterdir() if item.is_dir()]

    dfs = list()
    columns_to_read = ['file', 'class', 'type', 'loc', 'wmc', 'dit', 'noc', 'rfc', 'cbo', 'lcom']
    for v in versions:
        csv_paths = v.rglob('*.csv')
        for p in csv_paths:
            df = pd.read_csv(p, usecols=columns_to_read)
            df.insert(0, 'version', v.name)
            dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


def concat_metrics():
    """
    Concat class.csv files for each project into one
    """
    path_to_write = path_out / 'concat'
    path_to_write.mkdir(parents=True, exist_ok=True)

    projects = [item for item in PATH_METRICS.iterdir() if item.is_dir()]
    for project in projects:
        df = _concat_csvs(project.name)
        df.to_csv(path_to_write / f'{project.name}.csv', index=False)


def normalize_dataset():
    """
    Normalize the dataset using z-score normalization.
    """
    path_input = path_out / 'dataset'

    projects = path_input.glob('*.csv')
    dataframes = dict()
    for project in projects:
        dataframes[project.stem] = pd.read_csv(project)

    # Concatenate all dataframes into a single dataframe
    concatenated_df = pd.concat(dataframes.values())

    # Calculate mean and standard deviation across all dataframes
    mean_values = concatenated_df[METRIC_COLUMNS].mean()
    std_values = concatenated_df[METRIC_COLUMNS].std()

    # Normalize each dataframe using the computed mean and standard deviation
    normalized_dataframes = dict()
    for name, df in dataframes.items():
        df_copy = df.copy()
        for column in METRIC_COLUMNS:
            df_copy[column] = (df_copy[column] - mean_values[column]) / std_values[column]
        normalized_dataframes[name] = df_copy

    # Write normalized_dataframes
    path_to_write = path_out / 'normalized'
    path_to_write.mkdir(parents=True, exist_ok=True)
    for name, df in normalized_dataframes.items():
        df.to_csv(path_to_write / f'{name}.csv', index=False)


def load_metrics():
    path_normlized = path_out / 'concat'

    dataframes = dict()
    for p in path_normlized.glob('*.csv'):
        dataframes[p.stem] = pd.read_csv(p)

    return dataframes


def process_project(project_path:Path, project_metrics:pd.DataFrame):
    with open(project_path, 'r') as f:
        versions = json.load(f)

    # count the occurrences of the refactoring types
    counter = defaultdict(int)
    for version in versions:
        for ref_type, num in version['counter'].items():
            counter[ref_type] += num

    # Create the defaultdict with a lambda function as the default factory
    ref_mtr_dict = defaultdict(list)
    df = pd.DataFrame(columns=['refactoring', *METRIC_COLUMNS])
    for version in versions:
        mtrs_bf = project_metrics[project_metrics['version'] == version['rel_from']]
        mtrs_aft = project_metrics[project_metrics['version'] == version['rel_to']]

        rename = version['rename']

        for ref_type, classes in version['ref_dict'].items():
            # filter out refactoring types that occur less than 10 times to avoid creating unreliable logistic regression models
            freq = counter.get(ref_type, 0)
            if freq < 10:
                logging.info(f'Skip {ref_type} with frequence {freq}')
                continue

            # find metrics for each class
            for clazz in classes:
                # read metrics of clazz before and after applying the refactoring type
                mtr_before = mtrs_bf[(mtrs_bf['file'].str.endswith(clazz)) & (mtrs_bf['type'] == 'class')]

                if len(mtr_before) == 0: # may be a right side file for a renaming class refactoring, skip it
                    continue
                elif len(mtr_before) > 1:
                    # bad practice: more than one classes in one Java file
                    # e.g., kafka/examples/src/main/java/kafka/examples/Producer.java      kafka.examples.Producer
                    #       kafka/examples/src/main/java/kafka/examples/Producer.java  kafka.examples.DemoCallBack
                    # logging.warning(f"Multiple metrics for class {clazz} : {version['rel_from']}\n{mtr_before.to_string()}")
                    # mtr_before = mtr_before[mtr_before.apply(lambda row: row['file'].endswith(f"/{row['class'].split('.')[-1]}.java"), axis=1)]
                    
                    # if len(mtr_before) > 1:
                    #     logging.error(f"Multiple simple names same as the file name: {version['rel_from']}\n{mtr_before.to_string()}")
                    #     continue
                    logging.warning(f"Skip two classes in one file in {project_path.stem} : {version['rel_from']}\n{mtr_before.to_string()}")
                    continue

                if clazz in rename:
                    mtr_after = mtrs_aft[(mtrs_aft['file'].str.endswith(rename[clazz])) & (mtrs_aft['type'] == 'class')]
                else:
                    mtr_after = mtrs_aft[(mtrs_aft['file'].str.endswith(clazz)) & (mtrs_aft['type'] == 'class')]
                
                if len(mtr_after) == 0: # may be a left side file that has been removed in the next version
                    continue
                elif len(mtr_after) > 1:
                    logging.warning(f"Multiple metrics in {project_path.stem} for class {clazz} : {version['rel_to']}\n{mtr_after.to_string()}")
                    continue

                # compute the changes of metrics
                r1 = mtr_before.iloc[0]
                r2 = mtr_after.iloc[0]

                result_values = [ r2[col] - r1[col] for col in METRIC_COLUMNS ]
                # result_values = [ r2[col] /  r1[col] for col in METRIC_COLUMNS ]

                ref_mtr_dict[ref_type].append(result_values)
                df.loc[len(df.index)] = [ref_type, *result_values]

    return ref_mtr_dict, df
      

def gen_dataset():
    metrics = load_metrics()

    projects = path_input_refactorings.glob('*.json')
    for project in projects:
        project_metrics = metrics.get(project.stem, None)
        if project_metrics is None:
            logging.error(f"No metrics for project {project.stem}")

        ref_mtr, df = process_project(project, project_metrics)

        # filter out refactoring type which data number is less than 10
        
        substandard_data_count = {ref:len(data) for ref,data in ref_mtr.items() if len(data) < 10}
        if substandard_data_count:
            logging.info(f"Substandard data : {project.stem}\n{substandard_data_count}")
            for ref_type in substandard_data_count.keys():
                # del ref_mtr[ref_type]
                df = df[df['refactoring'] != ref_type]


        # write ref_mtr dict
        path_to_write = path_out / 'dataset'
        path_to_write.mkdir(parents=True, exist_ok=True)
        # with open(path_to_write / f'{project.stem}.json', 'w') as f:
        #     json.dump(ref_mtr, f, indent=4, cls=NumpyEncoder)
        df.to_csv(path_to_write / f'{project.stem}.csv', index=False)



if __name__ == '__main__':
    # # step 1
    # concat_metrics()

    # # step 2 
    # gen_dataset()

    # step 3
    normalize_dataset()
