from typing import Dict, List, Tuple

import os

from localpdb import PDB
from fuzzywuzzy import fuzz

from rich.progress import Progress

from pipeline import create_folder

from helpers.files import read_json, write_json, write_step_tmp_output
from helpers.text import slugify

from pymol import cmd


def parse_search_sequences(filename, mhc_class):
    raw_search_sequences = read_json(filename)[mhc_class]
    parsed_search_sequences = {mhc_class:{'labels':[],'sequences':[]}}
    parsed_search_sequences[mhc_class]['labels'] = [k for k,v in raw_search_sequences.items()]
    parsed_search_sequences[mhc_class]['sequences'] = [v for k,v in raw_search_sequences.items()]
    return parsed_search_sequences


def structure_match(pdb_code:str, mhc_class:str):
    cmd.fetch(pdb_code, quiet=1)
    cmd.load('assets/structures/class_i_1hhk.pdb')
    align = cmd.cealign('class_i_1hhk',pdb_code)
    cmd.delete('all')
    match_likelihood = align['alignment_length'] / 180
    fetched_file = f"{pdb_code}.cif"
    if os.path.exists(fetched_file):
        os.remove(fetched_file)
    return match_likelihood


def remove_leader_sequence(test_sequence:str, pdb_code:str):
    split_sequence = None
    remainder = None
    for class_i_start in class_i_starts:
        if class_i_start in test_sequence:
            remainder = test_sequence.split(class_i_start)[1]
            break
        elif class_i_start[1:] in test_sequence:
            remainder = test_sequence.split(class_i_start[1:])[1]
            break
        if remainder:
            split_sequence = f"{class_i_start}{remainder}"
        else:
            unable_to_split[pdb_code] = test_sequence
    if split_sequence:
       return split_sequence
    else:
        return None
 

def match_sequences(test_sequence:str, sequences:List, pdb_code:str, mhc_class:str='class_i'):
    i = 0
    best_score = 0
    best_match = None
    for sequence in sequences:
        ratio = fuzz.ratio(test_sequence, sequence) / 100
        if ratio > best_score:
            best_score = ratio
            best_match = search_sequences[mhc_class]['labels'][i]
        i += 1
    return best_match, best_score, test_sequence


def match_class_i_sequences(test_sequence:str, pdb_code:str):
    test_sequence = test_sequence.replace('HHHHHH','')
    if len(test_sequence) < 200:
        match_type = 'truncated'
        best_match, best_score, altered_sequence = match_truncated_class_i_sequences(test_sequence, pdb_code)
    elif len(test_sequence) > 370:
        match_type = 'single_chain_construct'
        best_match, best_score, altered_sequence = match_single_chain_construct_class_i_sequences(test_sequence, pdb_code)
    else:
        match_type = 'cytoplasmic'
        best_match, best_score, altered_sequence = match_cytoplasmic_class_i_sequences(test_sequence, pdb_code)
    return best_match, best_score, match_type, altered_sequence


def match_cytoplasmic_class_i_sequences(test_sequence:str, pdb_code:str):
    if len(test_sequence) > 280:
        split_sequence = remove_leader_sequence(test_sequence, pdb_code)
        if split_sequence:
            if len(split_sequence) > 275:
                test_sequence = split_sequence[0:275]
            else:
                test_sequence = split_sequence
    sequences = search_sequences['class_i']['sequences']
    best_match, best_score, altered_sequence = match_sequences(test_sequence, sequences, pdb_code)
    return best_match, best_score, altered_sequence


def match_truncated_class_i_sequences(test_sequence:str, pdb_code:str):
    sequences = [sequence[0:180] for sequence in search_sequences['class_i']['sequences']]
    best_match, best_score, altered_sequence = match_sequences(test_sequence, sequences, pdb_code)
    return best_match, best_score, altered_sequence


def match_single_chain_construct_class_i_sequences(test_sequence:str, pdb_code:str):
    sequences = search_sequences['class_i']['sequences']
    split_sequence = remove_leader_sequence(test_sequence, pdb_code)
    if split_sequence:
        best_match, best_score, altered_sequence = match_sequences(split_sequence, sequences, pdb_code)
    else:
        best_match, best_score, altered_sequence = match_sequences(test_sequence, sequences, pdb_code)
    return best_match, best_score, altered_sequence


