#!/bin/bash

set -euox pipefail
SCRIPT_DIR=$(dirname $0)

source ../../../config.sh

# TODO
# submit paralell pm6 calculations to slurm
$LIB/ligands/submit_all_cuby.sh -m "pm6" -d $SCRATCH_DATA_DIR_02 -o $PM6_DATA_DIR -c $NUM_CPUS -s $SCRATCH_PM6_DIR

# TODO extract the best conformer and its energy
# ./lib/extract/extract_pm6_results
