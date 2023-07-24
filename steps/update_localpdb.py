from typing import Dict

from pipeline import get_current_time

import os
import json

import datetime 


def update_localpdb(**kwargs):
    """
    This function updates the localpdb instance and any installed plugins

    Args:
        config(Dict): the configuration information containing the path to the localpdb instance
        
    """

    config = kwargs['config']

    update_command = f"localpdb_setup -db_path {config['PATHS']['LOCALPDB_PATH']} --update"

    os.system(update_command)

    status_log_path = f"{config['PATHS']['LOCALPDB_PATH']}/data/status.log"
    with open(status_log_path, "r") as status_logfile:
        version_info = json.load(status_logfile)
        print (version_info)

    current_version = {}
    
    for version in version_info:
        if version_info[version][0] == 'OK':
            current_version = {
                'version':version,
                'last_updated':version_info[version][1],
                'last_checked':get_current_time()
            }
    action_log = {}
    return action_log