def match_class_i_start(test_sequence:str):
    match = False
    for class_i_start in class_i_starts:
        if class_i_start in test_sequence:
            match = class_i_start
            break
        if class_i_start[1:] in test_sequence:
            match = class_i_start[1:]
            break
        if class_i_start[2:] in test_sequence:
            match = class_i_start[1:]
            break
    return match
    

def fast_match():
    pass 


def full_match():
    pass


class_i_starts = read_json('assets/sequences/class_i_starts.json')
search_sequences = parse_search_sequences('assets/sequences/search_sequences.json','class_i')

unable_to_split = {}

poor_matches = []
possible_matches = []
good_matches = []
excellent_matches = []

def add_to_matchtype(label:str, pdb_code:str, score:float, matched_to:str):
    eval(f"{label}_matches").append({'pdb_code':pdb_code, 'score':score, 'matched_to':matched_to})
    pass

def query_localpdb(**kwargs):
    verbose = kwargs['verbose']
    config = kwargs['config']
    console = kwargs['console']
    datehash = kwargs['datehash']
    function_name = kwargs['function_name']
    output_path = kwargs['output_path']

    low = 160
    high = 500

    output_folder = f"{output_path}/{function_name}"

    folder_status = create_folder(output_folder, verbose)

    with console.status(f"Searching localpdb..."):
        lpdb = PDB(db_path=config['PATHS']['LOCALPDB_PATH'])
        results = lpdb.chains.query(f"{low} <= sequence.str.len() <= {high}")

    console.print (f"{len(results)} possible sequences matching the length criteria")
    
    unique_matches = []
    length_matches = []

    start_matches = {}
    matches_used = []

    

    with Progress() as progress:
        task = progress.add_task("[white]Processing...", total=len(results))
        for structure in results.index:
            pdb_code = results.loc[structure]['pdb'].lower()
            length_matches.append(pdb_code)
            if not pdb_code in unique_matches:
                sequence = results.loc[structure]['sequence']
                start_match = match_class_i_start(sequence)

                if start_match:
                    if not start_match in start_matches:
                        start_matches[start_match] = []
                    start_matches[start_match].append(pdb_code)
                    best_match, best_score, match_type, altered_sequence = match_class_i_sequences(sequence, pdb_code)
                    
                    best_match_slug = slugify(best_match)

                    if best_score < 0.5:
                        match_likelihood = structure_match(pdb_code, 'class_i')
                        if match_likelihood < 0.5 and best_score < 0.4:
                            add_to_matchtype('poor', pdb_code, best_score, best_match_slug)    
                            print (f"Poor match for structure chain {structure} / pdb_code {pdb_code}")
                        else:
                            add_to_matchtype('possible', pdb_code, best_score, best_match_slug)
                            print (f"Possible match for structure chain {structure} / pdb_code {pdb_code}")
                        print (f"Best match is {best_match} / score {best_score}")
                        print (f"Structure match likelihood {match_likelihood:.2f}")
                        print (f"{len(sequence)}aa")
                        print ('')
                    elif best_score >= 0.9:
                        add_to_matchtype('excellent', pdb_code, best_score, best_match_slug)
                        if not best_match in matches_used:
                            matches_used.append(best_match)
                    else:
                        # less than 0.9, but greater than 0.4
                        add_to_matchtype('good', pdb_code, best_score, best_match_slug)
                        if not best_match in matches_used:
                            matches_used.append(best_match)
                
                unique_matches.append(pdb_code)
                    
            progress.update(task, advance=1)

    action_log = {
        'sequence_length_match':{'low':low,'high':high},
        'collections': {}
    }

    collections = {}        
    for collection in ['poor_matches', 'possible_matches', 'good_matches', 'excellent_matches', 'unique_matches', 'length_matches', 'start_matches']:
        items = eval(collection)

        collections[collection] = items
        action_log['collections'][collection] = len(items)

        console.print(f"{collection}: {len(items)}")

        filename = f"{output_folder}/{collection}.json"
        write_json(filename, items, pretty=True)


    raw_output = {
        'collections': collections,
    }

    write_step_tmp_output(config['PATHS']['TMP_PATH'], function_name, raw_output, datehash, verbose=verbose)

    missing_matches = list(set(search_sequences['class_i']['labels']).difference(set(matches_used)))

    console.print (f"Match types not found {missing_matches}")

    console.print (f"Number of structures which can't have leader peptides removed: {len(unable_to_split)}")

    console.print (action_log)

    return action_log