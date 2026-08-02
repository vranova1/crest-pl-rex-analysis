#!/bin/bash

set -euox pipefail

# Get the directory where this script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Source the config relative to the script directory
# load PROJECT_ROOT, LIB, E_CUTOFF, CREST_RESULTS
source "$SCRIPT_DIR/../../config.sh"

# from config get some energy treshold on which to cutoff conformers/rotamers
# $LIB/extract/count_best_conformers.sh -c $E_CUTOFF -o $ENERGY_CUTOFF_TABLE $CREST_RESULTS

# separate the given number of conformers into individual .xyz files
tail -n +2 $ENERGY_CUTOFF_TABLE | while read -r ligand cutoff N N_total; do
        echo "N: $N, ligand: $ligand, cutoff: $cutoff"
        # $LIB/prep/split_conformers_single.sh $CREST_RESULTS/$ligand $N $CREST_RESULTS $SPLIT_CONFS $LIMIT
done

# make the .xyz files into sdf
$LIB/prep/update_sdf.sh -i $SPLIT_CONFS -t $DATASET -o $SDF_CONFS
