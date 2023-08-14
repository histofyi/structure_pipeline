from typing import Dict, List, Tuple, Union

from localpdb import PDB
from fuzzywuzzy import fuzz


from helpers.files import read_json, write_json, write_step_tmp_output

from pipeline_specific_helpers import get_facet_path, build_core_record, do_work


def reorganize_array(similar_chains:List[Tuple[str,str,float]], unique_chains:List[str]) -> Dict[str,List[str]]:
    """
    This function reorganizes the similar chains and unique chains into a dictionary.

    Args:
        similar_chains (List[Tuple[str,str,float]]): The list of similar chains.
        unique_chains (List[str]): The list of unique chains.

    Returns:
        Dict[str,List[str]]: The dictionary of similar chains and unique chains.
    """
    # Create a dictionary to store the similar chains and unique chains
    result_dict = {}
    # Create a set to store the chains that have already been matched
    already_matched = set()

    # Iterate over the similar chains
    for a, b, score in similar_chains:
        # If the chain has not already been matched, then add it to the dictionary
        if a not in already_matched:
            # create an initial record for the first matched chains
            result_dict[a] = [a,b]
            # add both chains to the already matched set
            already_matched.add(a)
            already_matched.add(b)
        else:
            # if the chain isn't already in the dictionary, and the second chain hasn't been matched
            if a in result_dict and b not in already_matched:
                # add the second chain to the dictionary
                result_dict[a].append(b)
                # add the second chain to the already matched set
                already_matched.add(b)
    
    # then iterate through the unique chains (ones which don't have a match) 
    for chain in unique_chains:
        # if the chain hasn't already been matched, then add it to the dictionary
        if chain not in already_matched:
            # create a record for each unmatched chain (referencing itself)
            result_dict[chain] = [chain]
    # return the dictionary
    return result_dict


def find_unmatched_chains(chain_list:List[Dict[str,str]], matched_chains:List[str]) -> List[str]:
    """
    This function finds the chains that have not been matched.

    Args:
        chain_list (List[Dict[str,str]]): The list of chains.
        matched_chains (List[str]): The list of chains that have been matched.

    Returns:
        List[str]: The list of chains that have not been matched.
    """
    # Create a list to store the chains that have not been matched
    unmatched_chains = []

    # Iterate over the chains in the chain list
    for chain in chain_list:
        # If the chain has not been matched, then add it to the list of unmatched chains
        if chain['label'] not in matched_chains:
            unmatched_chains.append(chain['label'])
    
    # Return the list of unmatched chains
    return unmatched_chains



def match_chains(chain_list: List[Dict[str,str]], threshold:float = 0.95) -> Tuple[List[Tuple[str,str,float]], List[str]]:
    # Create a list to store the chains that are similar to each other
    similar_chains = []
    # Create a list to store the chains that have been matched
    matched_chains = []
    # Iterate over the chains in the chain list
    for i in range(len(chain_list)):
        # Iterate over the chains in the chain list starting from the next chain after the current chain
        for j in range(i+1, len(chain_list)):
            # Calculate the similarity between the sequences of the two chains
            similarity = fuzz.ratio(chain_list[i]['sequence'], chain_list[j]['sequence']) / 100
            # If the similarity is greater than or equal to the threshold, then the chains are similar and append them to the list of similar chains
            if similarity >= threshold:
                similar_chains.append((chain_list[i]['label'], chain_list[j]['label'], similarity))
                # If the first chain has not already been matched, then add it to the list of matched chains
                if chain_list[i]['label'] not in matched_chains:
                    matched_chains.append(chain_list[i]['label'])
                # If the second chain has not already been matched, then add it to the list of matched chains
                if chain_list[j]['label'] not in matched_chains:
                    matched_chains.append(chain_list[j]['label'])
    return similar_chains, matched_chains


