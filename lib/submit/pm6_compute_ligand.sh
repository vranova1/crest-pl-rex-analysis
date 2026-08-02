#!/bin/bash

#SBATCH --job-name pm6_crest
#SBATCH --time=0-0:35
#SBATCH --partition=b64_any
#SBATCH --ntasks-per-node=1
#SBATCH --mem=10G

set -euox pipefail

export PATH=~/programs/cuby4:$PATH

source /uochb/soft/generic/anaconda/202402/etc/profile.d/conda.sh
conda activate cuby_env
# module purge
# module load Anaconda3
# source /apps/all/Anaconda3/2024.02-1/etc/profile.d/conda.sh
# conda activate crest-clean

# handle symlinks
SOURCE="${BASH_SOURCE[0]}"
if [ -L "$SOURCE" ]; then
        SOURCE="$(readlink "$SOURCE")"
fi
echo $SOURCE

SCRIPT_DIR="$(dirname "$SOURCE")"

# while getopts "c:d:o:m:s:" opt; do
#    case $opt in
#	l) LIGAND="$OPTARG" ;;
#	o) OUTPUT_DIR="$OPTARG" ;;
#	s) SCRATCH_DIR="$OPTARG" ;;
#	c) CPUS="$OPTARG" ;;
# 	*) echo "Usage: $0 -l <ligand_dir> [-c <cpus>] -o <output_dir> -s <scratch_dir>" >&2; exit 1 ;;
#    esac
# done

ligand_name=$(basename "${LIGAND}")

# Define working directory on fast scratch storage
WORKDIR=${SCRATCH_DIR}/pm6/$ligand_name
if [[ -d $WORKDIR ]]; then
	rm -r $WORKDIR
fi
mkdir -p $WORKDIR

RESULTS=$OUTPUT_DIR/$ligand_name
if [[ -d $RESULTS ]]; then
	rm -r $RESULTS
fi
mkdir -p $RESULTS

charge=$(awk '/<charge>/{getline; print; exit}' $LIGAND| tr -d '[:space:]')
echo "Charge of $ligand_name is $charge "

cd $WORKDIR

# check mopac is there
/home/vranova/programs/mopac --version


# -----------------------------------
# PARALLEL CONFORMER PM6 COMPUTATIONS
# -----------------------------------

COUNTER=0
MAXJOBS=128

# for c in $LIGAND/conf_*.sdf; do
	c=$LIGAND
#( 
num=$(basename ${c} .sdf) #| cut -d _ -f 2)
	echo $num

	mkdir -p $num
	cd $num

	# prepare cuby input file (update ligand name in geometry: and charge_from_file: 
	cat >$WORKDIR/optimize_pm6scoring_conf_"${num}".yaml <<EOL
geometry: ${c}
charge_from_file: ${c}

job: optimize
optimizer: lbfgs
opt_quality: 0.5
maxcycles: 500
optimize_print: steps_as_dots, final_energy
history_freq: 0

interface: mopac
mopac_exe: /home/vranova/programs/mopac
mopac_custom_exe: no
method: pm6
mopac_mozyme: yes
modifiers: dispersion3, h_bonds4, x_bond, forcefield
mopac_relscf: 0.1
mopac_damp_scf: 0.5
modifier_dispersion3:
  d3_hh_fix_version: 2
# H-bonds correction: no scaling for charged groups
modifier_h_bonds4:
  h_bonds4_scale_charged: no
  h_bonds4_extra_scaling: {}
  h_bonds4_pt_corr: 18
  # New parameters
  h_bonds4_parameters:
    multiplier_wh_o: 0.4090
    oh_o: 1.8934
    oh_n: 3.2864
    nh_o: 0.4462
    nh_n: 1.6095
    # The rest are default values
    multiplier_coo: 1.41
    multiplier_nh4: 3.61
modifier_x_bond:
  xbond_parameters:
    :Cl:
      :N: [990079.0, -6.915]
      :O: [100891.0, -5.217]
      :S: [516740.0, -4.537]
    :Br:
      :N: [23215.0, -2.792]
      :O: [1485982.0, -5.131]
      :S: [131621890.0, -6.471]
    :I:
      :N: [13473085.0, -5.594]
      :O: [1484563.0, -4.738]


# Repulsive correction for S-O and S-N contacts
modifier_forcefield:
   forcefield_nonbonded:
      - {atomtype1: "^S:", atomtype2: "^N:", equation: "4.8596e6 * Math::exp(-5.1861 * r)", derivative: "-5.1861 * 4.8596e6 * Math::exp(-5.1861 * r)"}
      - {atomtype1: "^S:", atomtype2: "^O:", equation: "4.8677e6 * Math::exp(-5.1766 * r)", derivative: "-5.1766 * 4.8677e6 * Math::exp(-5.1766 * r)"}

solvent_model: cosmo
mopac_cosmo_nspa: 122

mopac_setpi_from_file: ${c}
mopac_setcharge: { "%atomtype(N:S1H1)": -1 }
# mopac_setcharge_from_file: ''

EOL

	# cat $WORKDIR/optimize_pm6scoring.yaml

	# run cuby
	/home/vranova/programs/cuby4/cuby4 $WORKDIR/optimize_pm6scoring_conf_"${num}".yaml > $RESULTS/conf_${num}_pm6e_log.txt
	
	mv optimized.xyz optimized_conf_$num.xyz
	cp optimized_conf_$num.xyz $OUTPUT_DIR/$ligand_name/
	cd ..
	rm -r $num

#	) &

	COUNTER=$((COUNTER + 1))
	
	# If enough jobs running, wait for them to finish
    	if [[ $COUNTER -ge $MAXJOBS ]]; then
        	wait
        	COUNTER=0
    	fi
# done

wait

echo "All $ligand_name conformers computed. "

# copy optimized molecule to results
