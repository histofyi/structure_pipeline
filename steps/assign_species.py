from typing import Dict, List, Tuple

from helpers.files import read_json, write_json
from helpers.text import slugify
from helpers.lists import hash_array

from pipeline_specific_helpers import do_work, get_facet_path

from providers import PDBeProvider


def assign_species_action(**action_args) -> Tuple[bool, Dict, List]:
    """
    This function retrieves the molecule information for a given PDB code from the PDBe API, and then assigns a species to each chain in the structure.

    Keyword Args:
        pdb_code (str): The PDB code of the structure to be processed
        verbose (bool): Whether to print verbose output
    
    Returns:
        Tuple[bool, Dict, List]: A tuple containing a boolean indicating whether the action was successful, a dictionary of data to be stored in the output facet, and a list of errors

    """
    # Get the PDB code from the action arguments
    pdb_code = action_args['pdb_code']
    # Get the verbose flag from the action arguments
    verbose = action_args['verbose']
    # Get the output path from the action arguments
    output_path = action_args['output_path']

    # Fetch the molecule information for the given PDB code from the PDBe API
    data, success, errors = PDBeProvider(pdb_code).fetch_molecules()

    if success:
        # Read the alike_chains facet for the given PDB code
        alike_chains = read_json(get_facet_path(output_path, 'structures', 'alike_chains', pdb_code))

        # Create a dictionary of alike chains, keyed by the hash of the chain array
        hashed_alike_chains = {}

        # Iterate over the alike chains
        for chain in alike_chains['chains']:
            # Add the chain to the dictionary, keyed by the hash of the chain array
            hashed_alike_chains[hash_array(alike_chains['chains'][chain])] = {
                'chains':alike_chains['chains'][chain],
                'chain':chain
            }

        # Create a dictionary to store the species information, keyed by the chain
        species_info = {}

        # Iterate over the molecules returned from the PDBe API
        for molecule in data:
            # If the molecule has a source dictionary
            if 'source' in molecule: 
                # Hash the in_chains array
                hashed_in_chains = hash_array(molecule['in_chains'])
                # If the hash of the in_chains array is in the hashed alike chains dictionary
                if hashed_in_chains in hashed_alike_chains:
                    # If the molecule has a source dictionary with a scientific name
                    if len(molecule['source']) > 0:
                        # Add the species information to the species info dictionary, keyed by the chain
                        species_info[hashed_alike_chains[hashed_in_chains]['chain']] = {
                            'species':molecule['source'][0]['organism_scientific_name'],
                            'species_slug':slugify(molecule['source'][0]['organism_scientific_name']),
                        }

        # If the verbose flag is set to true
        if verbose:
            # output some information to the console
            print (pdb_code)
            print (species_info)
            print ('')
    else:
        # if the PDBe fetch was not successful, return a tuple containing a boolean indicating failure, a None data object, and a list of errors
        return (False, None, ['unable_to_fetch_molecules'])

    # If the species info dictionary contains any species information
    if len(species_info) > 0:
        # Return a tuple containing a boolean indicating success, the species info dictionary, and a None error list
        return (True, species_info, None)
    else:
        # If no species information was found, return a tuple containing a boolean indicating failure, a None data object, and a list of errors
        return (False, None, ['unable_to_assign_species'])



def assign_species(**kwargs):
    """
    This function assigns a species to each chain in the structure.

    Keyword Args:
        verbose (bool): Whether to print verbose output

    Returns:
        Dict: A dictionary containing the results of the action
    """
    # Set the output facet to 'species'
    output_facet = 'species'

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    action_output = do_work(new_work, assign_species_action, output_facet, input_facet=None, kwargs=kwargs)

    return action_output