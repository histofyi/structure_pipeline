from typing import Dict, List, Tuple

from rich.progress import Progress

from pipeline import create_folder

from helpers.files import read_json, write_json, write_step_tmp_output
from helpers.dates import parse_pdbdate_to_isoformat

from pipeline_specific_helpers import get_facet_path, build_core_record, do_work

from providers import PDBeProvider

from datetime import datetime
import os

output_path = None
output_facet = 'chronology'

needs_updating = []


def fetch_chronology_data_action(**action_args) -> Tuple[bool, Dict, List]:
    # NOTE this function is different from any others which come after as we need to check if the underlying structure data has been updated since the last time we fetched any data
    pdb_code = action_args['pdb_code']

    facet_path = get_facet_path(output_path, 'structures', output_facet, pdb_code)
    

    data, success, errors = PDBeProvider(pdb_code).fetch_summary()

    if success:
        date_info = {}
        
        for date in ['deposition_date','release_date','revision_date']:
            date_info[date] = parse_pdbdate_to_isoformat(data[date])
            date_info['cached_date'] = datetime.now().date().isoformat()[0:10]

        if os.path.exists(facet_path):
            cached_data = read_json(facet_path)
        else:
            cached_data = None

        if cached_data:
            cached_date = datetime.fromisoformat(cached_data['cached_date'])
            revised_date = datetime.fromisoformat(date_info['revision_date'])

            if cached_date < revised_date:
                needs_updating.append(pdb_code)
        return (True, date_info, None)
    else:
        return (False, None, ['unable_to_fetch_chronology_data'])



def fetch_chronology_data(**kwargs):
    output_path = kwargs['output_path']

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    new_work = new_work[0:10]

    kwargs['force'] = True

    # TODO build the logic around adding structures that need updating to the new_work list
    print (needs_updating)

    action_output = do_work(new_work, fetch_chronology_data_action, output_facet, input_facet=None, kwargs=kwargs)