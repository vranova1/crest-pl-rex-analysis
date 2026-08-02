#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "${PROJECT_ROOT}"

source lib/config.sh
export PATH=~/programs/cuby4/cuby.rb:$PATH

mkdir -p methods/gfnff/updated_sdf

for ligand in "${PROJECT_ROOT}"/geometries/*/*/511-optimized_ligand.xyz; do
        ligand_name=$(basename "${ligand}".xyz)
	name=$(echo $ligand | cut -d'/' -f6,7)
	name2=$(echo $name | sed -e 's/calculation/_/g' | tr -d '/')
        echo "Processing $name2 "

        ligand_sdf=data/"${name2}".sdf
        updated_sdf=methods/gfnff/updated_geoms/"${name2}_new.sdf"


        echo "cuby -j geometry --geometry-action none -g $ligand_sdf --geometry_update_coordinates $ligand --geometry-write-format sdf --geometry-write $updated_sdf"

        ~/programs/cuby4/cuby4.rb -j geometry --geometry-action none -g $ligand_sdf --geometry_update_coordinates $ligand --geometry-write-format sdf --geometry-write $updated_sdf
done
