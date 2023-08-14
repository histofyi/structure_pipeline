from typing import Dict, List, Tuple

from helpers.files import read_json, write_json, write_step_tmp_output

from pipeline_specific_helpers import get_facet_path, build_core_record, do_work

from providers import PDBeProvider


def fetch_title_data_action(**action_args) -> Tuple[bool, Dict, List]:
    pdb_code = action_args['pdb_code']

    data, success, errors = PDBeProvider(pdb_code).fetch_summary()

    if success:
        title_info = {}
        title_info['pdb_title_original'] = data['title']
        title_info['pdb_title_capitalized'] = data['title'].capitalize()

        return (True, title_info, None)
    else:
        return (False, None, ['unable_to_fetch_title_data'])



def fetch_title_data(**kwargs):

    output_facet = 'title'

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    action_output = do_work(new_work, fetch_title_data_action, output_facet, input_facet=None, kwargs=kwargs)

    return action_output