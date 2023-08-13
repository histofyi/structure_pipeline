from typing import Dict, List, Tuple

from rich.progress import Progress

from pipeline import create_folder

from helpers.files import read_json, write_json, write_step_tmp_output

from pipeline_specific_helpers import get_facet_path, build_core_record, do_work


def create_core_record_action(input_facet=None, **action_args) -> bool:
    pdb_code = action_args['pdb_code']

    data = build_core_record(pdb_code)
    if data:
        return True, data, None
    else:
        return False, None, ['unable_to_generate_core_record']
    


def create_core_records(**kwargs):
    output_facet = 'core'

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    action_output = do_work(new_work, create_core_record_action, output_facet, input_facet=None, kwargs=kwargs)

    return action_output