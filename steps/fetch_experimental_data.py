from typing import Dict, List, Tuple

from helpers.files import read_json, write_json, write_step_tmp_output
from helpers.text import slugify

from pipeline_specific_helpers import get_facet_path, build_core_record, do_work

from providers import PDBeProvider


def fetch_experimental_data_action(**action_args) -> Tuple[bool, Dict, List]:
    pdb_code = action_args['pdb_code']

    data, success, errors = PDBeProvider(pdb_code).fetch_experiment()

    if success:
        experimental_info = {}
        method_slug = slugify(data['experimental_method'])
        if method_slug == 'x_ray_diffraction':
            experimental_info['experimental_method'] = 'x_ray_diffraction'
            experimental_info['resolution'] = data['resolution_high']
            experimental_info['spacegroup'] = data['spacegroup']
            experimental_info['cell'] = data['cell']
        elif method_slug == 'electron_microscopy':
            experimental_info['experimental_method'] = 'electron_microscopy'
            experimental_info['resolution'] = data['resolution']
        else:
            experimental_info['resolution'] = None
            experimental_info['experimental_method'] = 'nmr'

        return (True, experimental_info, None)
    else:
        return (False, None, ['unable_to_fetch_title_data'])



def fetch_experimental_data(**kwargs):

    output_facet = 'experimental'

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    action_output = do_work(new_work, fetch_experimental_data_action, output_facet, input_facet=None, kwargs=kwargs)

    return action_output