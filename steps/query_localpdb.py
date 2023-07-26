from typing import Dict, List, Tuple

from localpdb import PDB
from fuzzywuzzy import fuzz

from rich.progress import Progress


from helpers.files import read_json
from helpers.text import slugify


class_i_starts = read_json('assets/sequences/class_i_starts.json')
search_sequences = read_json('assets/sequences/search_sequences.json')

unable_to_split = {}

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
    return match
    

def query_localpdb(**kwargs):
    config = kwargs['config']
    console = kwargs['console']

    with console.status(f"Searching localpdb..."):
        lpdb = PDB(db_path=config['PATHS']['LOCALPDB_PATH'])
        results = lpdb.chains.query(f"{160} < sequence.str.len() < {500}")

    console.print (f"{len(results)} possible sequences matching the length criteria")
    possible_class_i = []
    already_matched = []
    start_matches = {}
    fuzzy_matches = {}

    matches_used = []

    match_types = {}

    poor_matches = []

    j = 0
    with Progress() as progress:
        task = progress.add_task("[white]Processing...", total=len(results))
        for structure in results.index:
            pdb_code = results.loc[structure]['pdb'].lower()
            if not pdb_code in already_matched:

                sequence = results.loc[structure]['sequence']
                start_match = match_class_i_start(sequence)

                if start_match:
                    if not start_match in start_matches:
                        start_matches[start_match] = []
                    start_matches[start_match].append(pdb_code)
                    best_match, best_score, match_type, altered_sequence = match_class_i_sequences(sequence, pdb_code)
                    if match_type not in match_types:
                        match_types[match_type] = []
                    match_types[match_type].append(pdb_code)
                    if best_match:
                        best_match_slug = slugify(best_match)
                        if not best_match_slug in fuzzy_matches:
                            fuzzy_matches[best_match_slug] = []
                        fuzzy_matches[best_match_slug].append(pdb_code)

                        if not best_match in matches_used:
                            matches_used.append(best_match)
                    if best_score < 0.7:
                        poor_matches.append(pdb_code)
                        print (f"Poor match for structure chain {structure} / pdb_code {pdb_code}")
                        print (f"Best match is {best_match} / score {best_score}")
                        print (f"{len(sequence)}aa")
                        print (altered_sequence)
                        print ('')
                    j += 1
                    possible_class_i.append(pdb_code)
                    already_matched.append(pdb_code)
            progress.update(task, advance=1)
            


    
    console.print ('')

    console.print (f"{j} possible sequences contain a Class I start")
    
    missing_matches = list(set(search_sequences['class_i']['labels']).difference(set(matches_used)))

    console.print (f"Matches not found {missing_matches}")

    console.print (f"Number of poor matches: {len(poor_matches)}")

    console.print (f"Number of structures which can't have leader peptides removed: {len(unable_to_split)}")