from typing import Dict

import argparse, configparser

from pipeline import Pipeline

from steps import steps

import toml

def run_pipeline(**kwargs) -> Dict:
    pipeline = Pipeline()
    pipeline.load_steps(steps)

    pipeline.run_step('1')

    action_logs = pipeline.finalise()

    return action_logs

def main():

    output = run_pipeline()

if __name__ == '__main__':
    main()
