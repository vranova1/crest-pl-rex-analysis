#!/bin/bash

set -euo pipefail

# handle symlinks
SOURCE="${BASH_SOURCE[0]}"
if [ -L "$SOURCE" ]; then
        SOURCE="$(readlink "$SOURCE")"
fi
echo $SOURCE

SCRIPT_DIR="$(dirname "$SOURCE")"

print_usage() {
        printf "Usage: count_best_conformers.sh[OPTIONS] SPLIT_CONFORMERS_DIR
        Positional arguments:

        Options:
         -t DIR                 Directory with template sdf files
         -o DIR                 Write results to DIR, default set to SCRIPT_DIR/updated_sdf
	 -i DIR                 DIR where are stored new xyz files, can be multiple conformers for each ligand (DIR/ligand/conformers/conf_1)"
}
# Should later make -r/c option for conformers or rotameres

output_dir=$SCRIPT_DIR/updated_sdf
template=$SCRIPT_DIR/dataset

while getopts 't:o:i:' flag; do
  case "${flag}" in
    t) template="${OPTARG}" ;;
    o) output_dir="${OPTARG}" ;;
    i) input_dir="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

shift $((OPTIND - 1))

mkdir -p $output_dir

for ligand in $input_dir/*; do
	ligand_name=$(basename "${ligand}" .xyz)
	echo "Processing $ligand_name "
	
	# Create clean directory for new SDFs
	if [[ -d $output_dir/$ligand_name ]]; then
		rm -r $output_dir/$ligand_name
	fi
	# mkdir -p $output_dir/$ligand_name

	ligand_sdf=$template/"${ligand_name}".sdf

	# for conformer in $input_dir/$ligand_name/*.xyz; do
	# 	conf_name=$(basename "${conformer}" .xyz)
	#	updated_sdf=$output_dir/$ligand_name/"${conf_name}.sdf"
	
	updated_sdf=$output_dir/$ligand_name.sdf

		# echo cuby -j geometry --geometry-action none -g $ligand_sdf --geometry_update_coordinates $conformer --geometry-write-format sdf --geometry-write $updated_sdf

		# cuby -j geometry --geometry-action none -g $ligand_sdf --geometry_update_coordinates $conformer --geometry-write-format sdf --geometry-write $updated_sdf
	~/iocb/software/cuby4/cuby4 -j geometry --geometry-action none -g $ligand_sdf --geometry_update_coordinates $ligand --geometry-write-format sdf --geometry-write $updated_sdf
	
	# done
done
