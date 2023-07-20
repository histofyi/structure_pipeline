from typing import Dict

import argparse, configparser

from pipeline import Pipeline

from steps import steps

import toml

def run_pipeline(**kwargs) -> Dict:
    pipeline = Pipeline()

    kwargs = pipeline.parse_cli_args()

    print (kwargs)
    pipeline.say_hello()


def main():

    

    output = run_pipeline()


if __name__ == '__main__':
    main()
