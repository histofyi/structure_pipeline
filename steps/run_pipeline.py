from typing import Dict

import argparse, configparser

from pipeline import Pipeline

from steps import steps

import toml

def run_pipeline(**kwargs) -> Dict:
    pipeline = Pipeline()

    pipeline.load_steps(steps)

    #pipeline.run_step('1')  # update_localpdb
    #pipeline.run_step('2')  # fetch_stcrdab_info
    #pipeline.run_step('3')  # fetch_sabdab_info
    #pipeline.run_step('4')  # query_localpdb
    #pipeline.run_step('5')  # process_localpdb_query_matches
    #pipeline.run_step('6')  # create_core_records
    #pipeline.run_step('7')  # fetch_chronology_data
    #pipeline.run_step('8')  # fetch_title_data
    #pipeline.run_step('9')  # fetch_experimental_data
    #pipeline.run_step('10')  # fetch_publication_data
    #pipeline.run_step('11') # find_alike_chains
    #pipeline.run_step('12') # assign_species
    #pipeline.run_step('13') # assign_chain_types
    #pipeline.run_step('14') # assign_complex_type
    pipeline.run_step('15') # assign_allele_number
    
    action_logs = pipeline.finalise()

    return action_logs

def main():

    output = run_pipeline()

if __name__ == '__main__':
    main()
