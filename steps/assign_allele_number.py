from typing import Dict, List, Tuple

import os
from fuzzywuzzy import fuzz


from helpers.files import read_json, write_json

from pipeline_specific_helpers import do_work, get_facet_path


matched_sequences = {}


threshold = 0.97

def check_species_loci(species_loci: Dict, species: str) -> bool:
    if species in species_loci:
        return species_loci[species]
    else:
        return False


def split_to_locus(match_allele_slug: str) -> str:
    if 'h2_' in match_allele_slug:
        locus = match_allele_slug[0:4]
    else:
        locus = '_'.join(match_allele_slug.split('_', 2)[:2])
    return locus



def do_allele_match(possible_locus, complex_species_loci, allele_slug):
    print ('doing exact match')
    print (possible_locus)
    print (allele_slug)
    pass


def do_sequence_match(test_locus, sequence, species_slug):
    matched = False
    found_match = None
    score = None
    for test_sequence in test_locus:
        if test_sequence == sequence:
            print ('EXACT MATCH')
            matched = True
            found_match = test_locus[test_sequence]['canonical_allele']
            found_match['type'] = 'exact'
            found_match['species_slug'] = species_slug
            found_match['score'] = 1.0
            score = 1.0
            break
    if not matched:
        best_score = 0
        best_match = None
        for test_sequence in test_locus:
            ratio = fuzz.ratio(test_sequence, sequence) / 100
            if ratio > best_score:
                best_score = ratio
                best_match = test_locus[test_sequence]['canonical_allele']

        if best_score > threshold:
            found_match = best_match
            found_match['type'] = 'fuzzy'
            found_match['species_slug'] = species_slug
            found_match['score'] = best_score
            score = best_score
    return found_match, score


def do_match(possible_locus, score, complex_species_loci, sequence, complex_species):
    print (len(sequence))

    # DO SOME SEQUENCE TRIMMING IF OVER 275

    found_match = None
    best_score = 0
    if possible_locus in complex_species_loci:
        print (complex_species)
        print (possible_locus)
        test_locus = complex_species_loci[possible_locus]
        found_match, score = do_sequence_match(test_locus, sequence, complex_species)
        if not found_match:
            remaining_loci = [locus for locus in complex_species_loci if locus != possible_locus]
            print (remaining_loci)
            test_loci = [locus for locus in remaining_loci]
            for test_locus in test_loci:
                print (test_locus)
                found_match, score = do_sequence_match(complex_species_loci[test_locus], sequence, complex_species)
                print (found_match)
                if score:
                    if score > threshold:
                        break
                
    else:
        print ('MISSING LOCUS')
        print (complex_species)
    return found_match
    


