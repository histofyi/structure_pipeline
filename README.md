# Structure pipeline

This is the pipeline for the structure microservice of the histo.fyi website.

It's a refactoring/reworking of the existing pipeline, with the specific aim of increasing reproducibility, logging and automation.

## Files/folders required but not part of this repository

The repository is designed to work with the warehouse respository structure, but can also be set up to use local directories for input, output and logs which should be put in the root folder of the repository.

To run the repository should also include a config file (config.toml). This file is not part of the repository as it may at some point contain secrets for cloud services.

The following variables are set in the config.toml file:

INPUT_PATH
OUTPUT_PATH
ASSET_PATH
LOGS_PATH
