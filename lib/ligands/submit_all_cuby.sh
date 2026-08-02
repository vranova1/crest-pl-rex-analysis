#!/bin/bash

set -euo pipefail
SCRIPT_DIR=$(dirname $0)

CPUS=1
INPUT_DIR=""
METHOD=""
OUTPUT_DIR="$SCRIPT_DIR/cuby_out"
SCRATCH_DIR="$SCRIPT_DIR/scratch"

while getopts "c:d:o:m:s:" opt; do
  case $opt in
    c) CPUS="$OPTARG" ;;
    d) INPUT_DIR="$OPTARG" ;;
    o) OUTPUT_DIR="$OPTARG" ;;
    m) METHOD="$OPTARG" ;;
    s) SCRATCH_DIR="$OPTARG" ;;
    *) echo "Usage: $0 -d <data_dir> [-c <cpus>] [-m <method>]" >&2; exit 1 ;;
  esac
done

# --- ENFORCE MANDATORY FLAGS ---
if [[ -z "$INPUT_DIR" ]]; then
	echo "ERROR: The -d (directory with input structures) flag is required." >&2
	exit 1
fi
if [[ -z "$METHOD" ]]; then
	echo  "ERROR: The -m (method for calculation) flag is required, pm6 or xtb." >&2
fi

if [[ ! -d $INPUT_DIR ]]; then
	echo "$INPUT_DIR doesnt exist. "
	exit 1
fi


if [[ $METHOD == "pm6" ]]; then
	for ligand in ${INPUT_DIR}/*; do
		echo Processing conformers of $ligand 
		ligand_name=$(basename ${ligand})
		# SLURM_LOG_DIR=$PROJECT_ROOT/data/logs/pm6_conf/$ligand_name
		# mkdir -p $SLURM_LOG_DIR
		# echo Slurm log dir for $name is $SLURM_LOG_DIR
		
		sbatch --open-mode=append \
 		--export=ALL,LIGAND="$ligand",OUTPUT_DIR="$OUTPUT_DIR",SCRATCH_DIR="$SCRATCH_DIR",CPUS="$CPUS" \
  		"$SCRIPT_DIR/../submit/pm6_compute_ligand.sh"
		sleep 3
	done

elif [[ $METHOD == "xtb" ]]; then
	for ligand in ${INPUT_DIR}/*; do
                echo Processing conformers of $ligand
                ligand_name=$(basename ${ligand})
                SLURM_LOG_DIR=$PROJECT_ROOT/data/logs/xtb_conf/$ligand_name
                mkdir -p $SLURM_LOG_DIR
                echo Slurm log dir for $name is $SLURM_LOG_DIR

                sbatch --output="$SLURM_LOG_DIR" --open-mode=append $SCRIPT_DIR/../submit/xtb_compute_ligand.sh $ligand
                sleep 4
        done
else
	echo "Method $METHOD is not acceptable this script. "
	exit 1
fi
