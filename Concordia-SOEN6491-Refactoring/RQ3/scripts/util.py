'''
common var and functions
'''

from pathlib import Path
import re

_path_util = Path(__file__).resolve()
PATH_SCRIPT = _path_util.parent
PATH_RQ3 = PATH_SCRIPT.parent
PATH_METRICS = PATH_RQ3 / "metrics"
PATH_REFACTORINGS = PATH_RQ3 / "refactorings"

METRIC_COLUMNS = ['loc', 'wmc', 'dit', 'noc', 'rfc', 'cbo', 'lcom']

def parse_versions(name:str):
    if name.startswith('gson'):
        # Find the index of the second occurrence of "jedit"
        second_jedit_index = name.find("gson", name.find("gson") + 1)
        # Split the string into two parts
        return name[:second_jedit_index - 1], name[second_jedit_index:]
    else:
        return name.split('-', 1)   # split at the first '-'



re_test = re.compile(r'\btests?/')

def is_mapping_main_test(left_side_files:set, right_side_files:set):
    """
    Determine whether a refactoring is a match between the main file and the test file
    """
    test1 = any(re_test.search(f) is None for f in left_side_files)
    test2 = any(re_test.search(f) is None for f in right_side_files)

    if test1 != test2:
        return True
    
    return False
