from typing import Dict, List

from pipeline import get_current_time

from helpers.files import write_json, write_step_tmp_output

import subprocess
import shlex

from time import sleep

import json

import datetime 



def parse_localpdb_output(raw_output:List) -> Dict:
    if 'localpdb' in raw_output[0] and 'is up to date' in raw_output[0]:
        updated = False
    else:
        updated = True

    plugins = {}

    for line in raw_output:
        plugin = None
        if line != '\n':
            if line.split(' ')[0] == 'Plugin' and 'is set up for' in line:
                plugin = line.split(' ')[1].strip().replace('\'','').lower()
                updated = False
            elif line.split(' ')[0] == 'Updating' and line.split(' ')[1] == 'plugin:':
                plugin = line.split(' ')[2].strip().replace('\'','').replace('.','').lower()
                updated = True
            if plugin:
                plugins[plugin] = updated
    
    return {
        'updated': updated,
        'plugin_updated': plugins
    }


def run_command(command:str):
    output_log = []
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline().decode()
        if output == '' and process.poll() is not None:
            break
        if output:
            if len(output) > 0:
                output_log.append(output.strip())
                print (output.strip())
    return output_log


def update_localpdb(**kwargs):
    """
    This function updates the localpdb instance and any installed plugins

    Args:
        config(Dict): the configuration information containing the path to the localpdb instance
        
    """

    config = kwargs['config']
    verbose = kwargs['verbose']
    datehash = kwargs['datehash']
    function_name = kwargs['function_name']

    update_command = f"localpdb_setup -db_path {config['PATHS']['LOCALPDB_PATH']} --update"

    raw_output = run_command(update_command)

    write_step_tmp_output(config['PATHS']['TMP_PATH'], function_name, raw_output, datehash, verbose=verbose)

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
        'plugin_updated': parsed_output['plugin_updated']
    }

    return action_log


