from typing import Dict, List

import pandas as pd
import os

from pipeline import create_folder, get_current_time
from helpers.text import slugify
from helpers.files import write_json

from rich.progress import Progress

chain_types = {
    'abTCR': [
        {'chain':'alpha','letter':'A'},
        {'chain':'beta','letter':'B'}
    ],
    'gdTCR': [
        {'chain':'gamma','letter':'G'},
        {'chain':'delta','letter':'D'}
    ]
}

def get_ab_pdbcode_list() -> List:
    """
    This function queries SABDab using pandas to generate a list of pdbcodes contained within the resource

    Returns:
        List: a list of pdb codes relating to structures in SABDab
    """
    df = pd.read_html('https://opig.stats.ox.ac.uk/webapps/sabdab-sabpred/sabdab/search/?all=true')[0]
    pdb_codes = pd.concat([df['PDB']])
    return pdb_codes


def process_ab_data(raw_ab_dict:Dict) -> Dict:
    """
    This function takes raw information on the antibody structure and creates a dictionary structure similar to that for an tcr structure 
    
    Args:
        raw_ab_dict (Dict): the output of the fetch_ab_info function

    Returns:
        Dict: a structured dictionary of the data
    """
    i = 0
    for row in raw_ab_dict:
        if i == 0:
            chain_info = {
                    'light':{
                        'sabdab':'Lchain',
                        'chains':[]
                    },
                    'heavy':{
                        'sabdab':'Hchain',
                        'chains':[]
                    }
                }
            for item in ['heavy_species','light_species', 'heavy_subclass','light_subclass','light_ctype','scfv']:
                if row[item] == 'nan':
                    chain_info[item] = None
                else:
                    chain_info[item] = row[item]
        for chain in [('heavy','Hchain'),('light','Lchain')]:
            if chain[1] in row:
                if row[chain[1]]:
                    chain_info[chain[0]]['chains'].append(row[chain[1]])
    return chain_info


def fetch_ab_info(pdb_code):
    """
    This function downloads the summary information from SABDab and generates a simple dictionary of the fields

    Args:
        pdb_code (str): the pdb_code for the structure

    Returns:
        Dict: a simple dictionary of values from SABDab
    """
    url = f'https://opig.stats.ox.ac.uk/webapps/sabdab-sabpred/sabdab/summary/{pdb_code}/'
    try:
        raw_ab_df = pd.read_table(url, sep='\t')
        raw_ab_dict = pd.concat([
            raw_ab_df['Hchain'], 
            raw_ab_df['Lchain'], 
            raw_ab_df['heavy_species'], 
            raw_ab_df['light_species'], 
            raw_ab_df['heavy_subclass'], 
            raw_ab_df['light_subclass'], 
            raw_ab_df['light_ctype'],
            raw_ab_df['scfv']
        ], axis = 1).to_dict(orient='records')
        return raw_ab_dict
    except:
        return None


def fetch_sabdab_info(**kwargs) -> Dict:
    """
    This function retrieves the dataset of information about antibody structures from SABDab

    Args:
        **kwargs: Arbitrary keyword arguments.

    Returns
        Dict: the action output for the step (a dictionary containing lists of pdb_codes for already cached, downloaded and errors)

    Keyword Args:
        config (Dict): the dictionary of configuration
        verbose (bool): the verbosity of the output to the terminal
        force (bool): whether the whole of the dataset should be refreshed   
        output_path (str): the output path for the processed data
        console (rich.console.Console) : the console instance from the pipeline class 
    """
    config = kwargs['config']
    verbose = kwargs['verbose']
    force = kwargs['force']
    output_path = kwargs['output_path']
    console = kwargs['console']

    output_folder = f"{output_path}/ab_details"

    folder_status = create_folder(output_folder, verbose)

    pdb_codes = get_ab_pdbcode_list()

    cached = []
    downloaded = []
    errors = []

    with Progress() as progress:
        task = progress.add_task("[white]Processing...", total=len(pdb_codes))
        
        action_progress = 0
        for pdb_code in pdb_codes:
            clean_ab_info = None
            cached_info_path = f"{output_folder}/{pdb_code}.json"
            if not os.path.exists(cached_info_path) or force:
                if verbose:
                    print (f"Downloading information for {pdb_code}")
                raw_ab_info = fetch_ab_info(pdb_code)
                if raw_ab_info:
                    clean_ab_info = process_ab_data(raw_ab_info)
                    if clean_ab_info:
                        write_json(cached_info_path, clean_ab_info)
                        downloaded.append(pdb_code)
                if not clean_ab_info:
                    errors.append(pdb_code)
                if verbose and clean_ab_info:
                    print (clean_ab_info) 
            else:
                cached.append(pdb_code)
                if verbose:
                    print (f"{pdb_code} is already cached")
            action_progress += 1

            progress.update(task, advance=1)

    return {
        'downloaded':downloaded,
        'cached':cached,
        'errors':errors
    }


