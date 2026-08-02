PROJECT_ROOT="/path/to/project"

# paths:
    DATA="${PROJECT_ROOT}/data"
    LIB="${PROJECT_ROOT}/lib"
    SCRATCH="/path/to/temporary/storage"
    STEPS="${PROJECT_ROOT}/steps"
  
# compute:
    NUM_CPUS=128

# STEPS
# 01_crest
	DATA_DIR_01="${DATA}/01_data"
	METHOD="--gfn2"
    LIGAND_BATCH="$DATA_DIR_01/batch3"
    BATCH_RESULTS="$DATA_DIR_01/batch_3_results"

	CURRENT_STRUCTURES_SDF="${DATA_DIR_01}/511_shortcut_structures"

	# currently used global minimum estimate structures
	CREST_DATA_TO_COMPUTE="${DATA}/pl_rex"
	CREST_COMPUTED_DATA="${DATA_DIR_01}/gfn2_on_pl_rex"
# 02_conformer_preparation
	DIR_02="${STEPS}/02_conformer_preparation"
	DATA_DIR_02="${PROJECT_ROOT}/data/02_data"

# 03_conformer_refinement
	SCRATCH_DATA_DIR_02="${SCRATCH}/02_data/sdf_rotamers/"
	SCRATCH_DATA_DIR_03="${SCRATCH}/03_data"
	DATA_DIR_03="${DATA}/03_data"
	PM6_DATA_DIR="${DATA_DIR_03}/pm6/rotamers"
	PM6_STEPS_DIR="${PROJECT_ROOT}/steps/03_conformer_refinement/pm6"
	SCRATCH_PM6_DIR="${SCRATCH}/03_data/pm6/rotamers/"
