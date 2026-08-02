#!/bin/bash

source ../../config.sh

for ligand in $CREST_DATA_TO_COMPUTE/*; do
	job_id=$(sbatch --open-mode=append "${LIB}"/submit/compute_xtb_energy.sh "$ligand" | awk '{print $4}')
	echo "Job ID: $job_id for ligand $ligand"
	sleep 3
done
