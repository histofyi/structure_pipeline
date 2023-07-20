# Structure pipeline

This is the pipeline for the structure microservice of the histo.fyi website.

It's a refactoring/reworking of the existing pipeline, with the specific aim of increasing reproducibility, logging and automation.

## Files/folders required but not part of this repository

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

