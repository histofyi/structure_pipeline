from typing import Dict, List

from pipeline import get_current_time


from subprocess import run
import json

import datetime 



def parse_localpdb_output(raw_output:List) -> Dict:
    if 'localpdb' in raw_output[0] and 'is up to date' in raw_output[0]:
        updated = False
    else:
        updated = True

    plugins = []

    for line in raw_output:
        if line.split(' ')[0] == 'Plugin':
            plugins.append(line.split(' ')[1].strip().replace('\'','').lower())
    
    return {
        'updated': updated,
        'plugins': plugins
    }


def update_localpdb(**kwargs):
    """
    This function updates the localpdb instance and any installed plugins

    Args:
        config(Dict): the configuration information containing the path to the localpdb instance
        
    """

    config = kwargs['config']
    verbose = kwargs['verbose']

    update_command = f"localpdb_setup -db_path {config['PATHS']['LOCALPDB_PATH']} --update"

    result = run(update_command, capture_output=True, shell=True, text=True)

    if len(result.stderr) > 0:
        success = False
        errors = result.stderr
    else:
        success = True
        if verbose:
            print(result.stdout)
            
        raw_output = [line for line in result.stdout.splitlines() if len(line) > 0]


        parsed_output = parse_localpdb_output(raw_output)

    status_log_path = f"{config['PATHS']['LOCALPDB_PATH']}/data/status.log"
    with open(status_log_path, "r") as status_logfile:
        version_info = json.load(status_logfile)

    current_version = {}
    
    for version in version_info:
        if version_info[version][0] == 'OK':
            current_version = {
                'current_version':version,
                'updated_at':version_info[version][1],
                'checked_at':get_current_time()
            }
    action_log = {
        'version': current_version,
        'updated': parsed_output['updated'],
        'plugins': parsed_output['plugins']
    }

    return action_log