def find_alike_chains_action(**action_args) -> Tuple[bool, Dict, List]:
    """
    This function finds chains that are similar to each other in a PDB structure.

    Returns:
        Tuple[bool, Dict, List]: A tuple containing a boolean indicating whether the action was successful, a dictionary containing the output of the action, and a list of any errors encountered.

    Keyword args:
        pdb_code (str): The PDB code of the structure to be processed
        all_chains (DataFrame): A dataframe containing all the chains in the PDB
        verbose (bool): Whether to print verbose output
    """

    # Get the keyword arguments
    pdb_code = action_args['pdb_code']
    all_chains = action_args['all_chains']
    verbose = action_args['verbose']

    # Get a list of the chains in the structure, each of these items is of the format 'pdb_code_chain_label' e.g. '1abc_A'
    structure_chains = [chain for chain in all_chains.loc[all_chains['pdb'] == pdb_code].index]

    # Get the sequences of the chains in the structure
    structure_sequences = [all_chains.loc[chain]['sequence'] for chain in structure_chains]
    # Get the labels of the chains in the structure that are of the format 'chain_label' e.g. 'A' by splitting the chain labels on the underscore
    chain_labels = [chain.split('_')[1] for chain in structure_chains]

    # Create a list of dictionaries containing the chain label and sequence for each chain in the structure
    chain_list = [{'label':chain_label, 'sequence':structure_sequence} for chain_label, structure_sequence in zip(chain_labels, structure_sequences)]
    
    # Get the number of chains in the structure
    found_chain_count = len(chain_list)


    # now start processing the data
    # first, find the chains that are similar to each other
    similar_chains, matched_chains = match_chains(chain_list)

    # then, find the chains that have no similar chains
    unmatched_chains = find_unmatched_chains(chain_list, matched_chains)

    # then, reorganize the similar chains and unique chains into a dictionary
    chain_dictionary = reorganize_array(similar_chains, unmatched_chains)

    # then, get the total number of matched chains
    matched_chain_count = sum(len(values) for values in chain_dictionary.values())

    # if the total number of matched chains is the same as the number of chains found in the structure
    if matched_chain_count == found_chain_count:
        # build the alike chains dictionary
        alike_chains = {
            'chains': chain_dictionary,
            'subunit_count': len(chain_dictionary),
            'assembly_count': min(len(values) for values in chain_dictionary.values()),
            'total_chain_counts': matched_chain_count,
            'raw_similarity': similar_chains,
            'chain_sequences': {chain_label: structure_sequences[chain_labels.index(chain_label)] for chain_label in chain_dictionary.keys()}
        }
    else:
        # else create an empty alike chains dictionary
        alike_chains = {}

    # if verbose output is enabled, print the pdb code, the alike chains dictionary, and a blank line
    if verbose:
        print (pdb_code)
        print (alike_chains)
        print ('')

    # return a tuple containing a boolean indicating whether the action was successful, the alike chains dictionary, and a list of any errors encountered
    if len(alike_chains) > 0:
        return (True, alike_chains, None)
    else:
        return (False, None, ['unable_to_fetch_or_find_alike_chains'])


def find_alike_chains(**kwargs):
    """
    This function simply calls the do_work function with the find_alike_chains_action function and the appropriate input and output facets.

    Returns:    
        Dict: The action output for the work done.
    """

    config = kwargs['config']
    console = kwargs['console']

    with console.status(f'Spinning up localpdb...'):
        localpdb_path = config['PATHS']['LOCALPDB_PATH']
        lpdb = PDB(db_path=localpdb_path)
        all_chains = lpdb.chains

    # Set the output facet to publication.
    output_facet = 'alike_chains'

    # Fetch the new work from the file.
    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    kwargs['all_chains'] = all_chains

    # Call the do_work function with the find_alike_chains_action function and the appropriate input and output facets.
    action_output = do_work(new_work, find_alike_chains_action, output_facet, input_facet=None, kwargs=kwargs)

    # Return the action output to the pipeline for logging.
    return action_output

    
        
