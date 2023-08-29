from typing import Dict, List, Tuple
import os

from rich.progress import Progress

from pipeline import create_folder

from helpers.files import read_json, write_json, write_step_tmp_output




def process_localpdb_query_matches(**kwargs):
    verbose = kwargs['verbose']
    config = kwargs['config']
    console = kwargs['console']
    datehash = kwargs['datehash']
    function_name = kwargs['function_name']
    output_path = kwargs['output_path']

    
    datehash = '20230812133017'
    previous_step = 'query_localpdb'

    # Read the output of the previous step

    previous_step_output = read_json(f"{config['PATHS']['TMP_PATH']}/steps/{previous_step}/output-{datehash}.json")

    ignore_structures = read_json(f"assets/overrides/{previous_step}/ignore_structures.json")

    known_matches_filename = f"assets/overrides/{previous_step}/known_matches.json"
    if os.path.exists(known_matches_filename):
        known_matches = read_json(known_matches_filename)
    else:
        known_matches = []

    ignore_matches_filename = f"assets/overrides/{previous_step}/ignore_matches.json"
    if os.path.exists(ignore_matches_filename):
        ignore_matches = read_json(ignore_matches_filename)
    else:
        ignore_matches = []
    
    new_work = []

    for collection in ['exact_matches', 'excellent_matches', 'good_matches']:
        for match in previous_step_output['collections'][collection]:
            if not match in known_matches:
                new_work.append(match)
            known_matches.append(match)


    for collection in ['no_matches', 'poor_matches']:
        for match in previous_step_output['collections'][collection]:
            ignore_matches.append(match)

    groupings = {}

    for grouping in ['known_matches', 'ignore_matches', 'new_work']:
        write_json(f"assets/overrides/{previous_step}/{grouping}.json", eval(grouping))
        groupings[grouping] = eval(grouping)

    action_output = {
        'known_matches': len(known_matches),
        'ignore_matches': len(ignore_matches),
        'new_work': len(new_work)
    }


    create_folder(f"{config['PATHS']['TMP_PATH']}/steps/{function_name}", verbose)    
    raw_output = {
        'groupings': groupings,
    }

    # then we write the raw output to a JSON file which we can interrogate later, the datehash matches the pipeline output datehash
    write_step_tmp_output(config['PATHS']['TMP_PATH'], function_name, raw_output, datehash, verbose=verbose)

    return action_output