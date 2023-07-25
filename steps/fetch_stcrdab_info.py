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

def get_tcr_pdbcode_list():
    df = pd.read_html('http://opig.stats.ox.ac.uk/webapps/stcrdab/Browser?all=true')[0]
    pdb_codes = pd.concat([df['PDB']])
    return pdb_codes


def chain_set_template():
  return {
      'chains':[],
      'subgroup':''
  }


def process_tcr_data(raw_tcr_dict, pdb_code):
  for row in raw_tcr_dict:
    clean_tcr_dict = {}
    if str(row['TCRtype']) != 'nan':
      clean_tcr_dict['pdb_code'] = pdb_code
      chain_type = chain_types[row['TCRtype']]
      for chain_row in chain_type:
        if str(row['mhc_type']) != 'nan':
          if row['mhc_type'] == 'MH1':
            clean_tcr_dict['mhc_type'] = 'class_i'
          elif row['mhc_type'] == 'MH2':
            clean_tcr_dict['mhc_type'] = 'class_ii'
        if not chain_row['chain'] in clean_tcr_dict:
          clean_tcr_dict[chain_row['chain']] = chain_set_template()
        clean_tcr_dict[chain_row['chain']]['chains'].append(row[f'{chain_row["letter"]}chain'])
        if not pd.isna(row[f'{chain_row["chain"]}_subgroup']):
            clean_tcr_dict[chain_row['chain']]['subgroup'] = row[f'{chain_row["chain"]}_subgroup']
        else:
            clean_tcr_dict[chain_row['chain']]['subgroup'] = None
    else:
      clean_tcr_dict = None
    return clean_tcr_dict


def fetch_tcr_info(pdb_code):
  url = f'http://opig.stats.ox.ac.uk/webapps/stcrdab/summary/{pdb_code}'
  raw_tcr_df = pd.read_table(url, sep='\t')
  raw_tcr_dict = pd.concat([
    raw_tcr_df['Achain'], 
    raw_tcr_df['Bchain'], 
    raw_tcr_df['Gchain'], 
    raw_tcr_df['Dchain'], 
    raw_tcr_df['TCRtype'], 
    raw_tcr_df['mhc_type'], 
    raw_tcr_df['antigen_chain'], 
    raw_tcr_df['mhc_chain1'], 
    raw_tcr_df['mhc_chain2'],
    raw_tcr_df['alpha_subgroup'],
    raw_tcr_df['beta_subgroup'],
    raw_tcr_df['gamma_subgroup'],
    raw_tcr_df['delta_subgroup'],
  ], axis = 1).to_dict(orient='records')
  return raw_tcr_dict


def fetch_stcrdab_info(**kwargs):
    
    config = kwargs['config']
    verbose = kwargs['verbose']
    force = kwargs['force']
    output_path = kwargs['output_path']
    console = kwargs['console']

    tcr_structures = {}

    output_folder = f"{output_path}/tcr_details"

    folder_status = create_folder(output_folder, verbose)

    pdb_codes = get_tcr_pdbcode_list()

    cached = []
    downloaded = []
    errors = []

    with Progress() as progress:
        task = progress.add_task("[white]Processing...", total=len(pdb_codes))
        
        action_progress = 0
        for pdb_code in pdb_codes:
            cached_info_path = f"{output_folder}/{pdb_code}.json"
            if not os.path.exists(cached_info_path):
                if verbose:
                    print (f"Downloading information for {pdb_code}")
                raw_tcr_info = fetch_tcr_info(pdb_code)
                clean_tcr_info = process_tcr_data(raw_tcr_info, pdb_code)
                if clean_tcr_info:
                    write_json(cached_info_path, clean_tcr_info)
                    downloaded.append(pdb_code)
                else:
                    errors.append(pdb_code)
                if verbose:
                    print (clean_tcr_info) 
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


