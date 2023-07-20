from typing import Dict

import argparse

from pipeline import Pipeline

from steps import steps

# Constants. These should be in config, but that's not loaded until after the instantiation of the Pipeline object, so these are hard coded as an exception
default_mhc_class = 'class_i'
default_data_level = 'new_only'


def run_pipeline(verbose:bool=False, force:bool=False, mode:bool='development', mhc_class:str=default_mhc_class, all_data:str=default_data_level) -> Dict:
    pipeline = Pipeline()


def main():
    parser = argparse.ArgumentParser(prog='Structure Pipeline',
                    description='This pipeline builds a dataset of information about 3D structures.',
                    epilog='For more information see - https://github.com/histofyi/structure_pipeline')
    parser.add_argument('-v','--verbose', help='increases output verbosity (non-verbosity is the default)', action='store_true')
    parser.add_argument('-f', '--force', help='forces reloading of underlying datasets (not forcing reload is the default)', action='store_true')
    parser.add_argument('-r', '--release', help='switch between development and release modes (development mode is the default)', action='store_true')
    parser.add_argument('-a', '--all_data', help='whether all data should be processed, or only new structures', action='store_true')
    parser.add_argument('-m', '--mhc_class', help='switch the pipeline between MHC Class I and Class II, currently only Class I to which it defaults')
    args = parser.parse_args() 

    if args.verbose:
        verbose = True
    else:
        verbose = False
    if args.force:
        force = True
    else:
        force = False
    if args.release:
        mode = 'release' 
    else:
        mode = 'development'    

    mhc_class = default_mhc_class
    if args.mhc_class:
        if args.mhc_class == 'class_ii':
            mhc_class = 'class_ii' 

    all_data = default_data_level
    if args.all_data:
        all_data = 'all'

    print (args)

    print (verbose)
    print (force)
    print (mode)
    print (mhc_class)
    print (all_data)

    output = run_pipeline(verbose=verbose, force=force, mode=mode, mhc_class=mhc_class, all_data=all_data)


if __name__ == '__main__':
    main()
