#%%
# A General Tag Format:
#       major version . minor version . patch version - ALPHA/BETA/RC.N
#  e.g., 3.7.0-rc0, where `-rc` stands for `release candidate`

from pathlib import Path
import re
from datetime import datetime
import json


cur_dir = Path(__file__).resolve().parent
input_dir = cur_dir / 'input'
path_out = cur_dir / 'out'

def _extract_tags(path_file: Path):
    tags = list()
    
    with open(path_file, 'r') as f:
        for line in f:
            tag = line.split(maxsplit=1)[0]
            tag = tag[len('refs/tags/'):]
            tags.append(tag)
            
    return tags


def _convert_time_string(input_time):
    # Parse the input string
    parsed_time = datetime.strptime(input_time, '%a %b %d %H:%M:%S %Y %z')
    
    # Format the parsed time as per desired output format
    formatted_time = parsed_time.strftime('%Y-%m-%d')
    
    return formatted_time


#%%
def process(path_file:Path):
    # tag examples of spring security:
    #       1.0.0
    #       2.0.0.M1            `M`: milestone, belonging to pre-release versions
    #       2.0.0.RC1           `RC`: release candidates, belonging to pre-release versions
    #       3.0.3.RELEASE       stable release of version
    
    pat = re.compile(r'(\d+(?:\.\d+)+)(?:\.RELEASE)?$')  # to find tag names with a suffix like 1.2

    tags = _extract_tags(path_file)
    
    ans = list()
    for tag in tags:
        m = pat.search(tag)
        if m:
            number_part = m.group(1) # e.g., 0.8.1.1
            
            # discard patch versions and  pre-release versions
            parts = number_part.split('.')
            
            if len(parts) < 3 or all(int(elem) == 0 for elem in parts[2:]):
                ans.append(tag)
        
    path_out.mkdir(parents=True, exist_ok=True)        
    with open(path_out / f'{path_file.stem}.txt', 'w') as f:
        f.write('\n'.join(ans))


def gen_release_date_table():
    
    # parse dates for all tags
    data = dict()
    for proj in input_dir.glob('*.txt'):
        proj_data = dict()
        
        with open(proj, 'r') as f:
            for line in f:
                parts = line.strip().split(' ', 1)
                tag = parts[0][len('refs/tags/'):]
                proj_data[tag] = _convert_time_string(parts[1])
                
        data[proj.stem] = proj_data
    
    # read all selected tags
    selected_tags = dict()
    for proj in path_out.glob('*.txt'): 
        with open(proj, 'r') as f:
            selected_tags[proj.stem] = [line.strip() for line in f]
            
    # filter dates for selected tags
    ans = dict()
    for proj, tags in selected_tags.items():
        ans[proj] = [f'{tag} & {data[proj][tag]}' for tag in tags]
    
    with open(cur_dir / 'release_dates.json', 'w') as f:
        json.dump(ans, f, indent=4)
        

# %%
# process(input_dir / 'kafka.txt')
# process(input_dir / 'gson.txt')
# process(input_dir / 'ms-spring-security.txt')
# process(input_dir / 'spring-security.txt')

gen_release_date_table()