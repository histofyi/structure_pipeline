from typing import Dict, List, Tuple

from rich.progress import Progress

from pipeline import create_folder

from helpers.files import read_json, write_json, write_step_tmp_output

from pipeline_specific_helpers import get_facet_path, build_core_record, do_work


def create_core_record_action(**action_args) -> bool:
    pdb_code = action_args['pdb_code']

    data = build_core_record(pdb_code)
    if data:
        return True, data, None
    else:
        return False, None, ['unable_to_generate_core_record']
    


def create_core_records(**kwargs):
    verbose = kwargs['verbose']
    config = kwargs['config']
    console = kwargs['console']
    datehash = kwargs['datehash']
    function_name = kwargs['function_name']
    output_path = kwargs['output_path']
    force = kwargs['force']

    facet = 'core'

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    create_folder(f"{output_path}/structures/{facet}", verbose)

    action_output = do_work(new_work, create_core_record_action, facet, kwargs)

    return action_output