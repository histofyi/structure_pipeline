from typing import Dict, List, Tuple

from helpers.files import read_json, write_json

from pipeline_specific_helpers import do_work


def do_something(pdb_code:str) -> Tuple[Dict, bool, List]:
    return None, None, None


def stub_method_action(**action_args) -> Tuple[bool, Dict, List]:
    pdb_code = action_args['pdb_code']

    data, success, errors = do_something(pdb_code)

    if success:
        # do something here

        return (True, {}, None)
    else:
        return (False, None, ['unable to do something'])



def stub_method(**kwargs):

    output_facet = ''

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    new_work = new_work[:25]

    action_output = do_work(new_work, stub_method_action, output_facet, input_facet=None, kwargs=kwargs)

    return action_output