from typing import Dict

import argparse, configparser

from pipeline import Pipeline

from steps import steps


def run_pipeline(**kwargs) -> Dict:
    pipeline = Pipeline(**kwargs)


def main():

    mhc_class = None

    parser = argparse.ArgumentParser(prog='Structure Pipeline',
                    description='This pipeline builds a dataset of information about 3D structures.',
                    epilog='For more information see - https://github.com/histofyi/structure_pipeline')    

    arguments = [{
            'flag':'v',
            'variable_name':'verbose',
            'help':'increases output verbosity (non-verbosity is the default)',
            'action':'store_true',
            'default':False
        },
        {
            'flag':'f',
            'variable_name':'force',
            'help':'forces reloading of underlying datasets (not forcing reload is the default)',
            'action':'store_true',
            'default':False
        },
        {
            'flag':'r',
            'variable_name':'release',
            'help':'switch between development and release modes (development mode is the default)',
            'action':'store_true',
            'default':False
        },
        {
            'flag':'a',
            'variable_name':'all_data',
            'help':'whether all data should be processed, or only new structures',
            'action':'store_true',
            'default':False
        },
        {
            'flag':'m',
            'variable_name':'mhc_class',
            'help':'switch the pipeline between MHC Class I and Class II, currently only Class I to which it defaults',
            'action':'store',
            'default':'class_i'
        }
        
    ]

    for argument in arguments:
        parser.add_argument(f"-{argument['flag']}", f"--{argument['variable_name']}", help=argument['variable_name'], action=argument['action'])

    defaults = {argument['variable_name']:argument['default'] for argument in arguments}
    parser.set_defaults(**defaults)

    kwargs = vars(parser.parse_args())

    output = run_pipeline(**kwargs)


if __name__ == '__main__':
    main()
