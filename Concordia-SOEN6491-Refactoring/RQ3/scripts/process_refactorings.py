
'''
Process the refactorings extracted by RefactoringMiner.
Output: a list of json objects representing a refactoring (relj, refk, C)
'''
#%%
#%%
from util import *

import json
import logging
from collections import defaultdict
import traceback


path_out = PATH_SCRIPT / 'out' / 'refactorings'
path_out.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(filename=path_out / 'process_refactorings.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def process_refactoring_json(json_file:Path):
    """
    Parse a refactoring file (e.g., 0.8.0-1.0.0.json) in a Json

    Returns:
        {
            "rel_from": str,
            "rel_to": str,
            "ref_dict": dict<str, list<str>>    # refactroing type : classes involved    
            "rename": dict<str, str>
            "counter": dict<str, int>           # the number of occurrences of each refactoring type
        }
    """

    rel_from, rel_to = parse_versions(json_file.stem)

    with open(json_file, 'r') as f:
        json_dic = json.load(f)

    if len(json_dic) > 1:
        logging.warning(f'len(json_dic) > 1 : {json_file.name}')

    rename = defaultdict(set)
    ref_dict = defaultdict(set)
    counter = defaultdict(int)
    for refactorings in json_dic.values():
        for ref_str in refactorings:
            try:
                refactoring = json.loads(ref_str)

                left_side_files = set(location['filePath'] for location in refactoring['leftSideLocations'])
                right_side_files = set(location['filePath'] for location in refactoring['rightSideLocations'])

                if is_mapping_main_test(left_side_files, right_side_files):
                    logging.warning(f"Skip suspicious refactoring mapping between main and test : {json_file.name} : {refactoring['type']}\n{refactoring}")
                    continue

                ref_type = refactoring['type']

                lower_ref_type = ref_type.lower()
                if any(x in lower_ref_type for x in ['rename class', 'rename package']):
                    # renaming class/package
                    if len(refactoring['leftSideLocations']) != len(refactoring['rightSideLocations']):
                        logging.error(f'Suspicious renaming\n{refactoring}')
                        continue
                    
                    for left_loc, right_loc in zip(refactoring['leftSideLocations'], refactoring['rightSideLocations']):
                        # check inner class
                        old_path = left_loc['filePath']
                        base_name = old_path.split('/')[-1].split('.')[0]
                        simple_name = left_loc['codeElement'].split('.')[-1]
                        if base_name != simple_name:
                            logging.warning(f"Skip inner class {left_loc['codeElement']} in {old_path}")
                            continue

                        new_path = right_loc['filePath']
                        ref_dict[ref_type].add(old_path)
                        rename[old_path].add(new_path)
                        counter[ref_type] += 1
                else:
                    # other refactoring types
                    ref_dict[ref_type].update(left_side_files)
                    counter[ref_type] += 1
               
            except Exception as e:
                logging.error(f'Fail to parse ref_str: {json_file.name}\n{traceback.format_exc()}\n{ref_str}')

    # Post-process renames and ref_dict, remove classes involving multiple renames, they may be false positive
    one_one_rename = dict()
    for old_name, new_names in rename.items():
        if len(new_names) == 1:
            one_one_rename[old_name] = new_names.pop()
        else:
            logging.warning(f"Skip classes involving multiple renames : {json_file.name}\n{old_name} : {new_names}")
            for _, classes in ref_dict.items():
                classes.discard(old_name)
                classes.difference_update(new_names)

    # cast the value of ref_dict into list
    ref_list_dict = dict()
    for ref_type, classes in ref_dict.items():
        if classes:
            ref_list_dict[ref_type] = list(classes)
        else:
            counter[ref_type] = 0

    return {'rel_from': rel_from, 'rel_to': rel_to, 'ref_dict': ref_list_dict, 'rename': one_one_rename, 'counter': counter}
    

def process_project(project:Path):
    """
    Parse the refactoring files for a project, return a list of Json
    """
    json_files = project.glob('*.json')

    refs_project = list()
    for json_file in json_files:
        refs_for_version = process_refactoring_json(json_file)
        refs_project.append(refs_for_version)

    return refs_project

def main():
    projects = [item for item in PATH_REFACTORINGS.iterdir() if item.is_dir()]

    for project in projects:
        refactorings = process_project(project)
        with open(path_out / f'{project.name}.json', 'w') as f:
            json.dump(refactorings, f, indent=4)

if __name__ == '__main__':
    main()
#%%