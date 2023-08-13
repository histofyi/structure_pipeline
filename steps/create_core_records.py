from typing import Dict, List, Tuple

from rich.progress import Progress

from pipeline import create_folder

from helpers.files import read_json, write_json, write_step_tmp_output

from pipeline_specific_helpers import get_facet_path, build_core_record

def create_core_records(**kwargs):
    verbose = kwargs['verbose']
    config = kwargs['config']
    console = kwargs['console']
    datehash = kwargs['datehash']
    function_name = kwargs['function_name']
    output_path = kwargs['output_path']

    facet = 'core'

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    create_folder(f"{output_path}/structures/{facet}", verbose)

    successful = []
    errors = []

    for structure in new_work:
        pdb_code = structure['pdb_code']
        success = write_json(get_facet_path(output_path, 'structures', facet, pdb_code), build_core_record(pdb_code), verbose)
        if success:
            successful.append(pdb_code)
        else:
            errors.append({'pdb_code':pdb_code, 'error':'unable_to_create_core_record'})

    raw_output = {
        'successful':successful,
        'errors':errors
    }

    action_output = {
        'successful':len(successful),
        'errors':len(errors)
    }

    # then we write the raw output to a JSON file which we can interrogate later, the datehash matches the pipeline output datehash
    write_step_tmp_output(config['PATHS']['TMP_PATH'], function_name, raw_output, datehash, verbose=verbose)

    return action_output