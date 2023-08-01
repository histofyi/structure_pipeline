from typing import Dict, List, Tuple, Union

import os
import gzip

from localpdb import PDB
from fuzzywuzzy import fuzz

from rich.progress import Progress

from pipeline import create_folder

from helpers.files import read_json, write_json, write_step_tmp_output
from helpers.text import slugify

from pymol import cmd




# this creates a Pymol session so it doesn't have to be instantiated for each comparison
cmd = cmd


# the basis for structures to ignore is this file, it contains outdated structures and ones which are known to crash Pymol and are not MHC related
ignore_structures = read_json('assets/overrides/query_localpdb/ignore_structures.json')


errors = []

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


def updated_structure_match(config:Dict, structure_id:str, mhc_class:str):

    two_digit_folder = structure_id[1:3]
    structure_filepath = f"{config['PATHS']['LOCALPDB_PATH']}/pdb_chain/{two_digit_folder}/{structure_id}.pdb.gz"

    if os.path.exists(structure_filepath):
        with gzip.open(structure_filepath, 'rt') as gziphandle:
            target_structure = gziphandle.read()

        tmp_filename = 'tmp/files/tmp_structure.pdb'

        with open(tmp_filename, 'w') as writefilehandle:
            writefilehandle.write(target_structure)

        cmd.load(tmp_filename, 'target')
        cmd.load('assets/structures/class_i_1hhk.pdb', 'template')
        align = cmd.cealign('template', 'target')
        cmd.delete('all')
        match_likelihood = align['alignment_length'] / 180

        if os.path.exists(tmp_filename):
            os.remove(tmp_filename)
    else:
        errors.append({'structure':structure_id, 'error':'file_not_found'})
        match_likelihood = 0
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
        if ratio == 1.0:
            break
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
exact_matches = []

unique_matches = []
length_matches = []

start_matches = {}
matches_used = []

collections = {}


def add_to_matchtype(label:str, pdb_code:str, score:float, matched_to:str):
    eval(f"{label}_matches").append({'pdb_code':pdb_code, 'score':score, 'matched_to':matched_to})
    pass


def collate_matches(match_sets:List):
    for collection in match_sets:
        items = eval(collection)
        collections[collection] = items
    pass


def store_progress(restart:Union[List, None], match_sets:List, output_folder:str, mode='tmp'):
    for collection in match_sets:
        items = eval(collection)
        filename = f"{output_folder}/{mode}-{collection}.json"
        write_json(filename, items, pretty=True)
    if restart and mode=='tmp':
        filename = f"{output_folder}/restart.json"
        write_json(filename, restart)


