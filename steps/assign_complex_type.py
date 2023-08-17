from typing import Dict, List, Tuple

from helpers.files import read_json, write_json
from helpers.lists import hash_dict

from pipeline_specific_helpers import do_work, get_facet_path



def assign_complex_type_action(**action_args) -> Tuple[bool, Dict, List]:
    pdb_code = action_args['pdb_code']
    output_path = action_args['output_path']
    complex_type_tests = action_args['complex_type_tests']

    chain_types = read_json(get_facet_path(output_path, 'structures', 'chain_types', pdb_code))
    alike_chains = read_json(get_facet_path(output_path, 'structures', 'alike_chains', pdb_code))

    complex_composition = {}

    for chain in chain_types.keys():
        complex_composition[chain_types[chain]['chain_type']] = int(len(alike_chains['chains'][chain])/alike_chains['assembly_count'])

    complex_composition = dict(sorted(complex_composition.items()))
    hashed_complex_composition = hash_dict(complex_composition)

    complex_type = None

    
    if hashed_complex_composition not in complex_type_tests:
        success = False
        errors = ['unknown_complex_composition', complex_composition]
        print (pdb_code)
        print ('ERROR! Unknown complex composition!')
        print (complex_composition)
        print ('Hashed complex composition:')
        print (hashed_complex_composition)
        print ('Chain types:')
        print (chain_types)
        print ('')
    else:
        complex_type = complex_type_tests[hashed_complex_composition]
        if 'check_assignment' in complex_type:
            print (pdb_code)
            errors = ['check_assignment', hashed_complex_composition]
            print ('Hashed complex composition:')
            print (hashed_complex_composition)
            print ('Complex type:')
            print (complex_type)
            print ('Chain types:')
            print (chain_types)
            print ('')
            success = False
        else:
            success = True

    if success:
        return (True, complex_type, None)
    else:
        return (False, None, ['unable to do something'])


def assign_complex_type(**kwargs):

    output_facet = 'complex_type'

    complex_type_tests = read_json(f"assets/constants/complex_types.json")

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    #new_work = new_work[:1000]

    kwargs['complex_type_tests'] = complex_type_tests

    action_output = do_work(new_work, assign_complex_type_action, output_facet, input_facet=None, kwargs=kwargs)

    return action_output