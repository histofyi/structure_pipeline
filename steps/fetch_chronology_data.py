from typing import Dict, List, Tuple



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

    known_matches = read_json(f"assets/overrides/query_localpdb/known_matches.json")

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    complete_work = known_matches.copy()

    for structure in new_work:
        if structure not in complete_work:
            complete_work.append(structure)

    kwargs['force'] = True

    action_output = do_work(complete_work, fetch_chronology_data_action, output_facet, input_facet=None, kwargs=kwargs)

    # TODO build the logic around adding structures that need updating to the new_work list
    print (f"There are {len(needs_updating)} structures that need to be updated due to revisions on the PBD.")

    if len(needs_updating) > 0:
        known_matches = read_json(f"assets/overrides/query_localpdb/known_matches.json")
        structures_to_update = {structure['pdb_code']:structure for structure in known_matches if structure['pdb_code'] in needs_updating}
        for pdb_code in needs_updating:
            new_work.append(structures_to_update[pdb_code])

    action_output['needs_updating'] = needs_updating

    return action_output