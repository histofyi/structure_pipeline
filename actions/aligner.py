import argparse
from rich import print
from rich.console import Console
console = Console()

from typing import List, Dict

from pymol import cmd

import os, sys

import datetime




canonical_structures = {
        'class_i': '1hhk'
    }

alignment_residues = [(3,13),(20,37),(43,48),(92,103),(110,127),(133,135)]

fixed_label = 'alignment_region'
canonical_label = 'canonical'
mobile_label = 'mobile_structure'

def get_canonical_structure_path(asset_path, mhc_class):
    return f'{asset_path}/structures/{mhc_class}_{canonical_structures[mhc_class]}.pdb'


def build_alignment_residue_list(alignment_residues:List) -> List:
    alignment_residue_list = []
    for low_high in alignment_residues:
        low = low_high[0]
        high = low_high[1]

        i = low
        while i <= high:
            i += 1
            alignment_residue_list.append(i)
    return alignment_residue_list


def build_pymol_selection_command(alignment_residues:List) -> str:
    pymol_selection_cmd = f"{canonical_label} and resi "
    for residue_id in build_alignment_residue_list(alignment_residues):
        pymol_selection_cmd += f'{residue_id}+'
    pymol_selection_cmd = pymol_selection_cmd[0:-1]    
    return pymol_selection_cmd


def pymol_alignment(asset_path:str, input_path:str, output_path:str, mhc_class:str, filename:str, alignment_structure:str) -> Dict:
    console.print('[white]Loading static structure')
    if alignment_structure is not None:
        aligned_against = alignment_structure
        cmd.load( f'{input_path}/{alignment_structure}', canonical_label, quiet=1)        
    else:
        aligned_against = canonical_structures[mhc_class]
        cmd.load( f'{asset_path}/structures/{mhc_class}_{aligned_against}.pdb', canonical_label, quiet=1)
    console.print('[white]Selecting alignment residues')
    cmd.select(fixed_label, build_pymol_selection_command(alignment_residues))
    console.print('[white]Loading mobile structure')
    
    cmd.load(f'{input_path}/{filename}', mobile_label, quiet=1)
    console.print('[white]Performing alignment')
   
    align = cmd.align(mobile_label, 'alignment_region')
    cmd.delete(canonical_label)

    for file_type in ['pdb', 'cif']:
        file_name = f"{output_path}/{filename.split('.')[0]}_aligned.{file_type}"
        cmd.save(file_name)

    alignment_data = {
        'filename':filename,
        'alignment_information':dict(zip(['rmsd','atom_count','cycle_count','starting_rmsd','starting_atom_count','match_align_score','aligned_residue_count'], list(align))),
        'aligned_against':aligned_against,
        'alignment_residues':build_alignment_residue_list(alignment_residues)
    }

    return alignment_data


def align_action(config:Dict, mhc_class:str, file_name:str, alignment_structure=None, quiet=False):
    align_data = pymol_alignment(config['ASSET_PATH'], config['INPUT_PATH'], config['OUTPUT_PATH'], mhc_class, file_name, alignment_structure)
    if not quiet:
        console.print(align_data)
    return align_data


def main():

    from shared.pipeline import load_config
    from shared.files import build_structure_filename

    parser = argparse.ArgumentParser(description='Aligns an MHC structure to a canonical one for its class, or to a supplied structure file.')

    parser.add_argument('-c', '--mhc_class')      # the class of MHC molecule
    parser.add_argument('-a', '--alignment_structure')      # the structure to be aligned to
    parser.add_argument('-p', '--pdb_code')      # the pdb_code of the molecule to be aligned
    parser.add_argument('-i', '--assembly_id')      # the assembly_id of the molecule to be aligned
    parser.add_argument('-n', '--filename')      # the filename of the molecule to be aligned
    parser.add_argument('-f', '--format')      # the format of the molecule to be aligned

    args = parser.parse_args()
    input_errors = []

    if args.format is None:
        format = 'pdb'
    else:
        format = args.format

    if args.mhc_class is None and args.alignment_structure is None:
        input_errors.append('[white]- an MHC class')
    if args.filename is None and (args.pdb_code is None  and args.assembly_id is None or args.assembly_id is None):
        input_errors.append("[white]- either a filename or a pdb code and assembly_id") 

    if input_errors:
        console.print("[red]Errors!")
        console.print("[white]Please supply the required inputs:")
        for error in input_errors:
            console.print(error)
    else:
        config = load_config()

        if args.filename:
            filename = args.filename
        else:
            filename = build_structure_filename(args.pdb_code, args.assembly_id, 'pdb')
        console.print(align_action(config, args.mhc_class, filename, quiet=True))
    pass


if __name__ == '__main__':
    main()