def query_localpdb(**kwargs):
    verbose = kwargs['verbose']
    config = kwargs['config']
    console = kwargs['console']
    force = kwargs['force']
    datehash = kwargs['datehash']
    function_name = kwargs['function_name']
    output_path = kwargs['output_path']


    match_sets = config['CONSTANTS']['STRUCTURE_MATCH_SETS']

    low = 160
    high = 500

    output_folder = f"{output_path}/{function_name}"

    folder_status = create_folder(output_folder, verbose)

    with console.status(f"Searching localpdb..."):
        lpdb = PDB(db_path=config['PATHS']['LOCALPDB_PATH'])
        results = lpdb.chains.query(f"{low} <= sequence.str.len() <= {high}")

    console.print (f"{len(results)} possible sequences matching the length criteria")
    
    if not force:
        known_matches = read_json('assets/overrides/query_localpdb/known_matches.json')
        ignore_matches = read_json('assets/overrides/query_localpdb/ignore_matches.json')
    else:
        known_matches = []
        ignore_matches = []

    
    restart = []

    to_process = [structure for structure in results.index if structure not in restart]
    
    

    j = 0

    # set up the rich progress bar
    with Progress() as progress:
        task = progress.add_task("[white]Processing...", total=len(to_process))
        
        # then start iterating through the length matches
        for structure in to_process:

            restart.append(structure)
            
            # we'll need two core properties of each chain, its pdb_code and its sequence
            pdb_code = results.loc[structure]['pdb'].lower()
            sequence = results.loc[structure]['sequence']

            # we need to note the pdb_code in the length matches
            if not pdb_code in length_matches:
                length_matches.append(pdb_code)
            
            # then generate a unique compound key for the combination of the pdb_code and sequence
            # we do this as a compound key as each pdb_code contains many chains, each of which has a sequence
            # and each sequence can be present in multiple pdb structures
            unique_key = f"{pdb_code}_{sequence}"        

            # then iterate through the unique structures, if they're not in ignore_structures    
            if not unique_key in unique_matches and pdb_code not in ignore_structures:
                

                # then on with the matching

                # first of all is an inexpensive query, whether the sequence contains one of the class I start sequences which are reasonably conserved/unique
                start_match = match_class_i_start(sequence)

                # if there's a start match
                if start_match:

                    # we record it in the table of start matches
                    if not start_match in start_matches:
                        start_matches[start_match] = []
                    if not pdb_code in start_matches[start_match]:
                        start_matches[start_match].append(pdb_code)
                    
                    # next up, it's the second most expensive match, matching using fuzzy matching against a panel of class I and homolog sequences
                    best_match, best_score, match_type, altered_sequence = match_class_i_sequences(sequence, pdb_code)
                    

                    best_match_slug = slugify(best_match)

                    if best_score < 0.5:
                        match_likelihood = updated_structure_match(config, structure, 'class_i')
                        if match_likelihood < 0.5 and best_score < 0.4:
                            add_to_matchtype('poor', pdb_code, best_score, best_match_slug)
                            if verbose:    
                                print (f"Poor match for structure chain {structure} / pdb_code {pdb_code}")
                        else:
                            add_to_matchtype('possible', pdb_code, best_score, best_match_slug)
                            if verbose:
                                print (f"Possible match for structure chain {structure} / pdb_code {pdb_code}")
                        if verbose:
                            print (f"Best match is {best_match} / score {best_score}")
                            print (f"Structure match likelihood {match_likelihood:.2f}")
                            print (f"{len(sequence)}aa")
                            print ('')
                    elif best_score == 1.0:
                        add_to_matchtype('exact', pdb_code, best_score, best_match_slug)
                        if not best_match in matches_used:
                            matches_used.append(best_match)
                    elif best_score >= 0.9:
                        add_to_matchtype('excellent', pdb_code, best_score, best_match_slug)
                        if not best_match in matches_used:
                            matches_used.append(best_match)
                    else:
                        # less than 0.9, but greater than 0.4
                        add_to_matchtype('good', pdb_code, best_score, best_match_slug)
                        if not best_match in matches_used:
                            matches_used.append(best_match)
                
                unique_matches.append(unique_key)
            j += 1
            if j >= 1000:
                collate_matches(match_sets)
                store_progress(restart, match_sets, output_folder, mode='tmp')
                j = 0
            progress.update(task, advance=1)
    
    collate_matches(match_sets)
    
    store_progress(None, match_sets, output_folder)

    action_log = {
        'sequence_length_match':{'low':low,'high':high},
        'collections': {}
    }

    for collection in config['CONSTANTS']['STRUCTURE_MATCH_SETS']:
        items = eval(collection)
        action_log['collections'][collection] = len(items)
        console.print(f"{collection}: {len(items)}")


    raw_output = {
        'collections': collections,
    }

    write_step_tmp_output(config['PATHS']['TMP_PATH'], function_name, raw_output, datehash, verbose=verbose)

    missing_matches = list(set(search_sequences['class_i']['labels']).difference(set(matches_used)))

    console.print (f"Match types not found {missing_matches}")

    console.print (f"Match types used {matches_used}")

    console.print (f"Number of structures which can't have leader peptides removed: {len(unable_to_split)}")

    console.print (action_log)

    return action_log