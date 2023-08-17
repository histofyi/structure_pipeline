from typing import Dict, List, Tuple, Union
import os

from fuzzywuzzy import fuzz

from helpers.files import read_json, write_json

from pipeline_specific_helpers import do_work, get_facet_path

from helpers.text import slugify


def get_tcr_info(output_path:str, pdb_code:str) -> Union[Dict, None]:
    tcr_file_path = f"{output_path}/tcr_details/{pdb_code}.json"
    if os.path.exists(tcr_file_path):
        return read_json(tcr_file_path)
    else:
        return None


def get_ab_info(output_path:str, pdb_code:str) -> Union[Dict, None]:
    ab_file_path = f"{output_path}/ab_details/{pdb_code}.json"
    if os.path.exists(ab_file_path):
        return read_json(ab_file_path)
    else:
        return None


def assign_receptor_chains(receptor_info, receptor_type, chains):
    chain_types = {
        'tcr': ['alpha','beta','gamma','delta'],
        'ab': ['light','heavy']
    }
    keys = {'tcr':'subgroup','ab':'sabdab'}
    match_types = {'tcr':'stcrdab','ab':'sabdab'}
    receptor_chain_types = chain_types[receptor_type]
    assigned_chains = {}
    for receptor_chain_type in receptor_chain_types:
        if receptor_chain_type in receptor_info:
            test_chain_label = receptor_info[receptor_chain_type]['chains'][0]
            for chain in chains:
                if test_chain_label in chains[chain]:
                    assigned_chains[chain] = {
                        'chains':chains[chain],
                        'chain_type': f"{receptor_type}_{receptor_chain_type}",
                        'subgroup':receptor_info[receptor_chain_type][keys[receptor_type]],
                        'matchtype': f'{match_types[receptor_type]}'
                    }
                    break
    for chain in chains:
        if not chain in assigned_chains:
            assigned_chains[chain] = None
    return assigned_chains


def assign_unmatched_chains(sequence, chain_type_tests):
    assignment = {}
    if len(sequence) <= 20:
        return {'chain_type':'peptide', 'matchtype':'peptide_length'}
    else:
        for test in chain_type_tests:
            
            best_score = 0
            best_match = None
            for test_sequence in chain_type_tests[test]['sequences']:
                if sequence == test_sequence or sequence in test_sequence or test_sequence in sequence:
                    assignment['chain_type'] = test
                    assignment['matchtype'] = 'exact'
                    return assignment
                else:
                    ratio = fuzz.ratio(test_sequence, sequence) / 100
                    if ratio > best_score:
                        best_score = ratio
                        best_match = test
                    if best_score > 0.75:
                        assignment['chain_type'] = best_match
                        assignment['matchtype'] = 'fuzzy'
                        assignment['ratio'] = best_score
                        return assignment
                    
    return None


def list_unassigned_chains(alike_chains, assigned_chains):
    unassigned_chains = [chain for chain in assigned_chains if assigned_chains[chain] == None]
    return unassigned_chains



def assign_chain_types_action(**action_args) -> Tuple[bool, Dict, List]:
    pdb_code = action_args['pdb_code']
    output_path = action_args['output_path']
    chain_type_tests = action_args['chain_type_tests']


    alike_chains = read_json(get_facet_path(output_path, 'structures', 'alike_chains', pdb_code))

    receptor_type = None
    receptor_info = None

    tcr_info = get_tcr_info(output_path, pdb_code)
    if tcr_info:
        receptor_type = 'tcr'
        receptor_info = tcr_info
    else:
        ab_info = get_ab_info(output_path, pdb_code)
        if ab_info:
            receptor_type = 'ab'
            receptor_info = ab_info
    
    if receptor_info:
        assigned_chains = assign_receptor_chains(receptor_info, receptor_type, alike_chains['chains'])
    else:
        assigned_chains = {k:None for k in alike_chains['chains']}    

    unassigned_chains = list_unassigned_chains(alike_chains, assigned_chains)

    for chain in unassigned_chains:
        chains = alike_chains['chains'][chain]
        chain_sequence = alike_chains['chain_sequences'][chain]
        assignment = assign_unmatched_chains(chain_sequence, chain_type_tests)
        if assignment:
            assigned_chains[chain] = assignment

    override = f"assets/overrides/assign_chain_types/{pdb_code}.json"
    if os.path.exists(override):
        override_info = read_json(override)
        for chain in override_info:
            assigned_chains[chain] = override_info[chain]

    unassigned_chains = list_unassigned_chains(alike_chains, assigned_chains)

    if len(unassigned_chains) > 0:
        print (pdb_code)
        print (action_args['matched_to'])
        print (unassigned_chains)
  
        errors = []
        for chain in unassigned_chains:
            errors.append(f"unassigned_chain_{chain}")
        success = False
        print (errors)
        print ('')
    else:
        success = True


    if success:
        return (True, assigned_chains, None)
    else:
        return (False, None, errors)



def assign_chain_types(**kwargs):

    output_facet = 'chain_types'

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    chain_type_tests = read_json(f"assets/sequences/chain_type_tests.json")

    kwargs['chain_type_tests'] = chain_type_tests

    action_output = do_work(new_work, assign_chain_types_action, output_facet, input_facet=None, kwargs=kwargs)

    return action_output