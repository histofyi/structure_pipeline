from typing import Dict, List, Tuple, Callable


import os 

from helpers.files import read_json, write_json, write_step_tmp_output

from pipeline import create_folder


from rich.progress import Progress


def get_overrides(pipeline_step:str) -> Tuple[Dict, Dict]:
    overrides = None
    pdb_overrides = None

    overrides_path = f"assets/overrides/{pipeline_step}"
    if os.path.exists(overrides_path):
        overrides = {filename:read_json(f"{overrides_path}/{filename}.json") for filemane in  os.listdir(overrides_path)}
        if len(overrides) > 0:
            pdb_overrides = {}
            for override in overrides:
                this_override = overrides[override]
                # TODO look at the override structures and work out a standardised way of doing this
                print (this_override)

    return (overrides, pdb_overrides)


def do_work(new_work:List, action:Callable, output_facet:str, input_facet:str=None, kwargs=None) -> Dict:
    """
    This function is used to run a function on a list of data, and return a tuple of lists of successful, unchanged and errored items.

    Args:
        new_work (List): A list of data to be processed
        action (Callable): The function to be run on each item in the list
        output_facet (str): The name of the output facet where the data will be stored

    Returns:
        Tuple[List, List, List]: A tuple containing lists of successful, unchanged and errored items

    Keyword Args:
        verbose (bool): Whether to print verbose output
        config (Dict): The configuration object
        console (Console): The Rich console object
        datehash (str): The datehash of the current pipeline run
        function_name (str): The name of the current pipeline step
        output_path (str): The path to the output folder
        force (bool): Whether to force the pipeline step to run
    """
    verbose = kwargs['verbose']
    config = kwargs['config']
    console = kwargs['console']
    datehash = kwargs['datehash']
    function_name = kwargs['function_name']
    output_path = kwargs['output_path']
    force = kwargs['force']

    unchanged = []
    successful = []
    errors = []
    applied_overrides = []

    overrides, pdb_overrides = get_overrides(function_name)

    create_folder(f"{output_path}/structures/{output_facet}", verbose)

    with Progress() as progress:
        task = progress.add_task("[white]Processing...", total=len(new_work))
        for structure in new_work:
            pdb_code = structure['pdb_code']

            facet_path = get_facet_path(output_path, 'structures', output_facet, pdb_code)

            if not force:
                if os.path.exists(facet_path):
                    existing_data = read_json(facet_path)
                else:
                    existing_data = None
            else:
                existing_data = None

            if existing_data:
                unchanged.append(pdb_code)
            else:
                structure_kwargs = structure.copy()
                for kwarg in kwargs:
                    structure_kwargs[kwarg] = kwargs[kwarg]
                success, output, error = action(input_facet=input_facet, **structure_kwargs)
                if success:
                    successful.append(pdb_code)
                    write_json(facet_path, output, verbose=verbose, pretty=True)
                else:
                    errors.append({'pdb_code':pdb_code, 'error':error})
            progress.update(task, advance=1)

    raw_output = {
        'successful':successful,
        'errors':errors,
        'unchanged':unchanged,
        'applied_overrides':applied_overrides
    }

    # then we write the raw output to a JSON file which we can interrogate later, the datehash matches the pipeline output datehash
    write_step_tmp_output(config['PATHS']['TMP_PATH'], function_name, raw_output, datehash, verbose=verbose)


    action_output = {}
    for key in raw_output:
        action_output[key] = len(raw_output[key])

    return action_output



def get_facet_path(output_path:str, domain:str, facet:str, pdb_code:str) -> str:
    return f"{output_path}/{domain}/{facet}/{pdb_code}.json"


def build_core_record(pdb_code:str) -> Dict:
    core_record = {
        "accessory_molecules": {},
        "allele": {
            "alpha": None,
            "beta": None
        },
        "assemblies": [],
        "assembly_count": None,
        "chain_count": None,
        "chronology": {
            "deposition_date": None,
            "release_date": None,
            "update_date": None
        },
        "class": None,
        "classical": None,
        "complex_type": None,
        "doi": {
            "doi": None,
            "url": None
        },
        "facets": {},
        "ligands": [],
        "locus": None,
        "manually_edited": {},
        "methodology": None,
        "missing_residues": [],
        "open_access": False,
        "organism": {},
        "pdb_code": pdb_code,
        "pdb_title": None,
        "peptide": {
            "actual_sequence": None,
            "epitope_info": {},
            "features": [],
            "full_sequence": None,
            "gap_info": {},
            "gapped_sequence": None,
            "length": {
                "numeric": None,
                "text": None

            },
            "unnatural_amino_acids": []
        },
        "publication": {},
        "resolution": None,
        "unique_chain_count": None
    }
    return core_record