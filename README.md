# Structure pipeline

This is the pipeline for the structure microservice of the histo.fyi website.

It's a refactoring/reworking of the existing pipeline, with the specific aim of increasing reproducibility, logging and automation.

## Project setup

The project relies on a conda environment so that steps involving the pymol can be run. Pymol is quite picky about python version and pymol version for the conda install. The following are known to work on some machines. 

```sh
conda create --name envionmentname python=3.8.8
conda activate envionmentname
```

Pip needs upgrading to a recent version if editable packages are needed

```sh
conda install pip
```

Pymol can then be installed through conda. Version 2.5.5 is known to work with Python 3.8.8 in a conda environment.

```sh
conda install -c schrodinger pymol
```


## Setup

The pipeline will need to have three directories created in the root of the folder:

- `tmp`
- `output`
- `logs`

These are not included in this repository as they will be filled with the outputs of steps. They are automatically created if they don't already exist in the first step of the pipeline.

The pipeline also needs some TOML formatted configuration files which are modular and assembled into a confg dictionary by the load_config() function in common/pipeline.py.

There are five files in total. 

### config.toml

Included in the repository. This file contains the filenames for the other configuration files.

### constants.toml

Included in the repository. This file contains constants used by the pipeline.

### dependencies.toml

Included in the repository. This file contains details of the dependency files used by the pipeline.

### paths.toml

Not included in the repository as it will depend on each user's directory structure.

Parameters for the following keys must be included.

- `WAREHOUSE_PATH`
- `PIPELINE_PATH`
- `TMP_PATH`
- `OUTPUT_PATH`
- `LOG_PATH`
- `LOCALPDB_PATH`

### secrets.toml

Currently not yet used. Will be used for uploading logs and compiled files to AMAZON S3 for the histo.fyi implementation of this pipeline.

## localpdb

The pipeline makes heavy use of the [localpdb](https://github.com/labstructbioinf/localpdb) python library. This creates a local copy of the protein databank that can be queried. [Citation](https://academic.oup.com/bioinformatics/article/38/9/2633/6535229)
