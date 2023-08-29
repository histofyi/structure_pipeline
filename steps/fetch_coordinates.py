from typing import Dict, List, Tuple

from helpers.files import read_json, write_json

from pipeline_specific_helpers import do_work, get_facet_path

from providers import PDBeProvider, httpProvider

def download_cif_coordinates(pdb_code:str, assembly_id:int) -> str:
    """
    This function
    """
    pdbe_url = f'https://www.ebi.ac.uk/pdbe/model-server/v1/{pdb_code}/assembly?name={assembly_id}&model_nums=1&encoding=cif&copy_all_categories=false&download=false'
    coordinates = httpProvider().get(pdbe_url, format='txt')
    return coordinates


def fetch_coordinates_action(**action_args) -> Tuple[bool, Dict, List]:
    pdb_code = action_args['pdb_code']
    verbose = action_args['verbose']
    output_path = action_args['output_path']

    print (pdb_code)

    data, success, errors = PDBeProvider(pdb_code).fetch_assembly()

    if len(data) > 0:

        assembly_id = 0
        for assembly in data:
            print (assembly)
            assembly_id += 1
            
            coordinates = download_cif_coordinates(pdb_code, assembly_id)

            coordinates_filepath = f"{output_path}/coordinates/raw_assemblies/{pdb_code}_{assembly_id}.cif"


    print ('')


    success = False
    if success:
        return (True, {}, None)
    else:
        return (False, None, ['unable to do something'])



def fetch_coordinates(**kwargs):

    output_facet = 'coordinates'

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    new_work = new_work[:10]

    action_output = do_work(new_work, fetch_coordinates_action, output_facet, input_facet=None, kwargs=kwargs)

    return action_output