def assign_allele_number_action(**action_args) -> Tuple[bool, Dict, List]:
    pdb_code = action_args['pdb_code']
    verbose = action_args['verbose']
    output_path = action_args['output_path']

    errors = []

    # get the loci sequences and loci alleles from the action_args
    loci_sequences = action_args['loci_sequences']
    loci_alleles = action_args['loci_alleles']

    # get the chain type classifications from the action_args for class I
    chain_type_classifications = action_args['chain_type_classifications']['class_i']


    print (pdb_code)


    # fetch the data from previous steps
    chain_types = read_json(get_facet_path(output_path, 'structures', 'chain_types', pdb_code))
    alike_chains = read_json(get_facet_path(output_path, 'structures', 'alike_chains', pdb_code))
    species = read_json(get_facet_path(output_path, 'structures', 'species', pdb_code))

    # set the species of the complex to an initial state of none
    complex_species = None
    found_match = None

    # iterate through the chains in the complex
    for chain in chain_types.keys():
        chain_type = chain_types[chain]['chain_type']

        # if the chain type is for a classical Class I molecule, we'll try to assign an allele number
        if chain_type in chain_type_classifications['classical']:

            # get the species of the alpha chain
            complex_species = species[chain]['species_slug']

            # create a dictionary of all of the sequences for the loci of the species for which we have data from IPD
            possible_locus = split_to_locus(action_args['matched_to'])



            sequence = alike_chains['chain_sequences'][chain]
            
            if sequence[0] == 'M':
                sequence = sequence[1:]
            

            # first, we'll deal with exact matches, for this we'll look up the allele in the allele table
            if action_args['score'] == 1.0:
                
                exact_match = None
                # since it's an exact match, we just want to retrieve the details about that allele_number
                complex_loci_alleles = check_species_loci(loci_alleles, complex_species)
                if complex_loci_alleles:
                    if possible_locus in complex_loci_alleles:
                        if action_args['matched_to'] in complex_loci_alleles[possible_locus]:
                            allele_match = complex_loci_alleles[possible_locus][action_args['matched_to']]['canonical_allele']
                            
                            canonical_sequence = complex_loci_alleles[possible_locus][action_args['matched_to']]['canonical_sequence']
                            ratio = fuzz.ratio(canonical_sequence, sequence) / 100

                            if sequence in canonical_sequence or canonical_sequence in sequence or ratio == 1.0:

                                found_match = allele_match
                                found_match['type'] = 'exact'
                                found_match['species_slug'] = complex_species

                            else:
                                print (f"sequence ratio is {ratio}")
                                print (allele_match)
                                print (action_args['matched_to'])

                            print (found_match)
                else:
                    print ('EXACT MATCH')
                    print ('NO LOCI ALLELES')
                    print (possible_locus)
                    
                
            else:
                complex_loci_sequences = check_species_loci(loci_sequences, complex_species)
            
                if complex_loci_sequences:
                    if action_args['score'] > 0.8:

                        print (possible_locus)
                        found_match = do_match(possible_locus, action_args['score'], complex_loci_sequences, sequence, complex_species)
                        
                    else:
                        print ('POOR MATCH')
                print (action_args['score'])
                print (action_args['matched_to'])
                

        # if the chain type is for a nonclassical Class I molecule, we don't need to assign an allele number
        # TODO think about how to structure this information
        elif chain_type in chain_type_classifications['nonclassical']:
            complex_species = species[chain]['species_slug']
            if action_args['score'] > threshold:
                found_match = {
                    'species_slug': complex_species,
                    'type': 'nonclassical',
                    'score': action_args['score'],
                    'matched_to': action_args['matched_to']
                }
            if verbose:
                print (chain_type)
                print (action_args['score'])
                print (action_args['matched_to'])
                print (complex_species)
            break
    
    if not complex_species:
        print ('NOT IN CLASSICAL OR NONCLASSICAL')
        print (chain_type_list)
        print (species)
        errors = ['not_in_classical_or_nonclassical']

    
    print ('')

    success = False

    if found_match:
        return (True, found_match, None)
    else:

        if len(errors) == 0:
            errors = ['unable_to_assign_allele_number']

        return (False, None, errors)


def load_sequences(config, species_loci):
    loci_sequences = {}
    i = 0
    for species in species_loci:
        search_loci = [f"{species_loci[species]['stem']}_{locus}" for locus in species_loci[species]['class_i']]
        for locus in search_loci:
            sequence_filepath = f"{config['PATHS']['WAREHOUSE_PATH']}/alleles/processed_data/cytoplasmic_sequences/{locus}.json"
            if os.path.exists(sequence_filepath):
                if species not in loci_sequences:
                    loci_sequences[species] = {}
                loci_sequences[species][locus] = read_json(sequence_filepath)
                i += 1
    print (f"Loaded {i} loci sequence sets for {len(loci_sequences)} species.")
    return loci_sequences


def load_alleles(config, species_loci):
    loci_alleles = {}
    i = 0
    for species in species_loci:
        search_loci = [f"{species_loci[species]['stem']}_{locus}" for locus in species_loci[species]['class_i']]
        for locus in search_loci:
            alleles_filepath = f"{config['PATHS']['WAREHOUSE_PATH']}/alleles/processed_data/protein_alleles/{locus}.json"
            if os.path.exists(alleles_filepath):
                if species not in loci_alleles:
                    loci_alleles[species] = {}
                loci_alleles[species][locus] = read_json(alleles_filepath)
                i += 1
    print (f"Loaded {i} loci protein allele sets for {len(loci_alleles)} species.")
    return loci_alleles


def assign_allele_number(**kwargs):
    config = kwargs['config']
    verbose = kwargs['verbose']

    output_facet = 'allele'

    species_loci = read_json(f"assets/constants/species_loci.json")

    loci_sequences = load_sequences(config, species_loci)
    loci_alleles = load_alleles(config, species_loci)

    chain_type_classifications = read_json(f"assets/constants/chain_type_classifications.json")

    new_work = read_json(f"assets/overrides/query_localpdb/new_work.json")

    #new_work = new_work[:500]

    kwargs['loci_sequences'] = loci_sequences
    kwargs['loci_alleles'] = loci_alleles   
    kwargs['chain_type_classifications'] = chain_type_classifications

    action_output = do_work(new_work, assign_allele_number_action, output_facet, input_facet=None, kwargs=kwargs)

    return action_output