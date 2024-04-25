
#%%
from util import *

import json
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns


path_dataset = PATH_SCRIPT / 'out' / 'metrics' / 'dataset'
path_models = PATH_SCRIPT / 'out' / 'models'
path_metrics = PATH_SCRIPT / 'out' / 'metrics' / 'concat'

path_out = PATH_SCRIPT / 'out' / 'count'
path_out.mkdir(parents=True, exist_ok=True)

#%%
def _compute_overlap(kafka_refs:list, gson_refs:list, spring_security_refs:list):
    k, edit, chart = set(kafka_refs), set(gson_refs), set(spring_security_refs)
    intersec_all = k.intersection(edit, chart)
    union_spring_gson = edit.union(chart)

    return {
        'overlap': list(intersec_all),
        'overlap_len': len(intersec_all),
        'union_spring_gson': list(union_spring_gson),
        'union_spring_gson_len': len(union_spring_gson)
    }


def count_dataset():    
    projects = path_dataset.glob('*.csv')

    stat = dict()
    for pro in projects:

        df = pd.read_csv(pro)
        refactorings = df['refactoring'].unique()

        data_count = {ref:len(df[df['refactoring'] == ref]) for ref in refactorings}

        stat[pro.stem] = {
            'ref_type_count': len(refactorings),
            'ref_types': list(refactorings),
            'data_count': data_count,
        }

    overlap = _compute_overlap(stat['kafka']['ref_types'], stat['gson']['ref_types'], stat['spring-security']['ref_types'])

    with open(path_out / 'dataset.json', 'w') as f:
        json.dump({'stat': stat, 'overlap': overlap}, f, indent=4)



def count_models():
    projects = path_models.glob('*.json')

    proj_dic = dict()
    for pro in projects:
        with open(pro, 'r') as f:
            models = json.load(f)

        models = models["refactoring models"].keys()
        proj_dic[pro.stem] = {"count": len(models), "refactorings": list(models)}

    overlap = _compute_overlap(proj_dic['kafka']['refactorings'], proj_dic['gson']['refactorings'], proj_dic['spring-security']['refactorings'])

    with open(path_out / 'models.json', 'w') as f:
        json.dump({'stat': proj_dic, 'overlap': overlap}, f, indent=4)


def count_refactorings():
    counter = dict()
    main_test_mappings = dict()
    version_counter = dict()  # most popular refactorings in each version
    projects = [item for item in PATH_REFACTORINGS.iterdir() if item.is_dir()]
    for project in projects:
        counter[project.stem] = defaultdict(int)
        main_test_mappings[project.stem] = defaultdict(int)
        version_counter[project.stem] = dict()

        for version in project.glob('*.json'):
            with open(version, 'r') as f:
                json_dic = json.load(f)

            version_counter[project.stem][version.stem] = defaultdict(int)

            for refactorings in json_dic.values():
                for ref_str in refactorings:
                    ref = json.loads(ref_str)

                    counter[project.stem][ref['type']] += 1
                    version_counter[project.stem][version.stem][ref['type']] += 1

                    left_side_files = set(location['filePath'] for location in ref['leftSideLocations'])
                    right_side_files = set(location['filePath'] for location in ref['rightSideLocations'])
                    if is_mapping_main_test(left_side_files, right_side_files):
                        main_test_mappings[project.stem][ref['type']] += 1


    sort_dict = lambda d: dict(sorted(d.items(), key=lambda x: x[1], reverse=True))

    # project counter
    overall = dict()
    for proj in counter.keys():
        counter[proj] = sort_dict(counter[proj])
        overall[proj] = {'types': len(counter[proj]) , 'refactoring': sum(counter[proj].values())}

    for proj in main_test_mappings:
        main_test_mappings[proj] = sort_dict(main_test_mappings[proj])
        overall[proj]['mismatch'] = sum(main_test_mappings[proj].values())


    for proj in version_counter.keys():
        version_counter[proj] = dict(sorted(version_counter[proj].items()))

        versions = version_counter[proj]
        v_dict = dict()
        
        for version in versions.keys():
            version_counter[proj][version] = sort_dict(version_counter[proj][version])
            v_dict[version] = {'types': len(version_counter[proj][version]), 'refactoring': sum(version_counter[proj][version].values())}
        overall[proj]['versions'] = v_dict

    overlap = _compute_overlap(counter['kafka'].keys(), counter['gson'].keys(), counter['spring-security'].keys())

    with open(path_out / 'refactorings.json', 'w') as f:
        json.dump({'overall': overall, 'counter': counter, 'main_test_mapping': main_test_mappings, 
                   'version_counter': version_counter, 'overlap': overlap}, f, indent=4)



def count_metrics():
    projects = path_metrics.glob('*.csv')

    class_counter = dict()
    for proj in projects:
        df = pd.read_csv(proj)
        versions = df['version'].unique()

        class_counter[proj.stem] = {v:len(df[df['version'] == v]) for v in versions}
        class_counter[proj.stem] = dict(sorted(class_counter[proj.stem].items()))

    path_metrics_out = path_out / 'metrics'
    path_metrics_out.mkdir(parents=True, exist_ok=True)
    with open(path_metrics_out / 'metrics.json', 'w') as f:
        json.dump(class_counter, f, indent=4)


    # Plotting the figure
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))

    mk_itr = iter(['o', 's', '^'])

    for proj, data in class_counter.items():

        sns.lineplot(x=range(len(data)), y=data.values(), marker=next(mk_itr), label=proj)
        # sns.lineplot(x=list(data.keys()), y=list(data.values()), marker='o', color='b')

    plt.xlabel('Version')
    plt.ylabel('Number of Classes')
    plt.tight_layout()
    plt.xticks([])
    # plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    
    plt.savefig(path_metrics_out / 'metrics.png', dpi=300)
        
    

count_dataset()
count_metrics()
count_refactorings()


count_models()